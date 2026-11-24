# FairSplit 公平分工引擎

讓大學小組看到「誰的負擔超過他的可用時間」，並取得分工建議。

國立中央大學「程式設計-Python」期末專題。完整規格見 [`docs/spec.md`](docs/spec.md)。

## 功能

1. **任務拆解與編輯**：AI 把專題描述拆成任務並估工時，組員可逐項修改、新增、刪除與拆分。
2. **可用時間與自動分配**：每人填每週可用小時與不可用日期（也可用一句話描述，由 AI 解析），程式依負載率用貪心法分配任務，可手動改指派並鎖定。
3. **公平指標與進度**：顯示每人的負載率（附算式）、最大最小比、超載提示與完成率，不做排名。

AI 只負責拆任務與解析可用時間；分配與所有指標都由 Python 計算，可以手算驗證。

## 環境需求

- Python 3.10 以上
- Streamlit 1.40 以上（由 `requirements.txt` 安裝）

## 安裝

```bash
git clone https://github.com/chidi0716/python-2-fairsplit.git
cd python-2-fairsplit
python -m venv .venv
```

啟用虛擬環境：

- Windows：`.venv\Scripts\activate`
- macOS／Linux：`source .venv/bin/activate`

安裝套件：

```bash
pip install -r requirements.txt
```

## AI 設定（選用）

> AI 供應商在 11/25 由 D 實測後決定，決定後更新本節。

不設定也能使用：AI 按鈕會失效，改用手動輸入完成全部流程。

1. 複製範本：Windows 用 `copy .env.example .env`，macOS／Linux 用 `cp .env.example .env`。
2. 依選定的服務填入 `.env` 的三個值：

| 服務 | `AI_BASE_URL` | `AI_MODEL` | `AI_API_KEY` 取得方式 |
|---|---|---|---|
| GitHub Models | `https://models.github.ai/inference` | `openai/gpt-4o-mini` | GitHub → Settings → Developer settings → Personal access tokens，建立權杖並開啟 `models:read` 權限 |
| Google AI Studio | `https://generativelanguage.googleapis.com/v1beta/openai/` | 待實測後填入 | 在 Google AI Studio 建立 API 金鑰 |

`.env` 已列入 `.gitignore`，**不要 commit，也不要貼給別人**。

## 執行

在專案根目錄執行：

```bash
streamlit run app.py
```

資料會自動存在 `data/`，刪除 `data/` 裡的 JSON 檔即可清除全部資料。

## 測試

在專案根目錄執行全部測試（`run_tests.py` 由 B 完成後可用）：

```bash
python run_tests.py
```

單獨執行某人的測試，例如 A：

```bash
python -m tests.test_a
```

## 檔案說明

| 路徑 | 內容 | 負責 |
|---|---|---|
| `app.py` | 主程式：初始化、側欄、分頁、告知彈窗、自動存檔 | A |
| `logic/storage.py` | 讀寫 JSON | A |
| `logic/members.py` | 組員 id 與刪除組員 | A |
| `logic/capacity.py` | 可用天數與可用工時 | C |
| `logic/validators.py` | 可用時間與日期的驗證 | C |
| `logic/planner.py` | 排序與分配 | B |
| `logic/task_ops.py` | 任務 id 與拆分 | B |
| `logic/fairness.py` | 負載率、公平指標與完成率 | C |
| `ai/client.py` | 共用的 AI 呼叫與姓名遮蔽 | D |
| `ai/tasks.py` | AI 拆任務、驗證與合併 | D |
| `ai/availability.py` | AI 解析可用時間 | D |
| `ui/tasks.py` | 分頁 1「任務」 | D |
| `ui/availability.py` | 分頁 2「可用時間」 | A |
| `ui/assign.py` | 分頁 3 上半：分配按鈕與指派表 | B |
| `ui/metrics.py` | 分頁 3 下半：圖表與指標 | C |
| `ui/reassign.py` | 第二版：重排建議 | A |
| `tests/test_a.py`～`test_d.py` | 各人的驗收案例 | A～D |
| `run_tests.py` | 依序執行四個測試檔 | B |
| `data/demo/` | Demo 與開發用的範例資料 | B |
| `docs/ai-log.md` | AI 協作紀錄 | 各人 |
| `docs/interviews.md` | 去識別化訪談紀錄 | C |

組員：A 林其棣、B 董謙耀、C 鄭勤翰、D 黃政捷。

## 開發流程

- `main` 只放能執行的版本，不直接 commit 到 `main`。
- 每人在 `feat-<組員代號>-<功能>` 分支開發，例如 `feat-B-assign`。
- 每完成一個函式就發 Pull Request，至少一位其他組員看過再合併。
- 發 PR 前先執行 `python run_tests.py`，全部通過才發。
- commit 訊息用中文寫「做了什麼」，例如「新增 gini 函式與案例 1、2 測試」。
- 只修改自己負責的檔案；要改別人的檔案，先請負責人改。
- 函式名稱、參數與回傳型別以 `docs/spec.md` 第 16 節為準，要改先在群組提出並經全組同意。
- 用 AI 程式助手時，提示詞開頭貼上 `docs/spec.md` 第 13 節的「固定前提」。

## AI 協助標示

> 程式完成後依實際情況補上哪些部分有 AI 協助。

每次使用 AI 的紀錄見 [`docs/ai-log.md`](docs/ai-log.md)。
