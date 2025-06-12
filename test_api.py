# api_test.py
import os
import requests
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# トークンとユーザーIDを取得
token = os.getenv("THREADS_ACCESS_TOKEN")
user_id = os.getenv("INSTAGRAM_USER_ID")

# APIリクエスト
url = f"https://graph.facebook.com/v18.0/{user_id}/threads"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "text": "APIテスト投稿 - " + str(os.urandom(4).hex()),
    "access_token": token
}

print("APIリクエスト送信中...")
print(f"URL: {url}")
print(f"ユーザーID: {user_id}")
print(f"トークン: {token[:10]}...{token[-10:]}")

try:
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    result = response.json()
    print("レスポンス:", response.status_code)
    print("レスポンス内容:", result)
    print("投稿成功!" if "id" in result else "投稿失敗")
except Exception as e:
    print("エラー:", e)
    print("レスポンス:", response.text if 'response' in locals() else "なし")