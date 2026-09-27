# llm-structured-output-extractor

Gemini API の Structured Output（`response_schema`）機能を使い、ファイル名を固定スキーマの構造化データに変換するマッパー。Step1-A1（[json-schema-mapper](https://github.com/ksip9012/json-schema-mapper)、ルールベース実装）と同じ課題を LLM で解き直す位置づけ。

## デモ

Vertex AI 経由（[decisions/0005](./decisions/0005-use-vertex-ai-auth.md)）で実際に動作確認済み。

```console
$ python -m llm_structured_output_extractor fixtures/sample_folder
[
  {
    "file_name": "draft_v1.md",
    "extension": ".md",
    "is_multi_extension": false,
    "size_bytes": 0,
    "modified_at": "2026-09-27T15:02:09.076000",
    "extracted_date": null,
    "category": "document",
    "is_hidden": false,
    "word_count": 2,
    "has_version_suffix": true,
    "duplicate_index": null,
    "separator_style": "underscore",
    "normalized_title": "draft"
  },
  ...
]
```

## 背景・課題

「自由入力をどう構造化データに落とし込むか」を学ぶ3ステップのうち、Step1-A2（LLM の Structured Output 機能を使った構造化）にあたる。Step1-A1 と同じ `schema.json` ・ `fixtures/` を使い、抽出方法だけを「ルールベースの正規表現」から「LLM への Structured Output 呼び出し」に差し替えることで、両者を同じ土俵で比較できるようにしている（[decisions/0002](./decisions/0002-reuse-step1a1-schema-and-fixtures.md)）。

## 主な機能

- フォルダを指定して実行し（`python -m llm_structured_output_extractor <folder>`）、フォルダ内の全ファイルを構造化した JSON 配列を標準出力に出力する
- 1ファイルを受け取り、[`schema.json`](./schema.json) に定義した13項目の構造化データに変換する（`map_file()`）
- `file_name` / `extension` / `is_multi_extension` / `size_bytes` / `modified_at` はコード側で直接算出し、残り8項目（`extracted_date` など）はファイル名を Gemini API に渡して Structured Output 機能で抽出する
- 組み立てた結果を `schema.json` に対して検証する
- 自動テストでは実 API を呼ばず、モッククライアントで固定応答を返す（[decisions/0004](./decisions/0004-mock-llm-responses-in-tests.md)）

## アーキテクチャ・技術スタック

- 言語: Python 3.14
- LLM: Google Gemini API（[google-genai](https://pypi.org/project/google-genai/)、Structured Output / `response_schema`）
- スキーマ定義・検証: [jsonschema](https://pypi.org/project/jsonschema/)（[`schema.json`](./schema.json), JSON Schema draft 2020-12）
- Lint: ruff（[`ruff.toml`](./ruff.toml)）
- テスト: pytest

モジュール構成:

- [`llm_structured_output_extractor/file_lister.py`](./llm_structured_output_extractor/file_lister.py): フォルダ内のファイル一覧・ファイル情報（`FileInfo`）の取得（Step1-A1 と同一実装）
- [`llm_structured_output_extractor/schema_convert.py`](./llm_structured_output_extractor/schema_convert.py): `schema.json`（JSON Schema draft 2020-12）を Gemini の `response_schema`（OpenAPI 3.0 サブセット）に変換する
- [`llm_structured_output_extractor/gemini_client.py`](./llm_structured_output_extractor/gemini_client.py): Gemini API を呼び出し、Structured Output でファイル名から構造化データを抽出する
- [`llm_structured_output_extractor/mapper.py`](./llm_structured_output_extractor/mapper.py): 上記を組み合わせて `schema.json` に準拠した辞書を組み立て・検証する（`map_file()` / `map_folder()`）
- [`llm_structured_output_extractor/__main__.py`](./llm_structured_output_extractor/__main__.py): `python -m llm_structured_output_extractor <folder>` の CLI エントリポイント

## 技術選定理由

主な技術選定は [`decisions/`](./decisions) に ADR として記録している。

- [0001](./decisions/0001-use-python.md): 開発言語に Python を採用
- [0002](./decisions/0002-reuse-step1a1-schema-and-fixtures.md): Step1-A1 の schema.json・fixtures を再利用
- [0003](./decisions/0003-use-gemini-for-structured-output.md): LLM プロバイダに Gemini API を採用（Claude API との比較）
- [0004](./decisions/0004-mock-llm-responses-in-tests.md): 自動テストでは LLM 応答をモックする
- [0005](./decisions/0005-use-vertex-ai-auth.md): Gemini API への認証は Vertex AI（プロジェクトベース）を使う

## セットアップ手順

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install google-genai jsonschema pytest ruff
```

Gemini API を実際に呼び出すには、Vertex AI 経由の認証が必要
（[decisions/0005](./decisions/0005-use-vertex-ai-auth.md)）。

```bash
gcloud auth application-default login

export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=test-adk-479704
export GOOGLE_CLOUD_LOCATION=us-central1
```

## 使い方

ターミナルから：

```bash
python -m llm_structured_output_extractor <folder>
```

Python から：

```python
from llm_structured_output_extractor.mapper import map_file, map_folder

result = map_file("fixtures/sample_folder/draft_v1.md")
results = map_folder("fixtures/sample_folder")
```

## テストの実行方法

```bash
pip install google-genai jsonschema pytest ruff
ruff check .
pytest
```

自動テストは Gemini API を実際には呼ばず、モッククライアントで固定応答を返す（[decisions/0004](./decisions/0004-mock-llm-responses-in-tests.md)）。

## 今後の展望・既知の制約

- Step1-A1（ルールベース）との精度比較を実施済み（[notes/step1a1-vs-step1a2-accuracy.md](./notes/step1a1-vs-step1a2-accuracy.md)）。`extracted_date` など仕様が明確な項目は12件全一致したが、`word_count`・`normalized_title` のような曖昧さの残る項目では、Gemini が意味的に拡大解釈する差異が見られた
- レイテンシ・実装コストの詳細な比較はまだ行っていない
- 次のステップ（Step1-B）では、スキーマ自体も LLM に考えさせる自由入力の JSON 化に発展する
