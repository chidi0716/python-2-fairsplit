from datetime import date, timedelta
from heapq import heappop, heappush

from logic.capacity import calc_capacity

# 排序與分配（負責：B）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
PREFERENCE_TOLERANCE = 0.1

def sort_tasks(tasks):
    """依工時大到小、再依 id 數字部分由小到大排序（spec 4.3 第 3 步）。
    輸入：tasks 任務 list[dict]
    輸出：排序後的新 list[dict]
    """
    sorted_tasks = sorted(
        tasks,
        key=lambda task: (-task["est_hours"], int(task["id"][1:])),
    )
    return sorted_tasks


def pick_member(task, loads, capacities):
    """選出接下這個任務的組員（spec 4.3 第 4、5 步）。
    輸入：task 任務 dict；loads 目前工時 dict（組員 id → 小時）；capacities 可用工時 dict
    輸出：組員 id str
    """
    eligible_members = []
    for member_id in capacities:
        if capacities[member_id] > 0:
            eligible_members.append(member_id)

    if not eligible_members:
        raise ValueError("沒有可用工時大於 0 的組員")

    task_hours = task["est_hours"]
    best_member = eligible_members[0]
    best_rate = (loads.get(best_member, 0) + task_hours) / capacities[best_member]

    for member_id in eligible_members[1:]:
        new_rate = (loads.get(member_id, 0) + task_hours) / capacities[member_id]
        has_lower_rate = new_rate < best_rate
        has_better_tie_break = (
            new_rate == best_rate
            and (
                capacities[member_id] > capacities[best_member]
                or (
                    capacities[member_id] == capacities[best_member]
                    and int(member_id[1:]) < int(best_member[1:])
                )
            )
        )
        if has_lower_rate or has_better_tie_break:
            best_member = member_id
            best_rate = new_rate

    preferred_member = task.get("preferred")
    if preferred_member in eligible_members:
        preferred_rate = (
            loads.get(preferred_member, 0) + task_hours
        ) / capacities[preferred_member]
        if preferred_rate <= best_rate + PREFERENCE_TOLERANCE:
            return preferred_member

    return best_member


def assign_tasks(tasks, capacities):
    """以貪心法分配任務（spec 4.3）。
    輸入：tasks 任務 list[dict]；capacities 可用工時 dict（組員 id → 小時）
    輸出：dict（任務 id → 組員 id），含鎖定與已完成任務；沒有人可分配時回傳空 dict
    """
    eligible_capacities = {}
    for member_id in capacities:
        if capacities[member_id] > 0:
            eligible_capacities[member_id] = capacities[member_id]

    if not eligible_capacities:
        return {}

    loads = {}
    for member_id in eligible_capacities:
        loads[member_id] = 0

    assignments = {}
    tasks_to_assign = []

    for task in tasks:
        is_fixed = task.get("locked", False) or task.get("status") == "done"
        if is_fixed:
            assignee = task.get("assignee")
            if assignee is not None:
                assignments[task["id"]] = assignee
                if assignee in loads:
                    loads[assignee] += task["est_hours"]
        else:
            tasks_to_assign.append(task)

    for task in sort_tasks(tasks_to_assign):
        assignee = pick_member(task, loads, eligible_capacities)
        assignments[task["id"]] = assignee
        loads[assignee] += task["est_hours"]

    return assignments


def topo_order(tasks):
    """依 depends_on 排出任務順序（第二版）。
    輸入：含 depends_on 的任務 list[dict]
    輸出：(順序 list, 錯誤訊息 str 或 None)
    """
    task_by_id = {}
    task_order = {}
    dependencies = {}

    for index, task in enumerate(tasks):
        task_id = task["id"]
        if task_id in task_by_id:
            return [], f"任務 id 重複：{task_id}"
        task_by_id[task_id] = task
        task_order[task_id] = index

    for task in tasks:
        task_id = task["id"]
        task_dependencies = list(dict.fromkeys(task.get("depends_on", [])))
        unknown_dependencies = [
            dependency
            for dependency in task_dependencies
            if dependency not in task_by_id
        ]
        if unknown_dependencies:
            missing_ids = "、".join(unknown_dependencies)
            return [], f"{task_id} 的相依任務不存在：{missing_ids}"
        dependencies[task_id] = task_dependencies

    dependent_tasks = {task_id: [] for task_id in task_by_id}
    remaining_dependencies = {}
    for task_id, task_dependencies in dependencies.items():
        remaining_dependencies[task_id] = len(task_dependencies)
        for dependency in task_dependencies:
            dependent_tasks[dependency].append(task_id)

    ready_tasks = []
    for task_id, dependency_count in remaining_dependencies.items():
        if dependency_count == 0:
            heappush(ready_tasks, (task_order[task_id], task_id))

    ordered_tasks = []
    while ready_tasks:
        _, task_id = heappop(ready_tasks)
        ordered_tasks.append(task_by_id[task_id])

        for dependent_id in dependent_tasks[task_id]:
            remaining_dependencies[dependent_id] -= 1
            if remaining_dependencies[dependent_id] == 0:
                heappush(
                    ready_tasks,
                    (task_order[dependent_id], dependent_id),
                )

    if len(ordered_tasks) == len(tasks):
        return ordered_tasks, None

    remaining_task_ids = {
        task_id
        for task_id, dependency_count in remaining_dependencies.items()
        if dependency_count > 0
    }
    visit_state = {}
    path = []

    def find_cycle(task_id):
        visit_state[task_id] = 1
        path.append(task_id)

        for dependency in dependencies[task_id]:
            if dependency not in remaining_task_ids:
                continue
            dependency_state = visit_state.get(dependency, 0)
            if dependency_state == 1:
                cycle_start = path.index(dependency)
                return path[cycle_start:] + [dependency]
            if dependency_state == 0:
                cycle = find_cycle(dependency)
                if cycle is not None:
                    return cycle

        path.pop()
        visit_state[task_id] = 2
        return None

    for task_id in task_by_id:
        if task_id in remaining_task_ids and visit_state.get(task_id, 0) == 0:
            cycle = find_cycle(task_id)
            if cycle is not None:
                cycle_path = " → ".join(cycle)
                return [], f"循環依賴：{cycle_path}"

    return [], "偵測到循環依賴"


def reassign_unfinished(tasks, members, today):
    """以今天起算未來 7 天的可用工時，重排未完成且未鎖定任務。
    輸入：tasks 任務 list[dict]；members 組員 list[dict]；today 日期 str
    輸出：新分配建議 dict（任務 id → 組員 id）
    """
    start_date = date.fromisoformat(today)
    deadline = (start_date + timedelta(days=6)).isoformat()
    capacities = {
        member["id"]: calc_capacity(member, today, deadline)
        for member in members
    }
    unfinished_tasks = [
        task for task in tasks if task.get("status") != "done"
    ]
    assignments = assign_tasks(unfinished_tasks, capacities)

    return {
        task["id"]: assignments[task["id"]]
        for task in unfinished_tasks
        if not task.get("locked", False) and task["id"] in assignments
    }
