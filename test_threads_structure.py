"""
新しいフォルダ構造のテスト用スクリプト
"""
import os
import sys
from threads_account_manager import ThreadsAccountManager
from threads_cloudinary_manager import ThreadsCloudinaryManager

def test_account_structure():
    """新しいアカウント構造のテスト"""
    print("\n🚀 === 新しいフォルダ構造テスト ===\n")
    
    # コンテンツマネージャー初期化
    try:
        content_manager = ThreadsAccountManager()
        print("✅ コンテンツマネージャーを初期化しました")
    except Exception as e:
        print(f"❌ コンテンツマネージャーの初期化に失敗: {str(e)}")
        return False
    
    # Cloudinaryマネージャー初期化
    try:
        cloudinary_manager = ThreadsCloudinaryManager()
        print("✅ Cloudinaryマネージャーを初期化しました")
    except Exception as e:
        print(f"❌ Cloudinaryマネージャーの初期化に失敗: {str(e)}")
        return False
    
    # 利用可能なアカウント
    accounts = content_manager.get_account_ids()
    print(f"📊 利用可能なアカウント: {len(accounts)}件")
    
    if not accounts:
        print("❌ アカウントが見つかりません")
        return False
    
    # アカウントを選択
    test_account = accounts[0]  # 最初のアカウントを使用
    print(f"✅ テスト用アカウント: {test_account}")
    
    # コンテンツ一覧
    content_ids = content_manager.get_account_content_ids(test_account)
    print(f"📊 {test_account} のコンテンツ数: {len(content_ids)}件")
    
    if not content_ids:
        print("❌ コンテンツが見つかりません")
        return False
    
    # ランダムコンテンツ取得
    print("\n🔄 ランダムコンテンツ選択テスト:")
    content = content_manager.get_random_content(test_account)
    
    if not content:
        print("❌ コンテンツの取得に失敗しました")
        return False
    
    content_id = content.get('id')
    print(f"✅ 選択されたコンテンツ: {content_id}")
    print(f"📝 メインテキスト: {content.get('main_text', '')[:100]}...")
    
    # 投稿タイプ判定
    post_type = content_manager.get_post_type(content)
    print(f"📊 投稿タイプ: {post_type}")
    
    # 画像URL取得テスト
    print("\n🖼️ 画像URL取得テスト:")
    if post_type in ["single_image", "carousel"]:
        image_urls = cloudinary_manager.detect_carousel_images(test_account, content_id)
        print(f"📊 取得した画像数: {len(image_urls)}件")
        
        for i, url in enumerate(image_urls, 1):
            print(f"  画像{i}: {url}")
    else:
        print("  📝 テキスト投稿（画像なし）")
    
    # アフィリエイト情報
    print("\n🔗 アフィリエイト情報:")
    if "affiliate_text" in content:
        print(f"📝 アフィリエイトテキスト: {content.get('affiliate_text', '')[:100]}...")
    else:
        print("  ℹ️ アフィリエイト情報なし")
    
    print("\n✅ テスト完了!")
    return True

if __name__ == "__main__":
    # 環境変数設定（本番ではconfig/settings.pyで行う）
    os.environ['CLOUDINARY_CLOUD_NAME'] = 'duu2ybdru'
    os.environ['CLOUDINARY_API_KEY'] = '925683855735695'
    os.environ['CLOUDINARY_API_SECRET'] = 'e7qWzubCbY8iJI2C8b1UvFcTsQU'
    
    try:
        result = test_account_structure()
        if result:
            print("\n🎉 テスト成功!")
        else:
            print("\n❌ テスト失敗!")
    except Exception as e:
        print(f"\n❌ 予期せぬエラー: {str(e)}")
        import traceback
        traceback.print_exc()