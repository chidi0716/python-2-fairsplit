# AI 拆任務與驗證（負責：D）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 目前是空殼：回傳固定範例值，由負責人換成真正的程式。


def build_task_prompt(description, deadline, member_count, weeks, project_type, member_level):
    """組出任務拆解的提示詞（spec 5.3）。
    輸入：description 專題描述 str；deadline 日期 str；member_count 人數 int；
          weeks 週數 int；project_type、member_level 選填 str
    輸出：提示詞 str
    """
    return ""


def validate_task(task):
    """驗證 AI 回傳的單一任務（spec 5.4）。
    輸入：task 任務 dict
    輸出：(是否合法 bool, 訊息 str)
    """
    return True, ""


def split_tasks_with_ai(description, deadline, member_count, weeks, project_type, member_level, names):
    """請 AI 拆任務並逐項驗證。
    輸入：同 build_task_prompt，加上 names 全部組員姓名 list[str]
    輸出：(只含 title、est_hours 的合法任務 list[dict], 提示訊息 list[str])
    """
    return [], ["AI 暫時無法使用，請手動新增任務"]


def explain_reassign_with_ai(before, after, metrics):
    """請 AI 用白話說明重排原因（第二版）。
    輸入：before、after 重排前後的分配 dict；metrics 指標 dict
    輸出：白話說明 str
    """
    return ""
