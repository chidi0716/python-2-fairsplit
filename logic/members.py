# 組員 id 與刪除組員（負責：A）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。


def next_member_id(members):
    """產生下一個組員 id。
    輸入：members 組員 list[dict]
    輸出：下一個組員 id str，例如 "m3"（現有 id 數字部分的最大值加 1）
    """
    largest = 0
    for member in members:
        member_id = str(member.get("id", ""))
        # 只看 "m" 加數字的 id，例如 "m2"；格式不對的 id 略過
        number_text = member_id[1:]
        if member_id.startswith("m") and number_text.isdigit():
            largest = max(largest, int(number_text))
    # 用最大值加 1，刪過組員後也不會跟舊 id 重複
    return "m" + str(largest + 1)


def remove_member(members, tasks, member_id):
    """刪除組員，並清除他在任務中的指派與偏好（案例 14）。
    輸入：members 組員 list[dict]；tasks 任務 list[dict]；member_id 組員 id str
    輸出：(新組員 list, 新任務 list)
    """
    # 留下其他組員；用 dict() 複製，不改動傳入的原資料
    new_members = [dict(member) for member in members if member.get("id") != member_id]

    new_tasks = []
    for task in tasks:
        new_task = dict(task)
        # 他負責的任務：改成未指派，並取消鎖定，讓之後重新分配
        if new_task.get("assignee") == member_id:
            new_task["assignee"] = None
            new_task["locked"] = False
        # 以他為偏好負責人的任務：偏好清成 null
        if new_task.get("preferred") == member_id:
            new_task["preferred"] = None
        new_tasks.append(new_task)

    return new_members, new_tasks
