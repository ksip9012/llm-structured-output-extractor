"""fixtures の各ファイルを実際の Gemini API で構造化し、1件あたりの
処理時間とトークン数を JSON Lines で出力するベンチマーク。

Step1 シリーズ（A1 / A2 / B）の横断比較用。3リポジトリで同じ形式の行を
出力し、Step1-A1（json-schema-mapper）の `scripts/summarize_benchmark.py`
でまとめる。Vertex AI の認証（README のセットアップ手順）が必要で、
実行するたびに API の料金がかかる。

使い方:
    python scripts/benchmark.py --runs 3 > notes/benchmark/a2.jsonl
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from google import genai
from google.genai import errors, types
from jsonschema.exceptions import SchemaError, ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm_structured_output_extractor.file_lister import (  # noqa: E402
    list_files,
)
from llm_structured_output_extractor.gemini_client import (  # noqa: E402
    DEFAULT_MODEL,
)
from llm_structured_output_extractor.mapper import map_file  # noqa: E402

_FIXTURES = Path(__file__).resolve().parent.parent / "fixtures/sample_folder"
_MAX_RETRIES = 5
# 試し直すエラーコード（レート制限と、サーバー側の一時的なエラー）
_RETRY_CODES = {429, 500, 503, 504}
# 1回の呼び出しの上限。ときどき返事が返らないまま止まることがあるため
_TIMEOUT_MS = 120_000


class _RecordingModels:
    """generate_content の応答から usage_metadata を記録するラッパー。"""

    def __init__(self, models: Any) -> None:
        self._models = models
        self.usages: list[Any] = []

    def generate_content(self, **kwargs: Any) -> Any:
        response = self._models.generate_content(**kwargs)
        self.usages.append(response.usage_metadata)
        return response


class _RecordingClient:
    """`client.models.generate_content` だけを持つ記録用のクライアント。"""

    def __init__(self, client: genai.Client) -> None:
        self.models = _RecordingModels(client.models)


def _measure(path: Path, client: genai.Client) -> dict[str, Any]:
    """1ファイルを構造化し、成功した試行の処理時間とトークン数を返す。

    SDK の自動の再試行は切ってあり（`main` 参照）、レート制限や
    サーバー側の一時的なエラーのときは、ここで待ってから試し直す。待った
    時間と失敗した試行は処理時間に含めず、試し直した回数とエラーコードを
    記録する。`_TIMEOUT_MS` を超えた呼び出しも "timeout" として試し直す。
    出力が JSON として読めない・スキーマの検証を通らないときは、
    `ok: false` として記録する。
    """
    retry_codes: list[int | str] = []
    for attempt in range(_MAX_RETRIES + 1):
        recorder = _RecordingClient(client)
        start = time.perf_counter()
        error = None
        result = None
        try:
            result = map_file(path, client=recorder)
        except errors.APIError as e:
            if e.code not in _RETRY_CODES or attempt == _MAX_RETRIES:
                raise
            retry_codes.append(e.code)
            time.sleep(10 * (attempt + 1))
            continue
        except httpx.TimeoutException:
            if attempt == _MAX_RETRIES:
                raise
            retry_codes.append("timeout")
            continue
        except (json.JSONDecodeError, SchemaError, ValidationError) as e:
            error = f"{type(e).__name__}: {str(e).splitlines()[0]}"
        latency_ms = (time.perf_counter() - start) * 1000
        usages = recorder.models.usages
        return {
            "ok": error is None,
            "error": error,
            "latency_ms": round(latency_ms, 3),
            "llm_calls": len(usages),
            "prompt_tokens": sum(u.prompt_token_count or 0 for u in usages),
            "output_tokens": sum(
                u.candidates_token_count or 0 for u in usages
            ),
            "thoughts_tokens": sum(
                u.thoughts_token_count or 0 for u in usages
            ),
            "retries": attempt,
            "retry_codes": retry_codes,
            "result": result,
        }
    raise AssertionError("unreachable")


def main() -> None:
    """各ファイルを runs 回ずつ構造化し、1回ごとに1行を出力する。"""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()

    # SDK の自動の再試行は、待ち時間が処理時間に混ざるので切る
    client = genai.Client(
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=1),
            timeout=_TIMEOUT_MS,
        )
    )
    for run in range(1, args.runs + 1):
        for name in list_files(_FIXTURES):
            row = {
                "step": "A2",
                "model": DEFAULT_MODEL,
                "run": run,
                "file": name,
                **_measure(_FIXTURES / name, client),
            }
            print(json.dumps(row, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
