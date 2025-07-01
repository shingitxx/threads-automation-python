"""
Threadsの直接投稿機能
新しいフォルダ構造に対応した投稿機能を提供
"""
import os
import time
import traceback
from typing import Dict, List, Optional, Any

from threads_account_manager import ThreadsAccountManager
from threads_cloudinary_manager import ThreadsCloudinaryManager
from src.core.threads_api import threads_api

class ThreadsDirectPost:
    """Threads直接投稿クラス"""
    
    def __init__(self):
        """初期化"""
        self.account_manager = ThreadsAccountManager()
        self.cloudinary_manager = ThreadsCloudinaryManager()
    
    def post_text(self, account_id, text):
        """テキスト投稿を実行"""
        try:
            # アカウント固有のユーザーIDを取得
            user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
            instagram_user_id = os.getenv(user_id_key, os.getenv("INSTAGRAM_USER_ID"))
            print(f"DEBUG: アカウント {account_id} のユーザーID: {instagram_user_id}")
            
            # アカウント固有のアクセストークンを取得
            token_key = f"TOKEN_{account_id}"
            access_token = os.getenv(token_key, os.getenv("THREADS_ACCESS_TOKEN"))
            
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": instagram_user_id,
                "access_token": access_token
            }
            
            # 投稿実行
            print(f"📡 APIを呼び出して投稿中...")
            result = threads_api.create_text_post(account_data, text)
            
            return result
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            return None
    
    def post_image(self, account_id, content_id):
        """画像投稿を実行"""
        try:
            # コンテンツ情報を取得
            content = self.account_manager.get_content(account_id, content_id)
            if not content:
                return {"success": False, "error": "コンテンツが見つかりません"}
            
            # メインテキストを取得
            main_text = content.get("main_text", "")
            
            # 画像URLを取得
            image_urls = self.cloudinary_manager.detect_carousel_images(account_id, content_id)
            if not image_urls:
                return {"success": False, "error": "画像が見つかりません"}
            
            # アカウント固有のユーザーIDとトークンを取得
            user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
            instagram_user_id = os.getenv(user_id_key, os.getenv("INSTAGRAM_USER_ID"))
            
            token_key = f"TOKEN_{account_id}"
            access_token = os.getenv(token_key, os.getenv("THREADS_ACCESS_TOKEN"))
            
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": instagram_user_id,
                "access_token": access_token
            }
            
            # 投稿タイプに応じた処理
            if len(image_urls) > 1:
                # 真のカルーセル投稿
                print(f"🎠 真のカルーセル投稿として {len(image_urls)}枚の画像で投稿を実行します")
                result = threads_api.create_true_carousel_post(account_data, main_text, image_urls)
            else:
                # 単一画像投稿
                print(f"🖼️ 画像URL: {image_urls[0]} で投稿を実行します")
                result = threads_api.create_image_post(account_data, main_text, image_urls[0])
            
            # 使用回数をインクリメント
            if result:
                self.account_manager.increment_usage_count(account_id, content_id)
            
            return result
        except Exception as e:
            print(f"❌ 画像投稿エラー: {e}")
            traceback.print_exc()
            return None
    
    def post_reply(self, account_id, text, reply_to_id):
        """リプライ投稿を実行"""
        try:
            # アカウント固有のユーザーIDを取得
            user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
            instagram_user_id = os.getenv(user_id_key, os.getenv("INSTAGRAM_USER_ID"))
            
            # アカウント固有のアクセストークンを取得
            token_key = f"TOKEN_{account_id}"
            access_token = os.getenv(token_key, os.getenv("THREADS_ACCESS_TOKEN"))
            
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": instagram_user_id,
                "access_token": access_token
            }
            
            # リプライ実行
            print(f"📡 APIを呼び出してリプライ中...")
            result = threads_api.create_reply_post(account_data, text, reply_to_id)
            
            return result
        except Exception as e:
            print(f"❌ リプライエラー: {e}")
            return None
    
    def post_with_affiliate(self, account_id, content_id):
        """メイン投稿＋ツリー投稿を実行（tree_post対応版）"""
        try:
            # コンテンツ情報を取得
            content = self.account_manager.get_content(account_id, content_id)
            if not content:
                return {"success": False, "error": "コンテンツが見つかりません"}
            
            # メインテキストを取得
            main_text = content.get("main_text", "")
            
            # 画像URLを取得
            image_urls = self.cloudinary_manager.detect_carousel_images(account_id, content_id)
            
            # アカウント固有のユーザーIDとトークンを取得
            user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
            instagram_user_id = os.getenv(user_id_key, os.getenv("INSTAGRAM_USER_ID"))
            
            token_key = f"TOKEN_{account_id}"
            access_token = os.getenv(token_key, os.getenv("THREADS_ACCESS_TOKEN"))
            
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": instagram_user_id,
                "access_token": access_token
            }
            
            # 投稿タイプに応じた処理
            if image_urls and len(image_urls) > 1:
                # 真のカルーセル投稿
                print(f"🎠 真のカルーセル投稿として {len(image_urls)}枚の画像で投稿を実行します")
                main_result = threads_api.create_true_carousel_post(account_data, main_text, image_urls)
            elif image_urls and len(image_urls) == 1:
                # 単一画像投稿
                print(f"🖼️ 画像URL: {image_urls[0]} で投稿を実行します")
                main_result = threads_api.create_image_post(account_data, main_text, image_urls[0])
            else:
                # テキストのみ投稿
                print(f"📝 テキストのみで投稿を実行します")
                main_result = threads_api.create_text_post(account_data, main_text)
            
            if not main_result:
                print(f"❌ {account_id}: メイン投稿に失敗しました")
                return {"success": False, "error": "メイン投稿に失敗しました"}
            
            main_post_id = main_result.get('id')
            print(f"✅ メイン投稿成功: {main_post_id}")
            
            # ツリー投稿の処理（tree_post = YES の場合）
            tree_post = content.get("tree_post", "NO").upper()
            if tree_post == "YES":
                tree_text = content.get("tree_text", "")
                quote_account = content.get("quote_account", "")
                
                if tree_text:
                    print(f"🌳 ツリー投稿を準備中...")
                    print(f"   内容: {tree_text[:50]}..." if len(tree_text) > 50 else f"   内容: {tree_text}")
                    
                    # 引用投稿IDを取得（もし指定されていれば）
                    quote_post_id = None
                    if quote_account:
                        quote_id_key = f"QUOTE_POST_ID_{quote_account}"
                        quote_post_id = os.getenv(quote_id_key)
                        if quote_post_id:
                            print(f"   📎 引用アカウント: @{quote_account}")
                            print(f"   📌 引用投稿ID: {quote_post_id}")
                    
                    print(f"⏸️ リプライ準備中（5秒待機）...")
                    time.sleep(5)
                    
                    # ツリー投稿（リプライ）を実行
                    if quote_post_id:
                        # 引用投稿として実行
                        reply_result = self.post_quote_reply(account_id, tree_text, main_post_id, quote_post_id)
                    else:
                        # 通常のリプライとして実行
                        reply_result = self.post_reply(account_id, tree_text, main_post_id)
                    
                    if not reply_result:
                        print(f"❌ ツリー投稿失敗")
                        return {
                            "success": True,  # メイン投稿は成功
                            "main_post_id": main_post_id,
                            "tree_status": "failed"
                        }
                    
                    reply_post_id = reply_result.get('id')
                    print(f"✅ ツリー投稿成功: {reply_post_id}")
                    
                    # 使用回数をインクリメント
                    self.account_manager.increment_usage_count(account_id, content_id)
                    
                    return {
                        "success": True,
                        "main_post_id": main_post_id,
                        "reply_post_id": reply_post_id,
                        "post_type": "carousel" if len(image_urls) > 1 else ("image" if image_urls else "text"),
                        "tree_post": "YES"
                    }
                else:
                    print(f"⚠️ tree_post=YESですが、tree_textが空です")
            else:
                print(f"ℹ️ ツリー投稿なし (tree_post={tree_post})")
            
            # 使用回数をインクリメント
            self.account_manager.increment_usage_count(account_id, content_id)
            
            return {
                "success": True,
                "main_post_id": main_post_id,
                "post_type": "carousel" if len(image_urls) > 1 else ("image" if image_urls else "text"),
                "tree_post": "NO"
            }
                
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        
    def post_quote_reply(self, account_id, text, reply_to_id, quote_post_id):
        """引用付きリプライ投稿を実行"""
        try:
            # アカウント固有のユーザーIDを取得
            user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
            instagram_user_id = os.getenv(user_id_key, os.getenv("INSTAGRAM_USER_ID"))
            
            # アカウント固有のアクセストークンを取得
            token_key = f"TOKEN_{account_id}"
            access_token = os.getenv(token_key, os.getenv("THREADS_ACCESS_TOKEN"))
            
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": instagram_user_id,
                "access_token": access_token
            }
            
            # 引用付きリプライ実行
            print(f"📡 APIを呼び出して引用リプライ中...")
            print(f"   引用投稿ID: {quote_post_id}")
            result = threads_api.create_quote_reply_post(account_data, text, reply_to_id, quote_post_id)
            
            return result
        except Exception as e:
            print(f"❌ 引用リプライエラー: {e}")
            return None

# モジュールとしてインポートされた場合の動作確認
if __name__ == "__main__":
    # テスト用コード
    direct_post = ThreadsDirectPost()
    
    # 環境変数設定が必要な場合
    import os
    if not os.getenv("CLOUDINARY_CLOUD_NAME"):
        os.environ['CLOUDINARY_CLOUD_NAME'] = 'duu2ybdru'
        os.environ['CLOUDINARY_API_KEY'] = '925683855735695'
        os.environ['CLOUDINARY_API_SECRET'] = 'e7qWzubCbY8iJI2C8b1UvFcTsQU'
    
    # テスト用アカウントとコンテンツID
    test_account = "ACCOUNT_001"
    test_content_id = "ACCOUNT_001_CONTENT_001"  # 実際のコンテンツIDに置き換え
    
    # テキスト投稿テスト
    # result = direct_post.post_text(test_account, "これはテストテキスト投稿です #テスト")
    
    # コンテンツ投稿テスト
    result = direct_post.post_with_affiliate(test_account, test_content_id)
    print(f"投稿結果: {result}")