# 分頁 1「任務」（負責：D）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。

from datetime import date
import math

import pandas as pd
import streamlit as st

from ai.tasks import split_tasks_with_ai
from logic.task_ops import merge_ai_tasks, next_task_id, split_task
from ui.state import update_tasks


def render_tasks_tab():
    """畫出分頁 1：專題描述、AI 拆任務、任務表（spec 3.1）。
    輸入：無（從 st.session_state 讀資料）
    輸出：無
    """
    project = st.session_state.get("project", {})
    members = st.session_state.get("members", [])
    tasks = st.session_state.get("tasks", [])
    settings = st.session_state.get("settings", {})

    st.subheader("任務")
    description = st.text_area(
        "專題描述",
        value=project.get("description", ""),
        key="tasks_description",
    )
    project_type = st.text_input(
        "專題類型（選填）",
        value=project.get("project_type", ""),
        key="tasks_project_type",
    )
    member_level = st.text_input(
        "組員程度（選填）",
        value=project.get("member_level", ""),
        key="tasks_member_level",
    )
    project["description"] = description
    project["project_type"] = project_type
    project["member_level"] = member_level

    member_names = [member.get("name", "") for member in members]
    member_id_by_name = {
        member.get("name", ""): member.get("id")
        for member in members
        if member.get("name")
    }
    member_name_by_id = {
        member.get("id"): member.get("name", "")
        for member in members
    }

    def generate_tasks():
        """呼叫 AI 並把合法任務合併到目前任務。
        輸入：使用 render_tasks_tab 讀取的專題資料、組員與任務
        輸出：無（透過 update_tasks 寫入任務）
        """
        current_project = st.session_state.get("project", {})
        current_members = st.session_state.get("members", [])
        current_tasks = st.session_state.get("tasks", [])
        deadline = current_project.get("deadline", "")
        try:
            deadline_date = date.fromisoformat(deadline)
        except (TypeError, ValueError):
            st.error("請先設定有效的截止日期")
            return

        days_remaining = (deadline_date - date.today()).days
        weeks = max(1, math.ceil(days_remaining / 7))
        current_names = [member.get("name", "") for member in current_members]
        ai_tasks, messages = split_tasks_with_ai(
            current_project.get("description", ""),
            deadline,
            len(current_members),
            weeks,
            current_project.get("project_type", ""),
            current_project.get("member_level", ""),
            current_names,
        )
        for message in messages:
            st.warning(message)
        if not ai_tasks:
            return

        merged_tasks = merge_ai_tasks(current_tasks, ai_tasks)
        if merged_tasks == current_tasks:
            st.warning("AI 任務未能加入目前清單，請稍後再試或手動新增")
            return
        update_tasks(merged_tasks)
        st.rerun()

    ai_enabled = settings.get("ai_enabled", False)
    if st.button("AI 拆任務", disabled=not ai_enabled):
        if tasks:
            st.session_state["confirm_ai_task_replacement"] = True
        else:
            generate_tasks()

    if st.session_state.get("confirm_ai_task_replacement", False):
        @st.dialog("確認重新拆任務")
        def confirm_ai_task_replacement():
            """確認是否以 AI 結果取代未鎖定且未完成的任務。
            輸入：無（使用目前畫面狀態）
            輸出：無
            """
            st.write("重新拆任務會移除未鎖定且未完成的任務，繼續嗎？")
            confirm_column, cancel_column = st.columns(2)
            if confirm_column.button("確認並拆任務"):
                st.session_state["confirm_ai_task_replacement"] = False
                generate_tasks()
            if cancel_column.button("取消"):
                st.session_state["confirm_ai_task_replacement"] = False
                st.rerun()

        confirm_ai_task_replacement()

    tasks = st.session_state.get("tasks", [])
    rows = []
    for task in tasks:
        row = dict(task)
        row["est_source"] = "AI 估計" if task.get("est_source") == "ai" else "手動"
        row["preferred"] = member_name_by_id.get(task.get("preferred"), "")
        rows.append(row)

    columns = [
        "id",
        "title",
        "est_hours",
        "est_source",
        "preferred",
        "assignee",
        "locked",
        "status",
        "actual_hours",
        "depends_on",
    ]
    task_editor = st.data_editor(
        pd.DataFrame(rows, columns=columns),
        column_order=["title", "est_hours", "est_source", "preferred"],
        column_config={
            "id": None,
            "title": st.column_config.TextColumn("任務名稱", required=True),
            "est_hours": st.column_config.NumberColumn(
                "估計工時",
                min_value=0.5,
                max_value=20.0,
                step=0.5,
            ),
            "est_source": st.column_config.SelectboxColumn(
                "來源",
                options=["AI 估計", "手動"],
            ),
            "preferred": st.column_config.SelectboxColumn(
                "偏好負責人",
                options=[""] + member_names,
            ),
            "assignee": None,
            "locked": None,
            "status": None,
            "actual_hours": None,
            "depends_on": None,
        },
        disabled=["id", "assignee", "locked", "status", "actual_hours", "depends_on"],
        num_rows="dynamic",
        hide_index=True,
        key="tasks_editor_" + str(st.session_state.get("tasks_version", 0)),
    )

    edited_rows = task_editor.to_dict("records")
    original_by_id = {task.get("id"): task for task in tasks}
    ids_for_new_tasks = list(tasks)
    updated_tasks = []
    incomplete_row_found = False
    for row in edited_rows:
        title = row.get("title")
        est_hours = row.get("est_hours")
        if (
            not isinstance(title, str)
            or not 1 <= len(title.strip()) <= 30
            or not isinstance(est_hours, (int, float))
            or isinstance(est_hours, bool)
            or not math.isfinite(est_hours)
            or not 0.5 <= est_hours <= 20
        ):
            incomplete_row_found = True
            continue

        task_id = row.get("id")
        if task_id in original_by_id:
            task = dict(original_by_id[task_id])
        else:
            task_id = next_task_id(ids_for_new_tasks)
            task = {
                "id": task_id,
                "assignee": None,
                "locked": False,
                "preferred": None,
                "status": "todo",
                "actual_hours": None,
                "depends_on": [],
            }
            ids_for_new_tasks.append(task)

        task["title"] = title.strip()
        task["est_hours"] = float(est_hours)
        task["est_source"] = "ai" if row.get("est_source") == "AI 估計" else "manual"
        task["preferred"] = member_id_by_name.get(row.get("preferred"))
        updated_tasks.append(task)

    if incomplete_row_found:
        st.warning("請填寫 1 到 30 字的任務名稱，以及 0.5 到 20 小時的工時")
    elif updated_tasks != tasks:
        update_tasks(updated_tasks)
        st.rerun()

    tasks = st.session_state.get("tasks", [])
    if tasks:
        task_labels = {
            task.get("id"): task.get("title", "")
            for task in tasks
        }
        selected_task_id = st.selectbox(
            "選擇要拆分的任務",
            options=list(task_labels),
            format_func=lambda task_id: f"{task_id}：{task_labels[task_id]}",
        )
        if st.button("拆成兩份"):
            split_tasks = split_task(tasks, selected_task_id)
            if split_tasks == tasks:
                st.warning("此任務目前無法拆分")
            else:
                update_tasks(split_tasks)
                st.rerun()
