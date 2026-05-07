import subprocess
import time


def run_applescript(script: str) -> str:
    """AppleScriptを実行して結果を返す"""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript error: {result.stderr.strip()}")
    return result.stdout.strip()


def find_kindle_window() -> bool:
    """Kindleアプリが起動しているか確認"""
    script = '''
    tell application "System Events"
        return (name of processes) contains "Kindle"
    end tell
    '''
    result = run_applescript(script)
    return result == "true"


def activate_kindle():
    """Kindleウィンドウをアクティブにする"""
    script = '''
    tell application "Amazon Kindle"
        activate
    end tell
    '''
    run_applescript(script)
    time.sleep(0.5)


def enter_fullscreen():
    """Kindleをフルスクリーンにする（Command+Control+F）"""
    script = '''
    tell application "System Events"
        tell process "Kindle"
            -- メニューバーから「表示」→「フルスクリーンにする」
            click menu item "Enter Full Screen" of menu "View" of menu bar 1
        end tell
    end tell
    '''
    try:
        run_applescript(script)
    except RuntimeError:
        # 英語メニューが失敗した場合、キーボードショートカットで試行
        shortcut_script = '''
        tell application "System Events"
            tell process "Kindle"
                keystroke "f" using {command down, control down}
            end tell
        end tell
        '''
        run_applescript(shortcut_script)
    time.sleep(1.0)


def send_page_key(direction: str):
    """ページ送りキーを送信する"""
    key_code = "123" if direction == "left" else "124"  # 123=←, 124=→
    script = f'''
    tell application "System Events"
        tell process "Kindle"
            key code {key_code}
        end tell
    end tell
    '''
    run_applescript(script)


def exit_fullscreen():
    """フルスクリーンを解除する"""
    script = '''
    tell application "System Events"
        tell process "Kindle"
            keystroke "f" using {command down, control down}
        end tell
    end tell
    '''
    try:
        run_applescript(script)
    except RuntimeError:
        pass
