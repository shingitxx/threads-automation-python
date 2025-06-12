import requests
import json
import logging
import time
from dataclasses import dataclass
from typing import Optional
from config.settings import THREADS_API_BASE_URL, THREADS_ACCESS_TOKEN, INSTAGRAM_USER_ID, logger, settings

@dataclass
class Account:
    """アカウント情報（GAS版互換）"""
    id: str
    username: str
    user_id: str
    access_token: str
    app_id: str
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
            target_user_id = user_id or self.user_id
            
            url = f"{self.base_url}/{target_user_id}"
            params = {
                "fields": "id,username",
                "access_token": token
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"ユーザー情報取得エラー: {str(e)}")
            return None
    
    def test_connection(self, access_token, user_id):
        """アクセストークンと接続をテスト"""
        try:
            user_info = self.get_user_info(access_token, user_id)
            return user_info is not None and 'id' in user_info
        except Exception as e:
            self.logger.error(f"接続テストエラー: {str(e)}")
            return False
    
    def create_text_post(self, account, text):
        """テキスト投稿を作成"""
        try:
            # Accountオブジェクトか辞書形式に対応
            user_id = account.user_id if hasattr(account, 'user_id') else account['user_id']
            token = account.access_token if hasattr(account, 'access_token') else self.access_token
            
            url = f"{self.base_url}/{user_id}/threads"
            payload = {
                "text": text,
                "access_token": token
            }
            response = requests.post(url, json=payload, headers=self.get_headers(token))
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"投稿成功: ID={result.get('id')}")
            return result
        except Exception as e:
            self.logger.error(f"テキスト投稿エラー: {str(e)}")
            return None
    
    def create_reply_post(self, account, text, reply_to_id):
        """リプライ投稿を作成"""
        try:
            # Accountオブジェクトか辞書形式に対応
            user_id = account.user_id if hasattr(account, 'user_id') else account['user_id']
            token = account.access_token if hasattr(account, 'access_token') else self.access_token
            
            url = f"{self.base_url}/{user_id}/threads"
            payload = {
                "text": text,
                "reply_to_post_id": reply_to_id,
                "access_token": token
            }
            response = requests.post(url, json=payload, headers=self.get_headers(token))
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"リプライ投稿成功: ID={result.get('id')}")
            return result
        except Exception as e:
            self.logger.error(f"リプライ投稿エラー: {str(e)}")
            return None
    
    def create_image_post(self, account, text, image_url):
        """画像付き投稿を作成"""
        try:
            # Accountオブジェクトか辞書形式に対応
            user_id = account.user_id if hasattr(account, 'user_id') else account['user_id']
            token = account.access_token if hasattr(account, 'access_token') else self.access_token
            
            url = f"{self.base_url}/{user_id}/threads"
            payload = {
                "text": text,
                "image_url": image_url,
                "access_token": token
            }
            response = requests.post(url, json=payload, headers=self.get_headers(token))
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"画像投稿成功: ID={result.get('id')}")
            return result
        except Exception as e:
            self.logger.error(f"画像投稿エラー: {str(e)}")
            return None
    
    def create_image_reply_post(self, account, text, image_url, reply_to_id):
        """画像付きリプライ投稿を作成"""
        try:
            # Accountオブジェクトか辞書形式に対応
            user_id = account.user_id if hasattr(account, 'user_id') else account['user_id']
            token = account.access_token if hasattr(account, 'access_token') else self.access_token
            
            url = f"{self.base_url}/{user_id}/threads"
            payload = {
                "text": text,
                "image_url": image_url,
                "reply_to_post_id": reply_to_id,
                "access_token": token
            }
            response = requests.post(url, json=payload, headers=self.get_headers(token))
            response.raise_for_status()
            result = response.json()
            self.logger.info(f"画像リプライ投稿成功: ID={result.get('id')}")
            return result
        except Exception as e:
            self.logger.error(f"画像リプライ投稿エラー: {str(e)}")
            return None
    
    def create_multi_image_post(self, account, text, image_urls):
        """複数画像投稿を作成（2枚画像問題の解決策）"""
        if not image_urls or len(image_urls) == 0:
            return self.create_text_post(account, text)
            
        # 1枚目の画像でメイン投稿
        result = self.create_image_post(account, text, image_urls[0])
        if not result or not result.get('id'):
            self.logger.error("メイン画像投稿に失敗しました")
            return None
            
        post_id = result.get('id')
        
        # 2枚目以降の画像は画像リプライとして投稿
        if len(image_urls) > 1:
            for i, img_url in enumerate(image_urls[1:], 1):
                # 投稿間隔を少し空ける（API制限対策）
                time.sleep(1)
                
                # リプライ投稿テキスト（空でも可）
                reply_text = f"追加画像 {i}" if i > 0 else ""
                
                # 画像リプライ
                reply_result = self.create_image_reply_post(
                    account, reply_text, img_url, post_id
                )
                
                if not reply_result:
                    self.logger.warning(f"{i+1}枚目の画像投稿に失敗しました")
        
        return result

# グローバルインスタンス作成
threads_api = ThreadsAPI()