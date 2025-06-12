"""
画像投稿システム - Cloudinary連携（1-2枚対応）
GAS版を超える機能：1枚画像投稿 + 2枚画像投稿対応
"""

import os
import sys
import requests
import json
import time
import hashlib
import hmac
import base64
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.append('.')

try:
    from config.settings import settings
    from src.core.threads_api import ThreadsAPI, Account, PostResult
    print("✅ 依存関係インポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print("💡 プロジェクトルートから実行してください")

class CloudinaryManager:
    """Cloudinary画像アップロード管理クラス"""
    
    def __init__(self):
        self.cloud_name = settings.cloudinary.cloud_name
        self.api_key = settings.cloudinary.api_key
        self.api_secret = settings.cloudinary.api_secret
        self.base_url = f"https://api.cloudinary.com/v1_1/{self.cloud_name}"
        
    def generate_signature(self, params: Dict[str, Any]) -> str:
        """APIシグネチャを生成"""
        # パラメータをソートして文字列化
        sorted_params = sorted(params.items())
        params_string = "&".join([f"{k}={v}" for k, v in sorted_params if v])
        params_string += self.api_secret
        
        # SHA1ハッシュを生成
        signature = hashlib.sha1(params_string.encode('utf-8')).hexdigest()
        return signature
    
    def upload_image(self, image_source: Union[str, bytes], 
                    filename: Optional[str] = None) -> Dict[str, Any]:
        """
        画像をCloudinaryにアップロード
        
        Args:
            image_source: 画像ファイルパス、URL、またはバイナリデータ
            filename: ファイル名（オプション）
            
        Returns:
            Dict: アップロード結果
        """
        try:
            # アップロード用パラメータ
            timestamp = str(int(time.time()))
            params = {
                "timestamp": timestamp,
                "folder": "threads_posts",  # フォルダ指定
                "quality": "auto:good",     # 自動品質最適化
                "format": "jpg"             # 形式統一
            }
            
            # シグネチャ生成
            signature = self.generate_signature(params)
            
            # アップロード用データ
            upload_data = {
                **params,
                "api_key": self.api_key,
                "signature": signature
            }
            
            # ファイルの準備
            files = {}
            if isinstance(image_source, str):
                if image_source.startswith(('http://', 'https://')):
                    # URLの場合
                    upload_data["file"] = image_source
                else:
                    # ファイルパスの場合
                    if os.path.exists(image_source):
                        files["file"] = open(image_source, "rb")
                    else:
                        raise FileNotFoundError(f"画像ファイルが見つかりません: {image_source}")
            elif isinstance(image_source, bytes):
                # バイナリデータの場合
                files["file"] = ("image.jpg", image_source, "image/jpeg")
            else:
                raise ValueError("無効な画像ソース形式です")
            
            # Cloudinary APIへアップロード
            upload_url = f"{self.base_url}/image/upload"
            response = requests.post(upload_url, data=upload_data, files=files)
            
            # ファイルハンドルをクローズ
            if "file" in files and hasattr(files["file"], 'close'):
                files["file"].close()
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "public_id": result.get("public_id"),
                    "secure_url": result.get("secure_url"),
                    "url": result.get("url"),
                    "width": result.get("width"),
                    "height": result.get("height"),
                    "format": result.get("format"),
                    "bytes": result.get("bytes")
                }
            else:
                return {
                    "success": False,
                    "error": f"Cloudinaryアップロードエラー: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"画像アップロード例外エラー: {str(e)}"
            }

class ThreadsImagePostingSystem:
    """Threads画像投稿システム（1-2枚対応）"""
    
    def __init__(self):
        self.threads_api = ThreadsAPI()
        self.cloudinary = CloudinaryManager()
        self.test_mode = os.getenv("TEST_MODE", "False").lower() == "true"
        
    def create_single_image_post(self, account: Account, text: str, 
                               image_source: Union[str, bytes]) -> PostResult:
        """
        1枚画像付き投稿を作成
        
        Args:
            account: アカウント情報
            text: 投稿テキスト
            image_source: 画像ファイルパス、URL、またはバイナリデータ
            
        Returns:
            PostResult: 投稿結果
        """
        try:
            print(f"🖼️ 1枚画像投稿開始: {account.username}")
            
            if self.test_mode:
                print("🧪 テストモード: 実際のアップロード・投稿は行いません")
                return PostResult(
                    success=True,
                    post_id=f"TEST_IMG_POST_{int(time.time())}",
                    creation_id=f"TEST_CREATION_{int(time.time())}",
                    has_image=True,
                    image_url="https://test.cloudinary.com/test_image.jpg"
                )
            
            # 1. 画像をCloudinaryにアップロード
            print("📤 Cloudinaryに画像アップロード中...")
            upload_result = self.cloudinary.upload_image(image_source)
            
            if not upload_result["success"]:
                return PostResult(
                    success=False,
                    error=f"画像アップロードエラー: {upload_result['error']}"
                )
            
            image_url = upload_result["secure_url"]
            print(f"✅ 画像アップロード成功: {image_url}")
            
            # 2. Threads APIで画像付き投稿
            print("📱 Threads画像投稿実行中...")
            result = self.threads_api.create_image_post(
                account=account,
                text=text,
                image_url=image_url
            )
            
            if result.success:
                print(f"✅ 画像投稿成功: {result.post_id}")
                result.has_image = True
                result.image_url = image_url
            else:
                print(f"❌ 画像投稿失敗: {result.error}")
            
            return result
            
        except Exception as e:
            return PostResult(
                success=False,
                error=f"画像投稿例外エラー: {str(e)}"
            )
    
    def create_multi_image_post(self, account: Account, text: str, 
                              image_sources: List[Union[str, bytes]]) -> PostResult:
        """
        複数画像（2枚）付き投稿を作成
        
        Args:
            account: アカウント情報
            text: 投稿テキスト
            image_sources: 画像ファイルパス、URL、またはバイナリデータのリスト
            
        Returns:
            PostResult: 投稿結果
        """
        try:
            if len(image_sources) > 2:
                return PostResult(
                    success=False,
                    error="画像は最大2枚まで対応しています"
                )
            
            print(f"🖼️🖼️ {len(image_sources)}枚画像投稿開始: {account.username}")
            
            if self.test_mode:
                print("🧪 テストモード: 実際のアップロード・投稿は行いません")
                return PostResult(
                    success=True,
                    post_id=f"TEST_MULTI_IMG_POST_{int(time.time())}",
                    creation_id=f"TEST_MULTI_CREATION_{int(time.time())}",
                    has_image=True,
                    image_url="https://test.cloudinary.com/test_multi_image.jpg"
                )
            
            # 1. 全画像をCloudinaryにアップロード
            image_urls = []
            for i, image_source in enumerate(image_sources, 1):
                print(f"📤 画像{i}をCloudinaryにアップロード中...")
                upload_result = self.cloudinary.upload_image(image_source)
                
                if not upload_result["success"]:
                    return PostResult(
                        success=False,
                        error=f"画像{i}アップロードエラー: {upload_result['error']}"
                    )
                
                image_urls.append(upload_result["secure_url"])
                print(f"✅ 画像{i}アップロード成功: {upload_result['secure_url']}")
            
            # 2. Threads APIで複数画像投稿
            print("📱 Threads複数画像投稿実行中...")
            result = self.threads_api.create_multi_image_post(
                account=account,
                text=text,
                image_urls=image_urls
            )
            
            if result.success:
                print(f"✅ 複数画像投稿成功: {result.post_id}")
                result.has_image = True
                result.image_url = ", ".join(image_urls)
            else:
                print(f"❌ 複数画像投稿失敗: {result.error}")
            
            return result
            
        except Exception as e:
            return PostResult(
                success=False,
                error=f"複数画像投稿例外エラー: {str(e)}"
            )
    
    def create_image_tree_post(self, account: Account, main_text: str,
                             image_sources: Union[str, List[str]], 
                             reply_text: str) -> Dict[str, Any]:
        """
        画像付きツリー投稿を作成（メイン画像投稿 + テキストリプライ）
        
        Args:
            account: アカウント情報
            main_text: メイン投稿テキスト
            image_sources: 画像ソース（1枚または2枚）
            reply_text: リプライテキスト
            
        Returns:
            Dict: ツリー投稿結果
        """
        try:
            print(f"🌳🖼️ 画像付きツリー投稿開始: {account.username}")
            
            # 画像ソースをリスト形式に統一
            if isinstance(image_sources, str):
                image_sources = [image_sources]
            
            # メイン投稿（画像付き）
            if len(image_sources) == 1:
                main_result = self.create_single_image_post(
                    account=account,
                    text=main_text,
                    image_source=image_sources[0]
                )
            else:
                main_result = self.create_multi_image_post(
                    account=account,
                    text=main_text,
                    image_sources=image_sources
                )
            
            if not main_result.success:
                return {
                    "success": False,
                    "error": f"メイン画像投稿失敗: {main_result.error}"
                }
            
            print(f"✅ メイン画像投稿成功: {main_result.post_id}")
            
            # リプライ待機時間
            wait_time = 5
            print(f"⏸️ リプライ準備中（{wait_time}秒待機）...")
            if not self.test_mode:
                time.sleep(wait_time)
            
            # リプライ投稿（テキストのみ）
            print("💬 アフィリエイトリプライ投稿中...")
            reply_result = self.threads_api.create_reply_post(
                account=account,
                text=reply_text,
                reply_to_id=main_result.post_id
            )
            
            if reply_result.success:
                print(f"✅ リプライ投稿成功: {reply_result.post_id}")
                print(f"🎉 画像付きツリー投稿完了！")
                
                return {
                    "success": True,
                    "main_post_id": main_result.post_id,
                    "reply_post_id": reply_result.post_id,
                    "image_url": main_result.image_url,
                    "main_text": main_text,
                    "reply_text": reply_text
                }
            else:
                return {
                    "success": False,
                    "error": f"リプライ投稿失敗: {reply_result.error}",
                    "main_post_id": main_result.post_id  # メイン投稿は成功
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"画像付きツリー投稿例外エラー: {str(e)}"
            }

def test_image_posting_system():
    """画像投稿システムのテスト"""
    print("🧪 画像投稿システム テスト開始")
    print("=" * 50)
    
    try:
        # システム初期化
        image_system = ThreadsImagePostingSystem()
        print("✅ 画像投稿システム初期化完了")
        
        # Cloudinary設定確認
        print(f"☁️ Cloudinary設定:")
        print(f"  Cloud Name: {image_system.cloudinary.cloud_name}")
        print(f"  API Key: {image_system.cloudinary.api_key[:10]}...")
        print(f"  テストモード: {image_system.test_mode}")
        
        # テスト用アカウント
        test_account = Account(
            id="ACCOUNT_011",
            username="test_user",
            user_id="test_user_id",
            access_token="test_token"
        )
        
        print("\n🧪 1. 1枚画像投稿テスト")
        result1 = image_system.create_single_image_post(
            account=test_account,
            text="Python画像投稿システムからのテスト🖼️",
            image_source="https://example.com/test_image.jpg"
        )
        print(f"結果: {result1}")
        
        print("\n🧪 2. 2枚画像投稿テスト")
        result2 = image_system.create_multi_image_post(
            account=test_account,
            text="Python複数画像投稿システムからのテスト🖼️🖼️",
            image_sources=[
                "https://example.com/test_image1.jpg",
                "https://example.com/test_image2.jpg"
            ]
        )
        print(f"結果: {result2}")
        
        print("\n🧪 3. 画像付きツリー投稿テスト")
        result3 = image_system.create_image_tree_post(
            account=test_account,
            main_text="画像付きメイン投稿テスト🖼️",
            image_sources="https://example.com/test_main_image.jpg",
            reply_text="アフィリエイトリプライテスト💬\nhttps://example.com/affiliate"
        )
        print(f"結果: {result3}")
        
        print("\n✅ 画像投稿システムテスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")

if __name__ == "__main__":
    test_image_posting_system()