# 共用的 AI 呼叫（負責：D）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 目前是空殼：回傳固定範例值，由負責人換成真正的程式。


def mask_names(text, names):
    """把文字中的組員姓名換成「組員」（spec 5.2、案例 16）。
    輸入：text 文字 str；names 全部組員姓名 list[str]
    輸出：遮蔽後的 str
    """
    return text


def call_ai(prompt, names):
    """呼叫 AI 服務（連線設定見 spec 5.5）。
    輸入：prompt 提示詞 str；names 全部組員姓名 list[str]（送出前用 mask_names 遮蔽）
    輸出：AI 回傳的文字 str；逾時 15 秒或任何錯誤回傳 None
    """
    return None
