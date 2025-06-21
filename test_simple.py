"""
シンプルなテストファイル
"""
import os

print("テスト開始")

# ディレクトリ構造を確認
accounts_dir = "accounts"
if os.path.exists(accounts_dir):
    print(f"{accounts_dir} ディレクトリは存在します")
    account_dirs = [d for d in os.listdir(accounts_dir) if os.path.isdir(os.path.join(accounts_dir, d))]
    print(f"アカウント数: {len(account_dirs)}")
    for account in account_dirs:
        print(f"- {account}")
else:
    print(f"{accounts_dir} ディレクトリは存在しません")

print("テスト終了")