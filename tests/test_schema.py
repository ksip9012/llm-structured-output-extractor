"""schema.json 自体の妥当性を検証するテスト。"""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.json"


def test_schema_json_is_valid_draft_2020_12_schema():
    schema = json.loads(SCHEMA_PATH.read_text())

    Draft202012Validator.check_schema(schema)
