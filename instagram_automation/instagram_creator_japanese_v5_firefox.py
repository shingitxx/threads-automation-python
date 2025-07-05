# instagram_automation/instagram_creator_japanese_v5_firefox.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import random
import string
import json
import os
from datetime import datetime
import requests
import re

class InstagramCreatorFirefox:
    def __init__(self, use_proxy=True):
        """Firefox版 - プロキシ対応 + mail.tm API"""
        self.use_proxy = use_proxy
        self.driver = None
        self.mail_account = None
        
        # アカウント番号を取得
        self.account_number = self.get_next_account_number()
        
        # アカウント情報
        self.account_data = {
            "account_number": self.account_number,
            "created_at": datetime.now().isoformat(),
            "browser": "Firefox"
        }
        
        # プロキシ設定
        if use_proxy:
            self.load_proxy()
    
    def get_next_account_number(self):
        """次のアカウント番号を取得"""
        accounts_dir = "instagram_accounts"
        if not os.path.exists(accounts_dir):
            os.makedirs(accounts_dir)
            return 1
            
        existing_files = [f for f in os.listdir(accounts_dir) if f.startswith("account_") and f.endswith(".json")]
        if not existing_files:
            return 1
            
        numbers = []
        for f in existing_files:
            try:
                num = int(f.replace("account_", "").replace(".json", ""))
                numbers.append(num)
            except:
                continue
                
        return max(numbers) + 1 if numbers else 1
    
    def load_proxy(self):
        """proxies.txtからプロキシを読み込む"""
        try:
            with open("proxies.txt", 'r', encoding='utf-8') as f:
                proxies = [line.strip() for line in f.readlines() if line.strip()]
            
            if proxies:
                # ランダムに選択
                selected = random.choice(proxies)
                self.account_data["proxy"] = selected
                print(f"✅ プロキシを選択: {selected[:50]}...")
            else:
                print("❌ proxies.txt が空です")
                self.use_proxy = False
                
        except FileNotFoundError:
            print("❌ proxies.txt が見つかりません")
            self.use_proxy = False
        except Exception as e:
            print(f"❌ エラー: {e}")
            self.use_proxy = False
    
    def create_mail_account(self):
        """mail.tmでメールアカウントを作成"""
        print("\n📧 メールアカウント作成中...")
        
        session = requests.Session()
        
        try:
            # ドメイン一覧を取得
            domains_response = session.get("https://api.mail.tm/domains")
            domains = domains_response.json()['hydra:member']
            
            if not domains:
                print("❌ 利用可能なドメインがありません")
                return False
            
            # ランダムにドメインを選択
            domain = random.choice(domains)['domain']
            
            # ランダムなメールアドレスを生成
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            email = f"{username}@{domain}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + "!@#"
            
            print(f"   メール: {email}")
            print(f"   ドメイン: {domain}")
            
            # アカウント作成
            account_data = {
                "address": email,
                "password": password
            }
            
            create_response = session.post(
                "https://api.mail.tm/accounts",
                json=account_data,
                headers={"Content-Type": "application/json"}
            )
            
            if create_response.status_code == 201:
                print("✅ メールアカウント作成成功")
                
                # ログインしてトークンを取得
                login_response = session.post(
                    "https://api.mail.tm/token",
                    json=account_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if login_response.status_code == 200:
                    token = login_response.json()['token']
                    
                    self.mail_account = {
                        "email": email,
                        "password": password,
                        "token": token,
                        "domain": domain,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # アカウント情報に保存
                    self.account_data["email"] = email
                    
                    print(f"✅ ログイン成功")
                    print(f"   トークン: {token[:20]}...")
                    return True
                else:
                    print(f"❌ ログイン失敗: {login_response.status_code}")
                    print(f"   レスポンス: {login_response.text}")
            else:
                print(f"❌ アカウント作成失敗: {create_response.status_code}")
                print(f"   レスポンス: {create_response.text}")
                
        except Exception as e:
            print(f"❌ メールアカウント作成エラー: {e}")
            import traceback
            traceback.print_exc()
            
        return False
    
    def generate_simple_credentials(self):
        """シンプルな認証情報生成"""
        # ユーザー名: ランダム8文字 + 4桁数字
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        username += str(random.randint(1000, 9999))
        
        # パスワード: 10文字 + 特殊文字
        password_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        special_chars = ['!', '@', '#', '$', '%', '^', '&', '*']
        password = password_chars[:2] + random.choice(special_chars) + password_chars[2:]
        
        # フルネーム（シンプルに）
        first_names = ["Yuki", "Hana", "Sora", "Kai", "Ren", "Mai", "Ryo", "Mio"]
        last_names = ["Tanaka", "Suzuki", "Sato", "Yamada", "Ito", "Watanabe", "Takahashi"]
        full_name = random.choice(first_names) + " " + random.choice(last_names)
        
        self.account_data["username"] = username
        self.account_data["password"] = password
        self.account_data["full_name"] = full_name
        
        print(f"\n📝 認証情報生成:")
        print(f"   ユーザー名: {username}")
        print(f"   パスワード: ***")
        print(f"   フルネーム: {full_name}")
        
        return True
    
    def start_browser(self):
        """Firefoxブラウザ起動（プロキシ認証は手動）"""
        print("\n🦊 Firefox起動中...")
        
        from selenium.webdriver.firefox.service import Service
        
        options = Options()
        
        # Firefoxの実行ファイルパス
        options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        
        # 基本設定
        options.set_preference("intl.accept_languages", "ja")
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        
        # プロキシ設定
        if self.use_proxy and "proxy" in self.account_data:
            proxy_line = self.account_data["proxy"]
            parts = proxy_line.split(':')
            
            if len(parts) >= 4:
                proxy_host = parts[0]
                proxy_port = int(parts[1])
                proxy_user = parts[2]
                proxy_pass = ':'.join(parts[3:])
                
                print(f"\n🔧 Firefoxプロキシ設定中...")
                
                # プロキシ設定
                options.set_preference("network.proxy.type", 1)
                options.set_preference("network.proxy.http", proxy_host)
                options.set_preference("network.proxy.http_port", proxy_port)
                options.set_preference("network.proxy.ssl", proxy_host)
                options.set_preference("network.proxy.ssl_port", proxy_port)
                options.set_preference("network.proxy.no_proxies_on", "")
                
                print("✅ プロキシ設定完了")
                
                # 認証情報を表示
                print("\n" + "="*60)
                print("📋 プロキシ認証情報（手動入力用）")
                print("="*60)
                print(f"ユーザー名: {proxy_user}")
                print(f"パスワード: {proxy_pass}")
                print("="*60)
                print("\n⚠️ プロキシ認証ダイアログが表示されたら上記を入力してください")
        
        try:
            service = Service(executable_path='./geckodriver.exe')
            self.driver = webdriver.Firefox(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Firefox起動完了")
            
            # 手動認証の待機
            if self.use_proxy:
                input("\n🔐 プロキシ認証を手動で完了したらEnterキーを押してください...")
                print("✅ プロキシ認証完了")
            
            return True
            
        except Exception as e:
            print(f"❌ Firefox起動エラー: {e}")
            return False
    
    def verify_proxy(self):
        """プロキシ動作確認（シンプル版）"""
        print("\n🔍 プロキシ動作確認中...")
        
        try:
            self.driver.get("https://httpbin.org/ip")
            time.sleep(3)
            
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            print(f"✅ プロキシIP確認: {body_text}")
            
            # IPアドレスを抽出
            import re
            ip_match = re.search(r'"origin":\s*"([^"]+)"', body_text)
            if ip_match:
                self.account_data["proxy_ip"] = ip_match.group(1)
                
        except Exception as e:
            print(f"⚠️ プロキシ確認エラー: {e}")
            # エラーでも続行
    
    def human_like_type(self, element, text):
        """人間らしいタイピング"""
        element.clear()
        time.sleep(random.uniform(0.5, 1))
        
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def get_verification_code(self):
        """mail.tmから認証コードを取得"""
        if not self.mail_account:
            return None
            
        print("\n📧 メールから認証コードを取得中...")
        headers = {"Authorization": f"Bearer {self.mail_account['token']}"}
        
        # 最大30回試行（5分間）
        for attempt in range(30):
            try:
                response = requests.get("https://api.mail.tm/messages", headers=headers)
                
                if response.status_code == 200:
                    messages = response.json()
                    
                    if messages['hydra:totalItems'] > 0:
                        print(f"   📬 メール数: {messages['hydra:totalItems']}")
                        
                        for msg in messages['hydra:member']:
                            subject = msg.get('subject', '')
                            from_addr = msg.get('from', {}).get('address', '')
                            
                            # Instagramからのメールを探す
                            if any(keyword in subject.lower() for keyword in ['instagram', 'verify', 'confirm', 'code', 'コード']):
                                print(f"   ✅ Instagramメール発見: {subject}")
                                
                                # メッセージの詳細を取得
                                msg_id = msg.get('id')
                                msg_response = requests.get(
                                    f"https://api.mail.tm/messages/{msg_id}",
                                    headers=headers
                                )
                                
                                if msg_response.status_code == 200:
                                    msg_detail = msg_response.json()
                                    
                                    # テキストとHTMLの両方をチェック
                                    text_content = msg_detail.get('text', '')
                                    html_content = msg_detail.get('html', [''])[0] if msg_detail.get('html') else ''
                                    
                                    # 6桁の数字を探す
                                    all_content = text_content + ' ' + html_content
                                    codes = re.findall(r'\b\d{6}\b', all_content)
                                    
                                    if codes:
                                        code = codes[0]
                                        print(f"   ✅ 認証コード発見: {code}")
                                        return code
                                    else:
                                        print("   ⚠️ このメールに認証コードが見つかりませんでした")
                
                print(f"   ⏳ 待機中... ({attempt + 1}/30)")
                time.sleep(10)
                
            except Exception as e:
                print(f"   ❌ メール確認エラー: {e}")
                time.sleep(10)
        
        print("   ❌ タイムアウト: 認証コードが見つかりませんでした")
        return None
    
    def create_account(self):
        """アカウント作成のメインプロセス（完成版）"""
        try:
            print("\n📝 Instagramアカウント作成開始...")
            
            # プロキシ確認
            if self.use_proxy:
                self.verify_proxy()
            
            # Instagram にアクセス（リトライ機能付き）
            print("\n📱 Instagramへアクセス中...")
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    time.sleep(random.uniform(2, 4))
                    self.driver.get("https://www.instagram.com/accounts/emailsignup/")
                    time.sleep(random.uniform(5, 8))
                    
                    # ページが正しく読み込まれたか確認
                    if "instagram" in self.driver.current_url.lower():
                        print("✅ Instagram接続成功")
                        break
                        
                except Exception as e:
                    if "proxyConnectFailure" in str(e):
                        print(f"⚠️ プロキシ接続エラー（試行 {attempt + 1}/{max_retries}）")
                        if attempt < max_retries - 1:
                            print("5秒後に再試行します...")
                            time.sleep(5)
                        else:
                            print("❌ プロキシ経由でInstagramに接続できません")
                            print("プロキシがHTTPSに対応しているか確認してください")
                            return False
                    else:
                        raise
            
            # 基本情報入力
            print("\n[STEP 1] 基本情報入力...")
            
            try:
                # メールアドレス
                email_input = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "emailOrPhone"))
                )
                self.human_like_type(email_input, self.account_data["email"])
                print(f"   ✅ メール: {self.account_data['email']}")
                
                # フルネーム
                fullname_input = self.driver.find_element(By.NAME, "fullName")
                self.human_like_type(fullname_input, self.account_data["full_name"])
                print(f"   ✅ 氏名: {self.account_data['full_name']}")
                
                # ユーザー名
                username_input = self.driver.find_element(By.NAME, "username")
                self.human_like_type(username_input, self.account_data["username"])
                print(f"   ✅ ユーザー名: {self.account_data['username']}")
                
                # パスワード
                password_input = self.driver.find_element(By.NAME, "password")
                self.human_like_type(password_input, self.account_data["password"])
                print(f"   ✅ パスワード: ***")
                
                time.sleep(2)
                
                # 登録ボタンクリック
                signup_success = False
                
                try:
                    signup_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                    if signup_button.is_enabled():
                        signup_button.click()
                        signup_success = True
                        print("   ✅ 登録ボタンクリック成功")
                except:
                    try:
                        signup_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                        self.driver.execute_script("arguments[0].click();", signup_button)
                        signup_success = True
                        print("   ✅ 登録ボタンクリック成功（JavaScript）")
                    except Exception as e:
                        print(f"   ❌ 登録ボタンクリックエラー: {e}")
                        return False
                
                print("✅ 基本情報送信完了")
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ 基本情報入力エラー: {e}")
                return False
            
            # 誕生日入力
            print("\n[STEP 2] 誕生日入力...")
            if not self.fill_birthday():
                return False
            
            # 認証コード処理
            print("\n[STEP 3] 認証コード処理...")
            
            # ページが完全に読み込まれるまで待機
            time.sleep(5)
            
            # メールから認証コードを自動取得
            verification_code = self.get_verification_code()
            
            if verification_code:
                print(f"\n✅ 認証コード自動取得成功: {verification_code}")
                
                # 認証コード入力
                try:
                    # 入力前に少し待機
                    time.sleep(3)
                    
                    # 6つの個別入力欄を確認（Instagram特有のパターン）
                    single_digit_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[maxlength='1']")
                    
                    if len(single_digit_inputs) == 6:
                        print("   📝 6つの個別入力欄を検出")
                        for i, digit in enumerate(verification_code):
                            single_digit_inputs[i].click()
                            single_digit_inputs[i].clear()
                            single_digit_inputs[i].send_keys(digit)
                            time.sleep(0.2)
                        print("   ✅ 認証コード入力完了（6桁個別）")
                        
                        # 送信
                        time.sleep(2)
                        # 最後の入力欄でEnterキーを押す
                        single_digit_inputs[-1].send_keys(Keys.RETURN)
                        
                    else:
                        # 通常の入力欄を探す（複数の方法）
                        print("   🔍 通常の入力欄を探しています...")
                        code_input = None
                        
                        # 方法1: name="confirmationCode"
                        try:
                            code_input = self.driver.find_element(By.NAME, "confirmationCode")
                            print("   ✅ 入力欄発見: name='confirmationCode'")
                        except:
                            pass
                        
                        # 方法2: name="email_confirmation_code"
                        if not code_input:
                            try:
                                code_input = self.driver.find_element(By.NAME, "email_confirmation_code")
                                print("   ✅ 入力欄発見: name='email_confirmation_code'")
                            except:
                                pass
                        
                        # 方法3: プレースホルダーやaria-labelで探す
                        if not code_input:
                            all_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='number'], input[type='tel']")
                            for inp in all_inputs:
                                if inp.is_displayed() and inp.is_enabled():
                                    placeholder = inp.get_attribute("placeholder") or ""
                                    aria_label = inp.get_attribute("aria-label") or ""
                                    name_attr = inp.get_attribute("name") or ""
                                    
                                    # 認証コード関連のキーワードをチェック
                                    keywords = ["code", "コード", "認証", "confirm", "確認", "verification"]
                                    if any(keyword in (placeholder + aria_label + name_attr).lower() for keyword in keywords):
                                        code_input = inp
                                        print(f"   ✅ 入力欄発見: placeholder/aria-label検索")
                                        break
                        
                        # 方法4: 表示されている最初の空の入力欄を使用
                        if not code_input:
                            visible_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input:not([type='hidden'])")
                            for inp in visible_inputs:
                                if inp.is_displayed() and inp.is_enabled() and not inp.get_attribute("value"):
                                    # パスワードやメールアドレス入力欄を除外
                                    input_type = inp.get_attribute("type") or ""
                                    name = inp.get_attribute("name") or ""
                                    if input_type not in ["password", "email"] and name not in ["password", "emailOrPhone", "fullName", "username"]:
                                        code_input = inp
                                        print("   ✅ 入力欄発見: 最初の空欄")
                                        break
                        
                        if code_input:
                            # スクリーンショット（デバッグ用）
                            self.driver.save_screenshot(f"before_code_input_{self.account_number}.png")
                            
                            # 入力欄をクリックしてフォーカス
                            code_input.click()
                            time.sleep(0.5)
                            
                            # クリアして入力
                            code_input.clear()
                            time.sleep(0.5)
                            
                            # 認証コードを入力
                            for digit in verification_code:
                                code_input.send_keys(digit)
                                time.sleep(0.1)
                            
                            print("   ✅ 認証コード入力完了")
                            time.sleep(1)
                            
                            # Enterキーで送信
                            code_input.send_keys(Keys.RETURN)
                            print("   ✅ 送信完了")
                        else:
                            print("   ❌ 認証コード入力欄が見つかりません")
                            # デバッグ用スクリーンショット
                            self.driver.save_screenshot(f"code_input_not_found_{self.account_number}.png")
                            
                            # 現在のページの入力欄情報を出力
                            print("\n   📋 デバッグ情報:")
                            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                            for i, inp in enumerate(all_inputs):
                                if inp.is_displayed():
                                    print(f"   Input {i}: type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, placeholder={inp.get_attribute('placeholder')}")
                    
                    # 結果を待つ
                    time.sleep(5)
                    
                    # 成功確認
                    current_url = self.driver.current_url.lower()
                    if "welcome" in current_url or "accounts/onetap" in current_url or "accounts/registered" in current_url:
                        self.account_data["status"] = "作成成功"
                        print("\n🎉 アカウント作成成功！")
                        return True
                    else:
                        # ページ内容を確認
                        page_source = self.driver.page_source.lower()
                        if self.account_data["username"].lower() in page_source:
                            # ユーザー名が表示されていれば成功の可能性
                            self.account_data["status"] = "作成成功（推定）"
                            print("\n🎉 アカウント作成成功（推定）！")
                            return True
                        
                except Exception as e:
                    print(f"❌ 認証コード入力エラー: {e}")
                    import traceback
                    traceback.print_exc()
                    
            # 認証コードが取得できなかった、または入力に失敗した場合
            print("\n" + "="*60)
            print("⚠️  認証コードを手動で入力してください")
            print("="*60)
            print(f"📧 メールアドレス: {self.account_data['email']}")
            print("📨 mail.tmでメールを確認してください")
            print("="*60)
            
            input("\n✅ 認証コードを入力したらEnterキーを押してください...")
            
            # 手動入力後の成功確認
            time.sleep(3)
            current_url = self.driver.current_url.lower()
            if "welcome" in current_url or "accounts/onetap" in current_url or "accounts/registered" in current_url:
                self.account_data["status"] = "作成成功（手動）"
                print("\n🎉 アカウント作成成功（手動）！")
                return True
            
            self.account_data["status"] = "作成失敗"
            print("❌ アカウント作成失敗")
            return False
                
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
            self.account_data["status"] = "エラー"
            self.account_data["error"] = str(e)
            import traceback
            traceback.print_exc()
            return False
    
    def fill_birthday(self):
        """誕生日入力（エラー詳細表示版）"""
        try:
            birth_year = random.randint(1990, 2005)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            
            print(f"   誕生日を入力中: {birth_year}年{birth_month}月{birth_day}日")
            
            # 月
            month_select = Select(self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[title*='月']"))
            ))
            month_select.select_by_value(str(birth_month))
            time.sleep(1)
            
            # 日
            day_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[title*='日']"))
            day_select.select_by_value(str(birth_day))
            time.sleep(1)
            
            # 年
            year_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[title*='年']"))
            year_select.select_by_value(str(birth_year))
            time.sleep(1)
            
            # 次へボタン
            next_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '次へ') or contains(text(), 'Next')]")
            next_button.click()
            
            print(f"✅ 誕生日入力完了: {birth_year}年{birth_month}月{birth_day}日")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ 誕生日入力エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_account(self):
        """アカウント情報を保存"""
        filename = f"instagram_accounts/account_{self.account_number:03d}.json"
        
        # 保存データを整形
        save_data = {
            "account_number": self.account_data.get("account_number"),
            "email": self.account_data.get("email"),
            "password": self.account_data.get("password"),
            "username": self.account_data.get("username"),
            "proxy": self.account_data.get("proxy", ""),
            "proxy_ip": self.account_data.get("proxy_ip", ""),
            "created_at": self.account_data.get("created_at"),
            "status": self.account_data.get("status", "不明"),
            "browser": "Firefox",
            "mail_account": self.mail_account if self.mail_account else None
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
            
        print(f"\n💾 保存完了: {filename}")
        
        # 成功情報を表示
        if save_data["status"] == "作成成功":
            print("\n" + "="*50)
            print("🎉 アカウント作成成功！")
            print("="*50)
            print(f"アカウント番号: {save_data['account_number']}")
            print(f"ユーザー名: {save_data['username']}")
            print(f"メール: {save_data['email']}")
            print(f"パスワード: {save_data['password']}")
            if save_data.get("proxy_ip"):
                print(f"使用IP: {save_data['proxy_ip']}")
            print("="*50)
    
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()

# メイン実行部分
def main():
    print("=== Instagram自動アカウント作成システム (Firefox版) ===")
    print("Firefox + プロキシ対応 + mail.tm API")
    
    # GeckoDriverの確認
    try:
        from selenium import webdriver
        test_driver = webdriver.Firefox()
        test_driver.quit()
        print("✅ GeckoDriver: 動作確認OK")
    except Exception as e:
        print("❌ GeckoDriverが見つかりません")
        print("geckodriver.exe がプロジェクトフォルダにあることを確認してください")
        return
    
    # プロキシ使用の確認（入力待ちを確実に）
    while True:
        proxy_input = input("\nプロキシを使用しますか？ (y/n): ").strip().lower()
        if proxy_input in ['y', 'n']:
            use_proxy = proxy_input == 'y'
            break
        else:
            print("❌ 'y' または 'n' を入力してください")
    
    if use_proxy:
        print("\n🌐 プロキシ: 有効")
    else:
        print("\n🌐 プロキシ: 無効（直接接続）")
    
    creator = InstagramCreatorFirefox(use_proxy=use_proxy)
    
    try:
        # メールアカウント作成
        if creator.create_mail_account():
            # 認証情報生成
            if creator.generate_simple_credentials():
                # ブラウザ起動
                if creator.start_browser():
                    # アカウント作成
                    if creator.create_account():
                        print("\n✅ プロセス完了")
                    else:
                        print("\n❌ アカウント作成失敗")
        else:
            print("\n❌ メールアカウント作成に失敗しました")
    
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # アカウント情報を保存
        creator.save_account()
        
        # ブラウザを閉じる
        creator.close()
        
    print("\n処理終了")

if __name__ == "__main__":
    main()