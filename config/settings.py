"""
Threads自動投稿システム - 設定管理
既存Google Apps Script版と完全互換性を保つ設定システム
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent

@dataclass
class ThreadsConfig:
    """Threads API設定"""
    api_base: str = "https://graph.threads.net/v1.0"
    app_id: str = "2542581129421398"  # 既存GAS版と同じ
    
@dataclass 
class CloudinaryConfig:
    """Cloudinary画像処理設定（既存GAS版互換）"""
    cloud_name: str = "duu2ybdru"
    api_key: str = "925683855735695"
    api_secret: str = "e7qWzubCbY8iJI2C8b1UvFcTsQU"
    base_url: str = "https://api.cloudinary.com/v1_1"

@dataclass
class PostingConfig:
    """投稿設定（完全無制限版）"""
    # 制限撤廃（既存GAS版の無制限化を継承）
    max_daily_posts: int = -1  # 無制限
    post_interval_minutes: int = 0  # 無制限
    reply_delay_minutes: int = 5  # アフィリエイトリプライ遅延
    
    # 安全間隔（既存GAS版と同じ）
    all_accounts_interval_seconds: int = 10  # アカウント間隔
    test_interval_seconds: int = 10
    account_interval_seconds: int = 30  # 時間指定投稿用

@dataclass
class ScheduleConfig:
    """時間指定投稿設定（既存GAS版と完全同期）"""
    enabled: bool = True
    posting_hours: List[int] = None  # [2, 5, 8, 12, 17, 20, 22, 0]
    timezone: str = "Asia/Tokyo"
    execution_log_enabled: bool = True
    
    def __post_init__(self):
        if self.posting_hours is None:
            self.posting_hours = [2, 5, 8, 12, 17, 20, 22, 0]

@dataclass
class RandomConfig:
    """ランダム選択設定（既存GAS版互換）"""
    enable_random_selection: bool = True
    avoid_recent_content: bool = True
    recent_content_limit: int = 3
    enable_shared_content: bool = True
    debug_mode: bool = False

@dataclass
class DataConfig:
    """データ管理設定"""
    accounts_file: str = "src/data/accounts.json"
    content_file: str = "src/data/content.json"
    logs_dir: str = "logs"
    
    @property
    def accounts_path(self) -> Path:
        return PROJECT_ROOT / self.accounts_file
        
    @property 
    def content_path(self) -> Path:
        return PROJECT_ROOT / self.content_file
        
    @property
    def logs_path(self) -> Path:
        return PROJECT_ROOT / self.logs_dir

class Settings:
    """統合設定管理クラス"""
    
    def __init__(self):
        # 各設定を初期化
        self.threads = ThreadsConfig()
        self.cloudinary = CloudinaryConfig()
        self.posting = PostingConfig()
        self.schedule = ScheduleConfig()
        self.random = RandomConfig()
        self.data = DataConfig()
        
        # 環境変数から設定を上書き
        self._load_from_env()
        
    def _load_from_env(self):
        """環境変数から設定を読み込み"""
        # Threads API設定
        if os.getenv("THREADS_APP_ID"):
            self.threads.app_id = os.getenv("THREADS_APP_ID")
            
        # Cloudinary設定
        if os.getenv("CLOUDINARY_CLOUD_NAME"):
            self.cloudinary.cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        if os.getenv("CLOUDINARY_API_KEY"):
            self.cloudinary.api_key = os.getenv("CLOUDINARY_API_KEY")
        if os.getenv("CLOUDINARY_API_SECRET"):
            self.cloudinary.api_secret = os.getenv("CLOUDINARY_API_SECRET")
            
        # スケジュール設定
        if os.getenv("SCHEDULE_ENABLED"):
            self.schedule.enabled = os.getenv("SCHEDULE_ENABLED").lower() == "true"
            
        # デバッグモード
        if os.getenv("DEBUG_MODE"):
            self.random.debug_mode = os.getenv("DEBUG_MODE").lower() == "true"
    
    def get_account_tokens(self) -> Dict[str, str]:
        """アカウントのアクセストークンを取得"""
        tokens = {}
        
        # 既存GAS版のアカウントID形式を継承
        account_ids = ["ACC001", "ACCOUNT_002", "ACCOUNT_003", "ACCOUNT_004"]
        
        for account_id in account_ids:
            token_key = f"TOKEN_{account_id}"
            if os.getenv(token_key):
                tokens[account_id] = os.getenv(token_key)
                
        return tokens
    
    def setup_directories(self):
        """必要なディレクトリを作成"""
        self.data.logs_path.mkdir(exist_ok=True)
        self.data.accounts_path.parent.mkdir(exist_ok=True)
        self.data.content_path.parent.mkdir(exist_ok=True)
    
    def validate(self) -> List[str]:
        """設定の妥当性をチェック"""
        errors = []
        
        # アクセストークンチェック
        tokens = self.get_account_tokens()
        if not tokens:
            errors.append("アカウントのアクセストークンが設定されていません")
            
        # Cloudinary設定チェック
        if not all([
            self.cloudinary.cloud_name,
            self.cloudinary.api_key, 
            self.cloudinary.api_secret
        ]):
            errors.append("Cloudinary設定が不完全です")
            
        return errors

# グローバル設定インスタンス
settings = Settings()

# 既存GAS版との互換性のための定数
CONFIG = {
    "THREADS_API_BASE": settings.threads.api_base,
    "APP_ID": settings.threads.app_id,
    "CLOUDINARY": {
        "CLOUD_NAME": settings.cloudinary.cloud_name,
        "API_KEY": settings.cloudinary.api_key,
        "API_SECRET": settings.cloudinary.api_secret,
        "BASE_URL": settings.cloudinary.base_url
    },
    "POSTING_HOURS": settings.schedule.posting_hours,
    "MAX_DAILY_POSTS": settings.posting.max_daily_posts,
    "REPLY_DELAY_MINUTES": settings.posting.reply_delay_minutes
}

if __name__ == "__main__":
    # 設定テスト
    print("🔧 設定システムテスト")
    print(f"✅ Threads API Base: {settings.threads.api_base}")
    print(f"✅ App ID: {settings.threads.app_id}")
    print(f"✅ 投稿時間: {settings.schedule.posting_hours}")
    print(f"✅ 最大投稿数: {settings.posting.max_daily_posts} (無制限)")
    
    # 設定検証
    errors = settings.validate()
    if errors:
        print("❌ 設定エラー:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ 設定は正常です")
    
    # ディレクトリ作成
    settings.setup_directories()
    print("✅ 必要なディレクトリを作成しました")