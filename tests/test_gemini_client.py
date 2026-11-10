"""Gemini API 呼び出しのテスト。実 API は呼ばず、モッククライアントで
リクエスト内容・レスポンス解釈を検証する（decisions/0004 参照）。"""

from dataclasses import dataclass

from google.genai import types

from llm_structured_output_extractor.gemini_client import extract_fields


@dataclass
class _FakeResponse:
    text: str | None


class _FakeModels:
    def __init__(self, response_text):
        self.response_text = response_text
        self.calls = []

    def generate_content(self, *, model, contents, config):
        self.calls.append(
            {"model": model, "contents": contents, "config": config}
        )
        return _FakeResponse(text=self.response_text)


class _FakeClient:
    def __init__(self, response_text):
        self.models = _FakeModels(response_text)


_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "category": types.Schema(type=types.Type.STRING),
        "is_hidden": types.Schema(type=types.Type.BOOLEAN),
    },
    required=["category", "is_hidden"],
)


def test_extract_fields_parses_json_response_from_client():
    fake_client = _FakeClient('{"category": "document", "is_hidden": false}')

    result = extract_fields("notes.txt", _SCHEMA, client=fake_client)

    assert result == {"category": "document", "is_hidden": False}


def test_extract_fields_passes_filename_and_schema_to_client():
    fake_client = _FakeClient('{"category": "document", "is_hidden": false}')

    extract_fields("notes.txt", _SCHEMA, client=fake_client)

    call = fake_client.models.calls[0]
    assert "notes.txt" in call["contents"]
    assert call["config"].response_schema is _SCHEMA
    assert call["config"].response_mime_type == "application/json"


def test_extract_fields_uses_given_model_name():
    fake_client = _FakeClient('{"category": "document", "is_hidden": false}')

    extract_fields(
        "notes.txt", _SCHEMA, client=fake_client, model="gemini-test-model"
    )

    assert fake_client.models.calls[0]["model"] == "gemini-test-model"


def test_extract_fields_creates_client_with_retry_options(monkeypatch):
    created = {}

    def fake_client_factory(**kwargs):
        created.update(kwargs)
        return _FakeClient('{"category": "document", "is_hidden": false}')

    monkeypatch.setattr(
        "llm_structured_output_extractor.gemini_client.genai.Client",
        fake_client_factory,
    )

    extract_fields("notes.txt", _SCHEMA)

    assert created["http_options"].retry_options is not None
