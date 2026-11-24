# 讀寫 JSON（負責：A）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
import json
from pathlib import Path


def load_json(path, default):
    """讀取 JSON 檔。
    輸入：path 檔案路徑 str；default 檔案不存在或損壞時回傳的預設值 dict
    輸出：dict
    """
    file_path = Path(path)

    # 檔案不存在：回傳預設值
    if not file_path.exists():
        return _copy_default(default)

    try:
        # 一律用 utf-8 讀，Windows 預設的 cp950 會讀錯中文（spec 13）
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        # 內容損壞：先備份壞檔，再回傳預設值，不讓程式當掉
        _backup_broken_file(file_path)
        return _copy_default(default)
    except OSError:
        # 讀不到檔案（例如沒有權限）：回傳預設值
        return _copy_default(default)

    # 最外層必須是 dict（spec 14 的檔案都是 dict），不是就當成損壞
    if not isinstance(data, dict):
        _backup_broken_file(file_path)
        return _copy_default(default)

    return data


def save_json(path, data):
    """把 dict 寫成 JSON 檔。
    輸入：path 檔案路徑 str；data 要寫入的 dict
    輸出：無
    """
    file_path = Path(path)

    # 資料夾不存在就先建立（例如第一次執行時還沒有 data/）
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # ensure_ascii=False 讓中文直接存成中文；indent=2 讓檔案方便人看
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _backup_broken_file(file_path):
    """（內部用）把損壞的檔案改名成 .bak 保留，避免之後自動存檔把它覆蓋掉。
    輸入：file_path 損壞檔案的 Path
    輸出：無；例如 tasks.json 會變成 tasks.json.bak，已有舊的 .bak 時會被取代
    """
    backup_path = file_path.with_name(file_path.name + ".bak")
    try:
        file_path.replace(backup_path)
    except OSError:
        # 改名失敗也不讓程式當掉，照樣回傳預設值
        pass


def _copy_default(default):
    """（內部用）複製一份預設值，避免多次讀取時共用同一個 list 或 dict。
    輸入：default 預設值 dict
    輸出：內容相同的新 dict
    """
    # 先轉成 JSON 字串再轉回來，裡面的 list、dict 都會是新的
    return json.loads(json.dumps(default))
