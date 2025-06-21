"""
Threads自動投稿スケジューラーシステム
新しいフォルダ構造に対応した自動スケジュール投稿機能を提供
"""
import os
import sys
import time
import random
import schedule
import traceback
import datetime
import threading
import json
from typing import Dict, List, Optional, Any

# ロガー設定
import logging

class EncodingStreamHandler(logging.StreamHandler):
    """エンコーディング問題に対応したストリームハンドラ"""
    def __init__(self, stream=None):
        super().__init__(stream)
    
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            
            # 絵文字をテキストに置換
            msg = msg.replace('✅', '[成功]').replace('❌', '[失敗]')
            
            try:
                stream.write(msg + self.terminator)
            except UnicodeEncodeError:
                # 絵文字などを置換
                safe_msg = ''.join(c if ord(c) < 0x10000 else '?' for c in msg)
                stream.write(safe_msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# ロガーの設定
def setup_logger():
    """ロガーを設定"""
    logger = logging.getLogger('threads-scheduler')
    logger.setLevel(logging.INFO)
    
    # ファイルハンドラ
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"scheduler_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # コンソールハンドラ（エンコーディング対応）
    console_handler = EncodingStreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # フォーマッタ
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # ハンドラをロガーに追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# ロガーの初期化
logger = setup_logger()

from threads_account_manager import ThreadsAccountManager
from threads_cloudinary_manager import ThreadsCloudinaryManager
from threads_direct_post import ThreadsDirectPost
from threads_automation_system import ThreadsAutomationSystem

class ThreadsSchedulerSystem:
    """Threads自動投稿スケジューラークラス"""
    
    def __init__(self):
        """初期化"""
        print("🚀 Threads自動投稿スケジューラーシステム 起動中...")
        logger.info("Threads自動投稿スケジューラーシステム 起動中...")
        
        # 各マネージャークラスの初期化
        self.account_manager = ThreadsAccountManager()
        self.cloudinary_manager = ThreadsCloudinaryManager()
        self.direct_post = ThreadsDirectPost()
        self.automation_system = ThreadsAutomationSystem()
        
        # スケジュール設定
        self.posting_hours = [2, 5, 8, 12, 17, 20, 22, 0]  # 投稿時間（24時間形式）
        self.is_running = False
        
        # 状態ファイルを確認して現在の状態を復元
        self._restore_status()
        
        print("✅ スケジューラー初期化完了")
        logger.info("スケジューラー初期化完了")
    
    def _restore_status(self):
        """状態ファイルから状態を復元する"""
        status_file = os.path.join('logs', 'scheduler_status.json')
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                    
                    # 実行中のプロセスかどうか確認
                    if status_data.get('status') == 'running' and 'pid' in status_data:
                        pid = status_data.get('pid')
                        try:
                            # プロセス確認（psutilがあれば使用）
                            try:
                                import psutil
                                if psutil.pid_exists(pid) and pid != os.getpid():
                                    # 他のプロセスが実行中
                                    self.is_running = False
                                    logger.info(f"別プロセスのスケジューラーが実行中 (PID: {pid})")
                                    return
                            except ImportError:
                                # psutilがない場合は単純にファイルの状態を確認
                                pass
                        except Exception:
                            pass
                            
                    # このプロセスが実行中のスケジューラーの場合
                    if status_data.get('status') == 'running' and status_data.get('pid') == os.getpid():
                        self.is_running = True
                        logger.info("スケジューラー状態を復元: 実行中")
            except Exception as e:
                logger.error(f"状態ファイル読み込みエラー: {e}")
    
    def retry_operation(self, operation, max_retries=3, retry_delay=5):
        """操作を再試行するユーティリティ"""
        retries = 0
        while retries < max_retries:
            try:
                return operation()
            except Exception as e:
                retries += 1
                if retries < max_retries:
                    logger.warning(f"操作に失敗しました。{retry_delay}秒後に再試行します。({retries}/{max_retries})")
                    print(f"⚠️ 操作に失敗しました。{retry_delay}秒後に再試行します。({retries}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"最大再試行回数に達しました。操作は失敗しました: {e}")
                    print(f"❌ 最大再試行回数に達しました。操作は失敗しました: {e}")
                    raise
        
    def scheduled_post(self):
        """スケジュール投稿の実行"""
        try:
            now = datetime.datetime.now()
            logger.info(f"=== スケジュール投稿実行 {now.strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"\n⏰ === スケジュール投稿実行 {now.strftime('%Y-%m-%d %H:%M:%S')} ===")
        
            # 全アカウント投稿を実行（再試行メカニズムを使用）
            result = self.retry_operation(
                lambda: self.automation_system.all_accounts_post(test_mode=False),
                max_retries=3,
                retry_delay=10
            )
        
            # 結果のログ記録
            logger.info(f"成功: {result['success']}件")
            logger.info(f"失敗: {result['failed']}件")
            
            for account in result['accounts']:
                status_text = '[成功]' if account['status'] == 'success' else '[失敗]'  # 絵文字を使わない
                logger.info(f"{status_text} {account['account_id']}")
        
            logger.info("スケジュール投稿完了")
            print(f"✅ スケジュール投稿完了")
        
        except Exception as e:
            error_msg = f"スケジュール投稿エラー: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            traceback.print_exc()
    
    def setup_schedule(self):
        """スケジュール設定"""
        # 既存のジョブをクリア
        schedule.clear()
        
        # 投稿時間ごとにスケジュール設定
        for hour in self.posting_hours:
            schedule.every().day.at(f"{hour:02d}:00").do(self.scheduled_post)
            logger.info(f"{hour:02d}:00 に投稿するようスケジュール設定しました")
            print(f"📅 {hour:02d}:00 に投稿するようスケジュール設定しました")
        
        logger.info("スケジュール設定完了")
        print(f"✅ スケジュール設定完了")
        
    def run_scheduler(self):
        """スケジューラーを実行"""
        if self.is_running:
            logger.warning("スケジューラーは既に実行中です")
            print("⚠️ スケジューラーは既に実行中です")
            return
        
        self.is_running = True
        logger.info("スケジューラーを開始します")
        print("🚀 スケジューラーを開始します")
        
        # スケジュール設定
        self.setup_schedule()
        
        # 状態ファイルを作成
        status_file = os.path.join('logs', 'scheduler_status.json')
        try:
            os.makedirs(os.path.dirname(status_file), exist_ok=True)
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'status': 'running',
                    'start_time': datetime.datetime.now().isoformat(),
                    'posting_hours': self.posting_hours,
                    'pid': os.getpid()  # プロセスIDを記録
                }, f, ensure_ascii=False)
            logger.info(f"状態ファイルを作成しました: {status_file}")
        except Exception as e:
            logger.error(f"状態ファイル作成エラー: {e}")
        
        # バックグラウンドスレッド
        def run_schedule():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 1分ごとにチェック
        
        # スレッド開始
        self.scheduler_thread = threading.Thread(target=run_schedule)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """スケジューラーを停止"""
        if not self.is_running:
            logger.warning("スケジューラーは実行されていません")
            print("⚠️ スケジューラーは実行されていません")
            return
        
        self.is_running = False
        logger.info("スケジューラーを停止しました")
        print("🛑 スケジューラーを停止しました")
        
        # 状態ファイルを更新
        status_file = os.path.join('logs', 'scheduler_status.json')
        try:
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'status': 'stopped',
                    'stop_time': datetime.datetime.now().isoformat(),
                    'pid': os.getpid()
                }, f, ensure_ascii=False)
            logger.info(f"状態ファイルを更新しました: {status_file}")
        except Exception as e:
            logger.error(f"状態ファイル更新エラー: {e}")
    
    def status(self):
        """スケジューラーの状態確認"""
        logger.info("スケジューラー状態確認")
        print("\n📊 === スケジューラー状況 ===")
        
        # 状態ファイルを確認
        status_file = os.path.join('logs', 'scheduler_status.json')
        scheduler_status = "不明"
        next_run_time = None
        pid = None
        start_time = None
        
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                    scheduler_status = status_data.get('status', '不明')
                    pid = status_data.get('pid')
                    
                    # 開始時間の取得
                    if 'start_time' in status_data:
                        start_time = datetime.datetime.fromisoformat(status_data['start_time'])
                    
                    # プロセスが実際に実行中か確認
                    if scheduler_status == 'running' and pid:
                        try:
                            import psutil
                            if not psutil.pid_exists(pid):
                                # プロセスが存在しない場合、異常終了と判断
                                scheduler_status = 'crashed'
                        except ImportError:
                            # psutilがない場合は単純にファイルの状態を信頼
                            pass
                    
                    # 次回実行時間の計算
                    if scheduler_status == 'running' and 'posting_hours' in status_data:
                        posting_hours = status_data.get('posting_hours', self.posting_hours)
                        now = datetime.datetime.now()
                        next_hour = None
                        
                        for hour in sorted(posting_hours):
                            if now.hour < hour:
                                next_hour = hour
                                break
                        
                        if next_hour is None and posting_hours:
                            next_hour = posting_hours[0]  # 翌日の最初の時間
                        
                        if next_hour is not None:
                            next_day = now.day + (1 if now.hour >= next_hour else 0)
                            try:
                                next_date = now.replace(day=next_day, hour=next_hour, minute=0, second=0, microsecond=0)
                                next_run_time = next_date.strftime('%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                # 月末の問題を処理
                                next_month = now.month + 1 if now.month < 12 else 1
                                next_year = now.year + (1 if now.month == 12 else 0)
                                next_date = now.replace(year=next_year, month=next_month, day=1, 
                                                      hour=next_hour, minute=0, second=0, microsecond=0)
                                next_run_time = next_date.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                logger.error(f"状態ファイル読み込みエラー: {e}")
                scheduler_status = "エラー"
        
        # ステータス表示
        if scheduler_status == 'running':
            logger.info("ステータス: 実行中")
            print("⚙️ ステータス: 実行中")
            if start_time:
                running_time = datetime.datetime.now() - start_time
                hours, remainder = divmod(running_time.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"⏱️ 実行時間: {int(hours)}時間 {int(minutes)}分 {int(seconds)}秒")
            if pid:
                print(f"🔄 プロセスID: {pid}")
        elif scheduler_status == 'stopped':
            logger.info("ステータス: 停止中")
            print("⚙️ ステータス: 停止中")
        elif scheduler_status == 'crashed':
            logger.info("ステータス: 異常終了")
            print("⚙️ ステータス: 異常終了 - 再起動が必要です")
        else:
            logger.info(f"ステータス: {scheduler_status}")
            print(f"⚙️ ステータス: {scheduler_status}")
        
        logger.info(f"投稿時間: {', '.join([f'{h:02d}:00' for h in self.posting_hours])}")
        print(f"⏰ 投稿時間: {', '.join([f'{h:02d}:00' for h in self.posting_hours])}")
        
        # 次回の投稿時間を表示
        if next_run_time:
            logger.info(f"次回投稿予定: {next_run_time}")
            print(f"📅 次回投稿予定: {next_run_time}")
        elif schedule.jobs:
            next_job = min(schedule.jobs, key=lambda x: x.next_run)
            next_run_time = next_job.next_run.strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"次回投稿予定: {next_run_time}")
            print(f"📅 次回投稿予定: {next_run_time}")
        
        # アカウント情報
        accounts = self.account_manager.get_account_ids()
        logger.info(f"投稿対象アカウント: {len(accounts)}件")
        print(f"👥 投稿対象アカウント: {len(accounts)}件")
        
    def manual_post(self):
        """手動でのスケジュール投稿実行"""
        logger.info("手動投稿を実行します")
        print("\n🔄 手動投稿を実行します")
        self.scheduled_post()
        logger.info("手動投稿完了")
        print("✅ 手動投稿完了")

def main():
    """メイン実行関数"""
    print("🚀 Threads自動投稿スケジューラーシステム v5.0")
    print("=" * 50)
    logger.info("Threads自動投稿スケジューラーシステム v5.0 起動")
    
    try:
        scheduler = ThreadsSchedulerSystem()
        
        # コマンドライン引数の処理
        if len(sys.argv) > 1:
            if sys.argv[1] == "--manual":
                # 手動実行
                logger.info("手動実行モード")
                scheduler.manual_post()
            elif sys.argv[1] == "--status":
                # 状態確認
                logger.info("状態確認モード")
                scheduler.status()
            elif sys.argv[1] == "--stop":
                # スケジューラー停止
                logger.info("スケジューラー停止モード")
                scheduler.stop_scheduler()
            else:
                error_msg = f"不明な引数: {sys.argv[1]}"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                print("使用法: python threads_scheduler_system.py [--manual|--status|--stop]")
                return 1
        else:
            # 通常実行
            logger.info("通常実行モード")
            scheduler.run_scheduler()
            
            print("\nスケジューラーがバックグラウンドで実行中です")
            print("終了するには Ctrl+C を押してください")
            logger.info("スケジューラーがバックグラウンドで実行中")
            
            try:
                # メインスレッドを待機状態にする
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                logger.info("ユーザーによる中断")
                print("\n🛑 スケジューラーを停止します")
                scheduler.stop_scheduler()
                print("👋 システムを終了します")
    
    except Exception as e:
        error_msg = f"システムエラー: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())