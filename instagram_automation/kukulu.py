import requests
import re
from bs4 import BeautifulSoup

class KukuluError(Exception):
    pass

class Kukulu:
    def __init__(self, csrf_token=None, sessionhash=None):
        self.session = requests.Session()
        self.csrf_token = csrf_token
        self.sessionhash = sessionhash

    def new_account(self):
        url = "https://m.kuku.lu/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36"
        }

        res = self.session.get(url, headers=headers)

        print(f"[DEBUG] Status Code: {res.status_code}")  # ← 任意で削除OK
        print(f"[DEBUG] HTML Head: {res.text[:300]}")     # ← 任意で削除OK

        if res.status_code != 200:
            raise KukuluError("🌐 kukuluトップページの取得に失敗しました")

        csrf_match = re.search(r"name='csrf_token' value='(.+?)'", res.text)
        session_match = re.search(r"name='sessionhash' value='(.+?)'", res.text)

        if not csrf_match or not session_match:
            raise KukuluError("🔐 CSRFトークンまたはセッション情報の取得に失敗しました")

        csrf_token = csrf_match.group(1)
        sessionhash = session_match.group(1)

        return {
            "csrf_token": csrf_token,
            "sessionhash": sessionhash
        }

    def create_mailaddress(self):
        # kukuluではアカウント作成後の表示メールアドレスをそのまま使用する想定
        # 一時的に仮のメールアドレス（固定パターン）を使う場合はこちらを変更
        raise NotImplementedError("create_mailaddress() は環境依存のため未実装です")

    def check_top_mail(self, mail_addr):
        url = f"https://m.kuku.lu/mail.php?box={mail_addr}"
        headers = {
            "Referer": "https://m.kuku.lu/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36"
        }

        res = self.session.get(url, headers=headers)
        if res.status_code != 200:
            raise KukuluError("📡 kukuluメール一覧ページの取得に失敗しました")

        match = re.search(r"openMail\('(.+?)'\)", res.text)
        if not match:
            raise KukuluError("📭 受信メールはまだありません")

        mail_id = match.group(1)
        mail_url = f"https://m.kuku.lu/mail.open.php?id={mail_id}"
        mail_res = self.session.get(mail_url, headers=headers)

        if mail_res.status_code != 200:
            raise KukuluError("📨 メール詳細の取得に失敗しました")

        soup = BeautifulSoup(mail_res.text, "html.parser")
        subject = soup.find("h2").text.strip() if soup.find("h2") else "（件名不明）"
        text = soup.get_text()

        return {
            "subject": subject,
            "text": text
        }
