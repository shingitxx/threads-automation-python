"""
Threads自動投稿システム - Cloudinary画像処理モジュール
GAS版と同等の機能を提供するPython実装
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
import logging
import os
from pathlib import Path
from config.settings import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, logger, settings

class CloudinaryUtil:
    """Cloudinaryとの連携を担当するクラス"""
    
    def __init__(self):
        # Cloudinary設定
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )
    
    def upload_image(self, image_path, folder="threads-automation"):
        """画像をCloudinaryにアップロード"""
        try:
            if not os.path.exists(image_path):
                logger.error(f"画像ファイルが存在しません: {image_path}")
                return None

            # ユニークなファイル名を生成
            public_id = f"{folder}/{os.path.basename(image_path).split('.')[0]}"

            # アップロード実行
            result = cloudinary.uploader.upload(
                image_path,
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )

            # 画像URL取得
            image_url = result.get('secure_url')
            logger.info(f"画像アップロード成功: {image_url}")

            return image_url
        except Exception as e:
            logger.error(f"画像アップロードエラー: {str(e)}")
            return None
    
    def upload_image_url(self, image_url, folder="threads-automation"):
        """画像URLをCloudinaryにアップロード"""
        try:
            # ユニークなファイル名を生成
            from uuid import uuid4
            public_id = f"{folder}/{uuid4().hex}"

            # アップロード実行
            result = cloudinary.uploader.upload(
                image_url,
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )

            # 画像URL取得
            new_image_url = result.get('secure_url')
            logger.info(f"画像URLアップロード成功: {new_image_url}")

            return new_image_url
        except Exception as e:
            logger.error(f"画像URLアップロードエラー: {str(e)}")
            return None
    
    def get_image_from_content_id(self, content_id):
        """コンテンツIDに対応する画像をローカルから取得（GAS版互換）"""
        try:
            # 画像を保存しているディレクトリパス
            image_dir = Path("images")
            
            # 環境変数から画像ディレクトリを取得（設定されている場合）
            if hasattr(settings, 'data') and hasattr(settings.data, 'drive_folder_name'):
                image_dir = Path(settings.data.drive_folder_name)
            
            # サポートされている画像拡張子
            extensions = ["jpg", "jpeg", "png"]
            if hasattr(settings, 'data') and hasattr(settings.data, 'image_extensions'):
                extensions = settings.data.image_extensions
            
            logger.info(f"🔍 コンテンツID {content_id} の画像を {image_dir} から検索中...")
            
            # 各拡張子で画像を検索
            for ext in extensions:
                image_path = image_dir / f"{content_id}_image.{ext}"
                if image_path.exists():
                    logger.info(f"✅ 画像ファイル発見: {image_path}")
                    
                    # 画像ファイルの詳細情報を取得
                    file_size = image_path.stat().st_size / (1024 * 1024)  # サイズをMB単位で計算
                    
                    # 画像のMIMEタイプを拡張子から推測
                    mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
                    
                    return {
                        "path": str(image_path),
                        "content_id": content_id,
                        "extension": ext,
                        "mime_type": mime_type,
                        "size_mb": file_size
                    }
            
            logger.warning(f"⚠️ コンテンツID {content_id} に対応する画像が見つかりません")
            return None
        except Exception as e:
            logger.error(f"❌ 画像検索エラー: {str(e)}")
            return None
    
    def upload_to_cloudinary_with_content_id(self, image_path, content_id):
        """画像をCloudinaryにアップロード（コンテンツID指定版）"""
        try:
            if not os.path.exists(image_path):
                logger.error(f"画像ファイルが存在しません: {image_path}")
                return {"success": False, "error": "ファイルが存在しません"}
            
            # コンテンツIDを使用したパブリックID
            public_id = f"threads/{content_id}"
            
            # アップロード用のパラメータ
            upload_params = {
                "public_id": public_id,
                "overwrite": True,
                "resource_type": "image",
                "tags": ["threads", f"content_{content_id}"]
            }
            
            logger.info(f"☁️ Cloudinaryに画像をアップロード中: {image_path}")
            
            # アップロード実行
            result = cloudinary.uploader.upload(image_path, **upload_params)
            
            logger.info(f"✅ Cloudinaryアップロード成功: {result['secure_url']}")
            return {
                "success": True,
                "image_url": result["secure_url"],
                "public_id": result["public_id"],
                "content_id": content_id
            }
        except Exception as e:
            logger.error(f"❌ Cloudinaryアップロードエラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_cloudinary_image_url(self, content_id):
        """コンテンツIDから画像をCloudinaryにアップロードしてURLを取得（GAS版互換）"""
        try:
            if not content_id:
                logger.warning("⚠️ コンテンツIDが指定されていません")
                return None
            
            logger.info(f"🔄 コンテンツID {content_id} の画像処理を開始")
            
            # ステップ1: すでにCloudinaryに画像があるか確認
            try:
                public_id = f"threads/{content_id}"
                result = cloudinary.api.resource(public_id)
                logger.info(f"✅ Cloudinaryに既存画像を発見: {result['secure_url']}")
                return {
                    "success": True,
                    "image_url": result["secure_url"],
                    "public_id": result["public_id"],
                    "content_id": content_id,
                    "from_cache": True
                }
            except Exception as e:
                logger.info(f"Cloudinaryに既存画像なし: {str(e)}")
            
            # ステップ2: ローカルから画像を検索
            image_info = self.get_image_from_content_id(content_id)
            if not image_info:
                logger.warning(f"⚠️ コンテンツID {content_id} の画像が見つからないため、テキストのみで投稿します")
                return None
            
            # ステップ3: Cloudinaryにアップロード
            upload_result = self.upload_to_cloudinary_with_content_id(image_info["path"], content_id)
            if not upload_result["success"]:
                logger.error(f"❌ 画像アップロード失敗: {upload_result.get('error')}")
                return None
            
            # ステップ4: 結果を返す
            logger.info(f"🎉 画像処理完了: {upload_result['image_url']}")
            return upload_result
        except Exception as e:
            logger.error(f"❌ Cloudinary画像URL取得エラー: {str(e)}")
            return None
    
    def delete_cloudinary_image(self, public_id):
        """Cloudinaryから画像を削除"""
        try:
            if not public_id:
                logger.warning("⚠️ 削除対象のパブリックIDが指定されていません")
                return False
            
            # 画像削除を実行
            result = cloudinary.uploader.destroy(public_id)
            
            if result.get("result") == "ok":
                logger.info(f"✅ Cloudinary画像削除成功: {public_id}")
                return True
            else:
                logger.warning(f"⚠️ Cloudinary画像削除失敗: {result}")
                return False
        except Exception as e:
            logger.error(f"❌ Cloudinary画像削除エラー: {str(e)}")
            return False
    
    def search_cloudinary_images(self, prefix="threads/", max_results=100):
        """Cloudinaryから特定のプレフィックスを持つ画像を検索"""
        try:
            result = cloudinary.api.resources(prefix=prefix, max_results=max_results)
            resources = result.get("resources", [])
            logger.info(f"🔍 Cloudinary検索結果: {len(resources)}件")
            return resources
        except Exception as e:
            logger.error(f"❌ Cloudinary検索エラー: {str(e)}")
            return []
    
    def test_cloudinary_connection(self):
        """Cloudinaryへの接続テスト"""
        try:
            # pingでAPIアクセステスト
            result = cloudinary.api.ping()
            logger.info(f"✅ Cloudinary接続テスト成功: {result}")
            return True
        except Exception as e:
            logger.error(f"❌ Cloudinary接続テストエラー: {str(e)}")
            return False

# グローバルインスタンス作成
cloudinary_util = CloudinaryUtil()

# GAS版互換のグローバル関数（クラスを使わずに直接呼び出し可能）
def get_cloudinary_image_url(content_id):
    """コンテンツIDから画像URLを取得（GAS版互換グローバル関数）"""
    return cloudinary_util.get_cloudinary_image_url(content_id)

def test_cloudinary_connection():
    """Cloudinary接続テスト（グローバル関数）"""
    return cloudinary_util.test_cloudinary_connection()