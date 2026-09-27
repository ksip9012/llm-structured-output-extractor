"""schema.json（JSON Schema draft 2020-12）を Gemini API の
response_schema（OpenAPI 3.0 サブセット）形式に変換するモジュール。"""

from typing import Any

from google.genai import types

_TYPE_MAP = {
    "string": types.Type.STRING,
    "integer": types.Type.INTEGER,
    "number": types.Type.NUMBER,
    "boolean": types.Type.BOOLEAN,
    "object": types.Type.OBJECT,
}


def _convert_property(prop_schema: dict[str, Any]) -> types.Schema:
    """JSON Schema のプロパティ定義1件を Gemini の Schema に変換する。

    `type: ["string", "null"]` のような nullable 表現は、Gemini の
    `nullable` フィールドに変換する。`format`（例: `"date"`）は Gemini の
    STRING 型では `"enum"` / `"date-time"` 以外の値が未サポートのため、
    プロンプト・description 側の指示に委ね、変換時には引き継がない。
    """
    json_type = prop_schema["type"]
    nullable = False
    if isinstance(json_type, list):
        non_null_types = [t for t in json_type if t != "null"]
        nullable = "null" in json_type
        json_type = non_null_types[0]

    if json_type == "object":
        schema = _convert_object(prop_schema)
    else:
        schema = types.Schema(type=_TYPE_MAP[json_type])

    if nullable:
        schema.nullable = True
    if "description" in prop_schema:
        schema.description = prop_schema["description"]
    if "enum" in prop_schema:
        schema.enum = prop_schema["enum"]
    return schema


def _convert_object(schema: dict[str, Any]) -> types.Schema:
    properties = schema.get("properties", {})
    return types.Schema(
        type=types.Type.OBJECT,
        properties={
            name: _convert_property(sub) for name, sub in properties.items()
        },
        required=schema.get("required", []),
        property_ordering=list(properties.keys()),
    )


def to_gemini_schema(schema: dict[str, Any]) -> types.Schema:
    """JSON Schema（`type: "object"`）を Gemini の response_schema に変換する。

    Args:
        schema: `properties` / `required` を持つオブジェクト型の JSON Schema。

    Returns:
        `google.genai.types.GenerateContentConfig(response_schema=...)` に
        渡せる `types.Schema`。
    """
    return _convert_object(schema)
