# image_posting_fix.py - 画像投稿システム修正版
import sys
import os
import time
import hashlib
import requests
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.append('.')

try:
    from config.settings import settings
    from src.core.threads_api import ThreadsAPI, Account, PostResult
    print("✅ 依存関係インポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)

# 環境変数読み込み
load_dotenv()

class FixedCloudinaryManager:
    """修正版Cloudinaryマネージャー"""
    
    def __init__(self):
        self.cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME', 'duu2ybdru')
        self.api_key = os.getenv('CLOUDINARY_API_KEY', '925683855735695')
        self.api_secret = os.getenv('CLOUDINARY_API_SECRET', 'e7qWzubCbY8iJI2C8b1UvFcTsQU')
        self.upload_url = f"https://api.cloudinary.com/v1_1/{self.cloud_name}/image/upload"
        
        print(f"☁️ Cloudinary設定:")
        print(f"  Cloud Name: {self.cloud_name}")
        print(f"  API Key: {self.api_key}")
        print(f"  Upload URL: {self.upload_url}")
    
    def generate_signature(self, params):
        """シグネチャ生成"""
        # パラメータを文字列に変換
        params_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature_string = f"{params_string}{self.api_secret}"
        signature = hashlib.sha1(signature_string.encode()).hexdigest()
        
        print(f"🔐 シグネチャ生成:")
        print(f"  Parameters: {params_string}")
        print(f"  Signature: {signature}")
        
        return signature
    
    def upload_image(self, image_path):
        """画像アップロード"""
        try:
            print(f"📤 画像アップロード開始: {image_path}")
            
            if not os.path.exists(image_path):
                return {"success": False, "error": f"画像ファイルが見つかりません: {image_path}"}
            
            # パラメータ準備
            timestamp = int(time.time())
            params = {
                "timestamp": timestamp
            }
            
            # シグネチャ生成
            signature = self.generate_signature(params)
            
            # リクエストデータ
            data = {
                "timestamp": timestamp,
                "signature": signature,
                "api_key": self.api_key
            }
            
            # ファイル準備
            with open(image_path, 'rb') as image_file:
                files = {
                    'file': (os.path.basename(image_path), image_file, 'image/jpeg')
                }
                
                print(f"📡 Cloudinaryにアップロード中...")
                response = requests.post(self.upload_url, data=data, files=files, timeout=60)
            
            print(f"📊 応答コード: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                image_url = response_data.get('secure_url')
                print(f"✅ アップロード成功: {image_url}")
                return {
                    "success": True,
                    "url": image_url,
                    "public_id": response_data.get('public_id')
                }
            else:
                error_msg = f"Cloudinaryアップロードエラー: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data}"
                except:
                    error_msg += f" - {response.text}"
                
                print(f"❌ アップロード失敗: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"画像アップロード例外: {e}"
            print(f"❌ 例外エラー: {error_msg}")
            return {"success": False, "error": error_msg}

class FixedImagePostingSystem:
    """修正版画像投稿システム"""
    
    def __init__(self):
        self.cloudinary = FixedCloudinaryManager()
        self.threads_api = ThreadsAPI()
        print("✅ 修正版画像投稿システム初期化完了")
    
    def create_single_image_post(self, account, text, image_path):
        """1枚画像投稿"""
        try:
            print(f"🖼️ 1枚画像投稿開始: {account.username}")
            
            # 画像アップロード
            upload_result = self.cloudinary.upload_image(image_path)
            if not upload_result["success"]:
                return PostResult(
                    success=False,
                    error=f"画像アップロードエラー: {upload_result['error']}"
                )
            
            image_url = upload_result["url"]
            print(f"🖼️ 画像URL取得: {image_url}")
            
            # Threads画像投稿
            post_result = self.threads_api.create_image_post(
                account=account,
                text=text,
                image_url=image_url
            )
            
            if post_result.success:
                print(f"✅ 画像投稿成功: {post_result.post_id}")
                return PostResult(
                    success=True,
                    post_id=post_result.post_id,
                    has_image=True,
                    image_url=image_url
                )
            else:
                return PostResult(
                    success=False,
                    error=f"Threads投稿エラー: {post_result.error}"
                )
                
        except Exception as e:
            return PostResult(
                success=False,
                error=f"画像投稿システムエラー: {e}"
            )
    
    def create_multi_image_post(self, account, text, image_paths):
        """2枚画像投稿"""
        try:
            print(f"🖼️🖼️ 2枚画像投稿開始: {account.username}")
            
            if len(image_paths) != 2:
                return PostResult(
                    success=False,
                    error="2枚画像投稿には正確に2つの画像が必要です"
                )
            
            # 1枚目の画像アップロード
            upload1_result = self.cloudinary.upload_image(image_paths[0])
            if not upload1_result["success"]:
                return PostResult(
                    success=False,
                    error=f"画像1アップロードエラー: {upload1_result['error']}"
                )
            
            # 2枚目の画像アップロード
            upload2_result = self.cloudinary.upload_image(image_paths[1])
            if not upload2_result["success"]:
                return PostResult(
                    success=False,
                    error=f"画像2アップロードエラー: {upload2_result['error']}"
                )
            
            image_urls = [upload1_result["url"], upload2_result["url"]]
            print(f"🖼️🖼️ 画像URL取得: {len(image_urls)}枚")
            
            # Threads複数画像投稿
            post_result = self.threads_api.create_multi_image_post(
                account=account,
                text=text,
                image_urls=image_urls
            )
            
            if post_result.success:
                print(f"✅ 2枚画像投稿成功: {post_result.post_id}")
                return PostResult(
                    success=True,
                    post_id=post_result.post_id,
                    has_image=True,
                    image_url=image_urls[0]  # 代表URL
                )
            else:
                return PostResult(
                    success=False,
                    error=f"Threads投稿エラー: {post_result.error}"
                )
                
        except Exception as e:
            return PostResult(
                success=False,
                error=f"2枚画像投稿システムエラー: {e}"
            )

def download_test_images():
    """テスト用画像ダウンロード"""
    import urllib.request
    
    image_urls = [
        "https://picsum.photos/800/600.jpg",
        "https://picsum.photos/600/800.jpg"
    ]
    
    downloaded_files = []
    
    for i, url in enumerate(image_urls, 1):
        filename = f"test_image_{i}.jpg"
        try:
            print(f"📥 画像{i}をダウンロード中: {url}")
            urllib.request.urlretrieve(url, filename)
            file_size = os.path.getsize(filename)
            print(f"✅ 画像{i}ダウンロード成功: {filename} ({file_size:,} bytes)")
            downloaded_files.append(filename)
        except Exception as e:
            print(f"❌ 画像{i}ダウンロード失敗: {e}")
    
    return downloaded_files

def main():
    """メインテスト実行"""
    print("🎯 修正版画像投稿システムテスト")
    print("=" * 60)
    
    # システム初期化
    image_system = FixedImagePostingSystem()
    
    # テスト用画像ダウンロード
    print("\n📥 テスト用画像ダウンロード中...")
    test_images = download_test_images()
    
    if len(test_images) < 2:
        print("❌ テスト画像のダウンロードに失敗しました")
        return
    
    # アカウント情報設定（実際のトークン必要）
    account = Account(
        id="ACCOUNT_011",
        username="kanae_15758",
        user_id="10068250716584647",
        access_token=os.getenv("TOKEN_ACCOUNT_011", "test_token")
    )
    
    print(f"\n👤 アカウント: {account.username}")
    print(f"🔑 トークン: {account.access_token[:20] if account.access_token else 'None'}...")
    
    # 1枚画像投稿テスト
    print("\n🖼️ === 1枚画像投稿テスト ===")
    proceed = input("🚀 1枚画像投稿をテストしますか？ (y/n): ")
    if proceed.lower() == 'y':
        result1 = image_system.create_single_image_post(
            account=account,
            text="修正版システムからの1枚画像投稿テスト 🖼️",
            image_path=test_images[0]
        )
        print(f"📊 1枚画像投稿結果:")
        print(f"  成功: {result1.success}")
        if result1.success:
            print(f"  投稿ID: {result1.post_id}")
            print(f"  画像URL: {result1.image_url}")
        else:
            print(f"  エラー: {result1.error}")
    
    # 2枚画像投稿テスト
    print("\n🖼️🖼️ === 2枚画像投稿テスト ===")
    proceed = input("🚀 2枚画像投稿をテストしますか？ (y/n): ")
    if proceed.lower() == 'y':
        result2 = image_system.create_multi_image_post(
            account=account,
            text="修正版システムからの2枚画像投稿テスト 🖼️🖼️",
            image_paths=test_images
        )
        print(f"📊 2枚画像投稿結果:")
        print(f"  成功: {result2.success}")
        if result2.success:
            print(f"  投稿ID: {result2.post_id}")
            print(f"  画像URL: {result2.image_url}")
        else:
            print(f"  エラー: {result2.error}")
    
    # ファイル削除
    print("\n🗑️ テスト用画像ファイル削除中...")
    for filename in test_images:
        try:
            os.remove(filename)
            print(f"🗑️ 削除: {filename}")
        except:
            pass
    
    print("\n✅ 修正版画像投稿システムテスト完了")

if __name__ == "__main__":
    main()