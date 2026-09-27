# 0002. Step1-A1 の schema.json と fixtures を再利用する

- Status: Accepted
- Date: 2026-09-27

## Context
Step1（構造化された出力の制御）は、同じ「ファイル名を構造化する」という課題を
Step1-A1（ルールベース）→ Step1-A2（LLM Structured Output）→ Step1-B（自由入力のJSON化）と
異なる手法で解いていく構成になっている（[[memo]] 参照）。
題材を毎回変えると、手法ごとの精度・実装コストの比較がしづらくなる。

## Decision
Step1-A1（json-schema-mapper）の `schema.json`（13項目・JSON Schema draft 2020-12）と
`fixtures/sample_folder`（ダミーファイル一式）をそのまま Step1-A2 に持ち込み、
抽出方法のみを LLM の Structured Output 機能に差し替える。

## Consequences
- 同一入出力に対する「ルールベース」と「LLM Structured Output」の結果を直接比較できる
  （精度・レイテンシ・実装コストなどをポートフォリオ上で語りやすくなる）
- 一方で題材自体の新規性はなく、あくまで抽出手法の比較が主目的になる
- `fixtures/README.md` の「実際の個人フォルダは使わない」という方針は Step1-A1 の
  ADR（旧 0003-use-folder-file-list.md）に基づくものだが、本プロジェクトでは
  この ADR 自体は移植していないため、方針の由来は本ファイルを正とする
