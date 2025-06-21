"""
すべてのアカウントディレクトリを削除するスクリプト
"""
import os
import shutil
import sys

def delete_all_accounts():
    """accountsディレクトリ内のすべてのアカウントフォルダを削除"""
    accounts_dir = "accounts"
    
    if not os.path.exists(accounts_dir):
        print(f"❌ {accounts_dir}ディレクトリが見つかりません")
        return False
    
    # アカウントディレクトリの一覧（ただし_で始まるものは除外）
    account_dirs = [d for d in os.listdir(accounts_dir) 
                   if os.path.isdir(os.path.join(accounts_dir, d)) and not d.startswith('_')]
    
    if not account_dirs:
        print(f"❌ {accounts_dir}内にアカウントディレクトリが見つかりません")
        return False
    
    print(f"⚠️ 以下のアカウントディレクトリを削除します:")
    for account_dir in account_dirs:
        print(f"  - {account_dir}")
    
    confirm = input("本当に削除しますか？ (y/n): ").strip().lower()
    if confirm != 'y':
        print("操作をキャンセルしました")
        return False
    
    deleted_count = 0
    error_count = 0
    
    for account_dir in account_dirs:
        account_path = os.path.join(accounts_dir, account_dir)
        try:
            shutil.rmtree(account_path)
            print(f"✅ {account_dir}ディレクトリを削除しました")
            deleted_count += 1
        except Exception as e:
            print(f"❌ {account_dir}の削除中にエラー: {str(e)}")
            error_count += 1
    
    print(f"\n📊 削除結果:")
    print(f"  成功: {deleted_count}アカウント")
    print(f"  失敗: {error_count}アカウント")
    
    return deleted_count > 0

if __name__ == "__main__":
    print("🚫 アカウントディレクトリ削除ユーティリティ")
    
    try:
        delete_all_accounts()
    except KeyboardInterrupt:
        print("\n操作が中断されました")
    except Exception as e:
        print(f"❌ 予期せぬエラー: {str(e)}")
        import traceback
        traceback.print_exc()