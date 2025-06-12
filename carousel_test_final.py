"""
最終版カルーセル投稿テスト
修正版threads_api.pyを使用
"""

import os
import sys
import requests
import time
import hashlib
import hmac
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.append('src')
from core.threads_api import ThreadsAPI

# 設定読み込み
load_dotenv()

class CloudinaryUploader:
    """Cloudinary画像アップロード"""
    
    def __init__(self):
        self.cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        self.api_key = os.getenv("CLOUDINARY_API_KEY")
        self.api_secret = os.getenv("CLOUDINARY_API_SECRET")
        self.upload_url = f"https://api.cloudinary.com/v1_1/{self.cloud_name}/image/upload"
        
        print(f"☁️ Cloudinary設定:")
        print(f"  Cloud Name: {self.cloud_name}")
        print(f"  API Key: {self.api_key}")
    
    def upload_image(self, image_path):
        """画像をCloudinaryにアップロード"""
        try:
            timestamp = int(time.time())
            params = f"timestamp={timestamp}"
            signature = hmac.new(
                self.api_secret.encode(),
                params.encode(),
                hashlib.sha1
            ).hexdigest()
            
            print(f"📤 画像アップロード開始: {image_path}")
            print(f"🔐 シグネチャ生成: {signature[:10]}...")
            
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'timestamp': timestamp,
                    'signature': signature,
                    'api_key': self.api_key
                }
                
                response = requests.post(self.upload_url, files=files, data=data)
                print(f"📊 応答コード: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    secure_url = result['secure_url']
                    print(f"✅ アップロード成功: {secure_url}")
                    return secure_url
                else:
                    raise Exception(f"アップロード失敗: {response.status_code}: {response.text}")
                    
        except Exception as e:
            print(f"❌ 画像アップロードエラー: {str(e)}")
            raise

def download_test_images():
    """テスト用画像をダウンロード"""
    print("📥 テスト用画像ダウンロード中...")
    
    image_urls = [
        "https://picsum.photos/800/600.jpg",
        "https://picsum.photos/600/800.jpg"
    ]
    
    local_images = []
    for i, url in enumerate(image_urls):
        filename = f"test_image_{i+1}.jpg"
        print(f"📥 画像{i+1}をダウンロード中: {url}")
        
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        file_size = len(response.content)
        local_images.append(filename)
        print(f"✅ 画像{i+1}ダウンロード成功: {filename} ({file_size:,} bytes)")
    
    return local_images

def test_carousel_posting():
    """カルーセル投稿テスト"""
    
    print("🎯 最終版カルーセル投稿テスト")
    print("=" * 60)
    
    try:
        # 環境変数確認
        if not all([
            os.getenv("THREADS_USER_ID"),
            os.getenv("THREADS_ACCESS_TOKEN"),
            os.getenv("CLOUDINARY_CLOUD_NAME"),
            os.getenv("CLOUDINARY_API_KEY"),
            os.getenv("CLOUDINARY_API_SECRET")
        ]):
            raise Exception("必要な環境変数が設定されていません")
        
        print("✅ 環境変数確認完了")
        
        # アカウント情報
        account = {
            "name": "kanae_15758",
            "user_id": os.getenv("THREADS_USER_ID"),
            "access_token": os.getenv("THREADS_ACCESS_TOKEN")
        }
        
        print(f"👤 アカウント: {account['name']}")
        print(f"🔑 ユーザーID: {account['user_id']}")
        
        # テスト画像ダウンロード
        local_images = download_test_images()
        
        # Cloudinaryアップロード
        uploader = CloudinaryUploader()
        uploaded_urls = []
        
        print("\n📤 Cloudinaryアップロード開始...")
        for image_path in local_images:
            url = uploader.upload_image(image_path)
            uploaded_urls.append(url)
            time.sleep(1)  # API制限回避
        
        print(f"\n✅ {len(uploaded_urls)}枚の画像アップロード完了")
        for i, url in enumerate(uploaded_urls):
            print(f"  画像{i+1}: {url}")
        
        # カルーセル投稿テスト
        print("\n🎠 カルーセル投稿テスト開始...")
        
        api = ThreadsAPI()
        
        # テスト実行確認
        confirm_carousel = input("\n🚀 カルーセル投稿をテストしますか？ (y/n): ")
        
        if confirm_carousel.lower() == 'y':
            print("\n🎠 カルーセル投稿実行中...")
            
            result = api.create_carousel_post(
                account=account,
                text="🔧 最終版システムからのカルーセル投稿テスト 🎠✨\n\n2枚の画像が1つの投稿内でスライド表示される予定です！",
                image_urls=uploaded_urls
            )
            
            print("\n📊 カルーセル投稿結果:")
            print("=" * 40)
            
            if result.success:
                print(f"✅ 成功: True")
                print(f"📝 投稿ID: {result.post_id}")
                print(f"🎠 カルーセルID: {result.carousel_id}")
                print(f"📸 子要素ID: {result.children_ids}")
                print(f"\n🔗 投稿URL: https://www.threads.net/@kanae_15758/post/{result.post_id}")
                print("\n🎉 カルーセル投稿成功！Threadsアプリで確認してください！")
            else:
                print(f"❌ 失敗: {result.error}")
                
                # 代替手段テスト
                print("\n🔄 代替手段（画像+リプライ）をテストしますか？")
                confirm_alternative = input("(y/n): ")
                
                if confirm_alternative.lower() == 'y':
                    print("\n📸 代替手段実行中...")
                    
                    alt_result = api.create_image_with_reply_post(
                        account=account,
                        text="🔧 代替手段テスト: メイン画像 + リプライ画像",
                        image_urls=uploaded_urls
                    )
                    
                    print("\n📊 代替手段結果:")
                    if alt_result.success:
                        print(f"✅ 成功: True")
                        print(f"📝 メイン投稿ID: {alt_result.post_id}")
                        print(f"🖼️ メイン画像: {alt_result.image_url}")
                    else:
                        print(f"❌ 失敗: {alt_result.error}")
        else:
            print("⏭️ カルーセル投稿テストをスキップしました")
    
    except Exception as e:
        print(f"❌ テスト実行エラー: {str(e)}")
    
    finally:
        # クリーンアップ
        print("\n🗑️ テスト用画像ファイル削除中...")
        for image_path in local_images:
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"🗑️ 削除: {image_path}")
        
        print("\n✅ 最終版カルーセル投稿テスト完了")

if __name__ == "__main__":
    test_carousel_posting()