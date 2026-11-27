# B 的驗收案例（負責：B）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
import sys

from logic.capacity import calc_capacity, count_available_days
from logic.planner import assign_tasks, pick_member, sort_tasks
from logic.task_ops import next_task_id


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


def case_1_to_4():
    """案例 1 至 4：檢查不同工時、零可用與超載時的分配。"""
    equal_capacities = {"m1": 10, "m2": 10}
    equal_tasks = [
        {"id": "T1", "est_hours": 5},
        {"id": "T2", "est_hours": 3},
        {"id": "T3", "est_hours": 2},
    ]
    check(
        "案例 1 均等分配",
        assign_tasks(equal_tasks, equal_capacities)
        == {"T1": "m1", "T2": "m2", "T3": "m2"},
    )

    same_hours_tasks = [
        {"id": "T10", "est_hours": 3},
        {"id": "T2", "est_hours": 3},
        {"id": "T1", "est_hours": 4},
    ]
    sorted_tasks = sort_tasks(same_hours_tasks)
    sorted_ids = [task["id"] for task in sorted_tasks]
    check("相同工時依任務 id 數字部分排序", sorted_ids == ["T1", "T2", "T10"])
    check(
        "排序會回傳新 list 並保留原順序",
        sorted_tasks is not same_hours_tasks and same_hours_tasks[0]["id"] == "T10",
    )
    check(
        "新負載率並列時優先可用工時較大的組員",
        pick_member(
            {"id": "T1", "est_hours": 2},
            {"m1": 0, "m2": 2},
            {"m1": 5, "m2": 10},
        ) == "m2",
    )

    unequal_tasks = [
        {"id": "T1", "est_hours": 6},
        {"id": "T2", "est_hours": 3},
        {"id": "T3", "est_hours": 1},
    ]
    check(
        "案例 2 不均等分配",
        assign_tasks(unequal_tasks, {"m1": 10, "m2": 5})
        == {"T1": "m1", "T2": "m2", "T3": "m1"},
    )

    zero_capacity_tasks = [
        {"id": "T1", "est_hours": 4},
        {"id": "T2", "est_hours": 2},
    ]
    check(
        "案例 3 排除零可用工時組員",
        assign_tasks(zero_capacity_tasks, {"m1": 10, "m2": 0})
        == {"T1": "m1", "T2": "m1"},
    )

    overload_tasks = [
        {"id": "T1", "est_hours": 8},
        {"id": "T2", "est_hours": 4},
    ]
    check(
        "案例 4 超載時仍完成分配",
        assign_tasks(overload_tasks, {"m1": 5, "m2": 5})
        == {"T1": "m1", "T2": "m2"},
    )
    check(
        "沒有正數可用工時時回傳空 dict",
        assign_tasks(overload_tasks, {"m1": 0, "m2": 0}) == {},
    )


def case_9_and_18():
    """案例 9、18：鎖定與已完成任務保留原指派並計入負載。"""
    capacities = {"m1": 10, "m2": 10}
    locked_tasks = [
        {"id": "T1", "est_hours": 5, "assignee": "m2", "locked": True},
        {"id": "T2", "est_hours": 4},
        {"id": "T3", "est_hours": 2},
    ]
    expected = {"T1": "m2", "T2": "m1", "T3": "m1"}
    check(
        "案例 9 鎖定任務保留並計入負載",
        assign_tasks(locked_tasks, capacities) == expected,
    )

    completed_tasks = [
        {"id": "T1", "est_hours": 5, "assignee": "m2", "status": "done"},
        {"id": "T2", "est_hours": 4},
        {"id": "T3", "est_hours": 2},
    ]
    check(
        "案例 18 已完成任務不重分並計入負載",
        assign_tasks(completed_tasks, capacities) == expected,
    )


def case_20_and_21():
    """案例 20、21：只在新負載率符合容差時採用偏好負責人。"""
    preferred_within_tolerance = [
        {"id": "T1", "est_hours": 4, "preferred": "m2"},
        {"id": "T2", "est_hours": 3},
    ]
    check(
        "案例 20 採用容差內的偏好負責人",
        assign_tasks(preferred_within_tolerance, {"m1": 10, "m2": 10})
        == {"T1": "m2", "T2": "m1"},
    )

    preferred_over_tolerance = [
        {"id": "T1", "est_hours": 8, "preferred": "m2"},
    ]
    check(
        "案例 21 不採用超過容差的偏好負責人",
        assign_tasks(preferred_over_tolerance, {"m1": 10, "m2": 5})
        == {"T1": "m1"},
    )


def case_15_task_id():
    """驗證案例 15 產生的新任務 id 從現有最大編號接續。"""
    existing_tasks = [
        {"id": "T1"},
        {"id": "T2"},
    ]
    check("案例 15 新任務 id 從 T3 接續", next_task_id(existing_tasks) == "T3")
    check("空任務清單的第一個 id 為 T1", next_task_id([]) == "T1")

    tasks_with_gaps = [
        {"id": "T2"},
        {"id": "T10"},
        {"id": "T4"},
    ]
    check("任務 id 依最大數字編號接續", next_task_id(tasks_with_gaps) == "T11")


def main():
    """執行 B 的驗收案例。
    輸入：無
    輸出：無；有任何失敗時以非 0 結束
    """
    print("== B 的驗收案例 ==")
    case_7()
    case_1_to_4()
    case_9_and_18()
    case_20_and_21()
    case_15_task_id()
    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
