import subprocess
from pathlib import Path

import Quartz


def capture_kindle_window(save_path: Path) -> Path:
    """Kindleウィンドウのみをキャプチャする（メニューバー除外）"""
    save_path.parent.mkdir(parents=True, exist_ok=True)

    window_id = _get_kindle_window_id()
    if not window_id:
        raise RuntimeError("Kindleウィンドウが見つかりません")

    # screencapture -x -o -l <windowID> でウィンドウ単体キャプチャ
    # -o: ウィンドウの影を除外
    result = subprocess.run(
        ["screencapture", "-x", "-o", "-l", str(window_id), str(save_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"screencapture failed: {result.stderr.strip()}")
    return save_path


def _get_kindle_window_id() -> int | None:
    """Quartz APIでKindleウィンドウIDを取得する"""
    # KindleのPIDを取得
    result = subprocess.run(
        ["pgrep", "-x", "Kindle"],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None

    pid = int(result.stdout.strip())

    # ウィンドウリストからKindleのメインウィンドウを探す
    window_list = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly,
        Quartz.kCGNullWindowID
    )
    for w in window_list:
        if (w.get("kCGWindowOwnerPID") == pid
                and w.get("kCGWindowLayer", -1) == 0):
            return w["kCGWindowNumber"]

    return None


def get_screenshot_path(screenshot_dir: Path, page_num: int) -> Path:
    """連番ファイルパスを生成する"""
    return screenshot_dir / f"{page_num:04d}.png"
