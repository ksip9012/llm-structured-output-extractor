"""Gemini API を呼び出すクライアントの型と、応答の読み取り。

本体の関数は、本物の `google.genai.Client` と、テストやベンチマークで使う
偽のクライアント・記録用のクライアントの両方を受け取る。そのため、使う形
（`client.models.generate_content(...)` と、応答の `text`）だけを Protocol
で定める（decisions/0008 参照）。
"""

import json
from typing import Any, Protocol

from google.genai import types


class LLMResponse(Protocol):
    """`generate_content` の応答。本文の JSON を `text` に持つ。"""

    @property
    def text(self) -> str | None: ...


class LLMModels(Protocol):
    """`client.models` の形。"""

    def generate_content(
        self,
        *,
        model: str,
        contents: str,
        config: types.GenerateContentConfig,
    ) -> LLMResponse: ...


class LLMClient(Protocol):
    """`google.genai.Client` のうち、このパッケージが使う部分の形。"""

    @property
    def models(self) -> LLMModels: ...


def parse_json_response(response: LLMResponse) -> dict[str, Any]:
    """応答の本文を JSON として読む。

    Args:
        response: `generate_content` の応答。

    Returns:
        本文の JSON を読んだ辞書。

    Raises:
        ValueError: 応答に本文がない場合（安全のための遮断などで空になる）。
    """
    if response.text is None:
        raise ValueError("Gemini の応答に本文がなかった")
    return json.loads(response.text)
