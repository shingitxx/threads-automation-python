# instagram_automation/instagram_creator_japanese_v4.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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

class InstagramCreatorJapaneseV4:
    def __init__(self, use_proxy=True):
        """
        シンプル版 - 成功例を参考に
        """
        self.use_proxy = use_proxy
        self.driver = None
        self.mail_driver = None
        
        # アカウント番号を取得
        self.account_number = self.get_next_account_number()
        
        # アカウント情報
        self.account_data = {
            "account_number": self.account_number,
            "created_at": datetime.now().isoformat()
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
        """proxies.txtからプロキシを読み込む（シンプル版）"""
        try:
            with open("proxies.txt", 'r', encoding='utf-8') as f:
                proxies = [line.strip() for line in f.readlines() if line.strip()]
            
            if proxies:
                # ランダムに1つ選択
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
    
    def generate_simple_credentials(self):
        """シンプルな認証情報生成（成功例を参考）"""
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
        
        print(f"📝 認証情報生成:")
        print(f"   ユーザー名: {username}")
        print(f"   パスワード: ***")
        print(f"   フルネーム: {full_name}")
        
        return True
    
    def create_temp_email(self):
        """一時メールアドレスを作成（複数サービス対応）"""
        print("\n📧 一時メールアドレス作成中...")
        
        # メールドメインのリスト（成功例のsomail.ukを優先）
        email_domains = [
            "somail.uk",      # 成功例で使用
            "tmpmail.net", 
            "tmpmail.org",
            "1secmail.com",
            "guerrillamail.com"
        ]
        
        # ランダムなメールアドレスを生成
        email_prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        email_domain = random.choice(email_domains)
        email = f"{email_prefix}@{email_domain}"
        
        self.account_data["email"] = email
        print(f"✅ メールアドレス: {email}")
        
        # メールサービスにアクセスする必要がある場合の処理
        if email_domain == "somail.uk":
            return self.setup_somail(email)
        else:
            # 他のサービスの実装
            return True
    
    def setup_somail(self, email):
        """somail.ukのセットアップ（仮実装）"""
        # 実際のsomail.ukの仕様に合わせて実装
        return True
    
    def start_browser(self):
        """ブラウザ起動（デバッグ版）"""
        print("\n🌐 ブラウザ起動中...")
        
        options = Options()
        options.add_argument('--lang=ja')
        
        # 基本的な検出回避のみ
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # プロキシ設定（拡張機能方式）
        if self.use_proxy and "proxy" in self.account_data:
            proxy_extension = self.create_simple_proxy_extension()
            if proxy_extension:
                # 拡張機能の読み込みを確認
                options.add_argument(f'--load-extension={proxy_extension}')
                
                # デバッグ: 拡張機能のパスを表示
                print(f"📂 拡張機能パス: {proxy_extension}")
                
                # 拡張機能が存在するか確認
                manifest_path = os.path.join(proxy_extension, "manifest.json")
                background_path = os.path.join(proxy_extension, "background.js")
                
                if os.path.exists(manifest_path) and os.path.exists(background_path):
                    print("✅ 拡張機能ファイル確認OK")
                else:
                    print("❌ 拡張機能ファイルが見つかりません")
        
        # 開発者モードを有効化（拡張機能のデバッグ用）
        options.add_argument('--enable-logging')
        options.add_argument('--v=1')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            
            # 拡張機能が読み込まれたか確認
            time.sleep(3)
            print("\n🔍 拡張機能の確認...")
            print("chrome://extensions/ で拡張機能を確認してください")
            
            print("✅ ブラウザ起動完了")
            return True
        except Exception as e:
            print(f"❌ ブラウザ起動エラー: {e}")
            return False
    
    def create_simple_proxy_extension(self):
        """プロキシ拡張機能作成（修正版）"""
        import shutil
        
        if "proxy" not in self.account_data:
            return None
        
        proxy_line = self.account_data["proxy"]
        parts = proxy_line.split(':')
        
        if len(parts) < 4:
            return None
        
        proxy_host = parts[0]
        proxy_port = parts[1]
        proxy_user = parts[2]
        proxy_pass = ':'.join(parts[3:])
        
        # 拡張機能ディレクトリ
        ext_dir = "proxy_extension_v4"
        if os.path.exists(ext_dir):
            shutil.rmtree(ext_dir)
        os.makedirs(ext_dir)
        
        # manifest.json - Manifest V2形式で修正
        manifest = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking",
                "webRequestAuthProvider"
            ],
            "background": {
                "scripts": ["background.js"],
                "persistent": True
            },
            "minimum_chrome_version": "22.0.0"
        }
        
        # background.js - より確実な実装
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

    chrome.webRequest.onAuthRequired.addListener(
        function(details) {{
            console.log('Authentication for: ' + details.url);
            return {{
                authCredentials: {{
                    username: "{proxy_user}",
                    password: "{proxy_pass}"
                }}
            }};
        }},
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );

    chrome.webRequest.onBeforeRequest.addListener(
        function(details) {{
            console.log('Request: ' + details.url);
            return {{cancel: false}};
        }},
        {{urls: ["<all_urls>"]}}
    );
    """
        
        # ファイル保存
        with open(os.path.join(ext_dir, "manifest.json"), 'w') as f:
            json.dump(manifest, f, indent=2)
        
        with open(os.path.join(ext_dir, "background.js"), 'w') as f:
            f.write(background_js)
        
        return os.path.abspath(ext_dir)
    
    def human_like_type(self, element, text):
        """人間らしいタイピング"""
        element.clear()
        time.sleep(random.uniform(0.5, 1))
        
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def create_account(self):
        """アカウント作成のメインプロセス（シンプル版）"""
        try:
            print("\n📝 Instagramアカウント作成開始...")
            
            # プロキシ確認
            if self.use_proxy:
                self.driver.get("https://httpbin.org/ip")
                time.sleep(3)
                ip_info = self.driver.find_element(By.TAG_NAME, "body").text
                print(f"✅ IP情報: {ip_info}")
                
                # IPアドレスを抽出して保存
                import re
                ip_match = re.search(r'"origin":\s*"([^"]+)"', ip_info)
                if ip_match:
                    self.account_data["proxy_ip"] = ip_match.group(1)
            
            # Instagram にアクセス
            time.sleep(random.uniform(2, 4))
            self.driver.get("https://www.instagram.com/accounts/emailsignup/")
            time.sleep(random.uniform(5, 8))
            
            # 基本情報入力
            print("\n[STEP 1] 基本情報入力...")
            
            # メールアドレス
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "emailOrPhone"))
            )
            self.human_like_type(email_input, self.account_data["email"])
            
            # フルネーム
            fullname_input = self.driver.find_element(By.NAME, "fullName")
            self.human_like_type(fullname_input, self.account_data["full_name"])
            
            # ユーザー名
            username_input = self.driver.find_element(By.NAME, "username")
            self.human_like_type(username_input, self.account_data["username"])
            
            # パスワード
            password_input = self.driver.find_element(By.NAME, "password")
            self.human_like_type(password_input, self.account_data["password"])
            
            time.sleep(2)
            
            # 登録ボタンクリック
            signup_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '登録') or contains(text(), 'Sign up')]")
            signup_button.click()
            
            print("✅ 基本情報送信完了")
            time.sleep(5)
            
            # 誕生日入力
            print("\n[STEP 2] 誕生日入力...")
            self.fill_birthday()
            
            # 認証コード（手動対応）
            print("\n[STEP 3] 認証コード...")
            print("\n⚠️ 手動で認証コードを入力してください")
            print(f"メールアドレス: {self.account_data['email']}")
            input("認証コードを入力したらEnterキーを押してください...")
            
            # 成功確認
            time.sleep(3)
            current_url = self.driver.current_url
            
            if "welcome" in current_url or "accounts/onetap" in current_url:
                self.account_data["status"] = "作成成功"
                print("✅ アカウント作成成功！")
                return True
            else:
                self.account_data["status"] = "作成失敗"
                print("❌ アカウント作成失敗")
                return False
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            self.account_data["status"] = "エラー"
            self.account_data["error"] = str(e)
            return False
    
    def fill_birthday(self):
        """誕生日入力"""
        try:
            birth_year = random.randint(1990, 2005)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            
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
            
        except Exception as e:
            print(f"❌ 誕生日入力エラー: {e}")
    
    def save_account(self):
        """アカウント情報を保存（成功例と同じ形式）"""
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
            "status": self.account_data.get("status", "不明")
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
            print("="*50)
    
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()

# メイン実行部分
def main():
    print("=== Instagram自動アカウント作成システム v4 ===")
    print("シンプル版 - 成功例を参考に")
    
    # プロキシ使用の確認
    use_proxy = input("\nプロキシを使用しますか？ (y/n): ").lower() == 'y'
    
    creator = InstagramCreatorJapaneseV4(use_proxy=use_proxy)
    
    try:
        # 認証情報生成
        if creator.generate_simple_credentials():
            # メールアドレス作成
            if creator.create_temp_email():
                # ブラウザ起動
                if creator.start_browser():
                    # アカウント作成
                    if creator.create_account():
                        print("\n✅ プロセス完了")
                    else:
                        print("\n❌ アカウント作成失敗")
    
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
    
def verify_proxy(self):
    """プロキシが正しく動作しているか確認"""
    print("\n🔍 プロキシ動作確認中...")
    
    try:
        # IPアドレスを確認
        self.driver.get("https://httpbin.org/ip")
        time.sleep(3)
        
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        print(f"レスポンス: {body_text}")
        
        # IPアドレスを抽出
        import re
        ip_match = re.search(r'"origin":\s*"([^"]+)"', body_text)
        
        if ip_match:
            current_ip = ip_match.group(1)
            self.account_data["proxy_ip"] = current_ip
            
            # 日本の一般的なIPレンジをチェック
            japan_ip_ranges = ["180.", "153.", "126.", "114.", "106."]
            is_japan_ip = any(current_ip.startswith(range) for range in japan_ip_ranges)
            
            if is_japan_ip and "smtproxies" in self.account_data.get("proxy", ""):
                print(f"⚠️ プロキシが効いていない可能性があります")
                print(f"   現在のIP: {current_ip} (日本の一般的なIP)")
                return False
            else:
                print(f"✅ プロキシIP: {current_ip}")
                return True
        else:
            print("❌ IPアドレスを取得できませんでした")
            return False
            
    except Exception as e:
        print(f"❌ プロキシ確認エラー: {e}")
        return False

if __name__ == "__main__":
    main()