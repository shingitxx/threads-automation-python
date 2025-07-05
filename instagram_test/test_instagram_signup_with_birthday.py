from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import json
import random
import string
import requests
from datetime import datetime, timedelta

class InstagramSignupComplete:
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
        """ユーザー情報を生成（誕生日含む）"""
        # 前回と同じユーザー情報生成
        username_base = ''.join(random.choices(string.ascii_lowercase, k=6))
        username = f"test_{username_base}_{random.randint(100, 999)}"
        
        first_names = ["田中", "佐藤", "鈴木", "高橋", "渡辺"]
        last_names = ["太郎", "花子", "一郎", "美咲", "健太"]
        fullname = random.choice(first_names) + " " + random.choice(last_names)
        
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + "!@"
        
        # 誕生日生成（18-35歳のランダム）
        today = datetime.now()
        age = random.randint(18, 35)
        birth_year = today.year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # 簡単のため28日まで
        
        return {
            "email": self.mail_account['email'],
            "fullname": fullname,
            "username": username,
            "password": password,
            "birth_year": birth_year,
            "birth_month": birth_month,
            "birth_day": birth_day
        }
    
    def start_browser(self):
        """ブラウザ起動"""
        print("ブラウザを起動中...")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
        
    def fill_signup_form(self, user_info):
        """サインアップフォームに入力（誕生日対応版）"""
        print("\n=== Instagram サインアップ開始 ===")
        
        try:
            # サインアップページを開く
            print("1. サインアップページにアクセス中...")
            self.driver.get("https://www.instagram.com/accounts/emailsignup/")
            time.sleep(3)
            
            # 基本情報入力（前回と同じ）
            print("\n2. 基本情報を入力中...")
            
            # メールアドレス
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "emailOrPhone"))
            )
            self.slow_type(email_input, user_info['email'])
            time.sleep(1)
            
            # フルネーム
            fullname_input = self.driver.find_element(By.NAME, "fullName")
            self.slow_type(fullname_input, user_info['fullname'])
            time.sleep(1)
            
            # ユーザー名
            username_input = self.driver.find_element(By.NAME, "username")
            self.slow_type(username_input, user_info['username'])
            time.sleep(1)
            
            # パスワード
            password_input = self.driver.find_element(By.NAME, "password")
            self.slow_type(password_input, user_info['password'])
            time.sleep(2)
            
            # 送信ボタンをクリック
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            if submit_button.is_enabled():
                print("3. フォームを送信中...")
                submit_button.click()
                time.sleep(3)
                
                # 誕生日入力画面を待機
                print("\n4. 誕生日入力画面を確認中...")
                
                # 誕生日セレクトボックスを探す
                try:
                    # 月のセレクトボックス
                    month_selects = self.driver.find_elements(By.TAG_NAME, "select")
                    
                    if len(month_selects) >= 3:
                        print(f"   誕生日を入力中: {user_info['birth_year']}年{user_info['birth_month']}月{user_info['birth_day']}日")
                        
                        # 月を選択（通常は最初のselect）
                        month_select = Select(month_selects[0])
                        month_select.select_by_value(str(user_info['birth_month']))
                        time.sleep(0.5)
                        
                        # 日を選択（通常は2番目のselect）
                        day_select = Select(month_selects[1])
                        day_select.select_by_value(str(user_info['birth_day']))
                        time.sleep(0.5)
                        
                        # 年を選択（通常は3番目のselect）
                        year_select = Select(month_selects[2])
                        year_select.select_by_value(str(user_info['birth_year']))
                        time.sleep(1)
                        
                        print("   ✅ 誕生日入力完了")
                        
                        # 次へボタンを探す
                        next_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in next_buttons:
                            button_text = button.text
                            if "次へ" in button_text or "Next" in button_text:
                                print("\n5. 次へボタンをクリック...")
                                self.driver.save_screenshot('instagram_data/temp/before_birthday_submit.png')
                                button.click()
                                break
                        
                        # 認証コード入力画面を待機
                        time.sleep(5)
                        
                        # 現在のページを確認
                        current_url = self.driver.current_url
                        print(f"\n6. 現在のページ: {current_url}")
                        self.driver.save_screenshot('instagram_data/temp/after_birthday.png')
                        
                        # 認証コード入力欄を探す
                        self.check_for_verification_code()
                        
                    else:
                        print("   ❌ 誕生日のセレクトボックスが見つかりません")
                        
                except Exception as e:
                    print(f"   誤生日入力でエラー: {e}")
                    
        except Exception as e:
            print(f"\n❌ エラー発生: {e}")
            import traceback
            traceback.print_exc()
            
    def check_for_verification_code(self):
        """認証コード入力画面の確認"""
        print("\n7. 認証コード入力画面を確認中...")
        
        try:
            # 認証コード入力欄を探す（一般的なパターン）
            code_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='number'], input[type='tel']")
            
            if code_inputs:
                print(f"   入力欄が{len(code_inputs)}個見つかりました")
                
                # メールを確認
                self.check_mail_for_code()
                
                # 画面の状態を保存
                self.driver.save_screenshot('instagram_data/temp/verification_page.png')
                print("   📸 認証画面のスクリーンショット保存: verification_page.png")
                
        except Exception as e:
            print(f"   認証コード確認でエラー: {e}")
    
    def check_mail_for_code(self):
        """メールから認証コードを取得"""
        print("\n8. メールを確認中...")
        
        max_attempts = 10
        for attempt in range(max_attempts):
            headers = {
                "Authorization": f"Bearer {self.mail_account['token']}"
            }
            
            response = requests.get(
                "https://api.mail.tm/messages",
                headers=headers
            )
            
            if response.status_code == 200:
                messages = response.json()
                
                if messages['hydra:totalItems'] > 0:
                    print(f"   ✅ メール受信！({messages['hydra:totalItems']}件)")
                    
                    # 最新のメールを確認
                    for msg in messages['hydra:member']:
                        print(f"\n   件名: {msg.get('subject', 'なし')}")
                        print(f"   差出人: {msg.get('from', {}).get('address', 'なし')}")
                        
                        # メールの詳細を取得
                        msg_id = msg.get('id')
                        if msg_id:
                            msg_response = requests.get(
                                f"https://api.mail.tm/messages/{msg_id}",
                                headers=headers
                            )
                            
                            if msg_response.status_code == 200:
                                msg_detail = msg_response.json()
                                msg_text = msg_detail.get('text', '')
                                
                                # 認証コードを探す（6桁の数字）
                                import re
                                codes = re.findall(r'\b\d{6}\b', msg_text)
                                
                                if codes:
                                    print(f"\n   🔑 認証コード発見: {codes[0]}")
                                    return codes[0]
                    
                    break
                else:
                    print(f"   まだメールが届いていません... (試行 {attempt + 1}/{max_attempts})")
                    time.sleep(10)  # 10秒待機
            else:
                print(f"   ❌ メール確認失敗: {response.status_code}")
                break
                
        return None
            
    def slow_type(self, element, text, delay=0.1):
        """人間のようにゆっくりタイプ"""
        for char in text:
            element.send_keys(char)
            time.sleep(delay + random.uniform(0, 0.1))
            
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            input("\n⏸️  エンターキーを押すとブラウザを閉じます...")
            self.driver.quit()

if __name__ == "__main__":
    tester = InstagramSignupComplete()
    
    try:
        # ユーザー情報生成
        user_info = tester.generate_user_info()
        
        print("=== 生成されたユーザー情報 ===")
        print(f"メール: {user_info['email']}")
        print(f"フルネーム: {user_info['fullname']}")
        print(f"ユーザー名: {user_info['username']}")
        print(f"パスワード: {'*' * len(user_info['password'])}")
        print(f"誕生日: {user_info['birth_year']}年{user_info['birth_month']}月{user_info['birth_day']}日")
        
        # ブラウザ起動
        tester.start_browser()
        
        # サインアップ実行
        tester.fill_signup_form(user_info)
        
        # ユーザー情報を保存
        with open('instagram_data/temp/instagram_account.json', 'w', encoding='utf-8') as f:
            json.dump(user_info, f, ensure_ascii=False, indent=2)
        
    finally:
        tester.close()