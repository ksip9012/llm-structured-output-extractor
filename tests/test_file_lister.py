from datetime import datetime
from pathlib import Path

from llm_structured_output_extractor.file_lister import (
    get_file_info,
    list_files,
)

FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_folder"
)


def test_list_files_returns_all_file_names():
    result = list_files(FIXTURES_DIR)

    assert len(result) == 12
    assert "notes.txt" in result
    assert ".hidden_config" in result


def test_list_files_returns_sorted_names():
    result = list_files(FIXTURES_DIR)

    assert result == sorted(result)


def test_list_files_excludes_directories():
    result = list_files(FIXTURES_DIR.parent)

    assert "sample_folder" not in result


def test_get_file_info_returns_name_size_and_mtime():
    info = get_file_info(FIXTURES_DIR / "notes.txt")

    assert info.name == "notes.txt"
    assert info.size == 0
    assert isinstance(info.mtime, datetime)
