# test_kukulu_mail.py
import sys
import os
import re
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instagram_automation')))
from kukulu import Kukulu

def main():
    print("📩 kukulu捨てメアドを自動生成中...")
    kuk = Kukulu()
    account = kuk.new_account()
    kuk = Kukulu(account["csrf_token"], account["sessionhash"])

    mail_addr = kuk.create_mailaddress()
    print(f"✅ 作成したメールアドレス: {mail_addr}")

    print("📬 認証コードメールを受信待機中（最大5分）...")
    timeout = 300
    interval = 5
    start = time.time()

    while time.time() - start < timeout:
        mail = kuk.check_top_mail(mail_addr)
        if mail:
            print(f"[受信] 件名: {mail['subject']}")
            match = re.search(r"\b\d{4,6}\b", mail.get("text", ""))
            if match:
                print(f"✅ 認証コード取得: {match.group()}")
                return
        time.sleep(interval)

    print("❌ タイムアウト。認証コードメールが届きませんでした。")

if __name__ == "__main__":
    main()
