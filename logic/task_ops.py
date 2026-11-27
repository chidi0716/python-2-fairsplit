# 任務 id、拆分與合併 AI 任務（負責：B）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 目前是空殼：回傳固定範例值，由負責人換成真正的程式。


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
    return list(tasks)


def merge_ai_tasks(existing, ai_tasks):
    """把 AI 拆出的任務併入現有任務（spec 5.4、案例 15）。
    輸入：existing 現有任務 list[dict]；ai_tasks 只含 title、est_hours 的合法任務 list[dict]
    輸出：新 list[dict]：保留鎖定或已完成的任務，刪除其他現有任務，AI 任務補齊欄位
    """
    return list(existing)
