"""FileInfo と Gemini API の抽出結果を組み合わせ、schema.json に準拠した
辞書を構築するモジュール。"""

import json
from pathlib import Path
from typing import Any

from google import genai
from jsonschema import validate

from llm_structured_output_extractor.file_lister import (
    get_file_info,
    list_files,
)
from llm_structured_output_extractor.gemini_client import extract_fields
from llm_structured_output_extractor.schema_convert import to_gemini_schema

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.json"
_SCHEMA = json.loads(_SCHEMA_PATH.read_text())

_FILE_INFO_FIELDS = {
    "file_name",
    "extension",
    "is_multi_extension",
    "size_bytes",
    "modified_at",
}

_LLM_FIELDS = [
    name for name in _SCHEMA["properties"] if name not in _FILE_INFO_FIELDS
]

_LLM_SCHEMA_JSON = {
    "type": "object",
    "properties": {
        name: _SCHEMA["properties"][name] for name in _LLM_FIELDS
    },
    "required": [
        name for name in _SCHEMA["required"] if name in _LLM_FIELDS
    ],
}

_LLM_SCHEMA = to_gemini_schema(_LLM_SCHEMA_JSON)


def map_file(
    path: str | Path, *, client: genai.Client | None = None
) -> dict[str, Any]:
    """1つのファイルを schema.json に準拠した辞書に構造化する。

    FileInfo からの転記項目（file_name, extension, is_multi_extension,
    size_bytes, modified_at）はコード側で直接算出し、それ以外の項目は
    Gemini API の Structured Output 機能にファイル名を渡して抽出する。
    組み立てた結果を schema.json に対して検証する。

    Args:
        path: 対象ファイルのパス。
        client: gemini_client.extract_fields に渡す genai.Client。
            省略時は環境変数から生成される（テストではモックを注入する）。

    Returns:
        schema.json のプロパティに対応するキーを持つ辞書。
    """
    info = get_file_info(path)
    name = info.name

    llm_result = extract_fields(name, _LLM_SCHEMA, client=client)

    result: dict[str, Any] = {
        "file_name": name,
        "extension": Path(name).suffix,
        "is_multi_extension": len(Path(name).suffixes) > 1,
        "size_bytes": info.size,
        "modified_at": info.mtime.isoformat(),
        **llm_result,
    }

    validate(instance=result, schema=_SCHEMA)
    return result


def map_folder(
    folder: str | Path, *, client: genai.Client | None = None
) -> list[dict[str, Any]]:
    """フォルダ直下にあるファイルを、それぞれ schema.json に準拠した
    辞書に構造化したリストを取得する。

    Args:
        folder: 対象フォルダのパス。
        client: `map_file` に渡す genai.Client。

    Returns:
        `map_file` の戻り値をファイル名の昇順に並べたリスト。
    """
    folder_path = Path(folder)
    return [
        map_file(folder_path / name, client=client)
        for name in list_files(folder_path)
    ]
