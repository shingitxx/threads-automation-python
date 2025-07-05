# kukulu_mail_handler.py
import os
import time
import requests

KUKULU_API_KEY = os.getenv("KUKULU_API_KEY", "1c26e1b55408c22530c7f4e300af81ad")
HEADERS = {"Authorization": f"Bearer {KUKULU_API_KEY}"}
BASE_URL = "https://m.kuku.lu"

def create_mailbox():
    resp = requests.post(f"{BASE_URL}/mailbox/create", headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    return data["address"]

def list_messages(address):
    resp = requests.get(f"{BASE_URL}/mailbox/{address}/messages", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()  # メッセージ一覧（id, from, subject）

def get_message_detail(address, msg_id):
    resp = requests.get(f"{BASE_URL}/mailbox/{address}/messages/{msg_id}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()  # 本文や受信日時など

def wait_for_code(address, timeout=300, interval=5):
    start = time.time()
    while time.time() - start < timeout:
        msgs = list_messages(address)
        if msgs:
            msg = msgs[0]
            detail = get_message_detail(address, msg["id"])
            # 認証コード抽出の正規表現例
            import re
            m = re.search(r"認証コード[:：]\s*([0-9]{4,6})", detail.get("body", ""))
            if m:
                return m.group(1)
        time.sleep(interval)
    raise TimeoutError("認証コードが受信できませんでした。")

if __name__ == "__main__":
    addr = create_mailbox()
    print(f"📧 生成した kukulu メールアドレス: {addr}")
    try:
        code = wait_for_code(addr)
        print(f"✅ 認証コード取得しました: {code}")
    except TimeoutError as e:
        print(f"⚠️ {e}")
