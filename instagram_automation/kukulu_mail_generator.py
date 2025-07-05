# instagram_automation/kukulu_mail_generator.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import random
import string

class KukuluMailGenerator:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.email = None
        
    def setup_driver(self):
        """ブラウザの設定"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--lang=ja')
        options.add_argument('--start-maximized')
        
        # 検出回避設定
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if self.headless:
            options.add_argument('--headless')
            
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # 検出回避JavaScript
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def generate_email(self):
        """新しいメールアドレスを生成"""
        try:
            self.setup_driver()
            
            print("🔍 kuku.luページにアクセス中...")
            self.driver.get("https://m.kuku.lu/")
            time.sleep(2)
            
            # 「アドレスを自動作成して追加」ボタンを押す
            print("📧 メールアドレス生成ボタンを探しています...")
            add_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "link_addMailAddrByAuto"))
            )
            add_button.click()
            print("✅ アドレス生成ボタンをクリック")
            
            time.sleep(1)
            
            # 利用規約の「はい」ボタンを押す
            try:
                confirm_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "area-confirm-dialog-button-ok"))
                )
                confirm_button.click()
                print("✅ 利用規約に同意しました")
            except:
                print("ℹ️ 利用規約ダイアログは表示されませんでした")
            
            time.sleep(2)
            
            # メールアドレスを取得
            mail_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "text_newaddr"))
            )
            self.email = mail_input.get_attribute("value")
            
            if not self.email:
                # 別の方法で取得を試みる
                mail_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                for elem in mail_elements:
                    val = elem.get_attribute("value")
                    if val and "@" in val:
                        self.email = val
                        break
                        
            print(f"✅ メールアドレス取得完了: {self.email}")
            
            # メールアドレスページをキープ（認証コード確認用）
            return self.email
            
        except Exception as e:
            print(f"❌ メールアドレスの生成に失敗しました: {e}")
            if self.driver:
                self.driver.save_screenshot("kukulu_error.png")
            return None
            
    def check_verification_code(self, timeout=300):
        """認証コードをチェック"""
        if not self.driver or not self.email:
            print("❌ ブラウザまたはメールアドレスが設定されていません")
            return None
            
        print(f"📬 {self.email} の認証コードを待機中...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # ページをリフレッシュ
                self.driver.refresh()
                time.sleep(3)
                
                # メール一覧を確認
                mail_items = self.driver.find_elements(By.CSS_SELECTOR, ".mail-item, tr[onclick*='showMailData']")
                
                for item in mail_items:
                    try:
                        # メールをクリック
                        item.click()
                        time.sleep(2)
                        
                        # メール本文を取得
                        body_elements = self.driver.find_elements(By.CSS_SELECTOR, "#area-data, .mail-body, .content")
                        
                        for body_elem in body_elements:
                            text = body_elem.text
                            
                            # Instagramの認証コードパターンを検索
                            patterns = [
                                r'(\d{6})',  # 6桁の数字
                                r'認証コード[:：]\s*(\d{4,6})',
                                r'verification code[:：]\s*(\d{4,6})',
                                r'code[:：]\s*(\d{4,6})',
                            ]
                            
                            for pattern in patterns:
                                match = re.search(pattern, text, re.IGNORECASE)
                                if match:
                                    code = match.group(1)
                                    print(f"✅ 認証コード発見: {code}")
                                    return code
                                    
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"⚠️ メールチェック中にエラー: {e}")
                
            print(f"⏳ 認証コード待機中... ({int(time.time() - start_time)}秒経過)")
            time.sleep(10)
            
        print("❌ タイムアウト: 認証コードが見つかりませんでした")
        return None
        
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()
            
    def get_random_username(self):
        """ランダムなユーザー名を生成"""
        prefixes = ['user', 'insta', 'account', 'jp']
        prefix = random.choice(prefixes)
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{prefix}_{random_str}"