"""
カスタムアカウント管理クラス
"""
import os

class MyAccountManager:
    """アカウント管理クラス"""
    
    def __init__(self):
        """初期化"""
        self.base_dir = "accounts"
    
    def get_account_ids(self):
        """利用可能なアカウントIDのリストを取得"""
        if not os.path.exists(self.base_dir):
            print(f"⚠️ アカウントディレクトリが見つかりません: {self.base_dir}")
            return []
        
        return [d for d in os.listdir(self.base_dir) 
                if os.path.isdir(os.path.join(self.base_dir, d))]