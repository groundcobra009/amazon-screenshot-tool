import subprocess
from pathlib import Path


def capture_screen(save_path: Path) -> Path:
    """Mac内蔵ディスプレイのスクリーンショットを撮影する

    screencaptureコマンドを使用。-D 1 でメインディスプレイを指定。
    """
    save_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["screencapture", "-x", "-D", "1", str(save_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"screencapture failed: {result.stderr.strip()}")
    return save_path


def get_screenshot_path(screenshot_dir: Path, page_num: int) -> Path:
    """連番ファイルパスを生成する"""
    return screenshot_dir / f"{page_num:04d}.png"
