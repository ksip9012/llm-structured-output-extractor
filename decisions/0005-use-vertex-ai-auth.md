# 0005. Gemini API への認証は Vertex AI（プロジェクトベース）を使う

- Status: Accepted
- Date: 2026-09-27

## Context
[0003](./0003-use-gemini-for-structured-output.md) で Gemini API の採用を決めた時点では、
Google AI Studio の API キー（`GEMINI_API_KEY`、開発者向け Gemini API）を使う想定だった。

実際にこの API キーで疎通確認したところ、すべてのモデルでエラーになった。

- `gemini-2.5-flash` 系: 404（新規ユーザー向け提供終了）
- `gemini-3.8-flash` / `gemini-flash-latest`: 402（プリペイド残高の枯渇）

一方、GCP プロジェクト `test-adk-479704`（アカウント: ksiper9012@gmail.com）では
`aiplatform.googleapis.com`（Vertex AI）・`generativelanguage.googleapis.com` が
どちらも有効化されており、`gcloud auth application-default login` 済みの
Application Default Credentials（ADC）が使える状態だった。

## Decision
Gemini API へのアクセスは、AI Studio の API キーではなく、Vertex AI 経由
（GCP プロジェクトベースの認証）を使う。

`google-genai` SDK は以下の環境変数から自動的に Vertex AI モードを検出するため、
アプリケーションコード（`gemini_client.py`）側の変更は不要:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=test-adk-479704
export GOOGLE_CLOUD_LOCATION=us-central1
```

認証情報は `gcloud auth application-default login` で得られる ADC を使う
（サービスアカウントキーファイルの発行・管理は行わない）。

使用モデルも、Vertex AI 側でまだ提供されていなかった `gemini-3.8-flash` から、
動作確認できた `gemini-2.5-flash` に変更した
（その後 [0006](./0006-upgrade-to-gemini-3-5-flash.md) で `gemini-3.5-flash` /
`location=global` に切り替えている。ここでの `us-central1` / `gemini-2.5-flash`
という記述は決定当時の記録として残す）。

## Consequences
- AI Studio 側のプリペイド課金設定を待たずに開発を進められる
- GCP プロジェクトの通常の請求（他プロジェクトと同じ Cloud Billing）で管理でき、
  個別の API キー課金設定を別途行う必要がない
- 実行には `gcloud auth application-default login` 済みであることが前提になる
  （API キーを配布するだけでは動かせない）。README のセットアップ手順に明記する
- 将来 Vertex AI 側に新しいモデル（例: gemini-3.x系）が展開され次第、
  `GEMINI_MODEL` 環境変数で切り替え可能
