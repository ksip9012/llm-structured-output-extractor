"""指定フォルダ内のファイル一覧・ファイル情報を取得するモジュール。"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class FileInfo:
    """1つのファイルの基本情報。

    Attributes:
        name: ファイル名（拡張子を含む）。
        size: ファイルサイズ（バイト）。
        mtime: 最終更新日時。
    """

    name: str
    size: int
    mtime: datetime


def list_files(folder: str | Path) -> list[str]:
    """指定フォルダ直下にあるファイルの名前一覧を取得する。

    サブディレクトリは再帰的に探索せず、ディレクトリ自体は結果に含めない。
    隠しファイル（`.` 始まり）は除外せず結果に含める。

    Args:
        folder: 走査対象のフォルダパス。

    Returns:
        ファイル名（拡張子を含む）を昇順にソートしたリスト。
    """
    folder_path = Path(folder)
    return sorted(p.name for p in folder_path.iterdir() if p.is_file())


def get_file_info(path: str | Path) -> FileInfo:
    """指定したファイル1件分の基本情報を取得する。

    Args:
        path: 対象ファイルのパス。

    Returns:
        ファイル名・サイズ・最終更新日時を保持する FileInfo。
    """
    path_obj = Path(path)
    stat_result = path_obj.stat()
    return FileInfo(
        name=path_obj.name,
        size=stat_result.st_size,
        mtime=datetime.fromtimestamp(stat_result.st_mtime),
    )
