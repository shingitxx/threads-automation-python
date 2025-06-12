# cloudinary_debug_system.py - Cloudinary認証問題解決ツール
import os
import time
import hashlib
import base64
import hmac
import json
import requests
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

def debug_cloudinary_settings():
    """Cloudinary設定の詳細デバッグ"""
    print("🔧 Cloudinary設定詳細デバッグ")
    print("=" * 50)
    
    # 設定値取得
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    print(f"☁️ Cloud Name: {cloud_name}")
    print(f"🔑 API Key: {api_key}")
    print(f"🔐 API Secret: {api_secret[:10] if api_secret else 'None'}...")
    
    # 設定値チェック
    missing = []
    if not cloud_name:
        missing.append("CLOUDINARY_CLOUD_NAME")
    if not api_key:
        missing.append("CLOUDINARY_API_KEY")
    if not api_secret:
        missing.append("CLOUDINARY_API_SECRET")
    
    if missing:
        print(f"❌ 不足している設定: {', '.join(missing)}")
        return False
    
    print("✅ 基本設定: 全て正常")
    return True

def test_cloudinary_signature():
    """Cloudinaryシグネチャ生成テスト"""
    print("\n🔐 Cloudinaryシグネチャ生成テスト")
    print("=" * 50)
    
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    if not api_secret:
        print("❌ API Secretが設定されていません")
        return False
    
    # シグネチャ生成テスト
    timestamp = int(time.time())
    params_to_sign = f"timestamp={timestamp}"
    signature_string = f"{params_to_sign}{api_secret}"
    signature = hashlib.sha1(signature_string.encode()).hexdigest()
    
    print(f"⏰ Timestamp: {timestamp}")
    print(f"📝 Parameters: {params_to_sign}")
    print(f"🔗 Signature String: {signature_string[:50]}...")
    print(f"🔐 Generated Signature: {signature}")
    
    return True

def test_cloudinary_connection():
    """Cloudinary接続テスト"""
    print("\n🌐 Cloudinary接続テスト")
    print("=" * 50)
    
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        print("❌ Cloudinary設定が不完全です")
        return False
    
    # 最小限のリクエストテスト
    upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    
    # シグネチャ生成
    timestamp = int(time.time())
    params_to_sign = f"timestamp={timestamp}"
    signature = hashlib.sha1(f"{params_to_sign}{api_secret}".encode()).hexdigest()
    
    # リクエストデータ
    data = {
        'timestamp': timestamp,
        'signature': signature,
        'api_key': api_key
    }
    
    # 最小テスト画像データ（1x1 PNG）
    test_image_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAFAlh1A3wAAAABJRU5ErkJggg=="
    )
    
    files = {
        'file': ('test.png', test_image_data, 'image/png')
    }
    
    print(f"📤 Upload URL: {upload_url}")
    print(f"🔑 API Key: {api_key}")
    print(f"⏰ Timestamp: {timestamp}")
    print(f"🔐 Signature: {signature}")
    
    try:
        print("📡 接続テスト実行中...")
        response = requests.post(upload_url, data=data, files=files, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ アップロード成功!")
            print(f"🖼️ 画像URL: {response_data.get('secure_url', 'N/A')}")
            return True
        else:
            print(f"❌ アップロード失敗: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 エラー詳細: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📝 エラーレスポンス: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False

def fix_cloudinary_settings():
    """Cloudinary設定修正ガイド"""
    print("\n🔧 Cloudinary設定修正ガイド")
    print("=" * 50)
    
    print("1. .envファイルの確認:")
    print("   - CLOUDINARY_CLOUD_NAME=duu2ybdru")
    print("   - CLOUDINARY_API_KEY=925683855735695")
    print("   - CLOUDINARY_API_SECRET=e7qWzubCbY8iJI2C8b1UvFcTsQU")
    print()
    print("2. Cloudinary Dashboardでの確認:")
    print("   - https://cloudinary.com/console")
    print("   - Settings → API Keys")
    print("   - 正しいAPI KeyとAPI Secretを確認")
    print()
    print("3. 考えられる問題:")
    print("   - API Secretの有効期限切れ")
    print("   - アカウントの制限")
    print("   - ネットワークファイアウォール")
    print("   - API使用量制限")

def main():
    """メインデバッグ実行"""
    print("🔧 Cloudinary認証問題デバッグツール")
    print("=" * 60)
    
    # Step 1: 基本設定確認
    if not debug_cloudinary_settings():
        fix_cloudinary_settings()
        return
    
    # Step 2: シグネチャテスト
    test_cloudinary_signature()
    
    # Step 3: 接続テスト
    if test_cloudinary_connection():
        print("\n🎉 Cloudinary接続成功！画像投稿システムが使用可能です！")
    else:
        print("\n❌ Cloudinary接続失敗")
        fix_cloudinary_settings()

if __name__ == "__main__":
    main()