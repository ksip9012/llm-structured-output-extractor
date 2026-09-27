# 0003. LLM プロバイダに Gemini API を採用する

- Status: Accepted
- Date: 2026-09-27

## Context
Step1-A2 は LLM の Structured Output 機能（固定スキーマを渡して入力から埋めてもらう）を
学ぶことが目的。候補として以下を比較した。

| 観点 | Claude API（tool use） | Gemini API（response_schema） |
|---|---|---|
| 構造化手段 | `tool_choice` 強制 + `input_schema` | `responseMimeType: application/json` + `response_schema` |
| 費用 | Anthropic の Claude Pro/Max 等の定期契約は claude.ai / Claude Code 用であり、Messages API（コード利用）は別課金（従量課金・無料枠なし） | Google AI Studio の API キー経由で無料枠あり（レート制限付き） |
| JSON Schema 対応 | JSON Schema のサブセット | OpenAPI 3.0 サブセットの `response_schema` |

自分は Claude は定期契約のみで API 従量課金は未設定、GCP アカウントは保有済みで
Gemini API キーをすぐ利用できる状態にある。

## Decision
Step1-A2 の実装は Gemini API を第一候補として採用する。
Claude API との比較を追加したくなった場合は、本 ADR を Superseded とせず、
別 ADR で「Claude 版を追加実装した」経緯として記録する。

## Consequences
- 追加の API 課金設定なしに、無料枠の範囲で試行錯誤できる
- Gemini の `response_schema` は OpenAPI 3.0 サブセットのため、`schema.json`（JSON Schema
  draft 2020-12）の一部キーワード（`format`, 一部の `type` 配列表現など）が
  そのままは使えない可能性があり、Gemini 向けスキーマへの変換層が必要になる見込み
  （実装時に別途 ADR で詳細を記録する）
- 将来 Claude 版を追加する場合、費用は都度従量課金で発生する点を踏まえて判断する
