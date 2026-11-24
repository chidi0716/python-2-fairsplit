# 可用時間與日期的驗證（負責：D）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 目前是空殼：回傳固定範例值，由負責人換成真正的程式。


def validate_availability(data, start, deadline):
    """驗證 AI 回傳的可用時間（spec 5.4）。
    輸入：data AI 回傳的 dict；start、deadline 日期 str
    輸出：(清理後的 dict, 提示訊息 list[str])
    """
    return {"weekly_hours": None, "unavailable_dates": []}, []
