"""mapper のテスト。Gemini API は呼ばず、Step1-A1（ルールベース実装）の
結果をそのまま「正解の LLM 応答」としてモックし、抽出結果の組み立て・
schema.json 検証ロジックを検証する（decisions/0004 参照）。"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from llm_structured_output_extractor.mapper import map_file, map_folder

FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_folder"
)

_CANNED_LLM_RESULTS = {
    ".hidden_config": {
        "extracted_date": None,
        "category": "other",
        "is_hidden": True,
        "word_count": 2,
        "has_version_suffix": False,
        "duplicate_index": None,
        "separator_style": "underscore",
        "normalized_title": ".hidden_config",
    },
    "2026-04-01-daily-log.md": {
        "extracted_date": "2026-04-01",
        "category": "document",
        "is_hidden": False,
        "word_count": 5,
        "has_version_suffix": False,
        "duplicate_index": None,
        "separator_style": "hyphen",
        "normalized_title": "daily-log",
    },
    "20260115_meeting-notes.md": {
        "extracted_date": "2026-01-15",
        "category": "document",
        "is_hidden": False,
        "word_count": 3,
        "has_version_suffix": False,
        "duplicate_index": None,
        "separator_style": "mixed",
        "normalized_title": "meeting-notes",
    },
    "IMG_20260210_143022.jpg": {
        "extracted_date": "2026-02-10",
        "category": "image",
        "is_hidden": False,
        "word_count": 3,
        "has_version_suffix": False,
        "duplicate_index": None,
        "separator_style": "underscore",
        "normalized_title": "IMG_143022",
    },
    "archive.tar.gz": {
        "extracted_date": None,
        "category": "archive",
        "is_hidden": False,
        "word_count": 1,
        "has_version_suffix": False,
        "duplicate_index": None,
        "separator_style": "none",
        "normalized_title": "archive",
    },
    "budget planning.xlsx": {
        "extracted_date": None,
        "category": "document",
        "is_hidden": False,
        "word_count": 2,
        "has_version_suffix": False,
        "duplicate_index": None,
        "separator_style": "space",
        "normalized_title": "budget planning",
    },
    "draft_v1.md": {
        "extracted_date": None,
        "category": "document",
        "is_hidden": False,
        "word_count": 2,
        "has_version_suffix": True,
        "duplicate_index": None,
        "separator_style": "underscore",
        "normalized_title": "draft",
    },
    "draft_v10.md": {
        "extracted_date": None,
        "category": "document",
        "is_hidden": False,
        "word_count": 2,
        "has_version_suffix": True,
        "duplicate_index": None,
        "separator_style": "underscore",
        "normalized_title": "draft",
    },
    "invoice_2026-03.pdf": {
        "extracted_date": None,
        "category": "document",
        "is_hidden": False,
        "word_count": 3,
        "has_version_suffix": False,
        "duplicate_index": None,
        "separator_style": "mixed",
        "normalized_title": "invoice_2026-03",
    },
    "notes.txt": {
        "extracted_date": None,
        "category": "document",
        "is_hidden": False,
        "word_count": 1,
        "has_version_suffix": False,
        "duplicate_index": None,
        "separator_style": "none",
        "normalized_title": "notes",
    },
    "photo (1).png": {
        "extracted_date": None,
        "category": "image",
        "is_hidden": False,
        "word_count": 2,
        "has_version_suffix": False,
        "duplicate_index": 1,
        "separator_style": "space",
        "normalized_title": "photo",
    },
    "report_final_v2.docx": {
        "extracted_date": None,
        "category": "document",
        "is_hidden": False,
        "word_count": 3,
        "has_version_suffix": True,
        "duplicate_index": None,
        "separator_style": "underscore",
        "normalized_title": "report_final",
    },
}


class _FakeModels:
    def generate_content(self, *, model, contents, config):
        for filename, fields in _CANNED_LLM_RESULTS.items():
            if filename in contents:
                return SimpleNamespace(text=json.dumps(fields))
        raise AssertionError(f"no canned response for prompt: {contents!r}")


class _FakeClient:
    def __init__(self):
        self.models = _FakeModels()


@pytest.fixture
def fake_client():
    return _FakeClient()


@pytest.mark.parametrize("filename", list(_CANNED_LLM_RESULTS))
def test_map_file_validates_against_schema(filename, fake_client):
    result = map_file(FIXTURES_DIR / filename, client=fake_client)

    assert result["file_name"] == filename


def test_map_file_fields_for_versioned_file(fake_client):
    result = map_file(FIXTURES_DIR / "draft_v1.md", client=fake_client)

    assert result["extension"] == ".md"
    assert result["is_multi_extension"] is False
    assert result["category"] == "document"
    assert result["is_hidden"] is False
    assert result["has_version_suffix"] is True
    assert result["duplicate_index"] is None
    assert result["separator_style"] == "underscore"
    assert result["normalized_title"] == "draft"


def test_map_file_fields_for_multi_extension_file(fake_client):
    result = map_file(FIXTURES_DIR / "archive.tar.gz", client=fake_client)

    assert result["extension"] == ".gz"
    assert result["is_multi_extension"] is True
    assert result["category"] == "archive"


def test_map_folder_returns_all_files_sorted_by_name(fake_client):
    results = map_folder(FIXTURES_DIR, client=fake_client)

    assert [r["file_name"] for r in results] == sorted(
        r["file_name"] for r in results
    )
    assert len(results) == 12
    assert {r["file_name"] for r in results} == set(_CANNED_LLM_RESULTS)
