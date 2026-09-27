from google.genai import types

from llm_structured_output_extractor.schema_convert import to_gemini_schema


def test_converts_plain_string_and_boolean_properties():
    schema = {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "分類",
            },
            "is_hidden": {
                "type": "boolean",
                "description": "隠しファイルか",
            },
        },
        "required": ["category", "is_hidden"],
    }

    result = to_gemini_schema(schema)

    assert result.type == types.Type.OBJECT
    assert result.properties["category"].type == types.Type.STRING
    assert result.properties["category"].description == "分類"
    assert result.properties["is_hidden"].type == types.Type.BOOLEAN
    assert result.required == ["category", "is_hidden"]
    assert result.property_ordering == ["category", "is_hidden"]


def test_converts_nullable_string_type_array():
    schema = {
        "type": "object",
        "properties": {
            "extracted_date": {
                "type": ["string", "null"],
                "format": "date",
            },
        },
        "required": ["extracted_date"],
    }

    result = to_gemini_schema(schema)

    prop = result.properties["extracted_date"]
    assert prop.type == types.Type.STRING
    assert prop.nullable is True


def test_embeds_date_format_hint_into_description():
    """Gemini の Schema は format: "date" を解釈しないため、
    description に形式を明記してモデルに伝える必要がある
    （実 API 検証で YYYYMMDD 表記が返る不具合があったための回帰テスト）。"""
    schema = {
        "type": "object",
        "properties": {
            "extracted_date": {
                "type": ["string", "null"],
                "format": "date",
                "description": "ファイル名から抽出した日付",
            },
        },
        "required": ["extracted_date"],
    }

    result = to_gemini_schema(schema)

    description = result.properties["extracted_date"].description
    assert "ファイル名から抽出した日付" in description
    assert "YYYY-MM-DD" in description


def test_converts_nullable_integer_type_array():
    schema = {
        "type": "object",
        "properties": {
            "duplicate_index": {"type": ["integer", "null"]},
        },
        "required": ["duplicate_index"],
    }

    result = to_gemini_schema(schema)

    prop = result.properties["duplicate_index"]
    assert prop.type == types.Type.INTEGER
    assert prop.nullable is True


def test_carries_over_enum_values():
    schema = {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["document", "image", "archive", "other"],
            },
        },
        "required": ["category"],
    }

    result = to_gemini_schema(schema)

    assert result.properties["category"].enum == [
        "document",
        "image",
        "archive",
        "other",
    ]
