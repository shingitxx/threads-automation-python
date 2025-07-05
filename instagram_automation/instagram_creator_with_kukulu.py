# instagram_automation/instagram_creator_with_kukulu.py
import time
import random
import string
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from kukulu_mail_generator import KukuluMailGenerator


class InstagramCreatorWithKukulu:
    def __init__(self, use_proxy=False):
        self.use_proxy = use_proxy
        self.mail_generator = None
        self.driver = None
        self.account_info = {}
        
    def create_account(self):
        """Instagramアカウント作成のメインフロー"""
        try:
            # 1. メールアドレス生成
            print("\n📧 ステップ1: メールアドレス生成")
            self.mail_generator = KukuluMailGenerator(headless=False)
            email = self.mail_generator.generate_email()
            
            if not email:
                print("❌ メールアドレスの生成に失敗しました")
                return False
                
            self.account_info['email'] = email
            
            # 2. Instagramアカウント作成開始
            print("\n📱 ステップ2: Instagramアカウント作成")
            self.setup_instagram_driver()
            
            # 3. 基本情報入力
            if not self.fill_instagram_form(email):
                return False
                
            # 4. 認証コード処理
            print("\n🔐 ステップ3: 認証コード処理")
            code = self.mail_generator.check_verification_code(timeout=300)
            
            if code:
                if self.enter_verification_code(code):
                    print("✅ アカウント作成成功！")
                    self.save_account_info()
                    return True
                    
            return False
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            return False
            
        finally:
            # クリーンアップ
            if self.mail_generator:
                self.mail_generator.close()
            if self.driver:
                time.sleep(5)
                self.driver.quit()
                
    def setup_instagram_driver(self):
        """Instagram用のブラウザ設定"""
        options = webdriver.ChromeOptions()
        options.add_argument('--lang=ja')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent設定
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def fill_instagram_form(self, email):
        """Instagram登録フォームの入力"""
        try:
            # Instagramサインアップページへ
            self.driver.get("https://www.instagram.com/accounts/emailsignup/")
            time.sleep(3)
            
            # ユーザー情報生成
            username = self.mail_generator.get_random_username()
            password = self.generate_password()
            fullname = self.generate_japanese_name()
            
            self.account_info.update({
                'username': username,
                'password': password,
                'fullname': fullname
            })
            
            # フォーム入力
            print("📝 フォーム入力中...")
            
            # メールアドレス
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "emailOrPhone"))
            )
            self.slow_type(email_input, email)
            
            # フルネーム
            fullname_input = self.driver.find_element(By.NAME, "fullName")
            self.slow_type(fullname_input, fullname)
            
            # ユーザー名
            username_input = self.driver.find_element(By.NAME, "username")
            self.slow_type(username_input, username)
            
            # パスワード
            password_input = self.driver.find_element(By.NAME, "password")
            self.slow_type(password_input, password)
            
            # 登録ボタンクリック
            signup_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '登録') or contains(text(), 'Sign up')]")
            signup_button.click()
            
            print("✅ フォーム送信完了")
            time.sleep(5)
            
            # 誕生日入力（必要な場合）
            self.fill_birthday_if_needed()
            
            return True
            
        except Exception as e:
            print(f"❌ フォーム入力エラー: {e}")
            self.driver.save_screenshot("form_error.png")
            return False
            
    def enter_verification_code(self, code):
        """認証コードを入力"""
        try:
            print(f"🔢 認証コード入力: {code}")
            
            # 認証コード入力欄を探す
            code_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "confirmationCode"))
            )
            
            code_input.clear()
            self.slow_type(code_input, code)
            
            # 確認ボタンをクリック
            confirm_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '確認') or contains(text(), 'Confirm')]")
            confirm_button.click()
            
            time.sleep(5)
            
            # 成功確認
            if "welcome" in self.driver.current_url.lower() or "accounts/onetap" in self.driver.current_url:
                return True
                
            return False
            
        except Exception as e:
            print(f"❌ 認証コード入力エラー: {e}")
            return False
            
    def slow_type(self, element, text, delay=0.1):
        """人間らしい入力速度"""
        for char in text:
            element.send_keys(char)
            time.sleep(delay + random.uniform(0, 0.1))
            
    def generate_password(self):
        """強力なパスワード生成"""
        chars = string.ascii_letters + string.digits
        password = ''.join(random.choices(chars, k=10))
        return password + "!@#"
        
    def generate_japanese_name(self):
        """日本人の名前生成"""
        first_names = ["優希", "陽斗", "結衣", "蒼太", "芽衣", "陸", "さくら", "海斗"]
        last_names = ["田中", "鈴木", "高橋", "渡辺", "伊藤", "山本", "中村", "佐藤"]
        
        return random.choice(last_names) + " " + random.choice(first_names)
        
    def fill_birthday_if_needed(self):
        """誕生日入力（必要な場合）"""
        try:
            # 誕生日セレクトボックスを確認
            month_select = self.driver.find_elements(By.CSS_SELECTOR, "select[title*='月']")
            if month_select:
                print("📅 誕生日入力中...")
                # 実装省略（既存のコードを使用）
                pass
        except:
            pass
            
    def save_account_info(self):
        """アカウント情報を保存"""
        import json
        import os
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"instagram_account_{timestamp}.json"
        
        os.makedirs("accounts", exist_ok=True)
        filepath = os.path.join("accounts", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.account_info, f, ensure_ascii=False, indent=2)
            
        print(f"💾 アカウント情報を保存: {filepath}")