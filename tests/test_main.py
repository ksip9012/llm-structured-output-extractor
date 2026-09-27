"""CLI のテスト。`genai.Client` をモックに差し替え、実 API は呼ばない
（decisions/0004 参照）。"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from llm_structured_output_extractor.__main__ import main

FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_folder"
)

_STATIC_LLM_RESPONSE = json.dumps(
    {
        "extracted_date": None,
        "category": "other",
        "is_hidden": False,
        "word_count": 1,
        "has_version_suffix": False,
        "duplicate_index": None,
        "separator_style": "none",
        "normalized_title": "x",
    }
)


class _FakeModels:
    def generate_content(self, *, model, contents, config):
        return SimpleNamespace(text=_STATIC_LLM_RESPONSE)


class _FakeClient:
    def __init__(self, *args, **kwargs):
        self.models = _FakeModels()


def test_main_prints_json_array_for_folder(monkeypatch, capsys):
    monkeypatch.setattr(
        "llm_structured_output_extractor.gemini_client.genai.Client",
        _FakeClient,
    )
    monkeypatch.setattr(
        "sys.argv", ["llm_structured_output_extractor", str(FIXTURES_DIR)]
    )

    main()

    output = json.loads(capsys.readouterr().out)
    assert len(output) == 12
    assert {item["file_name"] for item in output} == {
        p.name for p in FIXTURES_DIR.iterdir()
    }


def test_main_exits_with_error_for_missing_folder(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv", ["llm_structured_output_extractor", "no-such-folder"]
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    assert "no-such-folder" in capsys.readouterr().err
