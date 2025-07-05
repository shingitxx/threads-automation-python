from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json
import random
import string
import requests

class InstagramSignupTest:
    def __init__(self):
        # mail.tmアカウント情報を読み込み
        with open('instagram_data/temp/test_account.json', 'r', encoding='utf-8') as f:
            self.mail_account = json.load(f)
        
        # Chrome設定
        self.options = Options()
        self.options.add_argument("--lang=ja")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = None
        self.wait = None
        
    def generate_user_info(self):
        """ユーザー情報を生成"""
        # ランダムなユーザー名を生成
        username_base = ''.join(random.choices(string.ascii_lowercase, k=6))
        username = f"test_{username_base}_{random.randint(100, 999)}"
        
        # フルネーム生成
        first_names = ["田中", "佐藤", "鈴木", "高橋", "渡辺"]
        last_names = ["太郎", "花子", "一郎", "美咲", "健太"]
        fullname = random.choice(first_names) + " " + random.choice(last_names)
        
        # パスワード生成（大文字、小文字、数字、記号を含む）
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + "!@"
        
        return {
            "email": self.mail_account['email'],
            "fullname": fullname,
            "username": username,
            "password": password
        }
    
    def start_browser(self):
        """ブラウザ起動"""
        print("ブラウザを起動中...")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
        
    def fill_signup_form(self, user_info):
        """サインアップフォームに入力"""
        print("\n=== Instagram サインアップ開始 ===")
        
        try:
            # サインアップページを開く
            print("1. サインアップページにアクセス中...")
            self.driver.get("https://www.instagram.com/accounts/emailsignup/")
            time.sleep(3)
            
            # メールアドレス入力
            print("\n2. フォームに入力中...")
            print(f"   メール: {user_info['email']}")
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "emailOrPhone"))
            )
            email_input.clear()
            self.slow_type(email_input, user_info['email'])
            time.sleep(1)
            
            # フルネーム入力
            print(f"   フルネーム: {user_info['fullname']}")
            fullname_input = self.driver.find_element(By.NAME, "fullName")
            fullname_input.clear()
            self.slow_type(fullname_input, user_info['fullname'])
            time.sleep(1)
            
            # ユーザー名入力
            print(f"   ユーザー名: {user_info['username']}")
            username_input = self.driver.find_element(By.NAME, "username")
            username_input.clear()
            self.slow_type(username_input, user_info['username'])
            time.sleep(1)
            
            # パスワード入力
            print(f"   パスワード: {'*' * len(user_info['password'])}")
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            self.slow_type(password_input, user_info['password'])
            time.sleep(2)
            
            # 送信ボタンの状態確認
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            print(f"\n3. 送信ボタンの状態: {'有効' if submit_button.is_enabled() else '無効'}")
            
            if submit_button.is_enabled():
                print("   ✅ ボタンが有効になりました！")
                
                # スクリーンショット保存
                self.driver.save_screenshot('instagram_data/temp/before_submit.png')
                print("   📸 スクリーンショット保存: before_submit.png")
                
                # ここで一時停止（手動確認用）
                input("\n⏸️  エンターキーを押すと送信します...")
                
                # 送信
                print("\n4. フォームを送信中...")
                submit_button.click()
                
                # 次のページを待機
                time.sleep(5)
                
                # 現在のURLを確認
                current_url = self.driver.current_url
                print(f"\n5. 現在のURL: {current_url}")
                
                # スクリーンショット保存
                self.driver.save_screenshot('instagram_data/temp/after_submit.png')
                print("   📸 スクリーンショット保存: after_submit.png")
                
                # 結果を保存
                result = {
                    "user_info": user_info,
                    "status": "submitted",
                    "final_url": current_url,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                with open('instagram_data/temp/signup_result.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print("\n✅ 結果を保存しました: signup_result.json")
                
            else:
                print("   ❌ ボタンがまだ無効です。入力内容を確認してください。")
                
        except Exception as e:
            print(f"\n❌ エラー発生: {e}")
            import traceback
            traceback.print_exc()
            
    def slow_type(self, element, text, delay=0.1):
        """人間のようにゆっくりタイプ"""
        for char in text:
            element.send_keys(char)
            time.sleep(delay + random.uniform(0, 0.1))
            
    def check_mail(self):
        """メールを確認"""
        print("\n6. メールを確認中...")
        headers = {
            "Authorization": f"Bearer {self.mail_account['token']}"
        }
        
        response = requests.get(
            "https://api.mail.tm/messages",
            headers=headers
        )
        
        if response.status_code == 200:
            messages = response.json()
            print(f"   メッセージ数: {messages['hydra:totalItems']}")
            
            if messages['hydra:totalItems'] > 0:
                for msg in messages['hydra:member']:
                    print(f"\n   件名: {msg.get('subject', 'なし')}")
                    print(f"   差出人: {msg.get('from', {}).get('address', 'なし')}")
        else:
            print(f"   ❌ メール確認失敗: {response.status_code}")
            
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            print("\n20秒後にブラウザを閉じます...")
            time.sleep(20)
            self.driver.quit()

if __name__ == "__main__":
    tester = InstagramSignupTest()
    
    try:
        # ユーザー情報生成
        user_info = tester.generate_user_info()
        
        print("=== 生成されたユーザー情報 ===")
        print(f"メール: {user_info['email']}")
        print(f"フルネーム: {user_info['fullname']}")
        print(f"ユーザー名: {user_info['username']}")
        print(f"パスワード: {'*' * len(user_info['password'])}")
        
        # ブラウザ起動
        tester.start_browser()
        
        # サインアップ実行
        tester.fill_signup_form(user_info)
        
        # メール確認
        tester.check_mail()
        
    finally:
        tester.close()