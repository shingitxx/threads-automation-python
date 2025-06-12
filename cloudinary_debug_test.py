"""
Cloudinary詳細デバッグテスト
"""

import requests
import hashlib
import time
import sys
import os

sys.path.append('.')

from config.settings import settings

def test_cloudinary_credentials():
    """Cloudinary認証情報詳細テスト"""
    print("🔧 Cloudinary詳細デバッグ")
    print("=" * 50)
    
    # 設定確認
    cloud_name = settings.cloudinary.cloud_name
    api_key = settings.cloudinary.api_key
    api_secret = settings.cloudinary.api_secret
    
    print(f"☁️ Cloud Name: {cloud_name}")
    print(f"🔑 API Key: {api_key}")
    print(f"🔐 API Secret: {api_secret}")
    
    # 基本的なURL構築テスト
    upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    print(f"🌐 Upload URL: {upload_url}")
    
    # タイムスタンプとシグネチャ生成
    timestamp = str(int(time.time()))
    params = {
        "timestamp": timestamp
    }
    
    # シグネチャ生成プロセス詳細表示
    print(f"\n🔧 シグネチャ生成プロセス:")
    print(f"⏰ Timestamp: {timestamp}")
    
    sorted_params = sorted(params.items())
    params_string = "&".join([f"{k}={v}" for k, v in sorted_params if v])
    print(f"📝 Params string: '{params_string}'")
    
    signature_string = params_string + api_secret
    print(f"🔗 Signature string: '{signature_string}'")
    
    signature = hashlib.sha1(signature_string.encode('utf-8')).hexdigest()
    print(f"🔐 Generated signature: {signature}")
    
    # 最小限のテストアップロード
    upload_data = {
        "timestamp": timestamp,
        "api_key": api_key,
        "signature": signature,
        "file": "https://httpbin.org/image/jpeg"
    }
    
    print(f"\n📡 最小限のアップロードテスト実行中...")
    try:
        response = requests.post(upload_url, data=upload_data, timeout=30)
        print(f"📊 応答コード: {response.status_code}")
        print(f"📄 応答ヘッダー: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ アップロード成功!")
            print(f"🖼️ 画像URL: {result.get('secure_url')}")
        else:
            print(f"❌ アップロード失敗")
            print(f"📄 エラーレスポンス: {response.text}")
            
            # エラー詳細分析
            if response.status_code == 401:
                print("\n💡 401エラー分析:")
                print("- API Keyが間違っている可能性")
                print("- API Secretが間違っている可能性") 
                print("- シグネチャ生成に問題がある可能性")
            elif response.status_code == 400:
                print("\n💡 400エラー分析:")
                print("- パラメータが不正な可能性")
                print("- ファイルURLが無効な可能性")
                
    except Exception as e:
        print(f"❌ リクエストエラー: {e}")

if __name__ == "__main__":
    test_cloudinary_credentials()