"""
Threads直接投稿機能のテスト用スクリプト
"""
import os
import sys

from threads_direct_post import ThreadsDirectPost
from threads_account_manager import ThreadsAccountManager

def test_direct_post():
    """投稿機能のテスト"""
    print("\n🚀 === Threads直接投稿機能テスト ===\n")
    
    # 環境変数設定（本番ではconfig/settings.pyで行う）
    os.environ['CLOUDINARY_CLOUD_NAME'] = 'duu2ybdru'
    os.environ['CLOUDINARY_API_KEY'] = '925683855735695'
    os.environ['CLOUDINARY_API_SECRET'] = 'e7qWzubCbY8iJI2C8b1UvFcTsQU'
    
    # 直接投稿クラスの初期化
    direct_post = ThreadsDirectPost()
    account_manager = ThreadsAccountManager()
    
    # 利用可能なアカウント
    accounts = account_manager.get_account_ids()
    if not accounts:
        print("❌ 利用可能なアカウントが見つかりません")
        return False
    
    test_account = accounts[0]
    print(f"👤 テスト用アカウント: {test_account}")
    
    # アカウントのコンテンツを取得
    content_ids = account_manager.get_account_content_ids(test_account)
    if not content_ids:
        print("❌ コンテンツが見つかりません")
        return False
    
    # テスト用コンテンツを選択
    test_content_id = content_ids[0]
    print(f"📄 テスト用コンテンツ: {test_content_id}")
    
    # コンテンツ情報を取得
    content = account_manager.get_content(test_account, test_content_id)
    if not content:
        print("❌ コンテンツ情報の取得に失敗しました")
        return False
    
    print(f"📝 メインテキスト: {content.get('main_text', '')[:100]}...")
    
    # 投稿機能テスト（テストモード）
    print("\n🧪 テストモード：実際には投稿されません")
    
    # 投稿タイプを判定
    images = content.get('images', [])
    post_type = "carousel" if len(images) > 1 else ("image" if images else "text")
    print(f"📊 投稿タイプ: {post_type}")
    
    # 画像情報
    if images:
        print(f"🖼️ 画像数: {len(images)}枚")
        for i, image in enumerate(images, 1):
            print(f"  画像{i}: {image.get('path')}")
    
    # アフィリエイト情報
    has_affiliate = "affiliate_text" in content
    if has_affiliate:
        print("\n🔗 アフィリエイトテキスト:")
        print(content.get('affiliate_text', '')[:100] + "..." if len(content.get('affiliate_text', '')) > 100 else content.get('affiliate_text', ''))
    
    print("\n✅ テスト完了！実際の投稿を行いますか？")
    confirm = input("実際に投稿する場合は 'post' と入力してください: ").strip()
    
    if confirm.lower() == 'post':
        print("\n🚀 実際の投稿を実行します...")
        result = direct_post.post_with_affiliate(test_account, test_content_id)
        
        if result and result.get("success"):
            print(f"✅ 投稿成功: {result}")
            return True
        else:
            print(f"❌ 投稿失敗: {result}")
            return False
    else:
        print("投稿をキャンセルしました")
        return True

if __name__ == "__main__":
    try:
        test_direct_post()
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()