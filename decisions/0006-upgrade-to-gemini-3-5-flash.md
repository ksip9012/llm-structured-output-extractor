# 0006. 使用モデルを gemini-2.5-flash から gemini-3.5-flash に切り替える

- Status: Accepted
- Date: 2026-09-27

## Context
[0005](./0005-use-vertex-ai-auth.md) の時点では、Vertex AI（`us-central1`）で
動作確認できた `gemini-2.5-flash` をデフォルトモデルにしていた。

その後の確認で以下が分かった。

- Google AI Studio の Developer API では、`gemini-2.5-flash` は既に
  新規ユーザー向けの提供を終了している（[notes/gemini-api-access-issue.md](../notes/gemini-api-access-issue.md)）。
  Vertex AI 側もいずれ追随する可能性が高く、2.5系を前提にし続けるのは
  将来性の面で望ましくない
- Vertex AI では `us-central1` にはまだ 3.x 系モデルが展開されていないが、
  `location=global` を指定すると `gemini-3.5-flash` ・ `gemini-3.1-flash-lite`
  が利用できる
- `fixtures/sample_folder` 全12件で `gemini-2.5-flash` と `gemini-3.5-flash`
  を比較したところ、`gemini-3.5-flash` の方が Step1-A1（ルールベース）の
  結果と一致する項目が増えた（`word_count` が12件全一致、
  `normalized_title` の区切り文字保持も一部改善。詳細は
  [notes/step1a1-vs-step1a2-accuracy.md](../notes/step1a1-vs-step1a2-accuracy.md)）

## Decision
デフォルトモデルを `gemini-3.5-flash` に切り替え、Vertex AI の
`location` も `us-central1` から `global` に変更する。

`gemini-3.1-flash-lite` は精度を落とす軽量版のため採用しない
（コスト面で困っていないため、精度を優先する）。

## Consequences
- `us-central1` 固定のデータレジデンシー要件はない個人学習プロジェクトのため、
  `global` への変更に実害はない
- 3.x 系は Vertex AI でもまだ新しく、今後モデル名・提供状況が変わる
  可能性がある。`GEMINI_MODEL` 環境変数での上書きは引き続き可能にしておく
- 0005 に記載していた「使用モデルは gemini-2.5-flash」という記述は
  本 ADR により実質的に置き換わる（0005 の Vertex AI 認証採用という
  決定自体は変わらない）
