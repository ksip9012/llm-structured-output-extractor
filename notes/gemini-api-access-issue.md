# Gemini API 実呼び出しがブロックされている件（2026-09-27時点）

## 事象

環境変数 `GEMINI_API_KEY` を使って `client.models.generate_content()` を呼ぶと、
試した全モデルでエラーになり、まだ1件も実際の応答を得られていない。

```
gemini-2.5-flash        -> 404 NOT_FOUND: このモデルは新規ユーザーには提供終了
gemini-2.5-flash-lite   -> 404 NOT_FOUND: 同上
gemini-3.8-flash        -> 402 RESOURCE_EXHAUSTED: プリペイド残高が枯渇
gemini-flash-latest     -> 402 RESOURCE_EXHAUSTED: 同上
```

## 解釈

- 2.5系モデルは新規ユーザー向けには提供終了しており、404になる
- 3.x系・latestエイリアスは呼び出し自体はできるが、プリペイド残高（Google AI Studio の課金設定）が枯渇しており402になる

ADR [0003](../decisions/0003-use-gemini-for-structured-output.md) は「Gemini API キー経由で無料枠あり」という前提で書いたが、
現在のアカウントの状態を見る限り、この前提が現状のアカウントには当てはまらない
（無料枠自体がなくなったのか、このプロジェクトの請求設定が未了なのかは未確認）。

## 対応が必要な事項（要ユーザー判断）

- https://ai.studio/projects で当該プロジェクトの課金設定を確認する
- 前払いクレジットを追加するか、別の請求方法（Vertex AI 経由など）を検討する
- 上記を踏まえてもなお費用面で厳しい場合、ADR 0003 を見直し Claude API 版に切り替えることも選択肢

## 現状のコードへの影響

- スキーマ変換（`schema_convert.py`）・API呼び出しラッパー（`gemini_client.py`）・
  マッパー（`mapper.py`）・CLI（`__main__.py`）の実装とテスト（モック使用、29件）は完了している
- 実 API に対する動作確認（プロンプトが実際に意図通りの精度で抽出できるか）は未検証
