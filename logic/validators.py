# 可用時間與日期的驗證（負責：D）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。

from datetime import date


def validate_availability(data, start, deadline):
    """驗證 AI 回傳的可用時間（spec 5.4）。
    輸入：data AI 回傳的 dict；start、deadline 日期 str
    輸出：(清理後的 dict, 提示訊息 list[str])
    """
    cleaned = {"weekly_hours": None, "unavailable_dates": []}
    messages = []

    if not isinstance(data, dict):
        return cleaned, ["請手動填寫每週可用小時"]

    weekly_hours = data.get("weekly_hours")
    if (
        isinstance(weekly_hours, (int, float))
        and not isinstance(weekly_hours, bool)
        and 0 <= weekly_hours <= 60
    ):
        cleaned["weekly_hours"] = float(weekly_hours)
    else:
        messages.append("請手動填寫每週可用小時")

    unavailable_dates = data.get("unavailable_dates")
    if not isinstance(unavailable_dates, list):
        unavailable_dates = []
        messages.append("不可用日期格式錯誤，已略過")

    try:
        start_date = date.fromisoformat(start)
        deadline_date = date.fromisoformat(deadline)
    except (TypeError, ValueError):
        messages.append("專題日期格式錯誤，無法驗證不可用日期")
        return cleaned, messages

    invalid_date_found = False
    for unavailable_date in unavailable_dates:
        if not isinstance(unavailable_date, str):
            invalid_date_found = True
            continue

        try:
            parsed_date = date.fromisoformat(unavailable_date)
        except ValueError:
            invalid_date_found = True
            continue

        if (
            parsed_date.isoformat() != unavailable_date
            or parsed_date < start_date
            or parsed_date > deadline_date
        ):
            invalid_date_found = True
            continue

        cleaned["unavailable_dates"].append(unavailable_date)

    if invalid_date_found:
        messages.append("不合法或超出期間的不可用日期已略過")

    return cleaned, messages
