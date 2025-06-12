import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
import uuid
from config.settings import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    logger
)

class CloudinaryUtil:
    """Cloudinaryとの連携を担当するクラス"""
    
    def __init__(self):
        # Cloudinary設定
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET
        )
    
    def upload_image(self, image_path, folder="threads-automation"):
        """画像をCloudinaryにアップロード"""
        try:
            if not os.path.exists(image_path):
                logger.error(f"画像ファイルが存在しません: {image_path}")
                return None
            
            # ユニークなファイル名を生成
            public_id = f"{folder}/{uuid.uuid4().hex}"
            
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
            public_id = f"{folder}/{uuid.uuid4().hex}"
            
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