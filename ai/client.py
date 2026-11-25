# 共用的 AI 呼叫（負責：D）
# 規格：docs/spec.md 第 16 節，函式名稱、參數與回傳型別須完全一致。

import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger(__name__)


def mask_names(text, names):
    """把文字中的組員姓名換成「組員」（spec 5.2、案例 16）。
    輸入：text 文字 str；names 全部組員姓名 list[str]
    輸出：遮蔽後的 str
    """
    masked_text = text
    names_by_length = sorted(
        (name for name in names if name),
        key=len,
        reverse=True,
    )
    for name in names_by_length:
        masked_text = masked_text.replace(name, "組員")
    return masked_text


def call_ai(prompt, names):
    """呼叫 AI 服務（連線設定見 spec 5.5）。
    輸入：prompt 提示詞 str；names 全部組員姓名 list[str]（送出前用 mask_names 遮蔽）
    輸出：AI 回傳的文字 str；逾時 15 秒或任何錯誤回傳 None
    """
    try:
        load_dotenv()
        base_url = os.getenv("AI_BASE_URL")
        model = os.getenv("AI_MODEL")
        api_key = os.getenv("AI_API_KEY")

        if not base_url or not model or not api_key:
            logger.warning("AI 未設定完整的 AI_BASE_URL、AI_MODEL 與 AI_API_KEY")
            return None

        request_options: dict[str, object] = {
            "response_format": {"type": "json_object"}
        }
        if "generativelanguage.googleapis.com" in base_url.lower():
            request_options["reasoning_effort"] = "minimal"

        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=15.0,
            max_retries=0,
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": mask_names(prompt, names),
                }
            ],
            **request_options,
        )
        if not response.choices:
            logger.warning("AI 回應沒有任何選項")
            return None

        content = response.choices[0].message.content
        if not isinstance(content, str) or not content.strip():
            logger.warning("AI 回應沒有文字內容")
            return None
        return content
    except Exception:
        logger.exception("AI 呼叫失敗")
        return None
