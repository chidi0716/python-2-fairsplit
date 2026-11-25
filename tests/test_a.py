# A 的驗收案例（負責：A）：案例 6、12、13、14（spec 第 17 節）
# 執行方式：在專案根目錄執行 python -m tests.test_a
# 案例 12、13 與 14 的畫面部分以手動操作檢查，這裡只測邏輯。
import sys
from pathlib import Path

from logic.members import next_member_id, remove_member
from logic.storage import load_json, save_json

# 測試用的暫存資料夾，測完會刪掉
TMP_DIR = Path(__file__).parent / "_tmp_test_a"

results = []


def check(name, ok):
    """印出單一檢查的結果，並記錄是否通過。
    輸入：name 案例名稱 str；ok 是否通過 bool
    輸出：無
    """
    results.append(ok)
    print(f"{'通過' if ok else '失敗'}：{name}")


def case_6():
    """案例 6：含中文的資料用 save_json 寫入，再用 load_json 讀回，內容一字不差。"""
    path = TMP_DIR / "tasks.json"
    data = {"tasks": [{"id": "T1", "title": "整理問題陳述與訪談", "est_hours": 3.5, "assignee": None}]}
    save_json(str(path), data)
    check("案例 6 中文檔案：讀回內容一字不差", load_json(str(path), {"tasks": []}) == data)

    # 檔案裡的中文要直接存成中文，不是 \u 跳脫字元
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    check("案例 6 中文檔案：檔案內直接存中文", "整理問題陳述與訪談" in text)


def storage_edge_cases():
    """load_json、save_json 的邊界情況（spec 14 最後一段）。"""
    default = {"tasks": []}

    # 檔案不存在：回傳預設值
    missing = TMP_DIR / "missing.json"
    check("讀取不存在的檔案回傳預設值", load_json(str(missing), default) == {"tasks": []})

    # 內容損壞：回傳預設值，不當機
    broken = TMP_DIR / "broken.json"
    broken.write_text("{這不是 JSON", encoding="utf-8")
    check("讀取損壞的檔案回傳預設值", load_json(str(broken), default) == {"tasks": []})

    # 損壞的檔案改名成 .bak 保留，內容不變
    backup = TMP_DIR / "broken.json.bak"
    backup_text = backup.read_text(encoding="utf-8") if backup.exists() else ""
    check("損壞的檔案備份成 .bak", backup_text == "{這不是 JSON" and not broken.exists())

    # 最外層不是 dict 也算損壞，同樣備份
    not_dict = TMP_DIR / "list.json"
    not_dict.write_text("[1, 2]", encoding="utf-8")
    result_not_dict = load_json(str(not_dict), default)
    check("最外層不是 dict 時回傳預設值並備份",
          result_not_dict == {"tasks": []} and (TMP_DIR / "list.json.bak").exists())

    # 回傳的預設值是複本：改它不會改到原本的 default
    result = load_json(str(missing), default)
    result["tasks"].append("x")
    check("回傳的預設值是複本", default == {"tasks": []})

    # 資料夾不存在時會自動建立
    nested = TMP_DIR / "new_folder" / "settings.json"
    save_json(str(nested), {"notice_accepted": True})
    check("資料夾不存在時自動建立", load_json(str(nested), {}) == {"notice_accepted": True})


def case_14():
    """案例 14：刪除組員 m2 後，清除他的指派、鎖定與偏好（畫面上的 capacities 以手動檢查）。"""
    members = [
        {"id": "m1", "name": "組員甲", "weekly_hours": 6, "unavailable_dates": []},
        {"id": "m2", "name": "組員乙", "weekly_hours": 8, "unavailable_dates": []},
    ]
    tasks = [
        {"id": "T1", "title": "整理需求", "est_hours": 3, "assignee": "m2", "locked": True, "preferred": None},
        {"id": "T2", "title": "製作簡報", "est_hours": 2, "assignee": "m1", "locked": True, "preferred": "m2"},
    ]
    new_members, new_tasks = remove_member(members, tasks, "m2")

    check("案例 14 刪除組員：名單不再有 m2", [m.get("id") for m in new_members] == ["m1"])
    t1, t2 = new_tasks[0], new_tasks[1]
    check("案例 14 刪除組員：T1 改成未指派並取消鎖定", t1["assignee"] is None and t1["locked"] is False)
    check("案例 14 刪除組員：T2 的偏好清成 null，其他欄位不變",
          t2["preferred"] is None and t2["assignee"] == "m1" and t2["locked"] is True)
    check("案例 14 刪除組員：不改動傳入的原資料",
          len(members) == 2 and tasks[0]["assignee"] == "m2" and tasks[0]["locked"] is True
          and tasks[1]["preferred"] == "m2")


def member_id_cases():
    """next_member_id：取現有 id 數字部分的最大值加 1。"""
    check("沒有組員時 id 為 m1", next_member_id([]) == "m1")
    check("刪過組員後 id 不重複", next_member_id([{"id": "m1"}, {"id": "m3"}]) == "m4")
    check("數字比大小而不是比字串", next_member_id([{"id": "m9"}, {"id": "m10"}]) == "m11")


def remove_tmp_dir():
    """刪掉測試用的暫存資料夾。"""
    if not TMP_DIR.exists():
        return
    # 由深到淺刪除：先刪檔案，再刪資料夾
    for item in sorted(TMP_DIR.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if item.is_dir():
            item.rmdir()
        else:
            item.unlink()
    TMP_DIR.rmdir()


def main():
    """依序執行 A 的驗收案例。
    輸入：無
    輸出：無；有任何失敗時以非 0 結束，讓 run_tests.py 判斷
    """
    print("== A 的驗收案例 ==")
    remove_tmp_dir()
    TMP_DIR.mkdir()
    try:
        case_6()
        storage_edge_cases()
        case_14()
        member_id_cases()
    finally:
        remove_tmp_dir()
    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
