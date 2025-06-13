# cloudinary_search.py
import cloudinary
import cloudinary.api
from config.settings import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET
)

def setup_cloudinary():
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )

def search_image_by_content_id(content_id):
    setup_cloudinary()
    
    # Cloudinaryでの検索方法1: 完全一致でのpublic_id検索
    try:
        public_id = f"threads/{content_id}"
        result = cloudinary.api.resource(public_id)
        print(f"画像が見つかりました: {result.get('secure_url')}")
        return {
            "success": True,
            "image_url": result.get("secure_url"),
            "public_id": result.get("public_id")
        }
    except Exception as e:
        print(f"完全一致検索で画像が見つかりませんでした: {str(e)}")
    
    # Cloudinaryでの検索方法2: プレフィックス検索
    try:
        prefix = f"threads/{content_id}"
        result = cloudinary.api.resources(prefix=prefix, max_results=1)
        if result.get("resources") and len(result.get("resources")) > 0:
            image = result.get("resources")[0]
            print(f"プレフィックス検索で画像が見つかりました: {image.get('secure_url')}")
            return {
                "success": True,
                "image_url": image.get("secure_url"),
                "public_id": image.get("public_id")
            }
    except Exception as e:
        print(f"プレフィックス検索で画像が見つかりませんでした: {str(e)}")
    
    # 画像が見つからない場合
    print(f"コンテンツID {content_id} に対応する画像が見つかりませんでした")
    return {
        "success": False,
        "error": f"コンテンツID {content_id} に対応する画像が見つかりませんでした"
    }

if __name__ == "__main__":
    content_id = input("検索するコンテンツID（例: CONTENT_001）を入力してください: ")
    search_image_by_content_id(content_id)