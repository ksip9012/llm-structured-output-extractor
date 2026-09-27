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
