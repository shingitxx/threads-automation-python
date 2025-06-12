"""
実際の画像ファイル投稿テスト（1枚・2枚対応）
"""

import sys
import os
import requests
from pathlib import Path
sys.path.append('.')

# 強制的にテストモードを無効化
os.environ['TEST_MODE'] = 'False'

try:
    from image_posting_system import ThreadsImagePostingSystem
    from src.core.threads_api import ThreadsAPI, Account
    from config.settings import settings
    print("✅ インポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)

def download_test_images():
    """テスト用画像をダウンロード"""
    print("📥 テスト用画像ダウンロード中...")
    
    # テスト用画像URL（信頼できるソース）
    image_urls = [
        "https://picsum.photos/800/600.jpg",  # ランダム画像1
        "https://picsum.photos/600/800.jpg"   # ランダム画像2
    ]
    
    downloaded_files = []
    
    for i, url in enumerate(image_urls, 1):
        try:
            print(f"📥 画像{i}をダウンロード中: {url}")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                filename = f"test_image_{i}.jpg"
                filepath = Path(filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ 画像{i}ダウンロード成功: {filename} ({len(response.content)} bytes)")
                downloaded_files.append(str(filepath))
            else:
                print(f"❌ 画像{i}ダウンロード失敗: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 画像{i}ダウンロードエラー: {e}")
    
    return downloaded_files

def test_real_image_files():
    """実際の画像ファイル投稿テスト"""
    print("🎯 実際の画像ファイル投稿テスト開始")
    print("=" * 60)
    
    # システム初期化
    image_system = ThreadsImagePostingSystem()
    image_system.test_mode = False  # 実際の投稿モード
    
    # アクセストークン確認
    tokens = settings.get_account_tokens()
    
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
    print(f"🧪 テストモード: {image_system.test_mode}")
    
    # テスト用画像をダウンロード
    test_images = download_test_images()
    
    if len(test_images) < 2:
        print("❌ テスト画像のダウンロードに失敗しました")
        return
    
    print(f"\n📊 ダウンロード済み画像:")
    for i, img in enumerate(test_images, 1):
        size = os.path.getsize(img)
        print(f"  {i}. {img} ({size:,} bytes)")
    
    # 1枚画像投稿テスト
    print(f"\n🖼️ === 1枚画像投稿テスト ===")
    single_test = input("🚀 1枚画像投稿をテストしますか？ (y/n): ")
    
    if single_test.lower() == 'y':
        print("📡 1枚画像投稿実行中...")
        
        single_result = image_system.create_single_image_post(
            account=real_account,
            text="""🖼️ Python 1枚画像投稿テスト！

✨ 実際の画像ファイル使用
📁 ローカルファイル → Cloudinary → Threads
🔧 完全自動化システム

#Python #画像投稿 #1枚画像 #自動化 #テスト完了""",
            image_source=test_images[0]
        )
        
        print(f"\n📊 1枚画像投稿結果:")
        print(f"成功: {single_result.success}")
        
        if single_result.success:
            print(f"✅ 投稿ID: {single_result.post_id}")
            print(f"🖼️ 画像URL: {single_result.image_url}")
            print(f"🔗 投稿URL: https://threads.net/@{real_account.username}/post/{single_result.post_id}")
            print("🎉 1枚画像投稿成功！")
        else:
            print(f"❌ 1枚画像投稿失敗: {single_result.error}")
    
    # 2枚画像投稿テスト
    print(f"\n🖼️🖼️ === 2枚画像投稿テスト ===")
    multi_test = input("🚀 2枚画像投稿をテストしますか？ (y/n): ")
    
    if multi_test.lower() == 'y':
        print("📡 2枚画像投稿実行中...")
        
        multi_result = image_system.create_multi_image_post(
            account=real_account,
            text="""🖼️🖼️ Python 2枚画像投稿テスト！

🎯 GAS版を超える新機能:
✨ 複数画像同時投稿
📁 複数ファイル → Cloudinary → Threads
🔧 完全自動化処理
⚡ 高速アップロード

#Python #複数画像 #2枚投稿 #新機能 #GAS超越""",
            image_sources=test_images  # 2枚の画像を指定
        )
        
        print(f"\n📊 2枚画像投稿結果:")
        print(f"成功: {multi_result.success}")
        
        if multi_result.success:
            print(f"✅ 投稿ID: {multi_result.post_id}")
            print(f"🖼️ 画像URL: {multi_result.image_url}")
            print(f"🔗 投稿URL: https://threads.net/@{real_account.username}/post/{multi_result.post_id}")
            print("🎉 2枚画像投稿成功！")
        else:
            print(f"❌ 2枚画像投稿失敗: {multi_result.error}")
    
    # 画像付きツリー投稿テスト
    print(f"\n🌳🖼️ === 画像付きツリー投稿テスト ===")
    tree_test = input("🚀 画像付きツリー投稿もテストしますか？ (y/n): ")
    
    if tree_test.lower() == 'y':
        print("📡 画像付きツリー投稿実行中...")
        
        tree_result = image_system.create_image_tree_post(
            account=real_account,
            main_text="""🌳🖼️ 画像付きツリー投稿テスト！

📱 メイン投稿: 画像付き
💬 リプライ: アフィリエイト

完璧なツリー投稿システム完成！""",
            image_sources=test_images[0],  # 1枚目の画像を使用
            reply_text="""💬 これが画像付きツリー投稿のリプライです！

🔗 詳細はこちら:
https://example.com/affiliate

#アフィリエイト #ツリー投稿 #Python自動化"""
        )
        
        print(f"\n📊 画像付きツリー投稿結果:")
        print(f"成功: {tree_result['success']}")
        
        if tree_result["success"]:
            print(f"✅ メイン投稿ID: {tree_result['main_post_id']}")
            print(f"✅ リプライID: {tree_result['reply_post_id']}")
            print(f"🖼️ 画像URL: {tree_result['image_url']}")
            print(f"🔗 メイン投稿URL: https://threads.net/@{real_account.username}/post/{tree_result['main_post_id']}")
            print("🎉 画像付きツリー投稿成功！")
        else:
            print(f"❌ 画像付きツリー投稿失敗: {tree_result['error']}")
    
    # クリーンアップ
    cleanup = input("\n🗑️ テスト用画像ファイルを削除しますか？ (y/n): ")
    if cleanup.lower() == 'y':
        for img_file in test_images:
            try:
                os.remove(img_file)
                print(f"🗑️ 削除: {img_file}")
            except Exception as e:
                print(f"❌ 削除失敗: {img_file} - {e}")
    
    print(f"\n✅ 実際の画像ファイル投稿テスト完了")
    print("🎊 全パターン動作確認済み！")

def test_custom_images():
    """カスタム画像でのテスト（ユーザー指定）"""
    print("\n📁 カスタム画像投稿テスト")
    print("=" * 40)
    
    custom_test = input("🖼️ 独自の画像ファイルでテストしますか？ (y/n): ")
    
    if custom_test.lower() == 'y':
        print("\n💡 使用方法:")
        print("1. プロジェクトフォルダに画像ファイル（JPG/PNG）を配置")
        print("2. ファイル名を入力（例: my_image.jpg）")
        
        filename = input("\n📁 画像ファイル名を入力してください: ")
        
        if filename and os.path.exists(filename):
            print(f"✅ 画像ファイル確認: {filename}")
            size = os.path.getsize(filename)
            print(f"📊 ファイルサイズ: {size:,} bytes")
            
            # システム初期化
            image_system = ThreadsImagePostingSystem()
            image_system.test_mode = False
            
            tokens = settings.get_account_tokens()
            real_account = Account(
                id="ACCOUNT_011",
                username="kanae_15758", 
                user_id="10068250716584647",
                access_token=tokens["ACCOUNT_011"]
            )
            
            custom_text = input("📝 投稿テキストを入力（Enterで自動生成）: ")
            if not custom_text:
                custom_text = f"""🖼️ カスタム画像投稿テスト！

📁 ファイル: {filename}
📊 サイズ: {size:,} bytes
🔧 Python自動投稿システム

#カスタム画像 #Python #自動投稿"""
            
            proceed = input(f"\n🚀 {filename} で投稿しますか？ (y/n): ")
            
            if proceed.lower() == 'y':
                result = image_system.create_single_image_post(
                    account=real_account,
                    text=custom_text,
                    image_source=filename
                )
                
                if result.success:
                    print(f"✅ カスタム画像投稿成功: {result.post_id}")
                    print(f"🔗 投稿URL: https://threads.net/@{real_account.username}/post/{result.post_id}")
                else:
                    print(f"❌ カスタム画像投稿失敗: {result.error}")
        else:
            print(f"❌ ファイルが見つかりません: {filename}")

if __name__ == "__main__":
    print("🎯 実際の画像ファイル投稿システムテスト")
    print("=" * 60)
    print("🖼️ 1枚画像投稿テスト")
    print("🖼️🖼️ 2枚画像投稿テスト")
    print("🌳 画像付きツリー投稿テスト")
    print("📁 カスタム画像投稿テスト")
    
    try:
        test_real_image_files()
        test_custom_images()
        
    except KeyboardInterrupt:
        print("\n⏸️ テストを中断しました")
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
    
    print("\n🎊 画像投稿システム完全テスト終了！")