# Step1-A1（ルールベース）と Step1-A2（Gemini Structured Output）の精度比較

## 初回検証（gemini-2.5-flash, 2026-09-27）

Vertex AI（`gemini-2.5-flash`、decisions/0005、`location=us-central1`）経由で
`fixtures/sample_folder` 全12件を実際に抽出し、Step1-A1 のルールベース実装の
出力（正解データ扱い）と比較した。

### 修正前に見つかった不具合

`extracted_date` が `"20260115"`（ハイフンなし）で返ってきた。
`schema.json` の `format: "date"` を Gemini の Schema 変換時に
そのまま捨てていたことが原因（Gemini の Schema は STRING の format に
`"date"` を受け付けないため）。`description` に「YYYY-MM-DD形式の文字列で
返すこと」という文言を埋め込むことで解決した（`schema_convert.py`）。
修正後は12件すべて `extracted_date` が正しい形式で一致した。

### 修正後も残った差異（gemini-2.5-flash）

| ファイル | 項目 | ルールベース | Gemini | 差異の性質 |
|---|---|---|---|---|
| `invoice_2026-03.pdf` | `word_count` | 3 | 2 | ルールは区切り文字で機械的に分割するが、Gemini は `2026-03` を1つの日付表現として意味的にまとめてカウントしたとみられる |
| `.hidden_config` | `normalized_title` | `.hidden_config`（先頭ドット保持） | `hidden_config` | ルールは Unix の隠しファイル慣習（先頭ドット1つは拡張子区切りとみなさない）をそのまま保持するが、Gemini はドットを区切り文字とみなして除去した |
| `20260115_meeting-notes.md` | `normalized_title` | `meeting-notes`（ハイフン保持） | `meeting notes`（スペース化） | ルールは残った区切り文字をそのまま残すが、Gemini は表記を正規化してスペース区切りに変えた |
| `IMG_20260210_143022.jpg` | `normalized_title` | `IMG_143022`（時刻表記は未対応のため残る） | `IMG`（時刻表記も除去） | ルールは日付抽出ロジックが対応していない時刻部分をあえて残す設計（ADR 0009 参照）だが、Gemini は「日付っぽいもの」を広く解釈して除去した |

## gemini-3.5-flash への切り替え後（decisions/0006, 2026-09-27）

同じ12件を `gemini-3.5-flash`（`location=global`）で再実行したところ、精度が改善した。

| ファイル | 項目 | ルールベース | gemini-2.5-flash | gemini-3.5-flash |
|---|---|---|---|---|
| `invoice_2026-03.pdf` | `word_count` | 3 | 2（不一致） | 3（**一致**） |
| `20260115_meeting-notes.md` | `normalized_title` | `meeting-notes` | `meeting notes`（不一致） | `meeting-notes`（**一致**） |
| `.hidden_config` | `normalized_title` | `.hidden_config` | `hidden_config`（不一致） | `hidden_config`（不一致のまま） |
| `IMG_20260210_143022.jpg` | `normalized_title` | `IMG_143022` | `IMG`（不一致） | `IMG`（不一致のまま） |
| `invoice_2026-03.pdf` | `normalized_title` | `invoice_2026-03` | `invoice`（不一致） | `invoice`（不一致のまま） |

`word_count` は12件全一致に改善し、`normalized_title` の不一致も4件→3件に減少した。
残る3件はいずれも「LLM が日付・隠しファイルの慣習をより広く意味的に解釈して
文字列を削ってしまう」という同じ傾向によるもので、モデル世代が変わっても
解消していない。

## gemini-3.8-flash への切り替え後（decisions/0007, 2026-09-27）

「`gemini-3.8-flash-lite` が最新では」という指摘を受けて調査したところ、
汎用テキストモデルとしての `-lite` 版は存在せず、`gemini-3.8-flash`（lite なし）
が実際の最新モデルだった。同じ12件で実行した結果、`gemini-3.5-flash` と
**完全に同一の結果**（`word_count` 全一致、`normalized_title` の不一致も
同じ3件）になった。今回のタスクでは 3.5 → 3.8 による精度差は見られなかったが、
将来的なモデル提供終了リスクを避けるため、デフォルトは `gemini-3.8-flash` にした。

## 解釈

`extracted_date` / `category` / `is_hidden` / `has_version_suffix` /
`duplicate_index` / `separator_style` のような、schema の `description` や
`enum` で仕様が明確な項目は12件全一致した。

一方 `word_count`（機械的な区切り文字カウント）と `normalized_title`
（「実質的なタイトル」という曖昧な定義）は、Gemini が仕様を「意味的に」
拡大解釈する傾向が見られた。これは Step1-A1 のルールベース実装が
「検出ロジックが実際に見つけた箇所だけを削る」という狭いスコープを
意図的に採用している（ADR 0009）のに対し、LLM は description の
自然言語からより広い意図を読み取ろうとするための差異だと考えられる。

この差異自体が、ルールベースと LLM Structured Output の性質の違いを
示す学習成果として記録する価値があると判断し、schema・プロンプトを
「Gemini の出力がルールベースと完全一致するまで」調整することはしない
（それをやり出すとルールベースの再実装になってしまうため）。
