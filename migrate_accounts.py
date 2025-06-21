"""
アカウントデータを新しいフォルダ構造に移行するスクリプト
"""
import os
import sys
import argparse
from tools.migration.account_migrator import AccountMigrator

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='アカウントデータを新しいフォルダ構造に移行')
    parser.add_argument('--account', help='移行する特定のアカウントID (例: ACCOUNT_001)')
    parser.add_argument('--all', action='store_true', help='全アカウントを移行')
    parser.add_argument('--list', action='store_true', help='利用可能なアカウントを表示')
    parser.add_argument('--force', action='store_true', help='既存のフォルダを上書き')
    
    args = parser.parse_args()
    
    migrator = AccountMigrator()
    
    if args.list:
        migrator.list_available_accounts()
        return 0
        
    if args.all:
        success = migrator.migrate_all_accounts(force=args.force)
        return 0 if success else 1
        
    if args.account:
        success = migrator.migrate_account(args.account, force=args.force)
        return 0 if success else 1
        
    # 引数がない場合はヘルプを表示
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())