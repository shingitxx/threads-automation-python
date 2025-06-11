"""
スケジューラーシステム
既存Google Apps Script版の時間指定投稿を再現する自動化システム
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import List, Callable, Dict, Any, Optional
import logging

from config.settings import settings

class PostingScheduler:
    """投稿スケジューラークラス"""
    
    def __init__(self, posting_function: Callable = None):
        self.posting_function = posting_function
        self.is_running = False
        self.scheduler_thread = None
        self.execution_log = []
        self.setup_logging()
        
        # 既存GAS版と同じ投稿時間
        self.posting_hours = settings.schedule.posting_hours  # [2, 5, 8, 12, 17, 20, 22, 0]
        
    def setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(settings.data.logs_path / 'scheduler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('PostingScheduler')
    
    def set_posting_function(self, posting_function: Callable):
        """投稿実行関数を設定"""
        self.posting_function = posting_function
        self.logger.info(f"投稿関数を設定: {posting_function.__name__}")
    
    def setup_schedule(self):
        """
        投稿スケジュールを設定（既存GAS版のsetupScheduleTrigger互換）
        """
        if not settings.schedule.enabled:
            self.logger.warning("スケジュール投稿が無効化されています")
            return False
        
        # 既存のスケジュールをクリア
        schedule.clear()
        
        # 各時間にスケジュール設定
        for hour in self.posting_hours:
            schedule.every().day.at(f"{hour:02d}:00").do(self._execute_scheduled_posting, hour)
            self.logger.info(f"スケジュール設定: {hour:02d}:00")
        
        self.logger.info(f"✅ 投稿スケジュール設定完了: {self.posting_hours}")
        return True
    
    def _execute_scheduled_posting(self, hour: int):
        """
        スケジュール投稿実行（既存GAS版のcheckScheduledTime互換）
        """
        execution_time = datetime.now()
        execution_id = f"{execution_time.strftime('%Y%m%d')}_{hour:02d}"
        
        self.logger.info(f"🕐 {hour:02d}:00 スケジュール投稿開始")
        
        # 重複実行チェック
        if self._is_already_executed_today(hour):
            self.logger.warning(f"⏭️ {hour:02d}:00 の投稿は既に実行済み")
            return
        
        try:
            if self.posting_function:
                self.logger.info("🚀 投稿関数実行中...")
                result = self.posting_function()
                
                # 実行ログ記録
                log_entry = {
                    "execution_id": execution_id,
                    "execution_time": execution_time.isoformat(),
                    "hour": hour,
                    "success": result.get("success", False) if isinstance(result, dict) else True,
                    "result": result,
                    "accounts_processed": result.get("total_accounts", 0) if isinstance(result, dict) else 0,
                    "success_count": result.get("success_count", 0) if isinstance(result, dict) else 0
                }
                
                self.execution_log.append(log_entry)
                self._mark_as_executed(execution_id)
                
                if log_entry["success"]:
                    self.logger.info(f"✅ {hour:02d}:00 投稿完了 - 成功: {log_entry['success_count']}/{log_entry['accounts_processed']}")
                else:
                    self.logger.error(f"❌ {hour:02d}:00 投稿失敗")
                    
            else:
                self.logger.error("❌ 投稿関数が設定されていません")
                
        except Exception as e:
            self.logger.error(f"❌ {hour:02d}:00 投稿中にエラー: {e}")
            
            # エラーログ記録
            error_log = {
                "execution_id": execution_id,
                "execution_time": execution_time.isoformat(),
                "hour": hour,
                "success": False,
                "error": str(e)
            }
            self.execution_log.append(error_log)
    
    def _is_already_executed_today(self, hour: int) -> bool:
        """今日の指定時間に既に実行済みかチェック"""
        today = datetime.now().strftime('%Y%m%d')
        execution_id = f"{today}_{hour:02d}"
        
        # 実行ログから確認
        return any(
            log.get("execution_id") == execution_id 
            for log in self.execution_log
        )
    
    def _mark_as_executed(self, execution_id: str):
        """実行済みマークを設定"""
        # 実際の実装では永続化ストレージに保存
        # 現在はメモリ内のログで管理
        self.logger.debug(f"実行済みマーク: {execution_id}")
    
    def start_scheduler(self):
        """
        スケジューラー開始（バックグラウンド実行）
        """
        if self.is_running:
            self.logger.warning("スケジューラーは既に実行中です")
            return False
        
        if not self.setup_schedule():
            return False
        
        self.is_running = True
        
        def run_schedule():
            self.logger.info("🕐 スケジューラー開始 - バックグラウンド実行")
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 1分毎にチェック
            self.logger.info("🛑 スケジューラー停止")
        
        self.scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("✅ スケジューラーをバックグラウンドで開始しました")
        return True
    
    def stop_scheduler(self):
        """
        スケジューラー停止（既存GAS版のemergencyStop互換）
        """
        if not self.is_running:
            self.logger.warning("スケジューラーは実行されていません")
            return False
        
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("✅ スケジューラーを停止しました")
        return True
    
    def get_schedule_status(self) -> Dict[str, Any]:
        """
        スケジュール状況確認（既存GAS版のcheckScheduleStatus互換）
        """
        next_runs = []
        
        for job in schedule.jobs:
            next_run = job.next_run
            if next_run:
                next_runs.append({
                    "time": next_run.strftime("%H:%M"),
                    "next_run": next_run.isoformat()
                })
        
        # 次回投稿時間を計算
        now = datetime.now()
        next_posting_hour = None
        
        for hour in sorted(self.posting_hours):
            next_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            
            if next_posting_hour is None or next_time < next_posting_hour:
                next_posting_hour = next_time
        
        return {
            "is_running": self.is_running,
            "posting_hours": self.posting_hours,
            "scheduled_jobs": len(schedule.jobs),
            "next_runs": next_runs,
            "next_posting_hour": next_posting_hour.isoformat() if next_posting_hour else None,
            "execution_log_count": len(self.execution_log),
            "last_execution": self.execution_log[-1] if self.execution_log else None
        }
    
    def get_next_post_time(self) -> Dict[str, Any]:
        """
        次回投稿時間詳細取得（既存GAS版のgetNextPostTimeForUI互換）
        """
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        # 今日の残り投稿時間をチェック
        next_post_hour = None
        is_today = True
        
        for hour in sorted(self.posting_hours):
            if hour > current_hour or (hour == current_hour and current_minute < 5):
                next_post_hour = hour
                break
        
        # 今日に該当時間がない場合は翌日の最初の時間
        if next_post_hour is None:
            next_post_hour = min(self.posting_hours)
            is_today = False
        
        # 次回投稿までの時間計算
        next_post_time = now.replace(hour=next_post_hour, minute=0, second=0, microsecond=0)
        if not is_today:
            next_post_time += timedelta(days=1)
        
        time_diff = next_post_time - now
        hours_until = int(time_diff.total_seconds() // 3600)
        minutes_until = int((time_diff.total_seconds() % 3600) // 60)
        
        return {
            "next_post_time": f"{next_post_hour:02d}:00",
            "next_post_datetime": next_post_time.isoformat(),
            "is_today": is_today,
            "hours_until": hours_until,
            "minutes_until": minutes_until,
            "time_until_text": f"{hours_until}時間{minutes_until}分後",
            "posting_hours": self.posting_hours
        }
    
    def manual_trigger(self, hour: Optional[int] = None):
        """
        手動トリガー実行（テスト用）
        """
        if hour is None:
            hour = datetime.now().hour
        
        self.logger.info(f"🔧 手動トリガー実行: {hour:02d}:00")
        self._execute_scheduled_posting(hour)
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """実行履歴取得"""
        return self.execution_log[-limit:] if self.execution_log else []
    
    def clear_execution_history(self):
        """実行履歴クリア"""
        self.execution_log.clear()
        self.logger.info("✅ 実行履歴をクリアしました")

# グローバルスケジューラーインスタンス
posting_scheduler = PostingScheduler()

if __name__ == "__main__":
    # スケジューラーテスト
    print("🔧 スケジューラーシステムテスト")
    
    # ダミー投稿関数
    def dummy_posting_function():
        print("🧪 ダミー投稿関数実行")
        time.sleep(1)
        return {
            "success": True,
            "total_accounts": 2,
            "success_count": 2,
            "message": "テスト投稿完了"
        }
    
    # スケジューラー設定
    posting_scheduler.set_posting_function(dummy_posting_function)
    
    # スケジュール状況確認
    status = posting_scheduler.get_schedule_status()
    print(f"📊 スケジューラー状況:")
    print(f"  実行中: {status['is_running']}")
    print(f"  投稿時間: {status['posting_hours']}")
    
    # 次回投稿時間確認
    next_post = posting_scheduler.get_next_post_time()
    print(f"⏰ 次回投稿予定:")
    print(f"  時間: {next_post['next_post_time']}")
    print(f"  予定日: {'今日' if next_post['is_today'] else '明日'}")
    print(f"  残り時間: {next_post['time_until_text']}")
    
    # 手動トリガーテスト
    print(f"\n🧪 手動トリガーテスト:")
    posting_scheduler.manual_trigger()
    
    # 実行履歴確認
    history = posting_scheduler.get_execution_history()
    print(f"\n📋 実行履歴: {len(history)}件")
    for log in history:
        status_icon = "✅" if log.get('success') else "❌"
        print(f"  {status_icon} {log.get('execution_time', 'N/A')}: {log.get('hour', 'N/A')}時")
    
    print("\n✅ スケジューラーシステムテスト完了")
    print("🎯 次のステップ: 投稿システムとの統合")