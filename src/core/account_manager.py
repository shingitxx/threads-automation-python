"""
アカウント管理システム
既存Google Apps Script版との完全互換性を保つアカウント管理機能
"""

import json
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from config.settings import settings
from src.core.threads_api import Account, ThreadsAPI

# グローバルインスタンスを作成（既存コードとの互換性のため）
threads_api = ThreadsAPI()

@dataclass
class AccountInfo:
    """アカウント情報（既存GAS版互換）"""
    id: str
    username: str
    user_id: str
    app_id: str
    last_post_time: Optional[str] = None
    daily_post_count: int = 0
    status: str = "アクティブ"
    access_token: Optional[str] = None
    
    def to_account(self) -> Account:
        """Threads API用のAccountオブジェクトに変換"""
        return Account(
            id=self.id,
            username=self.username,
            user_id=self.user_id,
            access_token=self.access_token or "",
            app_id=self.app_id,
            last_post_time=self.last_post_time,
            daily_post_count=self.daily_post_count,
            status=self.status
        )

class AccountManager:
    """アカウント管理クラス"""
    
    def __init__(self):
        self.accounts_file = settings.data.accounts_path
        self.accounts: Dict[str, AccountInfo] = {}
        self._load_accounts()
        self._load_tokens()
    
    def _load_accounts(self):
        """アカウント情報をファイルから読み込み"""
        try:
            if self.accounts_file.exists():
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    # リスト形式の場合
                    for item in data:
                        if isinstance(item, dict) and 'id' in item:
                            account_info = AccountInfo(**item)
                            self.accounts[account_info.id] = account_info
                elif isinstance(data, dict):
                    # 辞書形式の場合
                    for account_id, account_data in data.items():
                        if isinstance(account_data, dict):
                            account_data['id'] = account_id
                            account_info = AccountInfo(**account_data)
                            self.accounts[account_id] = account_info
            else:
                # ファイルが存在しない場合は既存GAS版のデフォルトアカウントを作成
                self._create_default_accounts()
                
        except Exception as e:
            print(f"⚠️ アカウント読み込みエラー: {e}")
            self._create_default_accounts()
    
    def _create_default_accounts(self):
        """既存GAS版のデフォルトアカウントを作成"""
        default_accounts = [
            AccountInfo(
                id="ACC001",
                username="kana_chan_ura",
                user_id="23881245698173501",
                app_id=settings.threads.app_id,
                status="アクティブ"
            ),
            AccountInfo(
                id="ACCOUNT_002", 
                username="akari_chan_sab",
                user_id="8091935217596688",
                app_id=settings.threads.app_id,
                status="アクティブ"
            )
        ]
        
        for account in default_accounts:
            self.accounts[account.id] = account
            
        self._save_accounts()
        print("✅ デフォルトアカウントを作成しました")
    
    def _load_tokens(self):
        """環境変数からアクセストークンを読み込み"""
        tokens = settings.get_account_tokens()
        
        for account_id, token in tokens.items():
            if account_id in self.accounts:
                self.accounts[account_id].access_token = token
            else:
                print(f"⚠️ 不明なアカウントID: {account_id}")
    
    def _save_accounts(self):
        """アカウント情報をファイルに保存"""
        try:
            # ディレクトリが存在しない場合は作成
            self.accounts_file.parent.mkdir(parents=True, exist_ok=True)
            
            # アクセストークンを除いてJSONに保存
            accounts_data = {}
            for account_id, account in self.accounts.items():
                account_dict = asdict(account)
                # アクセストークンは環境変数で管理するためJSONには保存しない
                account_dict.pop('access_token', None)
                accounts_data[account_id] = account_dict
            
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(accounts_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ アカウント保存エラー: {e}")
    
    def get_active_accounts(self) -> List[Account]:
        """
        アクティブなアカウント一覧を取得（既存GAS版のgetActiveAccounts互換）
        """
        active_accounts = []
        
        for account_info in self.accounts.values():
            if account_info.status == "アクティブ" and account_info.access_token:
                active_accounts.append(account_info.to_account())
        
        return active_accounts
    
    def get_account_by_id(self, account_id: str) -> Optional[Account]:
        """
        IDでアカウントを取得（既存GAS版のgetAccountById互換）
        """
        if account_id in self.accounts:
            account_info = self.accounts[account_id]
            if account_info.access_token:
                return account_info.to_account()
        
        return None
    
    def update_last_post_time(self, account_id: str):
        """
        最終投稿時間を更新（既存GAS版のupdateAccountLastPostUnlimited互換）
        """
        if account_id in self.accounts:
            self.accounts[account_id].last_post_time = datetime.now().isoformat()
            self.accounts[account_id].daily_post_count += 1
            self._save_accounts()
            print(f"📝 {account_id}: 記録更新（制限なし）")
    
    def reset_daily_post_counts(self):
        """
        日次投稿数をリセット（既存GAS版のresetDailyPostCountsFromReply互換）
        """
        for account in self.accounts.values():
            account.daily_post_count = 0
        
        self._save_accounts()
        print("✅ 日次投稿数をリセットしました")
    
    def add_account(self, account_id: str, username: str, user_id: str, 
                   access_token: str, status: str = "アクティブ") -> bool:
        """
        新しいアカウントを追加（既存GAS版のaddAccountEasy互換）
        """
        try:
            # 重複チェック
            if account_id in self.accounts:
                print(f"⚠️ アカウントID {account_id} は既に存在します")
                return False
            
            # ユーザー名重複チェック
            for existing_account in self.accounts.values():
                if existing_account.username == username:
                    print(f"⚠️ ユーザー名 {username} は既に存在します")
                    return False
            
            # 新しいアカウント作成
            new_account = AccountInfo(
                id=account_id,
                username=username,
                user_id=user_id,
                app_id=settings.threads.app_id,
                status=status,
                access_token=access_token
            )
            
            self.accounts[account_id] = new_account
            self._save_accounts()
            
            print(f"✅ アカウント追加: {username} ({account_id})")
            return True
            
        except Exception as e:
            print(f"❌ アカウント追加エラー: {e}")
            return False
    
    def test_account_tokens(self) -> Dict[str, bool]:
        """
        各アカウントのトークン有効性をテスト（既存GAS版のtestAccountTokens互換）
        """
        results = {}
        
        for account_id, account_info in self.accounts.items():
            if account_info.access_token:
                print(f"🔑 {account_info.username} トークンテスト中...")
                
                try:
                    result = threads_api.test_connection(
                        account_info.access_token, 
                        account_info.user_id
                    )
                    results[account_id] = result
                    
                    if result:
                        print(f"✅ {account_info.username}: トークン有効")
                    else:
                        print(f"❌ {account_info.username}: トークン無効")
                        
                except Exception as e:
                    print(f"❌ {account_info.username}: テストエラー - {e}")
                    results[account_id] = False
            else:
                print(f"⚠️ {account_info.username}: トークン未設定")
                results[account_id] = False
        
        return results
    
    def get_account_status(self) -> Dict[str, Any]:
        """
        アカウント状況の詳細情報を取得
        """
        total_accounts = len(self.accounts)
        active_accounts = len([a for a in self.accounts.values() if a.status == "アクティブ"])
        accounts_with_tokens = len([a for a in self.accounts.values() if a.access_token])
        
        return {
            "total_accounts": total_accounts,
            "active_accounts": active_accounts,
            "accounts_with_tokens": accounts_with_tokens,
            "accounts": [
                {
                    "id": account.id,
                    "username": account.username,
                    "status": account.status,
                    "has_token": bool(account.access_token),
                    "last_post_time": account.last_post_time,
                    "daily_post_count": account.daily_post_count
                }
                for account in self.accounts.values()
            ]
        }

# グローバルアカウントマネージャーインスタンス
account_manager = AccountManager()