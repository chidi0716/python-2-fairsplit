# 共用狀態寫入：update_tasks（負責：A）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。
import streamlit as st


def update_tasks(new_tasks):
    """寫入任務並讓表格重新讀取（spec 15.2）。所有寫入 tasks 的地方都要透過這個函式。
    輸入：new_tasks 任務 list[dict]
    輸出：無（寫入 st.session_state["tasks"]，並把 tasks_version 加 1）
    """
    # 存一份新的 list，避免呼叫端之後改到同一個物件
    st.session_state["tasks"] = list(new_tasks)
    # 版本號加 1，data_editor 的 key 跟著改變，表格才會重新讀取 tasks（spec 15.5）
    st.session_state["tasks_version"] = st.session_state.get("tasks_version", 0) + 1
