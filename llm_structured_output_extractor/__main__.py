"""フォルダを指定してターミナルから実行するための CLI エントリポイント。"""

import argparse
import json
import sys
from pathlib import Path

from llm_structured_output_extractor.mapper import map_folder


def main() -> None:
    """指定フォルダ内のファイルを構造化し、JSON 配列を標準出力に出力する。"""
    parser = argparse.ArgumentParser(
        description=(
            "指定フォルダ内のファイルを Gemini API の Structured Output 機能で"
            "構造化し、JSON 配列を標準出力に出力する。"
        )
    )
    parser.add_argument("folder", help="対象フォルダのパス")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"エラー: フォルダが見つかりません: {folder}", file=sys.stderr)
        raise SystemExit(1)

    results = map_folder(folder)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
