# AI 拆任務與驗證（負責：D）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 第二版空殼：explain_reassign_with_ai。

import json
import math

from ai.client import call_ai


def build_task_prompt(description, deadline, member_count, weeks, project_type, member_level):
    """組出任務拆解的提示詞（spec 5.3）。
    輸入：description 專題描述 str；deadline 日期 str；member_count 人數 int；
          weeks 週數 int；project_type、member_level 選填 str
    輸出：提示詞 str
    """
    prompt_lines = [
        f"你是大學課堂專題的專案助理。以下是一個 {member_count} 人小組的專題，",
        f"距離截止日 {deadline} 還有 {weeks} 週。",
    ]
    if project_type:
        prompt_lines.append(f"專題類型：{project_type}")
    if member_level:
        prompt_lines.append(f"組員程度：{member_level}")
    prompt_lines.extend(
        [
            "請把專題拆成 5 到 15 個任務，並估計每個任務需要的工作小時",
            "（0.5 到 20 之間，以 0.5 為單位），估計時考慮專題類型與組員程度。",
            "",
            "只回傳 JSON，不要任何說明文字，格式如下：",
            '{"tasks": [{"title": "任務名稱，30 字以內", "est_hours": 3}]}',
            "",
            "專題描述：",
            description,
        ]
    )
    return "\n".join(prompt_lines)


def validate_task(task):
    """驗證 AI 回傳的單一任務（spec 5.4）。
    輸入：task 任務 dict
    輸出：(是否合法 bool, 訊息 str)
    """
    if not isinstance(task, dict):
        return False, "任務格式錯誤"

    title = task.get("title")
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 30:
        return False, "任務名稱必須是 1 到 30 字"

    est_hours = task.get("est_hours")
    if (
        not isinstance(est_hours, (int, float))
        or isinstance(est_hours, bool)
        or not 0.5 <= est_hours <= 20
        or not math.isfinite(est_hours)
    ):
        return False, "估計工時必須介於 0.5 到 20 小時"

    return True, ""


def _strip_json_fence(text):
    """移除 AI 回應外層的 Markdown 程式碼區塊。
    輸入：AI 回傳的文字 str
    輸出：去除程式碼區塊標記後的文字 str
    """
    cleaned_text = text.strip()
    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]
        if cleaned_text.lower().startswith("json"):
            cleaned_text = cleaned_text[4:]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
    return cleaned_text.strip()


def split_tasks_with_ai(description, deadline, member_count, weeks, project_type, member_level, names):
    """請 AI 拆任務並逐項驗證。
    輸入：同 build_task_prompt，加上 names 全部組員姓名 list[str]
    輸出：(只含 title、est_hours 的合法任務 list[dict], 提示訊息 list[str])
    """
    fallback_message = "AI 暫時無法使用，請手動新增任務"
    prompt = build_task_prompt(
        description,
        deadline,
        member_count,
        weeks,
        project_type,
        member_level,
    )
    response = call_ai(prompt, names)
    if not response:
        return [], [fallback_message]

    try:
        response_data = json.loads(_strip_json_fence(response))
    except (json.JSONDecodeError, TypeError):
        return [], [fallback_message]

    if (
        not isinstance(response_data, dict)
        or not isinstance(response_data.get("tasks"), list)
    ):
        return [], [fallback_message]

    valid_tasks = []
    invalid_count = 0
    for task in response_data["tasks"]:
        is_valid, _ = validate_task(task)
        if not is_valid:
            invalid_count += 1
            continue
        valid_tasks.append(
            {
                "title": task["title"].strip(),
                "est_hours": task["est_hours"],
            }
        )

    if not valid_tasks:
        return [], [fallback_message]

    messages = []
    if invalid_count:
        messages.append(f"{invalid_count} 個任務格式錯誤已略過")
    return valid_tasks, messages


def explain_reassign_with_ai(before, after, metrics):
    """請 AI 用白話說明重排原因（第二版）。
    輸入：before、after 重排前後的分配 dict；metrics 指標 dict
    輸出：白話說明 str
    """
    return ""
