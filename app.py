# 主程式：初始化、側欄、分頁、告知彈窗、自動存檔（負責：A）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

from logic.members import next_member_id, remove_member
from logic.storage import load_json, save_json
from ui.assign import render_assign_section
from ui.availability import render_availability_tab
from ui.metrics import render_metrics_section
from ui.state import update_tasks
from ui.tasks import render_tasks_tab

# 資料夾以本檔所在位置為基準，從其他資料夾啟動也讀得到（spec 13）
DATA_DIR = Path(__file__).parent / "data"
DEMO_DIR = DATA_DIR / "demo"

# 15.2 的共用 key；其他 key 都是各畫面自用的暫存 key
SHARED_KEYS = ["project", "members", "tasks", "tasks_version", "capacities", "settings"]

# 彈窗裡寫的 AI 服務名稱（spec 5.5 選定的服務）
AI_SERVICE_NAME = "Google Gemini API"

# 新專題預設的專題期間：從今天起 4 週
DEFAULT_PROJECT_WEEKS = 4


def init_state():
    """初始化 session_state：沒有該 key 時才從 data/ 載入，避免蓋掉畫面上的修改。
    輸入：無
    輸出：無
    """
    if "project" not in st.session_state:
        st.session_state["project"] = _load_project(DATA_DIR / "project.json")
    if "members" not in st.session_state:
        st.session_state["members"] = load_json(str(DATA_DIR / "members.json"), {"members": []})["members"]
    if "tasks" not in st.session_state:
        st.session_state["tasks"] = load_json(str(DATA_DIR / "tasks.json"), {"tasks": []})["tasks"]
    if "tasks_version" not in st.session_state:
        st.session_state["tasks_version"] = 0
    if "capacities" not in st.session_state:
        st.session_state["capacities"] = {}
    if "settings" not in st.session_state:
        default_settings = {"notice_accepted": False, "ai_enabled": False}
        loaded_settings = load_json(str(DATA_DIR / "settings.json"), default_settings)
        # 舊檔案少了欄位時，用預設值補齊
        st.session_state["settings"] = {**default_settings, **loaded_settings}


def show_notice():
    """顯示資料使用告知彈窗（spec 5.6），按下選項時立即寫入 data/settings.json。
    輸入：無
    輸出：無
    """
    settings = st.session_state["settings"]
    first_time = not settings.get("notice_accepted", False)
    # 側欄按「資料使用說明」時設成 True，選完才清掉；
    # 彈窗的按鈕要在下一次重跑時還有呼叫彈窗，按下去才會生效
    reopened = st.session_state.get("app_show_notice", False)
    if not first_time and not reopened:
        return

    _notice_dialog()
    if first_time:
        # 第一次使用：還沒選擇前不顯示主畫面（spec 5.6）
        st.stop()


def render_sidebar():
    """畫出側欄：專題資訊、組員名單、載入 Demo、資料使用說明。
    輸入：無
    輸出：無
    """
    st.sidebar.header("FairSplit")
    _render_project_info()
    st.sidebar.divider()
    _render_member_list()
    st.sidebar.divider()
    _render_demo_and_notice_buttons()


def save_all():
    """把 project、members、tasks、settings 寫回 data/（自動存檔）。
    輸入：無
    輸出：無
    """
    save_json(str(DATA_DIR / "project.json"), st.session_state["project"])
    save_json(str(DATA_DIR / "members.json"), {"members": st.session_state["members"]})
    save_json(str(DATA_DIR / "tasks.json"), {"tasks": st.session_state["tasks"]})
    save_json(str(DATA_DIR / "settings.json"), st.session_state["settings"])


# ---------- 以下是 app.py 內部用的小函式 ----------

def _load_project(path):
    """（內部用）讀取專題資料，缺的欄位補上預設值。
    輸入：path 檔案路徑
    輸出：專題 dict；起始日預設今天，截止日預設 4 週後
    """
    today = date.today()
    default_project = {
        "name": "",
        "description": "",
        "project_type": "",
        "member_level": "",
        "start": today.isoformat(),
        "deadline": (today + timedelta(weeks=DEFAULT_PROJECT_WEEKS)).isoformat(),
    }
    project = {**default_project, **load_json(str(path), default_project)}
    # 日期壞掉或空白時，改用預設值，避免後面計算可用工時時出錯
    for field in ["start", "deadline"]:
        if _parse_date(project[field]) is None:
            project[field] = default_project[field]
    return project


def _parse_date(text):
    """（內部用）把 "YYYY-MM-DD" 轉成 date。
    輸入：text 日期 str
    輸出：date；格式不對時回傳 None
    """
    try:
        return date.fromisoformat(text)
    except (TypeError, ValueError):
        return None


# dismissible=False：不顯示關閉鈕，一定要選一個選項（需要 Streamlit 1.48 以上）
@st.dialog("FairSplit 會記錄哪些資料", width="large", dismissible=False)
def _notice_dialog():
    """（內部用）資料使用告知彈窗的內容（spec 5.6）。
    輸入：無
    輸出：無；按下選項時寫入 settings 並存檔
    """
    st.markdown(
        "- 專題描述、任務、組員名稱與可用時間，每次修改後自動存在這台電腦的 data/ 資料夾，不會上傳。\n"
        "- 使用 AI 功能時，會把專題描述、截止日、組員人數、專題類型與組員程度（有填才送）"
        f"與可用時間描述句送到 {AI_SERVICE_NAME}；組員姓名不會送出。\n"
        "- Google 可能使用送出的內容改進其產品，請勿輸入個人資料。\n"
        "- 可用時間只用於計算工時，不顯示原因，也不做個人排名。\n"
        "- 刪除 data/ 資料夾即可清除全部資料。"
    )
    agree_column, manual_column = st.columns(2)
    if agree_column.button("同意並開始", type="primary", use_container_width=True):
        _save_notice_choice(ai_enabled=True)
    if manual_column.button("不使用 AI，只用手動輸入", use_container_width=True):
        _save_notice_choice(ai_enabled=False)


def _save_notice_choice(ai_enabled):
    """（內部用）記下告知彈窗的選擇，立即寫入 data/settings.json 並關閉彈窗。
    輸入：ai_enabled 是否啟用 AI bool
    輸出：無
    """
    st.session_state["settings"] = {"notice_accepted": True, "ai_enabled": ai_enabled}
    st.session_state["app_show_notice"] = False
    save_json(str(DATA_DIR / "settings.json"), st.session_state["settings"])
    st.rerun()


def _render_project_info():
    """（內部用）側欄的專題名稱、起始日與截止日；起始日不可晚於截止日。
    輸入：無
    輸出：無；合法時寫回 project
    """
    project = st.session_state["project"]
    # 元件的 key 第一次出現時才從 project 帶入，之後由元件自己保存畫面上的值
    if "app_project_name" not in st.session_state:
        st.session_state["app_project_name"] = project["name"]
    if "app_start" not in st.session_state:
        st.session_state["app_start"] = _parse_date(project["start"])
    if "app_deadline" not in st.session_state:
        st.session_state["app_deadline"] = _parse_date(project["deadline"])

    st.sidebar.subheader("專題資訊")
    name = st.sidebar.text_input("專題名稱", key="app_project_name")
    start = st.sidebar.date_input("起始日", key="app_start")
    deadline = st.sidebar.date_input("截止日", key="app_deadline")

    new_project = dict(project)
    new_project["name"] = name.strip()
    if start > deadline:
        # 日期不合法時保留原本的日期，不寫回
        st.sidebar.error("起始日不可晚於截止日")
    else:
        new_project["start"] = start.isoformat()
        new_project["deadline"] = deadline.isoformat()

    # 有變動才寫回，避免每次重跑都換掉 project
    if new_project != project:
        st.session_state["project"] = new_project


def _render_member_list():
    """（內部用）側欄的組員名單：新增與刪除組員。
    輸入：無
    輸出：無
    """
    st.sidebar.subheader("組員")
    members = st.session_state["members"]
    if not members:
        st.sidebar.caption("目前沒有組員，請在下方新增。")

    for member in members:
        name_column, delete_column = st.sidebar.columns([3, 2], vertical_alignment="center")
        name_column.write(member["name"])
        delete_column.button(
            "刪除",
            key="app_delete_" + member["id"],
            on_click=_delete_member,
            args=(member["id"],),
        )

    # 用 form 讓「新增」後自動清空輸入框
    with st.sidebar.form("app_add_member_form", clear_on_submit=True):
        new_name = st.text_input("新組員姓名")
        submitted = st.form_submit_button("新增")
    if submitted:
        _add_member(new_name)


def _add_member(name):
    """（內部用）新增組員；姓名不可空白也不可重複。
    輸入：name 姓名 str
    輸出：無；不合法時在側欄顯示錯誤
    """
    name = name.strip()
    members = st.session_state["members"]
    if not name:
        st.sidebar.error("姓名不可空白")
        return
    if name in [member["name"] for member in members]:
        st.sidebar.error("已經有同名的組員")
        return

    new_member = {
        "id": next_member_id(members),
        "name": name,
        "weekly_hours": 0,
        "unavailable_dates": [],
    }
    st.session_state["members"] = members + [new_member]
    st.rerun()


def _delete_member(member_id):
    """（內部用，按鈕回呼）刪除組員，並清除他的指派、鎖定與偏好（案例 14）。
    輸入：member_id 組員 id str
    輸出：無
    """
    new_members, new_tasks = remove_member(
        st.session_state["members"], st.session_state["tasks"], member_id
    )
    st.session_state["members"] = new_members
    update_tasks(new_tasks)
    # 可用工時也拿掉他，指標不會再出現這個人
    capacities = dict(st.session_state["capacities"])
    capacities.pop(member_id, None)
    st.session_state["capacities"] = capacities


def _render_demo_and_notice_buttons():
    """（內部用）側欄的「載入 Demo 資料」（先確認）與「資料使用說明」按鈕。
    輸入：無
    輸出：無
    """
    if st.session_state.get("app_confirm_demo", False):
        st.sidebar.warning("載入 Demo 資料會覆蓋目前的專題、組員與任務，確定嗎？")
        confirm_column, cancel_column = st.sidebar.columns(2)
        confirm_column.button("確定載入", on_click=_load_demo, type="primary")
        cancel_column.button("取消", on_click=_cancel_demo)
    else:
        st.sidebar.button(
            "載入 Demo 資料",
            on_click=lambda: st.session_state.update({"app_confirm_demo": True}),
        )

    st.sidebar.button(
        "資料使用說明",
        on_click=lambda: st.session_state.update({"app_show_notice": True}),
    )


def _load_demo():
    """（內部用，按鈕回呼）用 data/demo/ 的專題、組員、任務覆蓋目前資料，不改 settings。
    輸入：無
    輸出：無
    """
    st.session_state["project"] = _load_project(DEMO_DIR / "project.json")
    st.session_state["members"] = load_json(str(DEMO_DIR / "members.json"), {"members": []})["members"]
    st.session_state["capacities"] = {}
    # 清掉 15.2 以外的暫存 key（各分頁輸入框的值），讓畫面改從新資料讀值
    for key in list(st.session_state.keys()):
        if key not in SHARED_KEYS:
            del st.session_state[key]
    update_tasks(load_json(str(DEMO_DIR / "tasks.json"), {"tasks": []})["tasks"])


def _cancel_demo():
    """（內部用，按鈕回呼）取消載入 Demo 資料。
    輸入：無
    輸出：無
    """
    st.session_state["app_confirm_demo"] = False


st.set_page_config(page_title="FairSplit 公平分工引擎", layout="wide")
init_state()
show_notice()
render_sidebar()

tab_tasks, tab_availability, tab_assign = st.tabs(["任務", "可用時間", "分配與指標"])
with tab_tasks:
    render_tasks_tab()
with tab_availability:
    render_availability_tab()
with tab_assign:
    # 先分配再畫指標：render_metrics_section 讀取 render_assign_section 算好的 capacities（spec 15.5）
    render_assign_section()
    st.divider()
    render_metrics_section()

# 每次執行的最後自動存檔（spec 15.2）
save_all()
