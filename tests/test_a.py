# A 的驗收案例（負責：A）：案例 6、12、13、14（spec 第 17 節）
# 執行方式：在專案根目錄執行 python -m tests.test_a
# 案例 12、13 與 14 的畫面部分以手動操作檢查，這裡只測邏輯。
import sys

results = []


def check(name, ok):
    """印出單一檢查的結果，並記錄是否通過。
    輸入：name 案例名稱 str；ok 是否通過 bool
    輸出：無
    """
    results.append(ok)
    print(f"{'通過' if ok else '失敗'}：{name}")


def main():
    """依序執行 A 的驗收案例。
    輸入：無
    輸出：無；有任何失敗時以非 0 結束，讓 run_tests.py 判斷
    """
    print("== A 的驗收案例 ==")
    # 待實作：案例 6 中文檔案（save_json 寫入後 load_json 讀回，內容一字不差）
    # 待實作：案例 14 刪除組員（remove_member 清除指派、鎖定與偏好）
    print("（尚無案例，階段 1、2 補上）")
    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
