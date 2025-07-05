import requests
import json
import random
import string
from datetime import datetime

class MailTMTest:
    def __init__(self):
        self.base_url = "https://api.mail.tm"
        self.session = requests.Session()
        
    def generate_random_username(self, length=10):
        """ランダムなユーザー名を生成"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def create_account(self):
        """mail.tmアカウントを作成"""
        print("\n=== mail.tm アカウント作成テスト ===")
        
        # 1. ドメインを取得
        print("1. 利用可能なドメインを取得中...")
        domains_response = self.session.get(f"{self.base_url}/domains")
        domains = domains_response.json()['hydra:member']
        domain = domains[0]['domain']
        print(f"   使用ドメイン: {domain}")
        
        # 2. ランダムなメールアドレスを生成
        username = self.generate_random_username()
        email = f"{username}@{domain}"
        password = self.generate_random_username(12)  # パスワードも生成
        
        print(f"\n2. アカウント情報:")
        print(f"   メールアドレス: {email}")
        print(f"   パスワード: {password}")
        
        # 3. アカウント作成
        print("\n3. アカウントを作成中...")
        account_data = {
            "address": email,
            "password": password
        }
        
        create_response = self.session.post(
            f"{self.base_url}/accounts",
            json=account_data,
            headers={"Content-Type": "application/json"}
        )
        
        if create_response.status_code == 201:
            print("✅ アカウント作成成功！")
            account_info = create_response.json()
            
            # 4. ログイン（トークン取得）
            print("\n4. ログイン中...")
            login_response = self.session.post(
                f"{self.base_url}/token",
                json=account_data,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                token = token_data['token']
                print("✅ ログイン成功！")
                print(f"   トークン: {token[:20]}...（一部表示）")
                
                # アカウント情報を保存
                account_details = {
                    "email": email,
                    "password": password,
                    "token": token,
                    "created_at": datetime.now().isoformat(),
                    "account_id": account_info.get('id', '')
                }
                
                # ファイルに保存
                with open('instagram_data/temp/test_account.json', 'w', encoding='utf-8') as f:
                    json.dump(account_details, f, ensure_ascii=False, indent=2)
                
                print("\n✅ アカウント情報を保存しました: instagram_data/temp/test_account.json")
                
                return account_details
                
            else:
                print(f"❌ ログイン失敗: {login_response.status_code}")
                print(login_response.text)
                
        else:
            print(f"❌ アカウント作成失敗: {create_response.status_code}")
            print(create_response.text)
            
        return None

    def check_messages(self, token):
        """メッセージを確認"""
        print("\n5. メッセージ確認中...")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        messages_response = self.session.get(
            f"{self.base_url}/messages",
            headers=headers
        )
        
        if messages_response.status_code == 200:
            messages = messages_response.json()
            print(f"✅ メッセージ数: {messages['hydra:totalItems']}")
            return messages
        else:
            print(f"❌ メッセージ取得失敗: {messages_response.status_code}")
            return None

if __name__ == "__main__":
    # tempディレクトリを作成
    import os
    os.makedirs('instagram_data/temp', exist_ok=True)
    
    # テスト実行
    tester = MailTMTest()
    account = tester.create_account()
    
    if account:
        print("\n=== テスト成功！===")
        print("作成されたアカウント情報が保存されました。")