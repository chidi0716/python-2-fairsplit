# AI 解析可用時間（負責：D）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 目前是空殼：回傳固定範例值，由負責人換成真正的程式。


def build_availability_prompt(text, start, deadline):
    """組出可用時間解析的提示詞（spec 5.3）。
    輸入：text 可用時間描述 str；start、deadline 日期 str
    輸出：提示詞 str
    """
    return ""


def parse_availability_with_ai(text, names, start, deadline):
    """請 AI 把一句話轉成可用時間，回傳前呼叫 validate_availability。
    輸入：text 描述 str；names 全部組員姓名 list[str]；start、deadline 日期 str
    輸出：({"weekly_hours": float 或 None, "unavailable_dates": list} 或 None, 提示訊息 list[str])
    """
    return None, ["請手動填寫每週可用小時"]
