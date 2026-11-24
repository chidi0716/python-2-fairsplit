# 主程式：初始化、側欄、分頁、告知彈窗、自動存檔（負責：A）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 目前是框架：四個函式還是空殼，分頁會呼叫各組員的 render_ 函式。
from pathlib import Path

import streamlit as st

from ui.assign import render_assign_section
from ui.availability import render_availability_tab
from ui.metrics import render_metrics_section
from ui.tasks import render_tasks_tab

# 資料夾以本檔所在位置為基準，從其他資料夾啟動也讀得到（spec 13）
DATA_DIR = Path(__file__).parent / "data"


def init_state():
    """初始化 session_state：沒有該 key 時才設定，避免蓋掉畫面上的修改。
    輸入：無
    輸出：無
    空殼：先放預設空結構，之後改成從 data/ 載入。
    """
    defaults = {
        "project": {"name": "", "description": "", "project_type": "", "member_level": "",
                    "start": "", "deadline": ""},
        "members": [],
        "tasks": [],
        "tasks_version": 0,
        "capacities": {},
        "settings": {"notice_accepted": False, "ai_enabled": False},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def show_notice():
    """顯示資料使用告知彈窗（spec 5.6），按下選項時立即寫入 data/settings.json。
    輸入：無
    輸出：無
    """
    return None


def render_sidebar():
    """畫出側欄：專題資訊、組員名單、載入 Demo、資料使用說明。
    輸入：無
    輸出：無
    """
    st.sidebar.header("FairSplit")
    st.sidebar.info("（空殼）側欄：由 A 實作")


def save_all():
    """把 project、members、tasks、settings 寫回 data/（自動存檔）。
    輸入：無
    輸出：無
    """
    return None


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
