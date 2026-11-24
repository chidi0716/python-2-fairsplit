# 組員 id 與刪除組員（負責：A）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 目前是空殼：回傳固定範例值，由負責人換成真正的程式。


def next_member_id(members):
    """產生下一個組員 id。
    輸入：members 組員 list[dict]
    輸出：下一個組員 id str，例如 "m3"（現有 id 數字部分的最大值加 1）
    """
    return "m1"


def remove_member(members, tasks, member_id):
    """刪除組員，並清除他在任務中的指派與偏好（案例 14）。
    輸入：members 組員 list[dict]；tasks 任務 list[dict]；member_id 組員 id str
    輸出：(新組員 list, 新任務 list)
    """
    return list(members), list(tasks)
