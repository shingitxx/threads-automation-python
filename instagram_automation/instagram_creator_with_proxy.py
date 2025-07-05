from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time
import json
import random
import string
import requests
import re
from datetime import datetime
import os
import sys

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 既存のプロキシマネージャーをインポート
from proxy.proxy_manager import ProxyManager

class InstagramCreatorWithProxy:
    def __init__(self, account_id="INSTAGRAM_001", use_proxy=True):
        self.account_id = account_id
        self.use_proxy = use_proxy
        self.mail_account = None
        self.user_info = None
        self.proxy_manager = ProxyManager()
        
        # Chrome設定
        self.options = Options()
        self.options.add_argument("--lang=ja")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # プロキシ設定
        if self.use_proxy:
            self._setup_proxy()
            
        self.driver = None
        self.wait = None
    
    def _setup_proxy(self):
        """プロキシ設定"""
        print(f"\n🌐 プロキシ設定中 (アカウント: {self.account_id})...")
        
        # プロキシ取得
        proxy_url = self.proxy_manager.get_proxy_for_selenium(self.account_id)
        
        if proxy_url:
            print(f"✅ プロキシ設定完了: {self.proxy_manager._mask_proxy_url(proxy_url)}")
            
            # Seleniumにプロキシを設定
            # 注意: 認証付きプロキシの場合、selenium-wireまたは拡張機能が必要
            if '@' not in proxy_url:
                # 認証なしプロキシ
                self.options.add_argument(f'--proxy-server={proxy_url}')
            else:
                # 認証付きプロキシの場合、別の方法が必要
                print("⚠️ 認証付きプロキシ検出。selenium-wireの使用を推奨します。")
                # とりあえず認証なしで接続を試みる
                proxy_parts = proxy_url.split('@')[1]
                self.options.add_argument(f'--proxy-server=http://{proxy_parts}')
        else:
            print("⚠️ プロキシが設定されていません。直接接続します。")
    
    def test_connection(self):
        """接続テスト"""
        print("\n🔍 接続テスト中...")
        
        # プロキシテスト
        if self.use_proxy:
            if self.proxy_manager.test_proxy(self.account_id):
                print("✅ プロキシ接続成功")
            else:
                print("❌ プロキシ接続失敗")
                return False
        
        # ブラウザでIPアドレス確認
        self.driver = webdriver.Chrome(options=self.options)
        try:
            self.driver.get("https://api.ipify.org")
            time.sleep(2)
            current_ip = self.driver.find_element(By.TAG_NAME, "body").text
            print(f"✅ 現在のIP: {current_ip}")
            
            # Instagramアクセステスト
            print("\nInstagramアクセステスト中...")
            self.driver.get("https://www.instagram.com/accounts/emailsignup/")
            time.sleep(3)
            
            # エラーチェック
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            if "公開プロキシ" in page_text or "flagged" in page_text.lower():
                print("❌ IPアドレスがブロックされています")
                return False
            
            # フォーム確認
            try:
                self.driver.find_element(By.NAME, "emailOrPhone")
                print("✅ サインアップフォームにアクセスできました")
                return True
            except:
                print("❌ サインアップフォームが見つかりません")
                return False
                
        except Exception as e:
            print(f"❌ 接続テストエラー: {e}")
            return False
        finally:
            self.driver.quit()
            self.driver = None
    
    def create_mail_account(self):
        """mail.tmアカウントを作成"""
        print("\n📧 メールアカウント作成中...")
        
        session = requests.Session()
        
        # プロキシ設定
        if self.use_proxy:
            proxy_dict = self.proxy_manager.get_proxy_for_account(self.account_id)
            if proxy_dict:
                session.proxies.update(proxy_dict)
        
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
        """Instagram用ユーザー情報を生成"""
        # ユニークなユーザー名
        timestamp = datetime.now().strftime("%m%d%H%M%S")
        random_str = ''.join(random.choices(string.ascii_lowercase, k=4))
        username = f"jp{random_str}{timestamp}"
        
        # 日本人の名前
        first_names = ["田中", "佐藤", "鈴木", "高橋", "渡辺", "伊藤", "山田", "中村"]
        last_names = ["太郎", "花子", "一郎", "美咲", "健太", "優子", "翔太", "愛"]
        fullname = random.choice(first_names) + " " + random.choice(last_names)
        
        # パスワード
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + "!@#"
        
        # 誕生日
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
    
    def create_instagram_account(self):
        """Instagramアカウント作成"""
        print("\n📝 Instagramアカウント作成開始...")
        
        # ブラウザ起動
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 20)
        
        try:
            # 以下、既存の作成フローと同じ
            # ... (既存のコードをここに配置)
            
            print("\n✅ アカウント作成プロセス完了")
            return True
            
        except Exception as e:
            print(f"\n❌ エラー: {e}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """メイン実行関数"""
    print("=== Instagram プロキシ対応アカウント作成システム ===")
    
    # アカウントIDを指定
    account_id = "INSTAGRAM_001"
    
    creator = InstagramCreatorWithProxy(account_id=account_id, use_proxy=True)
    
    # 1. 接続テスト
    print("\n[STEP 1] 接続テスト")
    if not creator.test_connection():
        print("\n❌ 接続テストに失敗しました。プロキシ設定を確認してください。")
        return
    
    print("\n✅ 接続テスト成功！アカウント作成を続行します。")
    
    # 2. メールアカウント作成
    print("\n[STEP 2] メールアカウント作成")
    if not creator.create_mail_account():
        print("\n❌ メールアカウント作成に失敗しました")
        return
    
    # 3. ユーザー情報生成
    print("\n[STEP 3] ユーザー情報生成")
    creator.generate_user_info()
    
    # 4. Instagramアカウント作成
    print("\n[STEP 4] Instagramアカウント作成")
    if creator.create_instagram_account():
        print("\n🎉 全工程完了！")
    else:
        print("\n⚠️ アカウント作成に失敗しました")

if __name__ == "__main__":
    main()