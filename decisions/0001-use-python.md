# 0001. 開発言語に Python を採用する

- Status: Accepted
- Date: 2026-09-27

## Context
Step1-A1（json-schema-mapper）と同じ `schema.json`（JSON Schema draft 2020-12）・
`fixtures/` をそのまま再利用する方針（[0002](./0002-reuse-step1a1-schema-and-fixtures.md)）のため、
`jsonschema` パッケージでの検証ロジックをそのまま流用できる言語が望ましい。
また、選定した Gemini API（[0003](./0003-use-gemini-for-structured-output.md)）には
公式 Python SDK（`google-genai`）が提供されている。

## Decision
Step1-A1 に続き、開発言語には Python を採用する。

## Consequences
- Step1-A1 の `schema.json` 検証コード（`jsonschema.validate`）をほぼそのまま流用できる
- `pytest` によるテスト運用も Step1-A1 と共通化でき、学習コストが増えない
- 技術スタックは「プロジェクトごとに最適なものを選定する」（common_template 方針）が前提のため、
  Step1-B 以降で異なる言語を選ぶことは妨げない
