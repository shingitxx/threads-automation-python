from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import random
import string
import requests
import re
from datetime import datetime
import os
import zipfile
import shutil

class InstagramCreatorJapaneseV2:
    def __init__(self, use_proxy=False, sms_api_key=None, captcha_api_key=None):
        """
        統合版：既存のコードにSMS認証とCAPTCHA対応を追加
        """
        self.use_proxy = use_proxy
        self.sms_api_key = sms_api_key or "d7549f9386e4dc5349dAde541f83df6c"
        self.captcha_api_key = captcha_api_key or "6c900aee84f21e9923a34d1432022e2a"
        self.mail_account = None
        self.user_info = None
        self.proxy_session = None
        self.used_sessions = []
        self.phone_number = None
        self.activation_id = None
        
        # Chrome設定（日本語版）
        self.options = Options()
        self.options.add_argument("--lang=ja")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agentをランダム化
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        self.options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        # プロキシ設定
        if self.use_proxy:
            self.setup_proxy()
        else:
            print("🌐 プロキシなしで実行します")
            
        self.driver = None
        self.wait = None
    
    def create_proxy_extension(self, proxy_host, proxy_port, proxy_user, proxy_pass):
        """プロキシ認証用のChrome拡張機能を作成"""
        extension_dir = "proxy_auth_extension"
        
        # 既存のディレクトリを削除
        if os.path.exists(extension_dir):
            shutil.rmtree(extension_dir)
        
        os.makedirs(extension_dir)
        
        # manifest.json
        manifest = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy Auth",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version": "22.0.0"
        }
        
        # background.js
        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: parseInt({proxy_port})
                }},
                bypassList: ["localhost"]
            }}
        }};

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_user}",
                    password: "{proxy_pass}"
                }}
            }};
        }}

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """
        
        # ファイルを作成
        with open(os.path.join(extension_dir, "manifest.json"), 'w') as f:
            json.dump(manifest, f, indent=2)
        
        with open(os.path.join(extension_dir, "background.js"), 'w') as f:
            f.write(background_js)
        
        return extension_dir
    
    def setup_proxy(self):
        """プロキシ設定（新しいセッションリスト）"""
        sessions = [
            "7i7zey36_lifetime-12h",
            "wm6xvyww_lifetime-20h",
            "mtt1eo7g_lifetime-3h",
            "9drxv6m2_lifetime-5h",
            "lh8pnld8_lifetime-3h",
            "mqc7uh51_lifetime-4h",
            "2h9g1e99_lifetime-8h",
            "apqlpfsx_lifetime-19h",
            "3ya3z213_lifetime-7h",
            "p86tr9m9_lifetime-11h",
            "8csylzl9_lifetime-6h",
            "kojybfeg_lifetime-18h",
            "46q75oht_lifetime-19h",
            "5saamfkt_lifetime-23h",
            "83ucpem7_lifetime-11h"
        ]
        
        available_sessions = [s for s in sessions if s not in self.used_sessions]
        
        if not available_sessions:
            print("⚠️ すべてのセッションを使用しました。リセットします。")
            self.used_sessions = []
            available_sessions = sessions
        
        self.proxy_session = random.choice(available_sessions)
        self.used_sessions.append(self.proxy_session)
        
        proxy_host = "iproyal-aisa.hellworld.io"
        proxy_port = "12322"
        
        self.proxy_auth = {
            "host": proxy_host,
            "port": proxy_port,
            "user": "C9kNyNmY",
            "pass": f"fiWduY3n-country-jp_session-{self.proxy_session}"
        }
        
        # プロキシ認証拡張機能を作成
        extension_dir = self.create_proxy_extension(
            proxy_host,
            proxy_port,
            self.proxy_auth["user"],
            self.proxy_auth["pass"]
        )
        
        # 拡張機能を追加
        self.options.add_argument(f"--load-extension={os.path.abspath(extension_dir)}")
        
        print(f"🌐 プロキシ設定: {proxy_host}:{proxy_port} (セッション: {self.proxy_session})")
        print(f"   認証情報が拡張機能で自動設定されました")
    
    # === SMS認証関連のメソッド ===
    def request_phone_number(self):
        """SMS-Activateで電話番号を取得"""
        print("\n📱 電話番号を取得中...")
        
        try:
            # 残高確認
            balance_url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={self.sms_api_key}&action=getBalance"
            balance_response = requests.get(balance_url)
            balance = balance_response.text
            print(f"   残高: {balance}")
            
            # Instagram用の番号を取得（サービスコード: ig = 11）
            # 日本の番号を優先（国コード: 10）
            order_url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={self.sms_api_key}&action=getNumber&service=ig&country=10"
            order_response = requests.get(order_url)
            
            if "ACCESS_NUMBER" in order_response.text:
                parts = order_response.text.split(":")
                self.activation_id = parts[1]
                self.phone_number = parts[2]
                
                # 日本の番号の場合、+81を追加
                if not self.phone_number.startswith("+"):
                    self.phone_number = "+81" + self.phone_number[1:] if self.phone_number.startswith("0") else "+81" + self.phone_number
                
                print(f"✅ 電話番号取得成功: {self.phone_number}")
                print(f"   アクティベーションID: {self.activation_id}")
                return True
            else:
                print(f"❌ 電話番号取得失敗: {order_response.text}")
                
                # 他の国で試す（米国: 187）
                print("   米国の番号で再試行...")
                order_url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={self.sms_api_key}&action=getNumber&service=ig&country=187"
                order_response = requests.get(order_url)
                
                if "ACCESS_NUMBER" in order_response.text:
                    parts = order_response.text.split(":")
                    self.activation_id = parts[1]
                    self.phone_number = parts[2]
                    
                    if not self.phone_number.startswith("+"):
                        self.phone_number = "+1" + self.phone_number
                    
                    print(f"✅ 電話番号取得成功: {self.phone_number}")
                    return True
                    
        except Exception as e:
            print(f"❌ 電話番号取得エラー: {e}")
            
        return False
    
    def get_sms_code(self, timeout=300):
        """SMSコードを取得"""
        if not self.activation_id:
            return None
        
        print("\n📱 SMSコードを待機中...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                status_url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={self.sms_api_key}&action=getStatus&id={self.activation_id}"
                response = requests.get(status_url)
                
                if "STATUS_OK" in response.text:
                    code = response.text.split(":")[1]
                    print(f"✅ SMSコード受信: {code}")
                    return code
                elif "STATUS_CANCEL" in response.text:
                    print("❌ アクティベーションがキャンセルされました")
                    return None
                
                print(f"   待機中... ({int(time.time() - start_time)}秒)")
                time.sleep(10)
                
            except Exception as e:
                print(f"❌ SMS確認エラー: {e}")
                time.sleep(10)
        
        print("❌ タイムアウト: SMSコードが受信できませんでした")
        return None
    
    def cancel_phone_number(self):
        """電話番号をキャンセル"""
        if self.activation_id:
            try:
                cancel_url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={self.sms_api_key}&action=setStatus&status=8&id={self.activation_id}"
                requests.get(cancel_url)
                print("📱 電話番号をキャンセルしました")
            except:
                pass
    
    # === CAPTCHA関連のメソッド ===
    def solve_recaptcha(self, site_key, page_url):
        """reCAPTCHAを解決（2captcha使用）"""
        print("\n🤖 reCAPTCHAを解決中...")
        
        try:
            # CAPTCHAタスクを送信
            submit_url = "http://2captcha.com/in.php"
            submit_data = {
                'key': self.captcha_api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': page_url,
                'json': 1
            }
            
            submit_response = requests.post(submit_url, data=submit_data)
            submit_result = submit_response.json()
            
            if submit_result['status'] != 1:
                print(f"❌ CAPTCHA送信エラー: {submit_result}")
                return None
            
            request_id = submit_result['request']
            print(f"   タスクID: {request_id}")
            
            # 結果を待機
            result_url = f"http://2captcha.com/res.php?key={self.captcha_api_key}&action=get&id={request_id}&json=1"
            
            for i in range(30):
                time.sleep(10)
                result_response = requests.get(result_url)
                result = result_response.json()
                
                if result['status'] == 1:
                    print("✅ reCAPTCHA解決成功")
                    return result['request']
                elif result['request'] != 'CAPCHA_NOT_READY':
                    print(f"❌ CAPTCHA解決エラー: {result}")
                    return None
                
                print(f"   解決中... ({i+1}/30)")
            
        except Exception as e:
            print(f"❌ CAPTCHA処理エラー: {e}")
            
        return None
    
    def detect_and_solve_captcha(self):
        """ページ内のCAPTCHAを検出して解決"""
        try:
            # reCAPTCHAの存在を確認
            recaptcha_elements = self.driver.find_elements(By.CLASS_NAME, "g-recaptcha")
            
            if recaptcha_elements:
                print("🤖 reCAPTCHAを検出しました")
                
                # site-keyを取得
                site_key = recaptcha_elements[0].get_attribute("data-sitekey")
                page_url = self.driver.current_url
                
                if site_key:
                    # CAPTCHAを解決
                    captcha_token = self.solve_recaptcha(site_key, page_url)
                    
                    if captcha_token:
                        # トークンを挿入
                        self.driver.execute_script(f"""
                            document.getElementById('g-recaptcha-response').innerHTML = '{captcha_token}';
                            if (typeof ___grecaptcha_cfg !== 'undefined') {{
                                Object.entries(___grecaptcha_cfg.clients).forEach(([key, client]) => {{
                                    if (client.callback) {{
                                        client.callback('{captcha_token}');
                                    }}
                                }});
                            }}
                        """)
                        print("✅ CAPTCHAトークンを挿入しました")
                        time.sleep(2)
                        return True
                        
        except Exception as e:
            print(f"CAPTCHA検出エラー: {e}")
            
        return False
    
    def handle_phone_verification(self):
        """電話番号認証を処理"""
        print("\n📱 電話番号認証を処理中...")
        
        try:
            # 電話番号入力欄を探す
            phone_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='tel'], input[name*='phone'], input[placeholder*='電話']")
            
            if not phone_inputs:
                # より広範囲で探す
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                for inp in all_inputs:
                    placeholder = inp.get_attribute("placeholder") or ""
                    if "電話" in placeholder or "phone" in placeholder.lower():
                        phone_inputs.append(inp)
            
            if phone_inputs:
                # 電話番号を取得
                if self.request_phone_number():
                    # 電話番号を入力
                    phone_input = phone_inputs[0]
                    phone_input.click()
                    phone_input.clear()
                    
                    # 国コードが含まれている場合は除去
                    phone_to_enter = self.phone_number
                    if phone_to_enter.startswith("+81"):
                        phone_to_enter = "0" + phone_to_enter[3:]
                    elif phone_to_enter.startswith("+1"):
                        phone_to_enter = phone_to_enter[2:]
                    
                    for char in phone_to_enter:
                        phone_input.send_keys(char)
                        time.sleep(0.1)
                    
                    print(f"✅ 電話番号入力完了: {phone_to_enter}")
                    
                    # 次へボタンを探してクリック
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button_text = button.text
                            if any(text in button_text for text in ["次", "送信", "確認"]):
                                button.click()
                                print("✅ 確認コード送信")
                                time.sleep(5)
                                break
                    
                    # SMSコードを待機
                    sms_code = self.get_sms_code()
                    
                    if sms_code:
                        # コード入力欄を探す
                        code_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='number'], input[type='text']")
                        
                        for inp in code_inputs:
                            try:
                                if inp.is_displayed() and inp.is_enabled():
                                    # 既存のテキストがあるか確認
                                    if not inp.get_attribute("value"):
                                        inp.click()
                                        inp.send_keys(sms_code)
                                        print(f"✅ SMSコード入力: {sms_code}")
                                        time.sleep(2)
                                        
                                        # 確認ボタンをクリック
                                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                                        for button in buttons:
                                            if button.is_displayed() and button.is_enabled():
                                                button_text = button.text
                                                if any(text in button_text for text in ["次", "確認", "完了"]):
                                                    button.click()
                                                    print("✅ 電話番号認証完了")
                                                    return True
                                        break
                            except:
                                continue
                    else:
                        self.cancel_phone_number()
                        
        except Exception as e:
            print(f"❌ 電話番号認証エラー: {e}")
            import traceback
            traceback.print_exc()
            
        return False
    
    # === 既存のメソッド（修正版） ===
    def create_mail_account(self):
        """mail.tmアカウントを作成"""
        print("\n📧 メールアカウント作成中...")
        
        session = requests.Session()
        
        try:
            domains_response = session.get("https://api.mail.tm/domains")
            domains = domains_response.json()['hydra:member']
            domain = domains[0]['domain']
            
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            email = f"{username}@{domain}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
            account_data = {
                "address": email,
                "password": password
            }
            
            create_response = session.post(
                "https://api.mail.tm/accounts",
                json=account_data
            )
            
            if create_response.status_code == 201:
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
                    
        except Exception as e:
            print(f"❌ メールアカウント作成エラー: {e}")
            
        return False
    
    def generate_user_info(self):
        """日本人らしいユーザー情報を生成（より一意性の高いユーザー名）"""
        first_names_romaji = ["yuki", "haruto", "yui", "sota", "mei", "riku", "sakura", "kaito"]
        last_names_romaji = ["tanaka", "suzuki", "takahashi", "watanabe", "ito", "yamamoto", "nakamura", "sato"]
        
        first_names_kanji = ["優希", "陽斗", "結衣", "蒼太", "芽衣", "陸", "さくら", "海斗"]
        last_names_kanji = ["田中", "鈴木", "高橋", "渡辺", "伊藤", "山本", "中村", "佐藤"]
        
        first_idx = random.randint(0, len(first_names_romaji)-1)
        last_idx = random.randint(0, len(last_names_romaji)-1)
        
        # より一意性の高いユーザー名を生成（秒単位のタイムスタンプとランダム文字列）
        timestamp = datetime.now().strftime("%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        username = f"{first_names_romaji[first_idx]}_{timestamp}_{random_suffix}"
        
        fullname = f"{last_names_kanji[last_idx]} {first_names_kanji[first_idx]}"
        
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + "!@#"
        
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
        
        print(f"\n👤 ユーザー情報生成完了:")
        print(f"   ユーザー名: {username}")
        print(f"   フルネーム: {fullname}")
        print(f"   誕生日: {birth_year}年{birth_month}月{birth_day}日")
    
    def start_browser(self):
        """ブラウザ起動"""
        print("\n🌐 ブラウザ起動中...")
        
        self.driver = webdriver.Chrome(options=self.options)
        
        # 検出回避のJavaScript
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['ja-JP', 'ja']})")
        
        self.wait = WebDriverWait(self.driver, 20)
        print("✅ ブラウザ起動完了")
    
    def create_instagram_account(self):
        """日本語版Instagramアカウント作成（SMS認証・CAPTCHA対応）"""
        try:
            # サインアップページにアクセス
            print("\n📝 Instagramアカウント作成開始...")
            signup_urls = [
                "https://www.instagram.com/accounts/emailsignup/",
                "https://www.instagram.com/",
                "https://www.instagram.com/accounts/signup/email"
            ]
        
            for url in signup_urls:
                print(f"   アクセス試行: {url}")
                self.driver.get(url)
                time.sleep(5)
                
                # ページの内容を確認
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                
                # メール登録フォームが表示されているか確認
                if "メールアドレス" in page_text or "emailOrPhone" in self.driver.page_source:
                    print("   ✅ メール登録画面を発見")
                    break
                
                # サインアップリンクを探してクリック
                try:
                    signup_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "登録")
                    for link in signup_links:
                        if link.is_displayed():
                            link.click()
                            time.sleep(3)
                            break
                except:
                    pass
            
            # プロキシエラーチェック（プロキシ使用時のみ）
            if self.use_proxy:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                if "公開プロキシ" in page_text or "flagged" in page_text.lower():
                    print("❌ プロキシがブロックされています")
                    self.driver.save_screenshot('instagram_data/temp/proxy_blocked.png')
                    return False
            
            # CAPTCHAチェック
            self.detect_and_solve_captcha()
            
            # 1. 基本情報を入力
            if self.fill_basic_info():
                # 2. 誕生日を入力
                if self.fill_birthday():
                    # 3. 電話番号認証が必要かチェック
                    time.sleep(3)
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text
                    
                    if "電話番号" in page_text or "phone" in page_text.lower():
                        print("📱 電話番号認証が必要です")
                        if not self.handle_phone_verification():
                            print("❌ 電話番号認証に失敗しました")
                            return False
                    
                    # 4. メール認証コードを処理
                    return self.handle_verification()
            
            return False
            
        except Exception as e:
            print(f"\n❌ エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def fill_basic_info(self):
        """基本情報入力（メール、パスワード、氏名、ユーザー名）"""
        try:
            print("\n[STEP 1] 基本情報入力...")
            
            # 入力欄を取得
            inputs = self.wait.until(
                lambda d: d.find_elements(By.TAG_NAME, "input")
            )
            
            if len(inputs) >= 4:
                # メールアドレス（1番目の入力欄）
                print(f"   メール: {self.user_info['email']}")
                inputs[0].click()
                time.sleep(0.5)
                inputs[0].clear()
                for char in self.user_info['email']:
                    inputs[0].send_keys(char)
                    time.sleep(0.05)
                time.sleep(1)
                
                # パスワード（2番目の入力欄）
                print("   パスワード: ********")
                inputs[1].click()
                time.sleep(0.5)
                inputs[1].clear()
                for char in self.user_info['password']:
                    inputs[1].send_keys(char)
                    time.sleep(0.05)
                time.sleep(1)
                
                # フルネーム（3番目の入力欄）
                print(f"   氏名: {self.user_info['fullname']}")
                inputs[2].click()
                time.sleep(0.5)
                inputs[2].clear()
                inputs[2].send_keys(self.user_info['fullname'])
                time.sleep(1)
                
                # ユーザーネーム（4番目の入力欄）
                print(f"   ユーザー名: {self.user_info['username']}")
                inputs[3].click()
                time.sleep(0.5)
                inputs[3].clear()
                inputs[3].send_keys(self.user_info['username'])
                time.sleep(3)  # ユーザー名チェックの時間を増やす
                
                # ユーザー名のエラーチェックと修正
                print("\n   ユーザー名の確認中...")
                username_fixed = False
                max_username_attempts = 5
                
                for username_attempt in range(max_username_attempts):
                    time.sleep(2)  # エラーメッセージが表示されるのを待つ
                    
                    try:
                        # エラーメッセージを複数の方法で探す
                        error_found = False
                        
                        # 方法1: おすすめのユーザーネームテキスト
                        error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'おすすめのユーザーネーム')]")
                        if error_elements and any(elem.is_displayed() for elem in error_elements):
                            error_found = True
                            print("   ⚠️ ユーザー名が使用できません（おすすめメッセージ検出）")
                        
                        # 方法2: エラーアイコンやアラート
                        error_alerts = self.driver.find_elements(By.CSS_SELECTOR, "span[role='alert'], div[role='alert'], div[aria-label*='エラー']")
                        for alert in error_alerts:
                            if alert.is_displayed() and alert.text and "ユーザーネーム" in alert.text:
                                error_found = True
                                print(f"   ⚠️ エラー検出: {alert.text}")
                        
                        # 方法3: 赤いボーダーやエラークラス
                        username_input = inputs[3]
                        input_classes = username_input.get_attribute("class") or ""
                        if "error" in input_classes.lower() or "invalid" in input_classes.lower():
                            error_found = True
                            print("   ⚠️ ユーザー名入力欄にエラークラス検出")
                        
                        if error_found:
                            print(f"   🔄 ユーザー名修正試行 {username_attempt + 1}/{max_username_attempts}")
                            
                            # おすすめのユーザー名ボタンを探す
                            suggestion_found = False
                            suggestion_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                            
                            for button in suggestion_buttons:
                                button_text = button.text.strip()
                                # ユーザー名の形式に一致するボタンを探す
                                if (button_text and 
                                    re.match(r'^[a-zA-Z0-9_.]+$', button_text) and 
                                    len(button_text) > 3 and 
                                    button_text != self.user_info['username'] and
                                    button.is_displayed() and 
                                    button.is_enabled()):
                                    
                                    print(f"   📝 おすすめユーザー名を選択: {button_text}")
                                    try:
                                        # JavaScriptでクリック
                                        self.driver.execute_script("arguments[0].click();", button)
                                        self.user_info['username'] = button_text
                                        suggestion_found = True
                                        time.sleep(2)
                                        break
                                    except:
                                        # 通常クリック
                                        button.click()
                                        self.user_info['username'] = button_text
                                        suggestion_found = True
                                        time.sleep(2)
                                        break
                            
                            # おすすめが見つからない場合は、完全に新しいユーザー名を生成
                            if not suggestion_found:
                                # より確実にユニークなユーザー名を生成
                                timestamp = datetime.now().strftime("%H%M%S")
                                random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                                new_username = f"{self.user_info['username'].split('_')[0]}_{timestamp}_{random_suffix}"
                                
                                print(f"   📝 新しいユーザー名を生成: {new_username}")
                                
                                # 入力欄をクリア
                                username_input.click()
                                username_input.clear()
                                time.sleep(0.5)
                                
                                # Ctrl+A で全選択してから削除
                                username_input.send_keys(Keys.CONTROL + "a")
                                username_input.send_keys(Keys.DELETE)
                                time.sleep(0.5)
                                
                                # 新しいユーザー名を入力
                                for char in new_username:
                                    username_input.send_keys(char)
                                    time.sleep(0.05)
                                
                                self.user_info['username'] = new_username
                                time.sleep(2)
                            
                            # 変更後、エラーが消えるのを待つ
                            time.sleep(3)
                            
                        else:
                            # エラーが見つからない場合は成功
                            print("   ✅ ユーザー名使用可能")
                            username_fixed = True
                            break
                            
                    except Exception as e:
                        print(f"   ユーザー名チェックエラー: {e}")
                
                if not username_fixed:
                    print("   ⚠️ ユーザー名の問題を解決できませんでした")
                
                # 最終確認のための待機
                time.sleep(3)
                
                # CAPTCHAチェック（登録前）
                self.detect_and_solve_captcha()
                
                # スクリーンショット保存
                self.driver.save_screenshot('instagram_data/temp/basic_info_filled.png')
                print("   📸 スクリーンショット保存: basic_info_filled.png")
                
                # 登録ボタンを探してクリック
                print("\n   登録ボタンを探しています...")
                
                # 登録ボタンをクリックする前に、もう一度エラーチェック
                final_error_check = False
                error_messages = self.driver.find_elements(By.CSS_SELECTOR, "span[role='alert'], div[role='alert']")
                for error in error_messages:
                    if error.is_displayed() and error.text:
                        print(f"   ⚠️ 最終エラーチェック: {error.text}")
                        final_error_check = True
                
                if final_error_check:
                    print("   ❌ エラーが残っているため、登録をスキップします")
                    return False
                
                button_clicked = False
                
                # 複数の方法で登録ボタンを探す
                # 方法1: XPathで探す
                try:
                    register_buttons = self.driver.find_elements(By.XPATH, "//button[@type='submit']")
                    for button in register_buttons:
                        if button.is_displayed() and button.is_enabled():
                            button_text = button.text
                            if "登録" in button_text or "次へ" in button_text:
                                print(f"   ✅ 登録ボタン発見: '{button_text}'")
                                
                                # ボタンが有効になるまで待つ
                                time.sleep(2)
                                
                                # スクロールして表示
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(0.5)
                                
                                # JavaScriptで強制クリック
                                self.driver.execute_script("arguments[0].click();", button)
                                button_clicked = True
                                print("   ✅ 登録ボタンをクリック成功")
                                break
                except Exception as e:
                    print(f"   登録ボタン検索エラー: {e}")
                
                # 方法2: フォーム送信
                if not button_clicked:
                    try:
                        forms = self.driver.find_elements(By.TAG_NAME, "form")
                        if forms:
                            print("   📝 フォーム送信を試行")
                            self.driver.execute_script("arguments[0].submit();", forms[0])
                            button_clicked = True
                            print("   ✅ フォームをsubmit成功")
                    except Exception as e:
                        print(f"   フォーム送信エラー: {e}")
                
                # 方法3: Enterキー送信
                if not button_clicked:
                    try:
                        print("   ⌨️ Enterキーで送信を試行")
                        inputs[3].send_keys(Keys.RETURN)
                        button_clicked = True
                        print("   ✅ Enterキー送信成功")
                    except:
                        pass
                
                if button_clicked:
                    print("   ✅ 基本情報送信完了")
                    
                    # 画面遷移を待つ
                    print("   画面遷移を待機中...")
                    time.sleep(5)
                    
                    # 現在のURLを確認
                    current_url = self.driver.current_url
                    print(f"   現在のURL: {current_url}")
                    
                    # ページ内容を確認
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text
                    if "誕生日" in page_text:
                        print("   ✅ 誕生日入力画面に遷移しました")
                        return True
                    else:
                        # まだ同じ画面の場合
                        if "登録する" in page_text:
                            print("   ⚠️ まだ登録画面です。エラーを確認中...")
                            
                            # エラーメッセージを詳しく確認
                            errors = self.driver.find_elements(By.CSS_SELECTOR, "span[role='alert'], div[role='alert']")
                            for error in errors:
                                if error.text and error.is_displayed() and "おすすめ" not in error.text:
                                    print(f"   ❌ エラー: {error.text}")
                            
                            return False
                        else:
                            # 別の画面に遷移した場合は続行
                            return True
                else:
                    print("   ❌ 登録ボタンがクリックできませんでした")
                    return False
                
            else:
                print(f"   ❌ 入力欄が不足: {len(inputs)}個")
                return False
                
        except Exception as e:
            print(f"   ❌ 基本情報入力エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def fill_birthday(self):
        """誕生日入力"""
        try:
            print("\n[STEP 2] 誕生日入力...")
            
            # 誕生日画面が表示されるまで待機
            time.sleep(3)
            
            # セレクトボックスを取得
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            
            if len(selects) >= 3:
                # 月（1番目のセレクト）
                print(f"   月: {self.user_info['birth_month']}月")
                month_select = Select(selects[0])
                month_select.select_by_value(str(self.user_info['birth_month']))
                time.sleep(0.5)
                
                # 日（2番目のセレクト）
                print(f"   日: {self.user_info['birth_day']}日")
                day_select = Select(selects[1])
                day_select.select_by_value(str(self.user_info['birth_day']))
                time.sleep(0.5)
                
                # 年（3番目のセレクト）
                print(f"   年: {self.user_info['birth_year']}年")
                year_select = Select(selects[2])
                year_select.select_by_value(str(self.user_info['birth_year']))
                time.sleep(1)
                
                # スクリーンショット保存
                self.driver.save_screenshot('instagram_data/temp/birthday_filled.png')
                print("   📸 スクリーンショット保存: birthday_filled.png")
                
                # 次へボタンをクリック
                print("\n   '次へ'ボタンを探しています...")
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        button_text = button.text
                        if "次へ" in button_text or "次" in button_text:
                            print(f"   ✅ ボタン発見: '{button_text}'")
                            
                            # JavaScriptでクリック
                            try:
                                self.driver.execute_script("arguments[0].click();", button)
                                print("   ✅ 誕生日送信完了")
                                time.sleep(5)
                                return True
                            except:
                                # 通常クリック
                                button.click()
                                print("   ✅ 誕生日送信完了")
                                time.sleep(5)
                                return True
                
                print("   ❌ 次へボタンが見つかりません")
                return False
                
            else:
                print(f"   ❌ セレクトボックスが不足: {len(selects)}個")
                return False
                
        except Exception as e:
            print(f"   ❌ 誕生日入力エラー: {e}")
            return False
    
    def handle_verification(self):
        """認証コード処理（修正版）"""
        print("\n[STEP 3] 認証コード処理...")
        
        # 認証コード画面が表示されるまで待機
        time.sleep(3)
        
        # 認証コードを取得
        verification_code = self.get_verification_code()
        
        if verification_code:
            print(f"\n[STEP 4] 認証コード入力: {verification_code}")
            
            try:
                # 認証コード入力欄を探す
                code_input = None
                
                # 方法1: name属性で探す
                try:
                    code_input = self.driver.find_element(By.NAME, "email_confirmation_code")
                    print("   ✅ name='email_confirmation_code'で入力欄発見")
                except:
                    pass
                
                # 方法2: 最初のinput要素を使用
                if not code_input:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    if inputs:
                        code_input = inputs[0]
                        print("   ✅ 最初の入力欄を使用")
                
                if code_input:
                    # スクリーンショット（入力前）
                    self.driver.save_screenshot('instagram_data/temp/before_code_input.png')
                    
                    # 入力欄をクリックしてフォーカス
                    code_input.click()
                    time.sleep(0.5)
                    
                    # 既存の内容をクリア
                    code_input.clear()
                    time.sleep(0.5)
                    
                    # 認証コードを入力
                    code_input.send_keys(verification_code)
                    time.sleep(1)
                    
                    # スクリーンショット（入力後）
                    self.driver.save_screenshot('instagram_data/temp/after_code_input.png')
                    print("   ✅ 認証コード入力完了")
                    
                    # 確認ボタンを探す
                    print("\n   確認ボタンを探しています...")
                    button_clicked = False
                    
                    # テキストで探す
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button_text = button.text
                            if any(text in button_text for text in ["次へ", "確認", "送信"]):
                                print(f"   ✅ ボタン発見: '{button_text}'")
                                
                                # JavaScriptでクリック
                                self.driver.execute_script("arguments[0].click();", button)
                                button_clicked = True
                                print("   ✅ 確認ボタンクリック成功")
                                break
                    
                    # Enterキーでも試す
                    if not button_clicked:
                        try:
                            code_input.send_keys(Keys.RETURN)
                            button_clicked = True
                            print("   ✅ Enterキーで送信")
                        except:
                            pass
                    
                    if button_clicked:
                        # 結果を待つ
                        print("\n   処理結果を待機中...")
                        time.sleep(5)
                        
                        # 現在のURLを確認
                        current_url = self.driver.current_url
                        print(f"   現在のURL: {current_url}")
                        
                        # 成功判定
                        if "emailsignup" not in current_url:
                            print("\n🎉 アカウント作成成功！")
                            self.save_account_info()
                            return True
                        else:
                            print("   ⚠️ まだ認証画面にいます")
                            self.driver.save_screenshot('instagram_data/temp/still_on_verification.png')
                else:
                    print("   ❌ 認証コード入力欄が見つかりませんでした")
                    
            except Exception as e:
                print(f"   ❌ 認証コード入力エラー: {e}")
                import traceback
                traceback.print_exc()
                
        return False
    
    def get_verification_code(self):
        """認証コードを取得"""
        print("\n   📧 メールから認証コードを取得中...")
        headers = {"Authorization": f"Bearer {self.mail_account['token']}"}
        
        for attempt in range(30):
            try:
                response = requests.get("https://api.mail.tm/messages", headers=headers)
                
                if response.status_code == 200:
                    messages = response.json()
                    
                    if messages['hydra:totalItems'] > 0:
                        for msg in messages['hydra:member']:
                            subject = msg.get('subject', '')
                            if "instagram" in subject.lower() or "コード" in subject:
                                msg_id = msg.get('id')
                                msg_response = requests.get(
                                    f"https://api.mail.tm/messages/{msg_id}",
                                    headers=headers
                                )
                                
                                if msg_response.status_code == 200:
                                    msg_text = msg_response.json().get('text', '')
                                    codes = re.findall(r'\b\d{6}\b', msg_text)
                                    
                                    if codes:
                                        print(f"   ✅ 認証コード発見: {codes[0]}")
                                        return codes[0]
                
                print(f"   待機中... ({attempt + 1}/30)")
                time.sleep(10)
                
            except Exception as e:
                print(f"   メール確認エラー: {e}")
                time.sleep(10)
        
        print("   ❌ 認証コードが見つかりませんでした")
        return None
    
    def save_account_info(self):
        """アカウント情報を保存"""
        account_data = {
            "instagram": self.user_info,
            "email": self.mail_account,
            "phone": self.phone_number if self.phone_number else None,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "language": "japanese",
            "proxy_used": self.proxy_session if self.use_proxy else None
        }
        
        account_id = f"IG_JP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        save_dir = f"instagram_accounts/accounts/{account_id}"
        os.makedirs(save_dir, exist_ok=True)
        
        with open(f"{save_dir}/account_info.json", 'w', encoding='utf-8') as f:
            json.dump(account_data, f, ensure_ascii=False, indent=2)
        
        # 最終スクリーンショット
        self.driver.save_screenshot(f"{save_dir}/final_screen.png")
        
        print(f"\n💾 アカウント情報保存完了: {account_id}")
        print(f"   ユーザー名: {self.user_info['username']}")
        print(f"   パスワード: {self.user_info['password']}")
        print(f"   メール: {self.user_info['email']}")
        print(f"   電話番号: {self.phone_number if self.phone_number else 'なし'}")
        print(f"   フルネーム: {self.user_info['fullname']}")
    
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            print("\n処理完了。30秒後にブラウザを閉じます...")
            print("（手動で確認したい場合は、この間に確認してください）")
            time.sleep(30)
            self.driver.quit()
            
        # プロキシ拡張機能ディレクトリを削除
        if os.path.exists("proxy_auth_extension"):
            shutil.rmtree("proxy_auth_extension")

def main():
    print("=== Instagram 自動アカウント作成システム ===")
    print("SMS認証・CAPTCHA対応 + プロキシ拡張機能")
    
    # APIキーはコード内に設定済み
    print("\n✅ APIキー設定済み")
    print("   SMS-Activate: d7549f93...")
    print("   2captcha: 6c900aee...")
    
    # プロキシ使用を確認
    use_proxy = input("\nプロキシを使用しますか？ (y/n): ").lower() == 'y'
    
    max_attempts = 3
    
    for attempt in range(max_attempts):
        print(f"\n{'='*50}")
        print(f"試行 {attempt + 1}/{max_attempts}")
        print(f"{'='*50}")
        
        if use_proxy:
            print("\n🌐 プロキシ: 有効（拡張機能使用）")
        else:
            print("\n🌐 プロキシ: 無効（直接接続）")
        
        creator = InstagramCreatorJapaneseV2(use_proxy=use_proxy)
        
        try:
            # 1. メールアカウント作成
            if not creator.create_mail_account():
                print("メールアカウント作成に失敗しました")
                creator.close()
                continue
            
            # 2. ユーザー情報生成
            creator.generate_user_info()
            
            # 3. ブラウザ起動
            creator.start_browser()
            
            # 4. Instagramアカウント作成
            if creator.create_instagram_account():
                print("\n✨ 全工程完了！")
                print("\n" + "="*50)
                print("🎊 アカウント作成成功 🎊")
                print("="*50)
                creator.close()
                return
            else:
                print("\n⚠️ アカウント作成に失敗しました")
                
        except Exception as e:
            print(f"\n❌ システムエラー: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            creator.close()
        
        # 次の試行まで待機
        if attempt < max_attempts - 1:
            wait_time = 300  # 5分
            print(f"\n⏰ 次の試行まで{wait_time}秒待機します...")
            time.sleep(wait_time)
    
    print("\n❌ すべての試行が失敗しました")
    print("以下を確認してください:")
    print("1. インターネット接続")
    print("2. プロキシの状態")
    print("3. APIキーの有効性と残高")
    print("4. Instagramのサービス状態")

if __name__ == "__main__":
    # 必要なディレクトリを作成
    os.makedirs("instagram_accounts/accounts", exist_ok=True)
    os.makedirs("instagram_data/temp", exist_ok=True)
    
    main()