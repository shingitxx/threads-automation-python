#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Threads自動投稿スケジューラシステム
指定された時間に自動投稿を行うバックグラウンドサービス
"""

import os
import sys
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.append('.')

# 設定とスケジューラーのインポート
try:
    from config.settings import settings
    from test_scheduler import posting_scheduler
    from test_real_gas_data_system_v2 import RealGASDataSystemV2
    print("✅ スケジューラーシステムの初期化に成功しました")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)

def check_env():
    """環境変数の確認"""
    required_env = [
        'THREADS_ACCESS_TOKEN', 
        'INSTAGRAM_USER_ID'
    ]
    
    missing_env = [env for env in required_env if not os.getenv(env)]
    
    if missing_env:
        print("以下の環境変数が設定されていません:")
        for env in missing_env:
            print(f"- {env}")
        print("\n.envファイルを確認してください。")
        return False
    
    return True

def check_file_exists():
    """必要なファイルの存在確認"""
    required_files = [
        'main.csv',
        'affiliate.csv'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("以下のファイルが見つかりません:")
        for f in missing_files:
            print(f"- {f}")
        print("\nファイルを配置してください。")
        return False
    
    return True

def display_next_posting_times():
    """次回の投稿予定時刻を表示"""
    next_post_info = posting_scheduler.get_next_post_time()
    
    print("\n⏰ 次回の投稿予定:")
    print(f"  時間: {next_post_info['next_post_time']}")
    print(f"  予定: {'今日' if next_post_info['is_today'] else '明日'}")
    print(f"  残り時間: {next_post_info['time_until_text']}")
    
    print("\n📊 投稿スケジュール:")
    for hour in sorted(next_post_info['posting_hours']):
        print(f"  {hour:02d}:00")

def setup_posting_function():
    """投稿関数の設定"""
    # RealGASDataSystemV2 を初期化
    gas_system = RealGASDataSystemV2()
    
    # 投稿関数を定義
    def posting_function():
        """スケジュール投稿実行関数"""
        print(f"🔄 スケジュール投稿を実行中... {datetime.now().isoformat()}")
        
        try:
            # アクティブなアカウント確認
            account_stats = gas_system.get_system_stats()
            accounts = list(account_stats["account_stats"].keys())
            
            if not accounts:
                print("❌ 有効なアカウントがありません")
                return {
                    "success": False,
                    "error": "No active accounts",
                    "total_accounts": 0,
                    "success_count": 0
                }
            
            # 最初のアカウントで投稿実行
            account_id = accounts[0]
            print(f"👤 アカウント {account_id} で投稿実行")
            
            result = gas_system.execute_single_account_post(account_id, test_mode=False)
            
            if result and result.get("success"):
                print(f"✅ 投稿成功: {result.get('main_post_id')}")
                return {
                    "success": True,
                    "total_accounts": 1,
                    "success_count": 1,
                    "result": result
                }
            else:
                print(f"❌ 投稿失敗")
                return {
                    "success": False,
                    "total_accounts": 1,
                    "success_count": 0,
                    "error": "Posting failed",
                    "result": result
                }
                
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_accounts": 1,
                "success_count": 0
            }
    
    # スケジューラーに投稿関数を設定
    posting_scheduler.set_posting_function(posting_function)
    print("✅ 投稿関数を設定しました")

def run_scheduler(quiet=False, daemon=False):
    """スケジューラーを実行"""
    # 投稿関数を設定
    setup_posting_function()
    
    # 次回投稿時間を表示
    if not quiet:
        display_next_posting_times()
    
    # スケジューラー開始
    if posting_scheduler.start_scheduler():
        if daemon:
            print("🔄 スケジューラーをデーモンモードで開始しました")
        else:
            print("🔄 スケジューラーを開始しました")
        
        try:
            # メインスレッドを維持
            while posting_scheduler.is_running:
                time.sleep(60)
                
        except KeyboardInterrupt:
            print("\n⏹️ スケジューラーを停止します...")
            posting_scheduler.stop_scheduler()
            
    else:
        print("❌ スケジューラーの開始に失敗しました")

def run_immediate_post(post_type):
    """即時投稿を実行"""
    print(f"🔄 {post_type}投稿を実行中...")
    
    # RealGASDataSystemV2 を初期化
    gas_system = RealGASDataSystemV2()
    
    # アクティブなアカウント確認
    account_stats = gas_system.get_system_stats()
    accounts = list(account_stats["account_stats"].keys())
    
    if not accounts:
        print("❌ 有効なアカウントがありません")
        return False
    
    # 最初のアカウントで投稿実行
    account_id = accounts[0]
    print(f"👤 アカウント {account_id} で{post_type}投稿実行")
    
    result = gas_system.execute_single_account_post(account_id, test_mode=False)
    
    if result and result.get("success"):
        print(f"✅ 投稿成功！ メインID: {result.get('main_post_id')}")
        if result.get("affiliate"):
            print(f"  アフィリエイト: {result.get('affiliate')['id']}")
        return True
    else:
        print(f"❌ 投稿失敗: {result}")
        return False

def parse_args():
    """コマンドライン引数のパース"""
    parser = argparse.ArgumentParser(description='Threads自動投稿スケジューラシステム')
    
    parser.add_argument('--daemon', '-d', action='store_true',
                        help='デーモンモードで実行（コンソール出力なし）')
    
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='静かモードで実行（最小限の出力）')
    
    parser.add_argument('--post', '-p', choices=['text', 'tree'],
                        help='即時投稿を実行 (text: テキスト投稿, tree: ツリー投稿)')
    
    parser.add_argument('--manual', '-m', action='store_true',
                        help='手動でスケジューラーをトリガー（テスト用）')
    
    return parser.parse_args()

def main():
    """メイン関数"""
    # 環境変数の読み込み
    load_dotenv()
    
    # コマンドライン引数のパース
    args = parse_args()
    
    # 基本チェック
    if not check_env() or not check_file_exists():
        return 1
    
    try:
        # 手動トリガーモード
        if args.manual:
            setup_posting_function()
            print("🔧 手動トリガーを実行中...")
            posting_scheduler.manual_trigger()
            return 0
            
        # 即時投稿モード
        if args.post:
            return 0 if run_immediate_post(args.post) else 1
        
        # スケジューラー実行
        run_scheduler(quiet=args.quiet, daemon=args.daemon)
        return 0
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return 1

if __name__ == "__main__":
    print("🕒 Threads自動投稿スケジューラシステム")
    print("=" * 50)
    sys.exit(main())