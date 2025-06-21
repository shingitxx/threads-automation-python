"""
Threads Cloudinary管理システム
アカウントごとにCloudinaryリソースを管理
"""
import os
import json
import hashlib
import cloudinary
import cloudinary.uploader
import cloudinary.api
from datetime import datetime
from typing import Dict, List, Optional, Any

class ThreadsCloudinaryManager:
    """Threads Cloudinary管理クラス"""
    
    def __init__(self):
        """初期化"""
        # Cloudinary設定
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        
        self.base_dir = "accounts"
        self.cache_dir = os.path.join(self.base_dir, "_cache")
        
        # キャッシュディレクトリ作成
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def test_connection(self):
        """Cloudinary接続テスト"""
        try:
            result = cloudinary.api.ping()
            return True
        except Exception as e:
            print(f"❌ Cloudinary接続テストエラー: {str(e)}")
            return False
    
    def get_image_url(self, account_id, content_id, image_type="main", index=None):
        """画像URLを取得（キャッシュ優先、なければアップロード）"""
        # キャッシュから取得を試みる
        cache_key = self._generate_cache_key(account_id, content_id, image_type, index)
        cached_url = self._get_from_cache(cache_key)
        
        if cached_url:
            return {
                "success": True,
                "image_url": cached_url,
                "from_cache": True
            }
        
        # 画像ファイルのパスを取得
        image_path = self._get_image_path(account_id, content_id, image_type, index)
        if not image_path:
            return {
                "success": False,
                "error": "画像ファイルが見つかりません"
            }
        
        # Cloudinaryにアップロード
        try:
            upload_result = self._upload_to_cloudinary(image_path, account_id, content_id, image_type, index)
            
            if upload_result.get("success"):
                # キャッシュに保存
                self._save_to_cache(cache_key, upload_result.get("image_url"))
            
            return upload_result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_image_path(self, account_id, content_id, image_type="main", index=None):
        """画像ファイルのパスを取得"""
        content_dir = os.path.join(self.base_dir, account_id, "contents", content_id)
        
        if not os.path.exists(content_dir):
            return None
        
        # 画像ファイル名を生成
        if image_type == "main":
            filename_base = "image_main"
        elif image_type == "carousel" and index is not None:
            filename_base = f"image_{index}"
        else:
            return None
        
        # 拡張子の可能性をチェック
        for ext in ['.jpg', '.JPG', '.png', '.PNG']:
            filepath = os.path.join(content_dir, f"{filename_base}{ext}")
            if os.path.exists(filepath):
                return filepath
        
        return None
    
    def _upload_to_cloudinary(self, image_path, account_id, content_id, image_type="main", index=None):
        """Cloudinaryに画像をアップロード"""
        try:
            # アップロード先フォルダ (アカウントごとに分離)
            folder = f"threads/{account_id}"
            
            # 画像の識別子
            if image_type == "main":
                public_id = f"{content_id}"
            elif image_type == "carousel" and index is not None:
                public_id = f"{content_id}_{index}"
            else:
                public_id = f"{content_id}_{image_type}"
            
            # アップロード実行
            result = cloudinary.uploader.upload(
                image_path,
                folder=folder,
                public_id=public_id,
                overwrite=True
            )
            
            # 結果確認
            if result and "secure_url" in result:
                return {
                    "success": True,
                    "image_url": result["secure_url"],
                    "public_id": result["public_id"],
                    "version": result["version"]
                }
            else:
                return {
                    "success": False,
                    "error": "アップロード結果に画像URLが含まれていません"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_cache_key(self, account_id, content_id, image_type="main", index=None):
        """キャッシュキーを生成"""
        if image_type == "main":
            return f"{account_id}_{content_id}_main"
        elif image_type == "carousel" and index is not None:
            return f"{account_id}_{content_id}_carousel_{index}"
        else:
            return f"{account_id}_{content_id}_{image_type}"
    
    def _get_from_cache(self, cache_key):
        """キャッシュから取得"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                # キャッシュの有効期限チェック (3日間)
                if 'timestamp' in cache_data:
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    now = datetime.now()
                    
                    # 3日以内ならキャッシュ有効
                    if (now - cache_time).days < 3:
                        return cache_data.get('url')
            except Exception:
                pass
        
        return None
    
    def _save_to_cache(self, cache_key, url):
        """キャッシュに保存"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        cache_data = {
            'url': url,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ キャッシュ保存エラー: {str(e)}")
            return False
    
    def detect_carousel_images(self, account_id, content_id):
        """コンテンツのカルーセル画像を検出してURLを取得"""
        image_urls = []
        
        # メイン画像
        main_result = self.get_image_url(account_id, content_id, "main")
        if main_result and main_result.get("success"):
            image_urls.append(main_result.get("image_url"))
        else:
            # メイン画像がない場合は空リストを返す
            return image_urls
        
        # 追加画像を検索
        for i in range(1, 10):  # 最大9枚の追加画像
            add_result = self.get_image_url(account_id, content_id, "carousel", i)
            if add_result and add_result.get("success"):
                image_urls.append(add_result.get("image_url"))
            else:
                break  # 連続した画像でない場合は終了
        
        return image_urls
    
    def clear_cache(self, account_id=None, content_id=None):
        """キャッシュをクリア"""
        if account_id and content_id:
            # 特定のコンテンツのキャッシュをクリア
            prefix = f"{account_id}_{content_id}"
            deleted = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.startswith(prefix) and filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
                    deleted += 1
            
            return {
                "success": True,
                "deleted": deleted,
                "message": f"{account_id}/{content_id}のキャッシュをクリアしました"
            }
            
        elif account_id:
            # アカウント全体のキャッシュをクリア
            prefix = f"{account_id}_"
            deleted = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.startswith(prefix) and filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
                    deleted += 1
            
            return {
                "success": True,
                "deleted": deleted,
                "message": f"{account_id}のキャッシュをクリアしました"
            }
            
        else:
            # 全キャッシュをクリア
            deleted = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
                    deleted += 1
            
            return {
                "success": True,
                "deleted": deleted,
                "message": f"全キャッシュをクリアしました"
            }

# モジュールとしてインポートされた場合の動作確認
if __name__ == "__main__":
    # 環境変数設定（本番ではconfig/settings.pyで行う）
    os.environ['CLOUDINARY_CLOUD_NAME'] = 'duu2ybdru'
    os.environ['CLOUDINARY_API_KEY'] = '925683855735695'
    os.environ['CLOUDINARY_API_SECRET'] = 'e7qWzubCbY8iJI2C8b1UvFcTsQU'
    
    # テスト用コード
    manager = ThreadsCloudinaryManager()
    print("Cloudinary接続テスト:", manager.test_connection())