# D 的驗收案例（負責：D）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd

from ai.availability import parse_availability_with_ai
from ai.client import call_ai, mask_names
from ai.tasks import build_task_prompt, split_tasks_with_ai, validate_task
from logic.validators import validate_availability
from ui.tasks import render_tasks_tab

results = []


def check(name, passed):
    """記錄並印出一項案例的結果。
    輸入：name 案例名稱 str；passed 是否通過 bool
    輸出：無
    """
    results.append(passed)
    print(f"{'通過' if passed else '失敗'}：{name}")


def case_5():
    """案例 5：非 JSON、空任務清單與連線失敗都退回手動新增。
    輸入：預先設定的 AI 回應文字
    輸出：確認回傳空任務與手動輸入提示
    """
    responses = ["不是 JSON", '{"tasks": []}', None]
    expected_message = "AI 暫時無法使用，請手動新增任務"
    with patch("ai.tasks.call_ai", side_effect=responses):
        outcomes = [
            split_tasks_with_ai("專題描述", "2026-12-18", 4, 3, "", "", [])
            for _ in responses
        ]

    passed = all(
        tasks == [] and messages == [expected_message]
        for tasks, messages in outcomes
    )
    check("案例 5 AI 失敗時提示手動新增", passed)

    environment = {
        "AI_BASE_URL": "https://models.github.ai/inference",
        "AI_MODEL": "openai/gpt-4o-mini",
        "AI_API_KEY": "test-key",
    }
    with patch.dict(os.environ, environment, clear=True):
        with patch("ai.client.load_dotenv"):
            with patch("ai.client.OpenAI", side_effect=OSError("test connection failure")):
                with patch("ai.client.logger.exception") as log_exception:
                    result = call_ai("請回傳 JSON", [])
    check("案例 5 連線錯誤退回手動操作", result is None and log_exception.called)


def case_8():
    """案例 8：三個 AI 任務中略過工時為 -2 的錯誤任務。
    輸入：含兩個合法任務與一個錯誤任務的 AI 回應
    輸出：兩個合法任務及一則略過提示
    """
    response = (
        '```json\n{"tasks": ['
        '{"title": "整理需求", "est_hours": 2},'
        '{"title": "錯誤任務", "est_hours": -2},'
        '{"title": "製作原型", "est_hours": 1.5}]}'
        '\n```'
    )
    with patch("ai.tasks.call_ai", return_value=response):
        tasks, messages = split_tasks_with_ai(
            "公平分工工具",
            "2026-12-18",
            4,
            3,
            "程式專題",
            "初學者",
            [],
        )

    check(
        "案例 8 保留兩個合法任務",
        tasks == [
            {"title": "整理需求", "est_hours": 2},
            {"title": "製作原型", "est_hours": 1.5},
        ],
    )
    check(
        "案例 8 提示一個錯誤任務已略過",
        messages == ["1 個任務格式錯誤已略過"],
    )
    check(
        "任務名稱與工時邊界驗證",
        validate_task({"title": " 需求 ", "est_hours": 0.5}) == (True, "")
        and not validate_task({"title": " ", "est_hours": 1})[0]
        and not validate_task({"title": "有效名稱", "est_hours": 20.5})[0],
    )
    prompt = build_task_prompt("FairSplit", "2026-12-18", 4, 3, "", "")
    check(
        "選填欄位空白時不顯示在任務提示詞",
        "專題類型：" not in prompt and "組員程度：" not in prompt,
    )
    detailed_prompt = build_task_prompt(
        "FairSplit",
        "2026-12-18",
        4,
        3,
        "程式專題",
        "初學者",
    )
    check(
        "選填欄位有內容時放入任務提示詞",
        "專題類型：程式專題" in detailed_prompt
        and "組員程度：初學者" in detailed_prompt,
    )


def case_8_task_editor():
    """案例 8：工時變更後標記為手動，來源欄不可編輯。
    輸入：一筆 AI 任務與修改後的任務表資料
    輸出：工時更新、來源改為手動且來源欄唯讀
    """
    session_state = {
        "project": {"description": "", "deadline": "2026-12-18"},
        "members": [],
        "tasks": [
            {
                "id": "T1",
                "title": "整理需求",
                "est_hours": 2.0,
                "est_source": "ai",
                "assignee": None,
                "locked": False,
                "preferred": None,
                "status": "todo",
                "actual_hours": None,
                "depends_on": [],
            }
        ],
        "settings": {"ai_enabled": False},
        "tasks_version": 0,
    }
    streamlit_mock = MagicMock()
    streamlit_mock.session_state = session_state
    streamlit_mock.text_area.return_value = ""
    streamlit_mock.text_input.return_value = ""
    streamlit_mock.button.return_value = False
    streamlit_mock.data_editor.return_value = pd.DataFrame(
        [
            {
                "id": "T1",
                "title": "整理需求",
                "est_hours": 3.0,
                "est_source": "AI 估計",
                "preferred": "",
                "assignee": None,
                "locked": False,
                "status": "todo",
                "actual_hours": None,
                "depends_on": [],
            }
        ]
    )
    streamlit_mock.selectbox.return_value = "T1"

    def update_tasks_for_test(new_tasks):
        """模擬共用狀態更新以檢查任務表的輸出。
        輸入：新任務 list[dict]
        輸出：無（更新測試用 session state）
        """
        session_state["tasks"] = list(new_tasks)

    with patch("ui.tasks.st", streamlit_mock):
        with patch("ui.tasks.update_tasks", side_effect=update_tasks_for_test):
            render_tasks_tab()

    updated_task = session_state["tasks"][0]
    disabled_columns = streamlit_mock.data_editor.call_args.kwargs["disabled"]
    check(
        "任務表工時修改會改成手動來源且來源欄唯讀",
        updated_task["est_hours"] == 3.0
        and updated_task["est_source"] == "manual"
        and "est_source" in disabled_columns,
    )


def case_8_ai_warning():
    """案例 8：直接按 AI 拆任務時保留格式錯誤提示。
    輸入：部分任務合法的 AI 回應與空任務清單
    輸出：任務更新、提示顯示且不因拆任務而重跑
    """
    session_state = {
        "project": {
            "description": "公平分工工具",
            "deadline": "2026-12-18",
            "project_type": "",
            "member_level": "",
        },
        "members": [],
        "tasks": [],
        "settings": {"ai_enabled": True},
        "tasks_version": 0,
    }
    ai_tasks = [{"title": "整理需求", "est_hours": 2}]
    merged_tasks = [
        {
            "id": "T1",
            "title": "整理需求",
            "est_hours": 2,
            "est_source": "ai",
            "assignee": None,
            "locked": False,
            "preferred": None,
            "status": "todo",
            "actual_hours": None,
            "depends_on": [],
        }
    ]
    streamlit_mock = MagicMock()
    streamlit_mock.session_state = session_state
    streamlit_mock.text_area.return_value = "公平分工工具"
    streamlit_mock.text_input.return_value = ""
    streamlit_mock.button.side_effect = lambda label, disabled=False: (
        label == "AI 拆任務" and not disabled
    )
    streamlit_mock.data_editor.return_value = pd.DataFrame(
        [
            {
                "id": "T1",
                "title": "整理需求",
                "est_hours": 2.0,
                "est_source": "AI 估計",
                "preferred": "",
                "assignee": None,
                "locked": False,
                "status": "todo",
                "actual_hours": None,
                "depends_on": [],
            }
        ]
    )
    streamlit_mock.selectbox.return_value = "T1"

    def update_tasks_for_test(new_tasks):
        """模擬共用狀態更新以檢查 AI 任務輸出。
        輸入：新任務 list[dict]
        輸出：無（更新測試用 session state）
        """
        session_state["tasks"] = list(new_tasks)

    with patch("ui.tasks.st", streamlit_mock):
        with patch(
            "ui.tasks.split_tasks_with_ai",
            return_value=(ai_tasks, ["1 個任務格式錯誤已略過"]),
        ):
            with patch("ui.tasks.merge_ai_tasks", return_value=merged_tasks):
                with patch(
                    "ui.tasks.update_tasks",
                    side_effect=update_tasks_for_test,
                ):
                    render_tasks_tab()

    warning_was_shown = any(
        call.args[0] == "1 個任務格式錯誤已略過"
        for call in streamlit_mock.warning.call_args_list
    )
    check(
        "案例 8 直接拆任務顯示提示且不因生成結果重跑",
        warning_was_shown
        and session_state["tasks"] == merged_tasks
        and not streamlit_mock.rerun.called,
    )


def case_8_confirmation_warning():
    """案例 8：確認重新拆任務後保存提示並在重跑時顯示。
    輸入：已有任務、確認狀態與部分合法的 AI 回應
    輸出：重跑後顯示提示並清除暫存訊息
    """
    session_state = {
        "project": {
            "description": "公平分工工具",
            "deadline": "2026-12-18",
            "project_type": "",
            "member_level": "",
        },
        "members": [],
        "tasks": [
            {
                "id": "T1",
                "title": "原任務",
                "est_hours": 1.0,
                "est_source": "manual",
                "assignee": None,
                "locked": False,
                "preferred": None,
                "status": "todo",
                "actual_hours": None,
                "depends_on": [],
            }
        ],
        "settings": {"ai_enabled": True},
        "tasks_version": 0,
        "tasks_confirm_ai": True,
    }
    ai_tasks = [{"title": "整理需求", "est_hours": 2}]
    merged_tasks = [
        {
            "id": "T2",
            "title": "整理需求",
            "est_hours": 2,
            "est_source": "ai",
            "assignee": None,
            "locked": False,
            "preferred": None,
            "status": "todo",
            "actual_hours": None,
            "depends_on": [],
        }
    ]
    streamlit_mock = MagicMock()
    streamlit_mock.session_state = session_state
    streamlit_mock.text_area.return_value = "公平分工工具"
    streamlit_mock.text_input.return_value = ""
    streamlit_mock.button.return_value = False
    streamlit_mock.data_editor.return_value = pd.DataFrame(
        [
            {
                "id": "T2",
                "title": "整理需求",
                "est_hours": 2.0,
                "est_source": "AI 估計",
                "preferred": "",
                "assignee": None,
                "locked": False,
                "status": "todo",
                "actual_hours": None,
                "depends_on": [],
            }
        ]
    )
    streamlit_mock.selectbox.return_value = "T2"
    streamlit_mock.dialog.side_effect = lambda title: (
        lambda function: function
    ) if title == "確認重新拆任務" else None
    confirm_column = MagicMock()
    confirm_column.button.return_value = True
    cancel_column = MagicMock()
    cancel_column.button.return_value = False
    streamlit_mock.columns.return_value = (confirm_column, cancel_column)

    def update_tasks_for_test(new_tasks):
        """模擬共用狀態更新以檢查重拆後的任務。
        輸入：新任務 list[dict]
        輸出：無（更新測試用 session state）
        """
        session_state["tasks"] = list(new_tasks)

    with patch("ui.tasks.st", streamlit_mock):
        with patch(
            "ui.tasks.split_tasks_with_ai",
            return_value=(ai_tasks, ["1 個任務格式錯誤已略過"]),
        ):
            with patch("ui.tasks.merge_ai_tasks", return_value=merged_tasks):
                with patch(
                    "ui.tasks.update_tasks",
                    side_effect=update_tasks_for_test,
                ):
                    render_tasks_tab()

        message_saved = session_state.get("tasks_ai_messages") == [
            "1 個任務格式錯誤已略過"
        ]
        streamlit_mock.warning.reset_mock()
        render_tasks_tab()

    warning_was_shown = any(
        call.args[0] == "1 個任務格式錯誤已略過"
        for call in streamlit_mock.warning.call_args_list
    )
    check(
        "案例 8 確認重拆後提示跨重跑顯示",
        message_saved
        and warning_was_shown
        and "tasks_ai_messages" not in session_state
        and not session_state["tasks_confirm_ai"],
    )


def case_10():
    """案例 10：保留期間內日期並略過期間外日期。
    輸入：預先設定的 JSON 可用時間回應
    輸出：清理後的每週工時、日期與提示訊息
    """
    response = (
        '```json\n{"weekly_hours": 6, "unavailable_dates": '
        '["2026-12-01", "2027-01-05"]}\n```'
    )
    with patch("ai.availability.call_ai", return_value=response) as call_ai_mock:
        data, messages = parse_availability_with_ai(
            "每週 6 小時，12/1 不能工作",
            [],
            "2026-11-23",
            "2026-12-18",
        )

    check(
        "案例 10 保留可用工時與期間內日期",
        data == {"weekly_hours": 6.0, "unavailable_dates": ["2026-12-01"]},
    )
    check(
        "案例 10 提示期間外日期已略過",
        "不合法或超出期間的不可用日期已略過" in messages,
    )
    prompt = call_ai_mock.call_args.args[0]
    check(
        "可用時間提示詞包含期間與原句",
        "2026-11-23 到 2026-12-18" in prompt
        and "每週 6 小時，12/1 不能工作" in prompt,
    )
    check(
        "案例 10 的 Markdown JSON 區塊可解析",
        data is not None and data["weekly_hours"] == 6.0,
    )


def case_11():
    """案例 11：非 JSON 或每週工時為 null 時提示手動填寫。
    輸入：非 JSON 與缺少每週工時的合法 JSON 回應
    輸出：錯誤 JSON 為 None；合法 JSON 保留日期並提示手動填寫
    """
    fallback_message = "請手動填寫每週可用小時"
    responses = [
        "不是 JSON",
        '{"weekly_hours": null, "unavailable_dates": ["2026-12-01"]}',
    ]
    outcomes = []
    with patch("ai.availability.call_ai", side_effect=responses):
        for _ in responses:
            outcomes.append(
                parse_availability_with_ai(
                    "最近比較忙",
                    [],
                    "2026-11-23",
                    "2026-12-18",
                )
            )

    check(
        "案例 11 非 JSON 回傳 None 並提示手動填寫",
        outcomes[0][0] is None and fallback_message in outcomes[0][1],
    )
    check(
        "案例 11 每週工時為 null 時保留合法日期",
        outcomes[1][0]
        == {"weekly_hours": None, "unavailable_dates": ["2026-12-01"]}
        and fallback_message in outcomes[1][1],
    )
    invalid_data, invalid_messages = validate_availability(
        {"weekly_hours": 61, "unavailable_dates": []},
        "2026-11-23",
        "2026-12-18",
    )
    check(
        "每週工時超出範圍時清空並提示",
        invalid_data["weekly_hours"] is None and fallback_message in invalid_messages,
    )


def case_16():
    """案例 16：送出 AI 前遮蔽組員姓名。
    輸入：含組員姓名的文字與姓名清單
    輸出：不含原姓名的文字
    """
    masked_text = mask_names("週三跟組員乙對報告", ["組員甲", "組員乙"])
    check("案例 16 姓名遮蔽結果", masked_text == "週三跟組員對報告")
    check(
        "較長姓名先遮蔽且忽略空字串",
        mask_names("組員甲乙", ["組員甲", "組員甲乙", ""]) == "組員",
    )

    with patch.dict(os.environ, {}, clear=True):
        with patch("ai.client.load_dotenv"):
            with patch("ai.client.OpenAI") as openai_class:
                result = call_ai("組員乙要整理報告", ["組員乙"])
    check("缺少 API 設定時不呼叫外部服務", result is None and not openai_class.called)

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content='{"tasks": []}')
            )
        ]
    )
    environment = {
        "AI_BASE_URL": "https://models.github.ai/inference",
        "AI_MODEL": "openai/gpt-4o-mini",
        "AI_API_KEY": "test-key",
    }
    with patch.dict(os.environ, environment, clear=True):
        with patch("ai.client.load_dotenv"):
            with patch("ai.client.OpenAI", return_value=fake_client) as openai_class:
                result = call_ai("組員乙要整理報告", ["組員乙"])

    request = fake_client.chat.completions.create.call_args.kwargs
    sent_prompt = request["messages"][0]["content"]
    check("AI 請求中的姓名已遮蔽", result == '{"tasks": []}' and "組員乙" not in sent_prompt)
    check(
        "AI 請求要求 JSON 並設定 15 秒逾時",
        request["response_format"] == {"type": "json_object"}
        and openai_class.call_args.kwargs["timeout"] == 15.0,
    )

    gemini_client = MagicMock()
    gemini_client.chat.completions.create.return_value = fake_client.chat.completions.create.return_value
    gemini_environment = {
        "AI_BASE_URL": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "AI_MODEL": "gemini-flash",
        "AI_API_KEY": "test-key",
    }
    with patch.dict(os.environ, gemini_environment, clear=True):
        with patch("ai.client.load_dotenv"):
            with patch("ai.client.OpenAI", return_value=gemini_client):
                call_ai("請回傳 JSON", [])
    check(
        "Gemini 請求使用最低 reasoning_effort",
        gemini_client.chat.completions.create.call_args.kwargs["reasoning_effort"] == "minimal",
    )


def main():
    """依序執行 D 的離線驗收案例。
    輸入：無
    輸出：有任何失敗時以非 0 結束
    """
    print("== D 的驗收案例 ==")
    case_5()
    case_8()
    case_8_task_editor()
    case_8_ai_warning()
    case_8_confirmation_warning()
    case_10()
    case_11()
    case_16()
    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
