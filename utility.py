# utility.py（新規作成）
def safe_print(message):
    """Windows環境でも安全に表示できるようにする関数"""
    try:
        print(message)
    except UnicodeEncodeError:
        # 絵文字を置き換えたメッセージを表示
        safe_message = message.replace('\u2705', '[成功]').replace('\u274c', '[失敗]')
        print(safe_message)