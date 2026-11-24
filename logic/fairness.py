# 負載率與公平指標（負責：C）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 目前是空殼：回傳固定範例值，由負責人換成真正的程式。


def calc_load_rates(tasks, capacities):
    """計算每位組員的負載率 L_i（spec 4.1）。
    輸入：tasks 任務 list[dict]；capacities 可用工時 dict
    輸出：dict（組員 id → 負載率）
    """
    return {}


def format_load_formula(w, c):
    """產生負載率算式字串（spec 4.4、案例 22）。
    輸入：w 分配工時 float；c 可用工時 float
    輸出：算式 str；c 為 0 時回傳「無可用工時」
    """
    return "負載率 = 已分配工時 ÷ 可用工時 = 12 ÷ 15 = 0.80"


def max_min_ratio(rates):
    """最大最小比（spec 4.4）。
    輸入：rates 負載率 dict
    輸出：float；最小值為 0 時回傳 None
    """
    return 1.0


def std_dev(rates):
    """負載率的母體標準差（spec 4.4）。
    輸入：rates 負載率 dict
    輸出：float
    """
    return 0.0


def gini(rates):
    """負載率的 Gini 係數（spec 4.4）。
    輸入：rates 負載率 dict
    輸出：float
    """
    return 0.0


def find_overload(rates):
    """找出負載率大於 1 的組員（spec 4.4）。
    輸入：rates 負載率 dict
    輸出：超載組員 id list
    """
    return []


def calc_progress(tasks):
    """計算完成率（spec 4.5）。
    輸入：tasks 任務 list[dict]
    輸出：(每人完成率 dict, 全組完成率)；無法計算時為 None
    """
    return {}, None


def estimate_bias(tasks):
    """統計每位組員實際 ÷ 估計工時的平均（第二版）。
    輸入：含 actual_hours 的任務 list[dict]
    輸出：dict（組員 id → 平均比值）
    """
    return {}
