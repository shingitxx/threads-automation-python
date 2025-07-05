import requests
import json
from datetime import datetime

def test_mailtm_connection():
    """mail.tm APIの基本的な接続テスト"""
    
    print("=== mail.tm API接続テスト開始 ===")
    
    # 1. 利用可能なドメインを取得
    print("\n1. ドメイン一覧を取得中...")
    try:
        response = requests.get("https://api.mail.tm/domains")
        if response.status_code == 200:
            domains = response.json()
            print(f"✅ 取得成功！利用可能なドメイン数: {len(domains['hydra:member'])}")
            for domain in domains['hydra:member'][:3]:  # 最初の3つを表示
                print(f"   - {domain['domain']}")
        else:
            print(f"❌ エラー: ステータスコード {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False
    
    print("\n=== テスト完了 ===")
    return True

if __name__ == "__main__":
    test_mailtm_connection()