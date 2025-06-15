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
import traceback
import schedule
from datetime import datetime, timedelta
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.append('.')

# 設定とスケジューラーのインポート
try:
    from config.settings import settings
    from test_real_gas_data_system_v2 import RealGASDataSystemV2
    from final_system import ThreadsAutomationSystem
    print("✅ スケジューラーシステムの初期化に成功しました")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)

class SchedulerManager:
    """スケジューラー管理クラス"""
    
    def __init__(self):
        self.is_running = False
        self.gas_system = None
        self.threads_system = None
        self.posting_function = None
    
    def check_env(self):
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
    
    def check_file_exists(self):
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
    
    def get_next_post_time(self):
        """次回投稿時間を取得"""
        current_time = datetime.now()
        current_hour = current_time.hour
        posting_hours = settings.schedule.posting_hours
        
        # 今日の残り投稿時間をチェック
        remaining_hours = [h for h in posting_hours if h > current_hour]
        
        if remaining_hours:
            # 今日の次の投稿時間
            next_hour = min(remaining_hours)
            next_post_time = current_time.replace(hour=next_hour, minute=0, second=0, microsecond=0)
            is_today = True
        else:
            # 明日の最初の投稿時間
            next_hour = min(posting_hours)
            next_post_time = (current_time + timedelta(days=1)).replace(hour=next_hour, minute=0, second=0, microsecond=0)
            is_today = False
        
        # 残り時間を計算
        time_until = next_post_time - current_time
        hours_until = int(time_until.total_seconds() // 3600)
        minutes_until = int((time_until.total_seconds() % 3600) // 60)
        
        if hours_until > 0:
            time_until_text = f"{hours_until}時間{minutes_until}分後"
        else:
            time_until_text = f"{minutes_until}分後"
        
        return {
            'next_post_time': next_post_time.strftime('%Y-%m-%d %H:%M:%S'),
            'is_today': is_today,
            'time_until_text': time_until_text,
            'posting_hours': posting_hours
        }
    
    def display_next_posting_times(self):
        """次回の投稿予定時刻を表示"""
        next_post_info = self.get_next_post_time()
        
        print("\n⏰ 次回の投稿予定:")
        print(f"  時間: {next_post_info['next_post_time']}")
        print(f"  予定: {'今日' if next_post_info['is_today'] else '明日'}")
        print(f"  残り時間: {next_post_info['time_until_text']}")
        
        print("\n📊 投稿スケジュール:")
        for hour in sorted(next_post_info['posting_hours']):
            print(f"  {hour:02d}:00")
    
    def setup_posting_function(self):
        """投稿関数の設定"""
        # システムを初期化
        self.gas_system = RealGASDataSystemV2()
        self.threads_system = ThreadsAutomationSystem()
        
        # 投稿関数を定義
        def posting_function():
            """スケジュール投稿実行関数"""
            print(f"🔄 スケジュール投稿を実行中... {datetime.now().isoformat()}")
            
            try:
                # アクティブなアカウント確認
                account_stats = self.gas_system.get_system_stats()
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
                
                # ThreadsAutomationSystemのsingle_postメソッドを使用
                result = self.threads_system.single_post(account_id=account_id, test_mode=False)
                
                if result and isinstance(result, dict) and result.get("success"):
                    main_post_id = result.get('main_post_id')
                    reply_post_id = result.get('reply_post_id')
                    post_type = result.get('post_type', 'unknown')
                    
                    print(f"✅ 投稿成功: {main_post_id}")
                    print(f"📝 投稿タイプ: {post_type}")
                    
                    if result.get("is_image_post"):
                        print(f"  画像投稿: {'はい' if result.get('is_image_post') else 'いいえ'}")
                        if result.get('image_urls'):
                            print(f"  画像数: {len(result.get('image_urls'))}枚")
                    
                    if result.get("is_carousel_post"):
                        print(f"  カルーセル投稿: はい")
                    
                    if reply_post_id:
                        print(f"  リプライID: {reply_post_id}")
                    
                    return {
                        "success": True,
                        "total_accounts": 1,
                        "success_count": 1,
                        "result": result
                    }
                else:
                    error_message = result.get("error", "Unknown error") if isinstance(result, dict) else "Posting failed"
                    print(f"❌ 投稿失敗: {error_message}")
                    return {
                        "success": False,
                        "total_accounts": 1,
                        "success_count": 0,
                        "error": error_message,
                        "result": result
                    }
                    
            except Exception as e:
                error_message = str(e)
                print(f"❌ 投稿エラー: {error_message}")
                traceback.print_exc()
                return {
                    "success": False,
                    "error": error_message,
                    "total_accounts": 1,
                    "success_count": 0
                }
        
        self.posting_function = posting_function
        print("✅ 投稿関数を設定しました")
        return posting_function
    
    def setup_schedule(self):
        """スケジュール設定"""
        print("⏰ スケジュール設定を開始...")
        
        # 投稿関数を取得
        if not self.posting_function:
            self.setup_posting_function()
        
        # 既存のスケジュールをクリア
        schedule.clear()
        
        # 指定時間にスケジュール設定
        posting_hours = settings.schedule.posting_hours
        for hour in posting_hours:
            schedule.every().day.at(f"{hour:02d}:00").do(self.posting_function)
            print(f"📅 投稿スケジュール追加: 毎日 {hour:02d}:00")
        
        print(f"✅ スケジュール設定完了: {len(posting_hours)}個の時間帯")
        return True
    
    def start_scheduler(self):
        """スケジューラーを開始"""
        if self.is_running:
            print("⚠️ スケジューラーは既に実行中です")
            return False
        
        self.is_running = True
        return True
    
    def stop_scheduler(self):
        """スケジューラーを停止"""
        self.is_running = False
        print("⏹️ スケジューラーを停止しました")
    
    def manual_trigger(self):
        """手動でスケジューラーをトリガー（テスト用）"""
        if not self.posting_function:
            self.setup_posting_function()
        
        print("🔧 手動トリガーを実行中...")
        result = self.posting_function()
        
        if result and result.get("success"):
            print("✅ 手動投稿が正常に完了しました")
            return True
        else:
            print("❌ 手動投稿に失敗しました")
            if result and result.get("error"):
                print(f"エラー詳細: {result['error']}")
            return False

# グローバルスケジューラーマネージャー
scheduler_manager = SchedulerManager()

def run_scheduler(quiet=False, daemon=False):
    """スケジューラーを実行"""
    # 投稿関数を設定
    scheduler_manager.setup_posting_function()
    
    # 次回投稿時間を表示
    if not quiet:
        scheduler_manager.display_next_posting_times()
    
    # スケジュール設定
    if not scheduler_manager.setup_schedule():
        print("❌ スケジュール設定に失敗しました")
        return False
    
    # スケジューラー開始
    if scheduler_manager.start_scheduler():
        if daemon:
            print("🔄 スケジューラーをデーモンモードで開始しました")
        else:
            print("🔄 スケジューラーを開始しました")
        
        print("📋 投稿予定時間:", settings.schedule.posting_hours)
        print("🔄 監視を開始します（Ctrl+C で停止）")
        print("-" * 50)
        
        try:
            # メインループ
            while scheduler_manager.is_running:
                try:
                    # スケジュールされたジョブをチェック・実行
                    schedule.run_pending()
                    
                    # 次回実行時間の表示（1時間おき）
                    if datetime.now().minute == 0 and not quiet:
                        next_jobs = schedule.jobs
                        if next_jobs:
                            next_run = min(job.next_run for job in next_jobs)
                            print(f"⏰ 次回投稿予定: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # 1分待機
                    time.sleep(60)
                    
                except KeyboardInterrupt:
                    print("\n🛑 スケジューラーを停止中...")
                    break
                except Exception as e:
                    print(f"❌ スケジューラーエラー: {e}")
                    traceback.print_exc()
                    # エラーが発生しても継続
                    time.sleep(60)
            
            scheduler_manager.stop_scheduler()
            return True
            
        except Exception as e:
            print(f"❌ スケジューラー実行エラー: {e}")
            traceback.print_exc()
            scheduler_manager.stop_scheduler()
            return False
    else:
        print("❌ スケジューラーの開始に失敗しました")
        return False

def run_immediate_post(post_type):
    """即時投稿を実行"""
    print(f"🔄 {post_type}投稿を実行中...")
    
    try:
        # システム初期化
        gas_system = RealGASDataSystemV2()
        threads_system = ThreadsAutomationSystem()
        
        # アクティブなアカウント確認
        account_stats = gas_system.get_system_stats()
        accounts = list(account_stats["account_stats"].keys())
        
        if not accounts:
            print("❌ 有効なアカウントがありません")
            return False
        
        # 最初のアカウントで投稿実行
        account_id = accounts[0]
        print(f"👤 アカウント {account_id} で{post_type}投稿実行")
        
        # ThreadsAutomationSystemのsingle_postメソッドを使用
        result = threads_system.single_post(account_id=account_id, test_mode=False)
        
        if result and isinstance(result, dict) and result.get("success"):
            main_post_id = result.get('main_post_id')
            post_type = result.get('post_type', 'unknown')
            
            print(f"✅ 投稿成功！ メインID: {main_post_id}")
            print(f"📝 投稿タイプ: {post_type}")
            
            if result.get("is_image_post"):
                print(f"  画像投稿: はい")
                if result.get('image_urls'):
                    print(f"  画像数: {len(result.get('image_urls'))}枚")
            
            if result.get("is_carousel_post"):
                print(f"  カルーセル投稿: はい")
            
            if result.get("reply_post_id"):
                print(f"  アフィリエイトリプライ: {result.get('reply_post_id')}")
            
            return True
        else:
            error_message = result.get("error", "Unknown error") if isinstance(result, dict) else "Posting failed"
            print(f"❌ 投稿失敗: {error_message}")
            return False
            
    except Exception as e:
        print(f"❌ 即時投稿エラー: {e}")
        traceback.print_exc()
        return False

def show_schedule_status():
    """スケジュール状況を表示"""
    print("📊 === スケジュール状況 ===")
    
    posting_hours = settings.schedule.posting_hours
    current_time = datetime.now()
    current_hour = current_time.hour
    
    print(f"⏰ 現在時刻: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 投稿予定時間: {posting_hours}")
    print(f"🔍 現在の時刻: {current_hour}時")
    
    if current_hour in posting_hours:
        print("✅ 現在は投稿時間です")
    else:
        # 次回投稿時間を表示
        next_post_info = scheduler_manager.get_next_post_time()
        print(f"⏳ 次回投稿予定: {next_post_info['next_post_time']} ({next_post_info['time_until_text']})")
    
    print()

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
    
    parser.add_argument('--status', '-s', action='store_true',
                        help='スケジュール状況を表示')
    
    return parser.parse_args()

def main():
    """メイン関数"""
    # 環境変数の読み込み
    load_dotenv()
    
    # コマンドライン引数のパース
    args = parse_args()
    
    print("🕒 Threads自動投稿スケジューラシステム")
    print("=" * 50)
    
    # 基本チェック
    if not scheduler_manager.check_env() or not scheduler_manager.check_file_exists():
        return 1
    
    try:
        # スケジュール状況表示モード
        if args.status:
            show_schedule_status()
            return 0
        
        # 手動トリガーモード
        if args.manual:
            return 0 if scheduler_manager.manual_trigger() else 1
            
        # 即時投稿モード
        if args.post:
            return 0 if run_immediate_post(args.post) else 1
        
        # スケジューラー実行（デフォルト）
        show_schedule_status()
        success = run_scheduler(quiet=args.quiet, daemon=args.daemon)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 プログラムが中断されました")
        return 0
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)