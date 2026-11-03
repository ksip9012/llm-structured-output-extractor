# 0008. 開発環境を作者の dotfiles のひな形の形にそろえ、クライアントの型を Protocol にする

- Status: Accepted
- Date: 2026-11-03

## Context
このリポジトリには依存を書いたファイルも CI もなく、セットアップは `pip install google-genai jsonschema pytest ruff` だけだった。手元と CI で Python やライブラリの版がそろっておらず、型チェックもしていなかった。

作者の dotfiles に、新しいプロジェクトの開発のひな形（[ksip9012/dotfiles の templates/](https://github.com/ksip9012/dotfiles/tree/main/templates)）と、その決めごと（同じリポジトリの `decisions/0001`〜`0008`）ができた。

型チェック（pyright の basic）を入れると、次の指摘が出た。

- Gemini の応答の `response.text` は `None` になりうる（安全のための遮断などで本文が空になる）のに、そのまま `json.loads` していた
- 本体の関数は `genai.Client` を受け取る型だったが、テストの偽のクライアントやベンチマークの記録用のクライアントは `genai.Client` ではないので、型が合わなかった（0004 で、テストでは LLM の応答をモックにすると決めている）

## Decision
開発環境をひな形の形にそろえる。

- 版: Python と uv は `mise.toml` に書き、依存は `pyproject.toml` に下限だけを書いて `uv.lock` で固定する
- チェック: ruff check・ruff format・pyright・pytest を `mise run check` にまとめ、手元・pre-commit・CI で同じコマンドを動かす
- 厳しさ: ruff のルールは今のまま（E・W・F）、pyright は basic。ひな形と同じ厳しさにするのは別に行う
- パッケージとして配らないので `package = false` にし、ひな形の src レイアウトには移さない

あわせて、型の指摘を次のように直す。

- 本体の関数が受け取るクライアントの型を、使う形だけを定めた Protocol（`llm_client.LLMClient`）にする。本物の `genai.Client` も、テストの偽のクライアントも受け取れる
- 応答の本文が `None` のときは、`llm_client.parse_json_response` が `ValueError` を出す

## Consequences
- 手元・CI・ほかの PC で、Python とライブラリの版がそろう
- 応答が空のときに、`json.loads` の分かりにくいエラーではなく、原因のわかるエラーになる
- テストの偽のクライアントは、`text` を持つ小さな dataclass を返す形に替えた
- ひな形と同じ厳しさにするまでは、ひな形から作った新しいプロジェクトより、チェックがゆるい
