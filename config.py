from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    # ページめくり方向: "left" = ←キーで次ページ, "right" = →キーで次ページ
    page_direction: str = "left"
    # Mac画面サイズ（インチ）
    mac_screen_inch: int = 14
    # 本の名前
    book_name: str = ""
    # スクリーンショット保存先
    screenshot_dir: Path = Path("./screenshots")
    # PDF出力先
    output_dir: Path = Path("./output")
    # ページ送り後の待機時間（秒）
    page_wait: float = 1.5
    # 変化なし判定の閾値（ピクセル差分の割合）
    change_threshold: float = 0.001
    # 変化なし連続回数で停止
    no_change_limit: int = 2

    @property
    def book_screenshot_dir(self) -> Path:
        return self.screenshot_dir / self.book_name

    @property
    def output_pdf_path(self) -> Path:
        return self.output_dir / f"{self.book_name}.pdf"

    def next_page_key(self) -> str:
        """次ページに進むためのキーコード名を返す"""
        if self.page_direction == "left":
            return "left"  # ←キーで次ページ（右めくり）
        else:
            return "right"  # →キーで次ページ（左めくり）
