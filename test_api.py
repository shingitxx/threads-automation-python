"""
Threads API 動作確認テスト - スタンドアロン版
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config.settings import settings
    print("✅ config.settings インポート成功")
    
    print("🔧 Threads API基本テスト")
    print(f"✅ API Base URL: {settings.threads.api_base}")
    print(f"✅ App ID: {settings.threads.app_id}")
    print(f"✅ 投稿時間: {settings.schedule.posting_hours}")
    print(f"✅ 最大投稿数: {settings.posting.max_daily_posts} (無制限)")
    
    # アクセストークン確認
    tokens = settings.get_account_tokens()
    if tokens:
        print(f"✅ 設定済みアカウント: {list(tokens.keys())}")
    else:
        print("⚠️ アクセストークンが設定されていません")
        print("💡 .env ファイルを作成して TOKEN_ACC001 等を設定してください")
    
    print("✅ 基本設定テスト完了")
    
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print("📁 現在のディレクトリ:", os.getcwd())
    print("📁 スクリプトの場所:", os.path.dirname(os.path.abspath(__file__)))
    print("🔍 sys.path:", sys.path[:3])
    
except Exception as e:
    print(f"❌ その他のエラー: {e}")