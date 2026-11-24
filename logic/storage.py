# 讀寫 JSON（負責：A）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 目前是空殼：回傳固定範例值，由負責人換成真正的程式。


def load_json(path, default):
    """讀取 JSON 檔。
    輸入：path 檔案路徑 str；default 檔案不存在或損壞時回傳的預設值 dict
    輸出：dict
    """
    return dict(default)


def save_json(path, data):
    """把 dict 寫成 JSON 檔。
    輸入：path 檔案路徑 str；data 要寫入的 dict
    輸出：無
    """
    return None
