"""
新しい名前でのテスト
"""
from my_account_manager import MyAccountManager

# インスタンス作成
manager = MyAccountManager()

# アカウント取得
accounts = manager.get_account_ids()
print(f"アカウント数: {len(accounts)}")
for account in accounts:
    print(f"- {account}")