"""llm_client のテスト。"""

from dataclasses import dataclass

import pytest

from llm_structured_output_extractor.llm_client import parse_json_response


@dataclass
class _FakeResponse:
    text: str | None


def test_parse_json_response_reads_json_text():
    assert parse_json_response(_FakeResponse('{"a": 1}')) == {"a": 1}


def test_parse_json_response_raises_when_text_is_none():
    with pytest.raises(ValueError, match="本文がなかった"):
        parse_json_response(_FakeResponse(None))
