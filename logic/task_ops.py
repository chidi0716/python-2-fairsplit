import math

# 任務 id、拆分與合併 AI 任務（負責：B）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。


def next_task_id(tasks):
    """產生下一個任務 id。
    輸入：tasks 任務 list[dict]
    輸出：下一個任務 id str，例如 "T3"
    """
    highest_number = 0
    for task in tasks:
        task_number = int(task["id"][1:])
        if task_number > highest_number:
            highest_number = task_number

    return "T" + str(highest_number + 1)


def split_task(tasks, task_id):
    """把任務拆成兩份（spec 4.6）。
    輸入：tasks 任務 list[dict]；task_id 任務 id str
    輸出：拆分後的新 list[dict]
    """
    new_tasks = []
    task_to_split = None

    for task in tasks:
        new_task = dict(task)
        new_tasks.append(new_task)
        if task["id"] == task_id:
            task_to_split = task

    if task_to_split is None or task_to_split["est_hours"] < 1:
        return new_tasks

    original_hours = task_to_split["est_hours"]
    half_hours = original_hours / 2
    first_task_hours = math.ceil(half_hours / 0.5) * 0.5

    for task in new_tasks:
        if task["id"] == task_id:
            task["title"] = task_to_split["title"] + "（1）"
            task["est_hours"] = first_task_hours
            break

    second_task = dict(task_to_split)
    second_task["id"] = next_task_id(tasks)
    second_task["title"] = task_to_split["title"] + "（2）"
    second_task["est_hours"] = original_hours - first_task_hours
    second_task["assignee"] = None
    second_task["locked"] = False
    new_tasks.append(second_task)

    return new_tasks


def merge_ai_tasks(existing, ai_tasks):
    """把 AI 拆出的任務併入現有任務（spec 5.4、案例 15）。
    輸入：existing 現有任務 list[dict]；ai_tasks 只含 title、est_hours 的合法任務 list[dict]
    輸出：新 list[dict]：保留鎖定或已完成的任務，刪除其他現有任務，AI 任務補齊欄位
    """
    merged_tasks = []

    for task in existing:
        if task.get("locked", False) or task.get("status") == "done":
            merged_tasks.append(dict(task))

    next_id_number = int(next_task_id(existing)[1:])

    for ai_task in ai_tasks:
        merged_task = {
            "id": "T" + str(next_id_number),
            "title": ai_task["title"],
            "est_hours": ai_task["est_hours"],
            "est_source": "ai",
            "assignee": None,
            "locked": False,
            "preferred": None,
            "status": "todo",
            "actual_hours": None,
            "depends_on": [],
        }
        merged_tasks.append(merged_task)
        next_id_number += 1

    return merged_tasks
