from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
import json
import random
import string
import requests
import re
from datetime import datetime
import os

class InstagramAutoCreator:
    def __init__(self, headless=False):
        # 設定
        self.headless = headless
        self.mail_account = None
        self.user_info = None
        
        # Chrome設定
        self.options = Options()
        self.options.add_argument("--lang=ja")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        if self.headless:
            self.options.add_argument("--headless")
            self.options.add_argument("--disable-gpu")
            
        self.driver = None
        self.wait = None
        
    def create_mail_account(self):
        """mail.tmアカウントを作成"""
        print("\n📧 メールアカウント作成中...")
        
        session = requests.Session()
        
        # ドメイン取得
        domains_response = session.get("https://api.mail.tm/domains")
        domains = domains_response.json()['hydra:member']
        domain = domains[0]['domain']
        
        # アカウント情報生成
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        email = f"{username}@{domain}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        
        # アカウント作成
        account_data = {
            "address": email,
            "password": password
        }
        
        create_response = session.post(
            "https://api.mail.tm/accounts",
            json=account_data
        )
        
        if create_response.status_code == 201:
            # トークン取得
            login_response = session.post(
                "https://api.mail.tm/token",
                json=account_data
            )
            
            if login_response.status_code == 200:
                token = login_response.json()['token']
                
                self.mail_account = {
                    "email": email,
                    "password": password,
                    "token": token,
                    "created_at": datetime.now().isoformat()
                }
                
                print(f"✅ メールアカウント作成成功: {email}")
                return True
                
        print("❌ メールアカウント作成失敗")
        return False
        
    def generate_user_info(self):
        """Instagram用ユーザー情報を生成"""
        username_base = ''.join(random.choices(string.ascii_lowercase, k=6))
        username = f"auto_{username_base}_{random.randint(100, 999)}"
        
        first_names = ["田中", "佐藤", "鈴木", "高橋", "渡辺", "伊藤", "山田", "中村"]
        last_names = ["太郎", "花子", "一郎", "美咲", "健太", "優子", "翔太", "愛"]
        fullname = random.choice(first_names) + " " + random.choice(last_names)
        
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + "!@#"
        
        # 誕生日（18-35歳）
        age = random.randint(18, 35)
        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        
        self.user_info = {
            "email": self.mail_account['email'],
            "fullname": fullname,
            "username": username,
            "password": password,
            "birth_year": birth_year,
            "birth_month": birth_month,
            "birth_day": birth_day
        }
        
        print(f"\n👤 ユーザー情報生成完了")
        print(f"   ユーザー名: {username}")
        print(f"   フルネーム: {fullname}")
        
    def start_browser(self):
        """ブラウザ起動"""
        print("\n🌐 ブラウザ起動中...")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
        print("✅ ブラウザ起動完了")
        
    def create_instagram_account(self):
        """Instagramアカウント作成のメインフロー"""
        try:
            # 1. サインアップページ
            print("\n📝 アカウント作成開始...")
            self.driver.get("https://www.instagram.com/accounts/emailsignup/")
            time.sleep(3)
            
            # 2. 基本情報入力
            self._fill_basic_info()
            
            # 3. 誕生日入力
            self._fill_birthday()
            
            # 4. 認証コード入力
            verification_code = self._get_verification_code()
            if verification_code:
                self._enter_verification_code(verification_code)
                
                # 5. 完了確認
                time.sleep(5)
                current_url = self.driver.current_url
                
                if "instagram.com" in current_url and "emailsignup" not in current_url:
                    print("\n🎉 アカウント作成成功！")
                    self._save_account_info()
                    return True
                    
        except Exception as e:
            print(f"\n❌ エラー発生: {e}")
            import traceback
            traceback.print_exc()
            
        return False
        
    def _fill_basic_info(self):
        """基本情報入力"""
        print("   基本情報入力中...")
        
        # メール
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "emailOrPhone"))
        )
        self._slow_type(email_input, self.user_info['email'])
        time.sleep(1)
        
        # フルネーム
        fullname_input = self.driver.find_element(By.NAME, "fullName")
        self._slow_type(fullname_input, self.user_info['fullname'])
        time.sleep(1)
        
        # ユーザー名
        username_input = self.driver.find_element(By.NAME, "username")
        self._slow_type(username_input, self.user_info['username'])
        time.sleep(1)
        
        # パスワード
        password_input = self.driver.find_element(By.NAME, "password")
        self._slow_type(password_input, self.user_info['password'])
        time.sleep(2)
        
        # 送信
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(3)
        
    def _fill_birthday(self):
        """誕生日入力"""
        print("   誕生日入力中...")
        
        try:
            # セレクトボックスを待機
            time.sleep(2)
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            
            if len(selects) >= 3:
                # 月
                Select(selects[0]).select_by_value(str(self.user_info['birth_month']))
                time.sleep(0.5)
                
                # 日
                Select(selects[1]).select_by_value(str(self.user_info['birth_day']))
                time.sleep(0.5)
                
                # 年
                Select(selects[2]).select_by_value(str(self.user_info['birth_year']))
                time.sleep(1)
                
                # 次へボタン
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    if "次へ" in button.text or "Next" in button.text:
                        button.click()
                        break
                        
                time.sleep(3)
                
        except Exception as e:
            print(f"   誕生日入力エラー: {e}")
            
    def _get_verification_code(self):
        """認証コードを取得"""
        print("\n📮 認証コード取得中...")
        
        headers = {"Authorization": f"Bearer {self.mail_account['token']}"}
        
        # 最大30回試行（5分間）
        for attempt in range(30):
            response = requests.get("https://api.mail.tm/messages", headers=headers)
            
            if response.status_code == 200:
                messages = response.json()
                
                if messages['hydra:totalItems'] > 0:
                    # 最新のメールから認証コードを探す
                    for msg in messages['hydra:member']:
                        if "instagram" in msg.get('subject', '').lower():
                            msg_id = msg.get('id')
                            msg_response = requests.get(
                                f"https://api.mail.tm/messages/{msg_id}",
                                headers=headers
                            )
                            
                            if msg_response.status_code == 200:
                                msg_text = msg_response.json().get('text', '')
                                codes = re.findall(r'\b\d{6}\b', msg_text)
                                
                                if codes:
                                    print(f"✅ 認証コード取得: {codes[0]}")
                                    return codes[0]
                                    
            print(f"   待機中... ({attempt + 1}/30)")
            time.sleep(10)
            
        print("❌ 認証コードを取得できませんでした")
        return None
        
    def _enter_verification_code(self, code):
        """認証コードを入力"""
        print(f"\n🔢 認証コード入力中: {code}")
        
        try:
            # 認証コード入力欄を探す
            code_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='confirmationCode'], input[type='number'], input[type='tel']")
            code_input.clear()
            self._slow_type(code_input, code)
            time.sleep(1)
            
            # 確認ボタンを探して押す
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                button_text = button.text.lower()
                if "次" in button_text or "確認" in button_text or "next" in button_text or "confirm" in button_text:
                    button.click()
                    print("✅ 認証コード送信")
                    break
                    
        except Exception as e:
            print(f"❌ 認証コード入力エラー: {e}")
            
    def _slow_type(self, element, text, delay=0.1):
        """人間のようにタイプ"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(delay + random.uniform(0, 0.05))
            
    def _save_account_info(self):
        """アカウント情報を保存"""
        account_data = {
            "instagram": self.user_info,
            "email": self.mail_account,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # アカウントIDを生成
        account_id = f"INSTAGRAM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 保存先ディレクトリ
        save_dir = f"instagram_accounts/accounts/{account_id}"
        os.makedirs(save_dir, exist_ok=True)
        
        # アカウント情報保存
        with open(f"{save_dir}/account_info.json", 'w', encoding='utf-8') as f:
            json.dump(account_data, f, ensure_ascii=False, indent=2)
            
        print(f"\n💾 アカウント情報保存完了: {account_id}")
        
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            time.sleep(10)
            self.driver.quit()

def main():
    """メイン実行関数"""
    print("=== Instagram 自動アカウント作成システム ===")
    
    creator = InstagramAutoCreator(headless=False)  # headless=Trueでバックグラウンド実行
    
    try:
        # 1. メールアカウント作成
        if not creator.create_mail_account():
            print("メールアカウント作成に失敗しました")
            return
            
        # 2. ユーザー情報生成
        creator.generate_user_info()
        
        # 3. ブラウザ起動
        creator.start_browser()
        
        # 4. Instagramアカウント作成
        if creator.create_instagram_account():
            print("\n✨ 全工程完了！")
        else:
            print("\n⚠️ アカウント作成に失敗しました")
            
    except Exception as e:
        print(f"\n❌ システムエラー: {e}")
        
    finally:
        creator.close()

if __name__ == "__main__":
    # 必要なディレクトリを作成
    os.makedirs("instagram_accounts/accounts", exist_ok=True)
    os.makedirs("instagram_accounts/logs", exist_ok=True)
    
    main()