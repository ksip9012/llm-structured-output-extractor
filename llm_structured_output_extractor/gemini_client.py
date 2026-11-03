"""Gemini API の Structured Output（response_schema）を呼び出すモジュール。"""

import os
from typing import Any

from google import genai
from google.genai import types

from llm_structured_output_extractor.llm_client import (
    LLMClient,
    parse_json_response,
)

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

_PROMPT_TEMPLATE = (
    "次のファイル名を分析し、指定されたスキーマの各項目を抽出してください。\n"
    "ファイル名: {filename}"
)


def extract_fields(
    filename: str,
    schema: types.Schema,
    *,
    client: LLMClient | None = None,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """ファイル名を Gemini API に渡し、schema に従って構造化データを抽出する。

    Args:
        filename: 抽出対象のファイル名。
        schema: 抽出結果が従うべき Gemini Schema
            （`schema_convert.to_gemini_schema` の戻り値）。
        client: 使用するクライアント（`LLMClient` の形）。省略時は環境変数
            `GEMINI_API_KEY` から genai.Client を生成する。
            テストではモッククライアントを注入する
            （decisions/0004 参照）。
        model: 使用するモデル名。

    Returns:
        schema の各プロパティに対応する値を持つ辞書。
    """
    client = client or genai.Client()
    response = client.models.generate_content(
        model=model,
        contents=_PROMPT_TEMPLATE.format(filename=filename),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )
    return parse_json_response(response)
