# C 的驗收案例（負責：C）：案例 1–4（指標部分）、17、22（spec 第 17 節）
# 執行方式：在專案根目錄執行 python -m tests.test_c
import sys

from logic.fairness import (
    calc_load_rates,
    calc_progress,
    find_overload,
    format_load_formula,
    gini,
    max_min_ratio,
    std_dev,
)

results = []


def check(name, ok):
    # 做什麼：印出檢查結果並記錄狀態；輸入：案例名稱與結果 bool；輸出：無。
    results.append(ok)
    print(f"{'通過' if ok else '失敗'}：{name}")


def close_to(actual, expected):
    # 做什麼：比較數字是否在規格容差內；輸入：實際值與預期值；輸出：bool。
    return actual is not None and abs(actual - expected) <= 0.01


def case_1():
    # 做什麼：驗證均等負載率；輸入：案例 1 手算的分配；輸出：無。
    tasks = [
        {"assignee": "m1", "est_hours": 5},
        {"assignee": "m2", "est_hours": 3},
        {"assignee": "m2", "est_hours": 2},
    ]
    rates = calc_load_rates(tasks, {"m1": 10, "m2": 10})
    check("案例 1 負載率為 0.5／0.5", rates == {"m1": 0.5, "m2": 0.5})
    check("案例 1 最大最小比為 1.0", close_to(max_min_ratio(rates), 1.0))
    check("案例 1 標準差與 Gini 為 0", std_dev(rates) == 0 and gini(rates) == 0)


def case_2():
    # 做什麼：驗證不均等負載率指標；輸入：案例 2 手算的分配；輸出：無。
    tasks = [
        {"assignee": "m1", "est_hours": 6},
        {"assignee": "m2", "est_hours": 3},
        {"assignee": "m1", "est_hours": 1},
    ]
    rates = calc_load_rates(tasks, {"m1": 10, "m2": 5})
    check("案例 2 負載率為 0.7／0.6", rates == {"m1": 0.7, "m2": 0.6})
    check("案例 2 最大最小比約為 1.17", close_to(max_min_ratio(rates), 1.17))
    check("案例 2 標準差約為 0.05", close_to(std_dev(rates), 0.05))
    check("案例 2 Gini 約為 0.04", close_to(gini(rates), 0.04))


def case_3():
    # 做什麼：驗證零可用工時不參與負載率計算；輸入：案例 3 手算的分配；輸出：無。
    tasks = [
        {"assignee": "m1", "est_hours": 4},
        {"assignee": "m1", "est_hours": 2},
    ]
    rates = calc_load_rates(tasks, {"m1": 10, "m2": 0})
    check("案例 3 零可用工時的 m2 不列入負載率", rates == {"m1": 0.6})
    check("案例 3 最大最小比為 1.0", close_to(max_min_ratio(rates), 1.0))
    check("沒有負載率時最大最小比無法計算", max_min_ratio({}) is None)


def case_4():
    # 做什麼：驗證超載判斷；輸入：案例 4 手算的分配；輸出：無。
    tasks = [
        {"assignee": "m1", "est_hours": 8},
        {"assignee": "m2", "est_hours": 4},
    ]
    rates = calc_load_rates(tasks, {"m1": 5, "m2": 5})
    check("案例 4 負載率為 1.6／0.8", rates == {"m1": 1.6, "m2": 0.8})
    check("案例 4 只有 m1 超載", find_overload(rates) == ["m1"])


def case_17():
    # 做什麼：驗證每人與全組完成率；輸入：案例 17 的任務；輸出：無。
    tasks = [
        {"assignee": "m1", "est_hours": 5, "status": "done"},
        {"assignee": "m1", "est_hours": 3, "status": "todo"},
        {"assignee": "m2", "est_hours": 2, "status": "doing"},
    ]
    member_progress, team_progress = calc_progress(tasks)
    check("案例 17 m1 完成率為 0.625", close_to(member_progress["m1"], 0.625))
    check("案例 17 m2 完成率為 0", member_progress["m2"] == 0)
    check("案例 17 全組完成率為 0.5", close_to(team_progress, 0.5))
    check("沒有已指派任務時完成率無法計算", calc_progress([]) == ({}, None))


def case_22():
    # 做什麼：驗證負載率算式與零可用時間；輸入：案例 22 數值；輸出：無。
    expected = "負載率 = 已分配工時 ÷ 可用工時 = 12 ÷ 15 = 0.80"
    check("案例 22 算式格式正確", format_load_formula(12, 15) == expected)
    check("案例 22 零可用工時不顯示算式", format_load_formula(0, 0) == "無可用工時")


def main():
    # 做什麼：執行 C 負責的驗收案例；輸入：無；輸出：失敗時以非 0 結束。
    print("== C 的驗收案例 ==")
    case_1()
    case_2()
    case_3()
    case_4()
    case_17()
    case_22()
    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
