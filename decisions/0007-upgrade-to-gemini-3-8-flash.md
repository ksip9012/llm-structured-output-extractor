# 0007. 使用モデルを gemini-3.5-flash から gemini-3.8-flash に切り替える

- Status: Accepted
- Date: 2026-09-27

## Context
[0006](./0006-upgrade-to-gemini-3-5-flash.md) で `gemini-3.5-flash` に
切り替えた後、「`gemini-3.8-flash-lite` が最新では」という指摘があり調査した。

- 汎用テキストモデルとしての `gemini-3.8-flash-lite` は存在しない
  （存在するのは音声合成専用の `gemini-3.8-flash-lite-tts` のみ）
- `-lite` 系統（`gemini-3.1-flash-lite` / `gemini-3.5-flash-lite`）は
  軽量・低コスト版であり、世代が新しいほど高性能というわけではない
- 実際の最新の汎用 flash モデルは `gemini-3.8-flash`（lite なし）であり、
  Vertex AI の `location=global` で利用可能なことを確認した
- `fixtures/sample_folder` 全12件で `gemini-3.5-flash` と `gemini-3.8-flash`
  を比較したところ、結果は完全に同一だった（`word_count` 全一致、
  `normalized_title` の不一致3件も同じ箇所。詳細は
  [notes/step1a1-vs-step1a2-accuracy.md](../notes/step1a1-vs-step1a2-accuracy.md)）

## Decision
デフォルトモデルを `gemini-3.8-flash` に切り替える。
精度は `gemini-3.5-flash` と同等だが、より新しい世代の方が
今後長くサポートされる可能性が高いため（`gemini-2.5-flash` が
既に新規ユーザー向け提供を終了した前例を踏まえる）。

## Consequences
- 出力結果は 0006 時点から変化しない（同等の精度）
- `location=global` の利用は 0006 から変更なし
- 今後さらに新しいモデルが登場した場合も、同様に
  「`-lite` ではない汎用系統の最新モデルか」を確認してから切り替える
