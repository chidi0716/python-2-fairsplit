# 排序與分配（負責：B）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 目前是空殼：回傳固定範例值，由負責人換成真正的程式。


def sort_tasks(tasks):
    """依工時大到小、再依 id 數字部分由小到大排序（spec 4.3 第 3 步）。
    輸入：tasks 任務 list[dict]
    輸出：排序後的新 list[dict]
    """
    return list(tasks)


def pick_member(task, loads, capacities):
    """選出接下這個任務的組員（spec 4.3 第 4、5 步）。
    輸入：task 任務 dict；loads 目前工時 dict（組員 id → 小時）；capacities 可用工時 dict
    輸出：組員 id str
    """
    return "m1"


def assign_tasks(tasks, capacities):
    """以貪心法分配任務（spec 4.3）。
    輸入：tasks 任務 list[dict]；capacities 可用工時 dict（組員 id → 小時）
    輸出：dict（任務 id → 組員 id），含鎖定與已完成任務；沒有人可分配時回傳空 dict
    """
    return {}


def topo_order(tasks):
    """依 depends_on 排出任務順序（第二版）。
    輸入：含 depends_on 的任務 list[dict]
    輸出：(順序 list, 錯誤訊息 str 或 None)
    """
    return [], None


def reassign_unfinished(tasks, members, today):
    """以今天為起點重排未完成任務（第二版）。
    輸入：tasks 任務 list[dict]；members 組員 list[dict]；today 日期 str
    輸出：新分配建議 dict（任務 id → 組員 id）
    """
    return {}
