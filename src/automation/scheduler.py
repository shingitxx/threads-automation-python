import schedule
import time
import random
import datetime
from config.settings import logger, settings
from src.automation.posting import posting_manager
from src.core.account_manager import account_manager

class SchedulerManager:
    """スケジュールされた投稿を管理するクラス"""
    
    def __init__(self):
        self.posting_manager = posting_manager
        self.is_running = False
    
    def post_job(self):
        """スケジュールされた投稿ジョブ"""
        try:
            logger.info(f"スケジュールされた投稿を開始します: {datetime.datetime.now()}")
            
            # アクティブなアカウントを取得
            active_accounts = account_manager.get_active_accounts()
            if not active_accounts:
                logger.warning("アクティブなアカウントがありません")
                return False
            
            # ランダムにアカウントを選択
            account = random.choice(active_accounts)
            logger.info(f"投稿アカウント: {account.username} ({account.id})")
            
            # 投稿タイプをランダムに選択
            # 1: テキスト投稿, 2: ツリー投稿, 3: 画像投稿（将来的に実装）
            post_type = random.randint(1, 2)
            
            if post_type == 1:
                # テキスト投稿
                result = self.posting_manager.create_single_post(account.id)
                logger.info(f"テキスト投稿完了: {result.get('id') if result else 'Failed'}")
            else:
                # ツリー投稿
                result = self.posting_manager.create_tree_post(account.id)
                main_id = result.get('main', {}).get('id', 'Failed') if result else 'Failed'
                affiliate_id = result.get('affiliate', {}).get('id', 'Failed') if result else 'Failed'
                logger.info(f"ツリー投稿完了: メイン={main_id}, アフィリエイト={affiliate_id}")
            
            return True
        except Exception as e:
            logger.error(f"スケジュール投稿エラー: {str(e)}")
            return False
    
    def setup_schedule(self):
        """投稿スケジュールをセットアップ"""
        try:
            # すべてのジョブをクリア
            schedule.clear()
            
            # 指定された時間に投稿をスケジュール
            for hour in settings.schedule.posting_hours:
                schedule.every().day.at(f"{hour:02d}:00").do(self.post_job)
                logger.info(f"投稿スケジュール追加: 毎日 {hour:02d}:00")
            
            return True
        except Exception as e:
            logger.error(f"スケジュールセットアップエラー: {str(e)}")
            return False
    
    def run_scheduler(self):
        """スケジューラを実行"""
        try:
            if self.is_running:
                logger.warning("スケジューラは既に実行中です")
                return False
            
            self.is_running = True
            logger.info("スケジューラを開始します")
            
            # スケジュールのセットアップ
            self.setup_schedule()
            
            # 日次投稿数リセット
            account_manager.reset_daily_post_counts()
            
            # スケジューラループ
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 1分ごとにチェック
            
            return True
        except Exception as e:
            logger.error(f"スケジューラ実行エラー: {str(e)}")
            self.is_running = False
            return False
    
    def stop_scheduler(self):
        """スケジューラを停止"""
        try:
            self.is_running = False
            logger.info("スケジューラを停止します")
            return True
        except Exception as e:
            logger.error(f"スケジューラ停止エラー: {str(e)}")
            return False
    
    def run_immediate_post(self, post_type="text"):
        """即時投稿を実行"""
        try:
            logger.info(f"即時投稿を実行します: タイプ={post_type}")
            
            # アクティブなアカウントを取得
            active_accounts = account_manager.get_active_accounts()
            if not active_accounts:
                logger.warning("アクティブなアカウントがありません")
                return False
            
            # ランダムにアカウントを選択
            account = random.choice(active_accounts)
            logger.info(f"投稿アカウント: {account.username} ({account.id})")
            
            if post_type == "text":
                # テキスト投稿
                result = self.posting_manager.create_single_post(account.id)
                post_id = result.get('id') if result else 'Failed'
            elif post_type == "tree":
                # ツリー投稿
                result = self.posting_manager.create_tree_post(account.id)
                post_id = result.get('main', {}).get('id') if result else 'Failed'
            elif post_type == "image":
                # 画像投稿（画像パスは仮）
                image_path = "images/sample.jpg"
                result = self.posting_manager.create_image_post(account.id, image_path=image_path)
                post_id = result.get('id') if result else 'Failed'
            else:
                logger.error(f"不明な投稿タイプ: {post_type}")
                return False
            
            logger.info(f"即時投稿完了: ID={post_id}, タイプ={post_type}")
            return result
        except Exception as e:
            logger.error(f"即時投稿エラー: {str(e)}")
            return False

# グローバルインスタンス
scheduler_manager = SchedulerManager()