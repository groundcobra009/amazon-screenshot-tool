import sys
import time
from pathlib import Path

from config import Config
from kindle_controller import (
    find_kindle_window,
    activate_kindle,
    enter_fullscreen,
    send_page_key,
    exit_fullscreen,
)
from screenshot import capture_screen, get_screenshot_path
from page_compare import images_are_same
from pdf_generator import generate_pdf


def ask_screen_size() -> int:
    """Macの画面サイズを聞く"""
    print("\nお使いのMacの画面サイズを選択してください:")
    print("  1. 13インチ")
    print("  2. 14インチ")
    print("  3. 15インチ")
    print("  4. 16インチ")
    while True:
        choice = input("> ").strip()
        if choice in ("1", "2", "3", "4"):
            sizes = {1: 13, 2: 14, 3: 15, 4: 16}
            return sizes[int(choice)]
        print("1〜4の数字を入力してください")


def ask_page_direction() -> str:
    """ページめくり方向を聞く"""
    print("\nページめくり方向を選択してください:")
    print("  1. 右めくり（← で次ページ）")
    print("  2. 左めくり（→ で次ページ）")
    while True:
        choice = input("> ").strip()
        if choice == "1":
            return "left"
        elif choice == "2":
            return "right"
        print("1か2を入力してください")


def ask_book_name() -> str:
    """本の名前を聞く"""
    print("\n本の名前を入力してください（空欄で「book_YYYYMMDD_HHMMSS」）:")
    name = input("> ").strip()
    if not name:
        from datetime import datetime
        name = datetime.now().strftime("book_%Y%m%d_%H%M%S")
    # ファイル名に使えない文字を置換
    name = name.replace("/", "_").replace("\\", "_").replace(":", "_")
    return name


def main():
    print("=" * 50)
    print("  Kindle Screenshot Tool")
    print("=" * 50)

    # 初期設定
    screen_inch = ask_screen_size()
    page_direction = ask_page_direction()
    book_name = ask_book_name()

    config = Config(
        page_direction=page_direction,
        mac_screen_inch=screen_inch,
        book_name=book_name,
    )

    # ディレクトリ作成
    config.book_screenshot_dir.mkdir(parents=True, exist_ok=True)
    config.output_dir.mkdir(parents=True, exist_ok=True)

    # Kindle確認
    print("\nKindleウィンドウを検出中...")
    if not find_kindle_window():
        print("エラー: Kindleアプリが起動していません。")
        print("Kindleを起動し、撮影したい本を開いてから再実行してください。")
        sys.exit(1)

    print("✓ Kindleウィンドウを検出しました")

    # Mac内蔵ディスプレイへの案内
    print("\n※ KindleアプリがMacの内蔵ディスプレイに表示されていることを確認してください。")
    print("  外部モニターに表示されている場合は、Macの画面に移動してください。")
    input("  準備ができたらEnterを押してください...")

    # Kindle アクティブ化 → フルスクリーン
    print("\nKindleをアクティブ化しています...")
    activate_kindle()
    print("フルスクリーンに切り替えています...")
    enter_fullscreen()
    time.sleep(1.0)

    print(f"\n撮影開始します（3秒後に開始）...")
    time.sleep(3.0)

    # 撮影ループ
    page_num = 1
    no_change_count = 0
    prev_path = None

    try:
        while True:
            # スクリーンショット撮影
            current_path = get_screenshot_path(config.book_screenshot_dir, page_num)
            capture_screen(current_path)
            print(f"  [{page_num:04d}] 保存: {current_path.name}")

            # 前ページとの比較（2ページ目以降）
            if prev_path and prev_path.exists():
                if images_are_same(prev_path, current_path, config.change_threshold):
                    no_change_count += 1
                    print(f"         変化なし検出 ({no_change_count}/{config.no_change_limit})")
                    if no_change_count >= config.no_change_limit:
                        # 変化なし分の画像を削除
                        for i in range(no_change_count):
                            dup_path = get_screenshot_path(
                                config.book_screenshot_dir, page_num - i
                            )
                            if dup_path.exists():
                                dup_path.unlink()
                        print(f"\n✓ 最終ページと判定。撮影完了。")
                        break
                else:
                    no_change_count = 0

            prev_path = current_path
            page_num += 1

            # ページ送り
            send_page_key(config.next_page_key())
            time.sleep(config.page_wait)

    except KeyboardInterrupt:
        print("\n\n中断されました。")

    # フルスクリーン解除
    print("フルスクリーンを解除しています...")
    exit_fullscreen()

    # 結果集計
    total_pages = page_num - 1 - no_change_count
    print(f"\n撮影ページ数: {total_pages}")

    if total_pages == 0:
        print("撮影された画像がありません。終了します。")
        sys.exit(0)

    # PDF生成
    print("PDF生成中...")
    output_path = generate_pdf(config.book_screenshot_dir, config.output_pdf_path)
    print(f"✓ PDF生成完了: {output_path}")
    print("\n完了しました！")


if __name__ == "__main__":
    main()
