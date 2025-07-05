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

class InstagramCreatorJapanese:
    def __init__(self, use_proxy=True):
        self.use_proxy = use_proxy
        self.mail_account = None
        self.user_info = None
        self.proxy_session = None
        
        # Chrome設定（日本語版）
        self.options = Options()
        self.options.add_argument("--lang=ja")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # プロキシ設定
        if self.use_proxy:
            self.setup_proxy()
            
        self.driver = None
        self.wait = None
    
    def setup_proxy(self):
        """プロキシ設定"""
        # IPRoyalのセッション
        sessions = [
            "w0sc3hsf_lifetime-2h",
            "3icgignj_lifetime-9h", 
            "16u7hbrf_lifetime-4h",
            "ohxfhr7l_lifetime-15h",
            "uchw0mfn_lifetime-14h"
        ]
        
        self.proxy_session = random.choice(sessions)
        proxy_host = "iproyal-aisa.hellworld.io"
        proxy_port = "12322"
        
        self.proxy_auth = {
            "host": proxy_host,
            "port": proxy_port,
            "user": "C9kNyNmY",
            "pass": f"fiWduY3n-country-jp_session-{self.proxy_session}"
        }
        
        self.options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')
        print(f"🌐 プロキシ設定: {proxy_host}:{proxy_port} (セッション: {self.proxy_session})")
    
    def create_mail_account(self):
        """mail.tmアカウントを作成"""
        print("\n📧 メールアカウント作成中...")
        
        session = requests.Session()
        
        # プロキシ経由でリクエスト（必要に応じて）
        if self.use_proxy and hasattr(self, 'proxy_auth'):
            # 注: requestsでの認証付きプロキシは別途設定が必要
            pass
        
        try:
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
                    
        except Exception as e:
            print(f"❌ メールアカウント作成エラー: {e}")
            
        return False
    
    def generate_user_info(self):
        """日本人らしいユーザー情報を生成"""
        # 日本人の名前（ローマ字）
        first_names_romaji = ["yuki", "haruto", "yui", "sota", "mei", "riku", "sakura", "kaito"]
        last_names_romaji = ["tanaka", "suzuki", "takahashi", "watanabe", "ito", "yamamoto", "nakamura", "sato"]
        
        # 日本人の名前（漢字）
        first_names_kanji = ["優希", "陽斗", "結衣", "蒼太", "芽衣", "陸", "さくら", "海斗"]
        last_names_kanji = ["田中", "鈴木", "高橋", "渡辺", "伊藤", "山本", "中村", "佐藤"]
        
        # ユーザー名生成
        first_idx = random.randint(0, len(first_names_romaji)-1)
        last_idx = random.randint(0, len(last_names_romaji)-1)
        
        timestamp = datetime.now().strftime("%m%d")
        username = f"{first_names_romaji[first_idx]}_{last_names_romaji[last_idx]}{timestamp}"
        
        # フルネーム（漢字）
        fullname = f"{last_names_kanji[last_idx]} {first_names_kanji[first_idx]}"
        
        # パスワード
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
        
        print(f"\n👤 ユーザー情報生成完了:")
        print(f"   ユーザー名: {username}")
        print(f"   フルネーム: {fullname}")
    
    def start_browser(self):
        """ブラウザ起動"""
        print("\n🌐 ブラウザ起動中...")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
        print("✅ ブラウザ起動完了")
        
        # プロキシ認証処理
        if self.use_proxy:
            print("\n⚠️ プロキシ認証が必要です:")
            print(f"ユーザー名: {self.proxy_auth['user']}")
            print(f"パスワード: {self.proxy_auth['pass']}")
            
            # Googleにアクセスして認証
            self.driver.get("https://www.google.com")
            input("\n認証完了後、Enterキーを押してください...")
    
    def create_instagram_account(self):
        """日本語版Instagramアカウント作成"""
        try:
            # 1. サインアップページ
            print("\n📝 Instagramアカウント作成開始...")
            self.driver.get("https://www.instagram.com/accounts/emailsignup/")
            time.sleep(5)
            
            # ページタイプを判定
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            if "携帯電話番号またはメールアドレス" in page_text:
                # 新フォーマット
                print("📱 新フォーマット検出 - 対応モードで実行")
                return self.create_account_new_format()
            else:
                # 旧フォーマット
                print("📱 旧フォーマット検出 - 標準モードで実行")
                return self.create_account_old_format()
                
        except Exception as e:
            print(f"\n❌ エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_account_new_format(self):
        """新フォーマットでのアカウント作成"""
        try:
            print("\n[STEP 1] 基本情報入力...")
            
            # すべての入力欄を取得
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            
            if len(inputs) >= 4:
                # 1番目: メールアドレス
                print("   メールアドレス入力中...")
                inputs[0].click()
                time.sleep(0.5)
                inputs[0].clear()
                inputs[0].send_keys(self.user_info['email'])
                time.sleep(1)
                
                # 2番目: パスワード
                print("   パスワード入力中...")
                inputs[1].click()
                time.sleep(0.5)
                inputs[1].clear()
                inputs[1].send_keys(self.user_info['password'])
                time.sleep(1)
                
                # ページをスクロール（必要に応じて）
                self.driver.execute_script("window.scrollBy(0, 200)")
                time.sleep(1)
                
                # 誕生日セレクト
                print("\n[STEP 2] 誕生日入力...")
                selects = self.driver.find_elements(By.TAG_NAME, "select")
                
                if len(selects) >= 3:
                    # 年
                    Select(selects[0]).select_by_value(str(self.user_info['birth_year']))
                    time.sleep(0.5)
                    
                    # 月
                    Select(selects[1]).select_by_value(str(self.user_info['birth_month']))
                    time.sleep(0.5)
                    
                    # 日
                    Select(selects[2]).select_by_value(str(self.user_info['birth_day']))
                    time.sleep(1)
                
                # 3番目: 氏名
                print("   氏名入力中...")
                inputs[2].click()
                time.sleep(0.5)
                inputs[2].clear()
                inputs[2].send_keys(self.user_info['fullname'])
                time.sleep(1)
                
                # 4番目: ユーザーネーム
                print("   ユーザーネーム入力中...")
                inputs[3].click()
                time.sleep(0.5)
                inputs[3].clear()
                inputs[3].send_keys(self.user_info['username'])
                time.sleep(2)
                
                # スクリーンショット
                self.driver.save_screenshot('instagram_data/temp/before_submit_jp.png')
                
                # 登録ボタンを探す
                print("\n[STEP 3] 登録ボタンを探しています...")
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                
                for button in buttons:
                    if "登録する" in button.text:
                        print("✅ 登録ボタン発見")
                        button.click()
                        break
                
                time.sleep(5)
                
                # 認証コード画面を待機
                return self.handle_verification()
                
            else:
                print(f"❌ 入力欄が不足しています: {len(inputs)}個")
                return False
                
        except Exception as e:
            print(f"❌ 新フォーマット処理エラー: {e}")
            return False
    
    def create_account_old_format(self):
        """旧フォーマットでのアカウント作成"""
        # 既存の処理（英語版と同様）
        pass
    
    def handle_verification(self):
        """認証コード処理"""
        print("\n[STEP 4] 認証コード待機中...")
        
        # 認証コードを取得
        verification_code = self.get_verification_code()
        
        if verification_code:
            print(f"\n[STEP 5] 認証コード入力: {verification_code}")
            
            # 認証コード入力欄を探す
            try:
                # name属性で探す
                code_input = self.driver.find_element(By.NAME, "email_confirmation_code")
            except:
                # 見つからない場合は最初のinput要素
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                if inputs:
                    code_input = inputs[0]
                else:
                    print("❌ 認証コード入力欄が見つかりません")
                    return False
            
            code_input.clear()
            code_input.send_keys(verification_code)
            time.sleep(1)
            
            # 次へボタン
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "次へ" in button.text or "確認" in button.text:
                    button.click()
                    break
            
            time.sleep(5)
            
            # 成功確認
            current_url = self.driver.current_url
            if "emailsignup" not in current_url:
                print("\n🎉 アカウント作成成功！")
                self.save_account_info()
                return True
                
        return False
    
    def get_verification_code(self):
        """認証コードを取得"""
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
                                        print(f"✅ 認証コード発見: {codes[0]}")
                                        return codes[0]
                
                print(f"   待機中... ({attempt + 1}/30)")
                time.sleep(10)
                
            except Exception as e:
                print(f"   メール確認エラー: {e}")
                time.sleep(10)
        
        return None
    
    def save_account_info(self):
        """アカウント情報を保存"""
        account_data = {
            "instagram": self.user_info,
            "email": self.mail_account,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "language": "japanese",
            "proxy_used": self.proxy_session if self.use_proxy else None
        }
        
        # 保存
        account_id = f"IG_JP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        save_dir = f"instagram_accounts/accounts/{account_id}"
        os.makedirs(save_dir, exist_ok=True)
        
        with open(f"{save_dir}/account_info.json", 'w', encoding='utf-8') as f:
            json.dump(account_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 アカウント情報保存完了: {account_id}")
        print(f"   ユーザー名: {self.user_info['username']}")
        print(f"   パスワード: {self.user_info['password']}")
        print(f"   メール: {self.user_info['email']}")
    
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            print("\n10秒後にブラウザを閉じます...")
            time.sleep(10)
            self.driver.quit()

def main():
    print("=== Instagram 日本語版自動アカウント作成システム ===")
    
    # プロキシ使用の選択
    use_proxy = input("\nプロキシを使用しますか？ (y/n): ").lower() == 'y'
    
    creator = InstagramCreatorJapanese(use_proxy=use_proxy)
    
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
            print("\n=== 作成されたアカウント ===")
            print(f"ユーザー名: {creator.user_info['username']}")
            print(f"パスワード: {creator.user_info['password']}")
            print(f"メール: {creator.user_info['email']}")
            print(f"フルネーム: {creator.user_info['fullname']}")
        else:
            print("\n⚠️ アカウント作成に失敗しました")
            
    except Exception as e:
        print(f"\n❌ システムエラー: {e}")
        
    finally:
        creator.close()

if __name__ == "__main__":
    # ディレクトリ作成
    os.makedirs("instagram_accounts/accounts", exist_ok=True)
    os.makedirs("instagram_data/temp", exist_ok=True)
    main()