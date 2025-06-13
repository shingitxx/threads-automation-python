# cloudinary_test.py
import cloudinary
import cloudinary.uploader
from config.settings import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET
)

def test_cloudinary_connection():
    # Cloudinaryの設定
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )
    
    print(f"Cloudinary設定: {CLOUDINARY_CLOUD_NAME}")
    
    try:
        # 接続テスト
        result = cloudinary.api.ping()
        print(f"Cloudinary接続テスト結果: {result}")
        return True
    except Exception as e:
        print(f"Cloudinary接続エラー: {str(e)}")
        return False

if __name__ == "__main__":
    test_cloudinary_connection()