"""
実際の画像投稿テスト
"""

import sys
import os
sys.path.append('.')

try:
    from image_posting_system import ThreadsImagePostingSystem
    from src.core.threads_api import ThreadsAPI, Account
    from config.settings import settings
    print("✅ インポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)

def test_real_image_posting():
    """実際の画像投稿テスト"""
    print("🚀 実際の画像投稿テスト開始")
    print("=" * 50)
    
    # システム初期化
    image_system = ThreadsImagePostingSystem()
    api = ThreadsAPI()
    
    print(f"🧪 テストモード: {image_system.test_mode}")
    
    # アクセストークン確認
    tokens = settings.get_account_tokens()
    print(f"🔑 利用可能トークン: {list(tokens.keys())}")
    
    if "ACCOUNT_011" not in tokens:
        print("❌ ACCOUNT_011のトークンが見つかりません")
        return
    
    # 実際のアカウント情報
    real_account = Account(
        id="ACCOUNT_011",
        username="kanae_15758",
        user_id="10068250716584647",
        access_token=tokens["ACCOUNT_011"]
    )
    
    print(f"👤 アカウント: {real_account.username}")
    print(f"🆔 ユーザーID: {real_account.user_id}")
    
    # テスト画像URL（小さなテスト画像）
    test_image_url = "https://httpbin.org/image/jpeg"
    
    print(f"\n🧪 1枚画像投稿テスト")
    print(f"🖼️ テスト画像: {test_image_url}")
    
    # 実際の投稿確認
    proceed = input("🚀 実際にThreadsに画像投稿しますか？ (y/n): ")
    
    if proceed.lower() == 'y':
        print("📡 実際の画像投稿実行中...")
        
        # 1枚画像投稿テスト
        result = image_system.create_single_image_post(
            account=real_account,
            text="Python画像投稿システムからのテスト🖼️\n#Python #自動投稿 #テスト",
            image_source=test_image_url
        )
        
        print(f"\n📊 投稿結果:")
        print(f"成功: {result.success}")
        
        if result.success:
            print(f"✅ 投稿ID: {result.post_id}")
            print(f"🖼️ 画像URL: {result.image_url}")
            print(f"🔗 投稿URL: https://threads.net/@{real_account.username}/post/{result.post_id}")
            
            # 2枚画像投稿テスト
            test2 = input("\n🖼️🖼️ 2枚画像投稿もテストしますか？ (y/n): ")
            if test2.lower() == 'y':
                print("📡 2枚画像投稿実行中...")
                
                result2 = image_system.create_multi_image_post(
                    account=real_account,
                    text="Python 2枚画像投稿システムからのテスト🖼️🖼️\n#Python #複数画像 #自動投稿",
                    image_sources=[test_image_url, test_image_url]  # 同じ画像を2枚
                )
                
                if result2.success:
                    print(f"✅ 2枚画像投稿成功: {result2.post_id}")
                    print(f"🔗 投稿URL: https://threads.net/@{real_account.username}/post/{result2.post_id}")
                else:
                    print(f"❌ 2枚画像投稿失敗: {result2.error}")
            
            # 画像付きツリー投稿テスト
            tree_test = input("\n🌳 画像付きツリー投稿もテストしますか？ (y/n): ")
            if tree_test.lower() == 'y':
                print("📡 画像付きツリー投稿実行中...")
                
                result3 = image_system.create_image_tree_post(
                    account=real_account,
                    main_text="画像付きメイン投稿🖼️\nPython自動投稿システムテスト",
                    image_sources=test_image_url,
                    reply_text="これは画像付きツリー投稿のリプライです💬\n#アフィリエイト #テスト\nhttps://example.com/test"
                )
                
                if result3["success"]:
                    print(f"✅ ツリー投稿成功!")
                    print(f"📱 メイン投稿: {result3['main_post_id']}")
                    print(f"💬 リプライ: {result3['reply_post_id']}")
                    print(f"🔗 メイン投稿URL: https://threads.net/@{real_account.username}/post/{result3['main_post_id']}")
                else:
                    print(f"❌ ツリー投稿失敗: {result3['error']}")
                    
        else:
            print(f"❌ 投稿失敗: {result.error}")
            
    else:
        print("⏸️ テストをキャンセルしました")
    
    print("\n✅ 画像投稿テスト完了")

if __name__ == "__main__":
    test_real_image_posting()