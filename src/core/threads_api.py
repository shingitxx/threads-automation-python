import requests
import json
import logging
import time
from dataclasses import dataclass
from typing import Optional, List
from config.settings import THREADS_API_BASE_URL, THREADS_ACCESS_TOKEN, INSTAGRAM_USER_ID, logger, settings

@dataclass
class Account:
    """アカウント情報（GAS版互換）"""
    id: str
    username: str = ""
    user_id: str = ""
    access_token: str = ""
    app_id: str = ""
    last_post_time: Optional[str] = None
    daily_post_count: int = 0
    status: str = "アクティブ"

class ThreadsAPI:
    """Threads Graph APIとの連携を担当するクラス"""
    
    def __init__(self):
        self.base_url = THREADS_API_BASE_URL
        self.access_token = THREADS_ACCESS_TOKEN
        self.user_id = INSTAGRAM_USER_ID
        self.logger = logger
    
    def get_headers(self, access_token=None):
        """API呼び出し用のヘッダーを取得"""
        token = access_token or self.access_token
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_user_info(self, access_token=None, user_id=None):
        """ユーザー情報を取得"""
        try:
            token = access_token or self.access_token
            
            url = f"{self.base_url}/me"
            headers = self.get_headers(token)
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"ユーザー情報取得成功: {result}")
            return result
        except Exception as e:
            self.logger.error(f"ユーザー情報取得エラー: {str(e)}")
            return None
    
    def test_connection(self, access_token=None, user_id=None):
        """アクセストークンと接続をテスト"""
        try:
            token = access_token or self.access_token
            
            user_info = self.get_user_info(token)
            return user_info is not None and 'id' in user_info
        except Exception as e:
            self.logger.error(f"接続テストエラー: {str(e)}")
            return False
    
    def create_text_post(self, account, text):
        """テキスト投稿を作成"""
        try:
            # 1. ユーザーIDを取得
            user_info = self.get_user_info()
            if not user_info or 'id' not in user_info:
                self.logger.error("ユーザーIDの取得に失敗しました")
                return None
            
            user_id = user_info['id']
            token = self.access_token
            
            # 2. スレッド（投稿）の作成
            url = f"{self.base_url}/{user_id}/threads"
            payload = {
                "text": text,
                "media_type": "TEXT"
            }
            
            self.logger.info(f"投稿URL: {url}")
            self.logger.info(f"ユーザーID: {user_id}")
            self.logger.info(f"ペイロード: {payload}")
            
            headers = self.get_headers(token)
            response = requests.post(url, json=payload, headers=headers)
            
            self.logger.info(f"レスポンスステータス: {response.status_code}")
            self.logger.info(f"レスポンス内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            creation_id = result.get("id")
            
            if not creation_id:
                self.logger.error("投稿IDの取得に失敗しました")
                return None
            
            # 3. スレッドの公開
            publish_url = f"{self.base_url}/{user_id}/threads_publish"
            publish_payload = {
                "creation_id": creation_id
            }
            
            # 少し待機（API制限対策）
            time.sleep(2)
            
            publish_response = requests.post(publish_url, json=publish_payload, headers=headers)
            publish_response.raise_for_status()
            publish_result = publish_response.json()
            
            self.logger.info(f"投稿成功: {publish_result}")
            return publish_result
        except Exception as e:
            self.logger.error(f"テキスト投稿エラー: {str(e)}")
            return None
    
    def create_reply_post(self, account, text, reply_to_id):
        """リプライ投稿を作成 (GASコードと同じパラメータ名)"""
        try:
            # 1. ユーザーIDを取得
            user_info = self.get_user_info()
            if not user_info or 'id' not in user_info:
                self.logger.error("ユーザーIDの取得に失敗しました")
                return None
            
            user_id = user_info['id']
            token = self.access_token
            
            # 2. リプライ投稿の作成 - GASコードと同じパラメータ名を使用
            url = f"{self.base_url}/{user_id}/threads"
            payload = {
                "text": text,
                "media_type": "TEXT",
                "reply_to_id": reply_to_id  # GASコードと同じパラメータ名
            }
            
            self.logger.info(f"リプライURL: {url}")
            self.logger.info(f"ユーザーID: {user_id}")
            self.logger.info(f"リプライ先ID: {reply_to_id}")
            self.logger.info(f"ペイロード: {payload}")
            
            headers = self.get_headers(token)
            response = requests.post(url, json=payload, headers=headers)
            
            self.logger.info(f"レスポンスステータス: {response.status_code}")
            self.logger.info(f"レスポンス内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            creation_id = result.get("id")
            
            if not creation_id:
                self.logger.error("リプライ投稿IDの取得に失敗しました")
                return None
            
            # 3. スレッドの公開
            publish_url = f"{self.base_url}/{user_id}/threads_publish"
            publish_payload = {
                "creation_id": creation_id
            }
            
            # 少し待機（API制限対策）
            time.sleep(2)
            
            publish_response = requests.post(publish_url, json=publish_payload, headers=headers)
            publish_response.raise_for_status()
            publish_result = publish_response.json()
            
            self.logger.info(f"リプライ投稿成功: {publish_result}")
            return publish_result
        except Exception as e:
            self.logger.error(f"リプライ投稿エラー: {str(e)}")
            return None
    
    def create_image_post(self, account, text, image_url):
        """画像付き投稿を作成"""
        try:
            # 1. ユーザーIDを取得
            user_info = self.get_user_info()
            if not user_info or 'id' not in user_info:
                self.logger.error("ユーザーIDの取得に失敗しました")
                return None
            
            user_id = user_info['id']
            token = self.access_token
            
            # 2. 画像付きスレッドの作成
            url = f"{self.base_url}/{user_id}/threads"
            payload = {
                "text": text,
                "image_url": image_url,
                "media_type": "IMAGE"
            }
            
            self.logger.info(f"画像投稿URL: {url}")
            self.logger.info(f"ユーザーID: {user_id}")
            self.logger.info(f"画像URL: {image_url}")
            self.logger.info(f"ペイロード: {payload}")
            
            headers = self.get_headers(token)
            response = requests.post(url, json=payload, headers=headers)
            
            self.logger.info(f"レスポンスステータス: {response.status_code}")
            self.logger.info(f"レスポンス内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            creation_id = result.get("id")
            
            if not creation_id:
                self.logger.error("投稿IDの取得に失敗しました")
                return None
            
            # 3. スレッドの公開
            publish_url = f"{self.base_url}/{user_id}/threads_publish"
            publish_payload = {
                "creation_id": creation_id
            }
            
            # 少し待機（API制限対策）
            time.sleep(2)
            
            publish_response = requests.post(publish_url, json=publish_payload, headers=headers)
            publish_response.raise_for_status()
            publish_result = publish_response.json()
            
            self.logger.info(f"画像投稿成功: {publish_result}")
            return publish_result
        except Exception as e:
            self.logger.error(f"画像投稿エラー: {str(e)}")
            return None
    
    def create_image_reply_post(self, account, text, image_url, reply_to_id):
        """画像付きリプライ投稿を作成"""
        try:
            # 1. ユーザーIDを取得
            user_info = self.get_user_info()
            if not user_info or 'id' not in user_info:
                self.logger.error("ユーザーIDの取得に失敗しました")
                return None
            
            user_id = user_info['id']
            token = self.access_token
            
            # 2. 画像付きリプライの作成 - GASコードと同じパラメータ名を使用
            url = f"{self.base_url}/{user_id}/threads"
            payload = {
                "text": text,
                "image_url": image_url,
                "media_type": "IMAGE",
                "reply_to_id": reply_to_id  # GASコードと同じパラメータ名
            }
            
            self.logger.info(f"画像リプライURL: {url}")
            self.logger.info(f"ユーザーID: {user_id}")
            self.logger.info(f"リプライ先ID: {reply_to_id}")
            self.logger.info(f"画像URL: {image_url}")
            self.logger.info(f"ペイロード: {payload}")
            
            headers = self.get_headers(token)
            response = requests.post(url, json=payload, headers=headers)
            
            self.logger.info(f"レスポンスステータス: {response.status_code}")
            self.logger.info(f"レスポンス内容: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            creation_id = result.get("id")
            
            if not creation_id:
                self.logger.error("画像リプライ投稿IDの取得に失敗しました")
                return None
            
            # 3. スレッドの公開
            publish_url = f"{self.base_url}/{user_id}/threads_publish"
            publish_payload = {
                "creation_id": creation_id
            }
            
            # 少し待機（API制限対策）
            time.sleep(2)
            
            publish_response = requests.post(publish_url, json=publish_payload, headers=headers)
            publish_response.raise_for_status()
            publish_result = publish_response.json()
            
            self.logger.info(f"画像リプライ投稿成功: {publish_result}")
            return publish_result
        except Exception as e:
            self.logger.error(f"画像リプライ投稿エラー: {str(e)}")
            return None
    
    def create_carousel_post(self, account, text, image_urls):
        """カルーセル投稿（複数画像）を作成"""
        try:
            # 画像URLが空の場合はテキスト投稿
            if not image_urls or len(image_urls) == 0:
                return self.create_text_post(account, text)
            
            # 単一画像の場合は通常の画像投稿
            if len(image_urls) == 1:
                return self.create_image_post(account, text, image_urls[0])
            
            # 複数画像の場合はマルチポスト方式で対応
            # 1. メイン投稿（1枚目の画像）
            result = self.create_image_post(account, text, image_urls[0])
            if not result or not result.get('id'):
                self.logger.error("メイン画像投稿に失敗しました")
                return None
                
            post_id = result.get('id')
            self.logger.info(f"カルーセルメイン投稿成功: {post_id}")
            
            # 2. 2枚目以降の画像をリプライとして投稿
            reply_posts = []
            for i, img_url in enumerate(image_urls[1:], 1):
                # 投稿間隔を少し空ける（API制限対策）
                time.sleep(3)
                
                # リプライ投稿テキスト（空でも可）
                reply_text = f"画像 {i+1}/{len(image_urls)}" if len(image_urls) > 2 else ""
                
                # 画像リプライ
                reply_result = self.create_image_reply_post(
                    account, reply_text, img_url, post_id
                )
                
                if reply_result and reply_result.get('id'):
                    reply_id = reply_result.get('id')
                    self.logger.info(f"カルーセル追加画像 {i+1} 投稿成功: {reply_id}")
                    reply_posts.append(reply_id)
                else:
                    self.logger.warning(f"{i+1}枚目の画像投稿に失敗しました")
            
            # 結果を返す（メイン投稿IDと追加画像の投稿ID）
            result = {
                "id": post_id,
                "reply_posts": reply_posts,
                "total_images": len(image_urls),
                "success": True
            }
            
            self.logger.info(f"カルーセル投稿完了: {len(image_urls)}枚")
            return result
            
        except Exception as e:
            self.logger.error(f"カルーセル投稿エラー: {str(e)}")
            return None
    
    def create_multi_image_post(self, account, text, image_urls):
        """複数画像投稿を作成（2枚画像問題の解決策）"""
        return self.create_carousel_post(account, text, image_urls)

# グローバルインスタンス作成
threads_api = ThreadsAPI()