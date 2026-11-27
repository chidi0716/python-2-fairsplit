# AI 解析可用時間（負責：D）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。

import json

from ai.client import call_ai
from logic.validators import validate_availability


def build_availability_prompt(text, start, deadline):
    """組出可用時間解析的提示詞（spec 5.3）。
    輸入：text 可用時間描述 str；start、deadline 日期 str
    輸出：提示詞 str
    """
    return (
        f"專題期間是 {start} 到 {deadline}。請把下面這句話轉成可用時間：\n"
        "每週可投入的總小時數，以及期間內完全不能工作的日期。\n"
        "句子沒提到的部分不要自行假設；無法判斷每週小時數時填 null。\n\n"
        "只回傳 JSON，不要任何說明文字，格式如下：\n"
        '{"weekly_hours": 6, "unavailable_dates": ["2026-12-01"]}\n\n'
        f"句子：{text}"
    )


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


def parse_availability_with_ai(text, names, start, deadline):
    """請 AI 把一句話轉成可用時間，回傳前呼叫 validate_availability。
    輸入：text 描述 str；names 全部組員姓名 list[str]；start、deadline 日期 str
    輸出：({"weekly_hours": float 或 None, "unavailable_dates": list} 或 None, 提示訊息 list[str])
    """
    fallback_message = "請手動填寫每週可用小時"
    prompt = build_availability_prompt(text, start, deadline)
    response = call_ai(prompt, names)
    if not response:
        return None, [fallback_message]

    try:
        response_data = json.loads(_strip_json_fence(response))
    except (json.JSONDecodeError, TypeError):
        return None, [fallback_message]

    if not isinstance(response_data, dict):
        return None, [fallback_message]

    cleaned_data, messages = validate_availability(response_data, start, deadline)
    if cleaned_data["weekly_hours"] is None:
        if fallback_message not in messages:
            messages.append(fallback_message)
        return cleaned_data, messages

    return cleaned_data, messages
