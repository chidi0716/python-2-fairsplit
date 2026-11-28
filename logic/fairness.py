# 負載率與公平指標（負責：C）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
# 目前是空殼：第二版 estimate_bias 尚未實作。


def calc_load_rates(tasks, capacities):
    # 做什麼：計算有可用工時組員的負載率；輸入：任務 list 與可用工時 dict；輸出：組員 id 對負載率 dict。
    rates = {}
    for member_id, capacity in capacities.items():
        if capacity <= 0:
            continue

        assigned_hours = 0
        for task in tasks:
            if task.get("assignee") == member_id:
                assigned_hours += task.get("est_hours", 0)

        rates[member_id] = assigned_hours / capacity
    return rates


def format_load_formula(w, c):
    # 做什麼：建立負載率算式；輸入：分配工時 w 與可用工時 c；輸出：格式化算式 str。
    if c == 0:
        return "無可用工時"

    hours_text = f"{w:.1f}".rstrip("0").rstrip(".")
    capacity_text = f"{c:.1f}".rstrip("0").rstrip(".")
    rate = w / c
    return (
        "負載率 = 已分配工時 ÷ 可用工時 = "
        f"{hours_text} ÷ {capacity_text} = {rate:.2f}"
    )


def max_min_ratio(rates):
    # 做什麼：計算最大負載率除以最小負載率；輸入：負載率 dict；輸出：float，最小值為 0 時回傳 None。
    if not rates:
        return None

    minimum_rate = min(rates.values())
    if minimum_rate == 0:
        return None
    return max(rates.values()) / minimum_rate


def std_dev(rates):
    # 做什麼：計算負載率的母體標準差；輸入：負載率 dict；輸出：float。
    if not rates:
        return 0.0

    values = list(rates.values())
    average = sum(values) / len(values)
    squared_differences = 0
    for value in values:
        squared_differences += (value - average) ** 2
    return (squared_differences / len(values)) ** 0.5


def gini(rates):
    # 做什麼：計算負載率的 Gini 係數；輸入：負載率 dict；輸出：float。
    if not rates:
        return 0.0

    values = list(rates.values())
    average = sum(values) / len(values)
    if average == 0:
        return 0.0

    difference_sum = 0
    for first_value in values:
        for second_value in values:
            difference_sum += abs(first_value - second_value)

    count = len(values)
    return difference_sum / (2 * count * count * average)


def find_overload(rates):
    # 做什麼：找出負載率大於 1 的組員；輸入：負載率 dict；輸出：組員 id list。
    overloaded_members = []
    for member_id, rate in rates.items():
        if rate > 1:
            overloaded_members.append(member_id)
    return overloaded_members


def calc_progress(tasks):
    # 做什麼：計算每位組員與全組完成率；輸入：任務 list；輸出：每人完成率 dict 與全組完成率。
    member_hours = {}
    member_done_hours = {}
    total_assigned_hours = 0
    total_done_hours = 0

    for task in tasks:
        member_id = task.get("assignee")
        if member_id is None:
            continue

        hours = task.get("est_hours", 0)
        member_hours[member_id] = member_hours.get(member_id, 0) + hours
        total_assigned_hours += hours

        if task.get("status") == "done":
            member_done_hours[member_id] = member_done_hours.get(member_id, 0) + hours
            total_done_hours += hours

    member_progress = {}
    for member_id, assigned_hours in member_hours.items():
        if assigned_hours == 0:
            member_progress[member_id] = None
        else:
            done_hours = member_done_hours.get(member_id, 0)
            member_progress[member_id] = done_hours / assigned_hours

    if total_assigned_hours == 0:
        team_progress = None
    else:
        team_progress = total_done_hours / total_assigned_hours

    return member_progress, team_progress


def estimate_bias(tasks):
    """統計每位組員實際 ÷ 估計工時的平均（第二版）。
    輸入：含 actual_hours 的任務 list[dict]
    輸出：dict（組員 id → 平均比值）
    """
    return {}
