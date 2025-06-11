"""
Threads API基本実装
既存Google Apps Script版と完全互換の投稿機能
"""

import requests
import time
import json
from typing import Dict, Optional, Union, Any
from dataclasses import dataclass
from config.settings import settings

@dataclass
class PostResult:
    """投稿結果クラス"""
    success: bool
    post_id: Optional[str] = None
    creation_id: Optional[str] = None
    error: Optional[str] = None
    has_image: bool = False
    image_url: Optional[str] = None

@dataclass
class Account:
    """アカウント情報クラス"""
    id: str
    username: str
    user_id: str
    access_token: str
    app_id: str = None
    last_post_time: Optional[str] = None
    daily_post_count: int = 0
    status: str = "アクティブ"
    
    def __post_init__(self):
        if self.app_id is None:
            self.app_id = settings.threads.app_id

class ThreadsAPI:
    """Threads API操作クラス"""
    
    def __init__(self):
        self.base_url = settings.threads.api_base
        self.session = requests.Session()
        
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """API リクエストの共通処理"""
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def get_user_info(self, access_token: str, user_id: str) -> Dict[str, Any]:
        """
        ユーザー情報取得（既存GAS版のgetThreadsUserInfo互換）
        """
        url = f"{self.base_url}/{user_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"fields": "id,username,name,threads_profile_picture_url,threads_biography"}
        
        response = self._make_request("GET", url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "user_id": data.get("id"),
                "username": data.get("username"),
                "display_name": data.get("name", ""),
                "profile_picture_url": data.get("threads_profile_picture_url", ""),
                "biography": data.get("threads_biography", ""),
                "full_response": data
            }
        else:
            error_msg = f"API call failed: {response.status_code} - {response.text}"
            return {
                "success": False,
                "error": error_msg,
                "response_code": response.status_code
            }
    
    def create_text_post(self, account: Account, text: str) -> PostResult:
        """
        テキスト投稿作成（既存GAS版のexecuteTextOnlyPost互換）
        """
        url = f"{self.base_url}/{account.user_id}/threads"
        headers = {
            "Authorization": f"Bearer {account.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "media_type": "TEXT"
        }
        
        try:
            # 投稿作成
            response = self._make_request("POST", url, headers=headers, json=payload)
            
            if response.status_code != 200:
                return PostResult(
                    success=False,
                    error=f"Post creation failed: HTTP {response.status_code}: {response.text}"
                )
            
            result = response.json()
            creation_id = result.get("id")
            
            if not creation_id:
                return PostResult(
                    success=False,
                    error="No creation_id returned from API"
                )
            
            # 2秒待機（既存GAS版と同じ）
            time.sleep(2)
            
            # 投稿公開
            publish_result = self.publish_post(account, creation_id)
            
            if publish_result.success:
                return PostResult(
                    success=True,
                    post_id=publish_result.post_id,
                    creation_id=creation_id,
                    has_image=False
                )
            else:
                return PostResult(
                    success=False,
                    error=f"Publish failed: {publish_result.error}"
                )
                
        except Exception as e:
            return PostResult(
                success=False,
                error=f"Exception during text post: {str(e)}"
            )
    
    def create_reply_post(self, account: Account, text: str, reply_to_id: str, media_id: Optional[str] = None) -> PostResult:
        """
        リプライ投稿を作成
        
        Args:
            account: アカウント情報
            text: リプライテキスト
            reply_to_id: リプライ先の投稿ID
            media_id: メディアID（オプション）
        
        Returns:
            PostResult: 投稿結果
        """
        try:
            # リプライ投稿用のパラメータ
            data = {
                "media_type": "TEXT",
                "text": text,
                "reply_to_id": reply_to_id  # リプライ先指定
            }
            
            # メディアが指定されている場合
            if media_id:
                data["media_type"] = "IMAGE"
                data["image_url"] = media_id
            
            # Threads APIエンドポイント
            url = f"{self.base_url}/{account.user_id}/threads"
            headers = {
                "Authorization": f"Bearer {account.access_token}",
                "Content-Type": "application/json"
            }
            
            # 投稿作成リクエスト
            response = self._make_request("POST", url, headers=headers, json=data)
            
            if response.status_code == 200:
                result_data = response.json()
                creation_id = result_data.get("id")
                
                if creation_id:
                    # 2秒待機
                    time.sleep(2)
                    
                    # 投稿公開
                    publish_result = self.publish_post(account, creation_id)
                    
                    if publish_result.success:
                        return PostResult(
                            success=True,
                            post_id=publish_result.post_id,
                            creation_id=creation_id,
                            has_image=bool(media_id)
                        )
                    else:
                        return PostResult(
                            success=False,
                            error=f"リプライ公開失敗: {publish_result.error}",
                            creation_id=creation_id
                        )
                else:
                    return PostResult(
                        success=False,
                        error=f"リプライ作成失敗: creation_idが取得できませんでした",
                        creation_id=None
                    )
            else:
                error_msg = f"リプライ作成API失敗: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f" - {error_data['error'].get('message', '')}"
                except:
                    error_msg += f" - {response.text}"
                
                return PostResult(
                    success=False,
                    error=error_msg
                )
                
        except Exception as e:
            return PostResult(
                success=False,
                error=f"リプライ投稿例外エラー: {str(e)}"
            )
    
    def create_image_post(self, account: Account, text: str, image_url: str) -> PostResult:
        """
        画像投稿作成（既存GAS版のexecuteImagePostToThreads互換）
        """
        url = f"{self.base_url}/{account.user_id}/threads"
        headers = {
            "Authorization": f"Bearer {account.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "image_url": image_url,
            "media_type": "IMAGE"
        }
        
        try:
            # 投稿作成
            response = self._make_request("POST", url, headers=headers, json=payload)
            
            if response.status_code != 200:
                return PostResult(
                    success=False,
                    error=f"Image post creation failed: HTTP {response.status_code}: {response.text}"
                )
            
            result = response.json()
            creation_id = result.get("id")
            
            # 3秒待機（画像処理のため既存GAS版より長め）
            time.sleep(3)
            
            # 投稿公開
            publish_result = self.publish_post(account, creation_id)
            
            if publish_result.success:
                return PostResult(
                    success=True,
                    post_id=publish_result.post_id,
                    creation_id=creation_id,
                    has_image=True,
                    image_url=image_url
                )
            else:
                return PostResult(
                    success=False,
                    error=f"Publish failed: {publish_result.error}"
                )
                
        except Exception as e:
            return PostResult(
                success=False,
                error=f"Exception during image post: {str(e)}"
            )
    
    def create_reply(self, account: Account, text: str, parent_post_id: str) -> PostResult:
        """
        リプライ投稿作成（既存GAS版のexecuteThreadReplySimple互換）
        """
        url = f"{self.base_url}/{account.user_id}/threads"
        headers = {
            "Authorization": f"Bearer {account.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "media_type": "TEXT",
            "reply_to_id": parent_post_id
        }
        
        try:
            # リプライ作成
            response = self._make_request("POST", url, headers=headers, json=payload)
            
            if response.status_code != 200:
                return PostResult(
                    success=False,
                    error=f"Reply creation failed: HTTP {response.status_code}: {response.text}"
                )
            
            result = response.json()
            creation_id = result.get("id")
            
            # 2秒待機
            time.sleep(2)
            
            # リプライ公開
            publish_result = self.publish_post(account, creation_id)
            
            if publish_result.success:
                return PostResult(
                    success=True,
                    post_id=publish_result.post_id,
                    creation_id=creation_id,
                    has_image=False
                )
            else:
                return PostResult(
                    success=False,
                    error=f"Reply publish failed: {publish_result.error}"
                )
                
        except Exception as e:
            return PostResult(
                success=False,
                error=f"Exception during reply: {str(e)}"
            )
    
    def publish_post(self, account: Account, creation_id: str) -> PostResult:
        """
        投稿公開（既存GAS版のpublishPost互換）
        """
        url = f"{self.base_url}/{account.user_id}/threads_publish"
        headers = {
            "Authorization": f"Bearer {account.access_token}",
            "Content-Type": "application/json"
        }
        payload = {"creation_id": creation_id}
        
        try:
            response = self._make_request("POST", url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get("id")
                
                if post_id:
                    return PostResult(success=True, post_id=post_id)
                else:
                    return PostResult(success=False, error="No post_id returned from publish")
            else:
                return PostResult(
                    success=False,
                    error=f"Publish failed: HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return PostResult(
                success=False,
                error=f"Exception during publish: {str(e)}"
            )
    
    def test_connection(self, access_token: str, user_id: str) -> bool:
        """
        接続テスト（既存GAS版のtestAccountTokens互換）
        """
        try:
            result = self.get_user_info(access_token, user_id)
            return result.get("success", False)
        except Exception:
            return False

# グローバルAPIインスタンス
threads_api = ThreadsAPI()

if __name__ == "__main__":
    # API接続テスト
    print("🔧 Threads API基本テスト")
    
    # 設定確認
    print(f"✅ API Base URL: {threads_api.base_url}")
    print(f"✅ App ID: {settings.threads.app_id}")
    
    # アクセストークン確認
    tokens = settings.get_account_tokens()
    if tokens:
        print(f"✅ 設定済みアカウント: {list(tokens.keys())}")
        
        # 最初のアカウントで接続テスト
        first_account_id = list(tokens.keys())[0]
        first_token = tokens[first_account_id]
        
        # ダミーユーザーIDでテスト（実際の値は環境変数で設定）
        test_user_id = "test_user_id"
        
        print(f"🧪 {first_account_id} 接続テスト実行中...")
        # test_result = threads_api.test_connection(first_token, test_user_id)
        # print(f"📊 接続結果: {'✅ 成功' if test_result else '❌ 失敗'}")
        print("📝 実際のテストは .env ファイル設定後に実行可能")
        
    else:
        print("⚠️ アクセストークンが設定されていません")
        print("💡 .env ファイルを作成して TOKEN_ACC001 等を設定してください")
    
    print("✅ Threads API基本実装完了")