# 可用天數與可用工時（負責：B）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。

from datetime import date

def count_available_days(start, deadline, unavailable):
    """計算可用天數（spec 4.2）。
    輸入：start、deadline 日期 str（YYYY-MM-DD）；unavailable 不可用日期 list[str]
    輸出：int
    """
    start_date = date.fromisoformat(start)
    deadline_date = date.fromisoformat(deadline)
    total_days = (deadline_date - start_date).days + 1

    unavailable_dates = set()
    for unavailable_date in unavailable:
        current_date = date.fromisoformat(unavailable_date)
        if start_date <= current_date <= deadline_date:
            unavailable_dates.add(current_date)

    return total_days - len(unavailable_dates)


def calc_capacity(member, start, deadline):
    """計算組員的可用工時 C_i（spec 4.2）。
    輸入：member 組員 dict；start、deadline 日期 str
    輸出：float
    """
    available_days = count_available_days(
        start,
        deadline,
        member["unavailable_dates"],
    )
    return member["weekly_hours"] / 7 * available_days
