import requests
import time
import random
import string
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

class SecMail:
    def __init__(self):
        self.login = self._generate_username()
        self.domain = "1secmail.com"
        self.email = f"{self.login}@{self.domain}"

    def _generate_username(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

    def get_email_address(self):
        return self.email

    def get_verification_code(self, max_tries=30, interval=10):
        print(f"[INFO] Waiting for verification code at: {self.email}")
        for i in range(max_tries):
            try:
                url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={self.login}&domain={self.domain}"
                response = requests.get(url, headers=HEADERS)
                text = response.text.strip()
                if not text:
                    print(f"[WARN] Empty response (try {i+1}/{max_tries})")
                    time.sleep(interval)
                    continue
                try:
                    messages = response.json()
                except ValueError:
                    print(f"[ERROR] Invalid JSON: {text[:100]}")
                    time.sleep(interval)
                    continue

                if messages:
                    message_id = messages[0]['id']
                    msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={self.login}&domain={self.domain}&id={message_id}"
                    msg_response = requests.get(msg_url, headers=HEADERS).json()
                    body = msg_response.get("body", "")
                    code = self._extract_code(body)
                    if code:
                        print(f"[SUCCESS] Code received: {code}")
                        return code
            except Exception as e:
                print(f"[ERROR] Failed to fetch email: {e}")
            time.sleep(interval)
        print("[FAIL] Verification code not received in time.")
        return None

    def _extract_code(self, text):
        match = re.search(r'\b(\d{6})\b', text)
        return match.group(1) if match else None
