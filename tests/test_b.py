# B 的驗收案例（負責：B）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
import sys

from logic.capacity import calc_capacity, count_available_days


results = []


def check(name, ok):
    """印出單一檢查結果並記錄是否通過。
    輸入：name 案例名稱 str；ok 是否通過 bool
    輸出：無
    """
    results.append(ok)
    print(f"{'通過' if ok else '失敗'}：{name}")


def case_7():
    """案例 7：依期間天數與不可用日期計算可用天數及可用工時。"""
    start = "2026-11-23"
    deadline = "2026-12-18"
    member = {
        "weekly_hours": 8,
        "unavailable_dates": ["2026-12-01"],
    }

    available_days = count_available_days(
        start,
        deadline,
        member["unavailable_dates"],
    )
    capacity = calc_capacity(member, start, deadline)
    check("案例 7 可用天數為 25 天", available_days == 25)
    expected_capacity = 8 / 7 * 25
    check("案例 7 可用工時約為 28.6 小時", abs(capacity - expected_capacity) <= 0.01)

    unavailable_with_duplicates_and_outside = [
        "2026-12-01",
        "2026-12-01",
        "2026-11-22",
        "2026-12-19",
    ]
    check(
        "重複及期間外的不可用日期不重複扣除",
        count_available_days(
            start,
            deadline,
            unavailable_with_duplicates_and_outside,
        ) == 25,
    )
    check(
        "起訖同一天時兩端都計入",
        count_available_days("2026-11-23", "2026-11-23", []) == 1,
    )


def main():
    """執行 B 的驗收案例。
    輸入：無
    輸出：無；有任何失敗時以非 0 結束
    """
    print("== B 的驗收案例 ==")
    case_7()
    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
