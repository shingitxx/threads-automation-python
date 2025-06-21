"""
Threadsアカウント管理システム
新しいフォルダ構造に対応したコンテンツ管理機能を提供
"""
import os
import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

class ThreadsAccountManager:
    """Threadsアカウント管理クラス"""
    
    def __init__(self):
        """初期化"""
        self.base_dir = "accounts"
        self.accounts = {}
        self.load_accounts()
    
    def load_accounts(self):
        """利用可能なアカウント情報を読み込み（_で始まるディレクトリは除外）"""
        if not os.path.exists(self.base_dir):
            print(f"⚠️ アカウントディレクトリが見つかりません: {self.base_dir}")
            return
        
        # _で始まるディレクトリを除外
        for account_dir in [d for d in os.listdir(self.base_dir) 
                        if os.path.isdir(os.path.join(self.base_dir, d)) and not d.startswith('_')]:
            account_path = os.path.join(self.base_dir, account_dir)
            settings_file = os.path.join(account_path, "settings", "account_settings.json")
            
            if os.path.exists(settings_file):
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        account_settings = json.load(f)
                        self.accounts[account_dir] = account_settings
                except Exception as e:
                    print(f"❌ アカウント設定読み込みエラー ({account_dir}): {e}")
            else:
                # 設定ファイルがない場合は基本情報のみ
                self.accounts[account_dir] = {
                    "id": account_dir,
                    "content_count": self._count_contents(account_path)
                }
        
        print(f"📊 読み込んだアカウント: {len(self.accounts)}件")
    
    def _count_contents(self, account_path):
        """アカウントのコンテンツ数をカウント"""
        contents_path = os.path.join(account_path, "contents")
        if os.path.exists(contents_path):
            return len([d for d in os.listdir(contents_path) if os.path.isdir(os.path.join(contents_path, d))])
        return 0
    
    def get_account_ids(self):
        """利用可能なアカウントIDのリストを取得（_で始まるディレクトリは除外）"""
        if not os.path.exists(self.base_dir):
            print(f"⚠️ アカウントディレクトリが見つかりません: {self.base_dir}")
            return []
        
        # _で始まるディレクトリを除外する
        return [d for d in os.listdir(self.base_dir) 
                if os.path.isdir(os.path.join(self.base_dir, d)) and not d.startswith('_')]
    
    def get_account_content_ids(self, account_id):
        """指定したアカウントのコンテンツIDリストを取得"""
        account_contents_dir = os.path.join(self.base_dir, account_id, "contents")
        if not os.path.exists(account_contents_dir):
            return []
        
        return [d for d in os.listdir(account_contents_dir) 
                if os.path.isdir(os.path.join(account_contents_dir, d))]
    
    def get_random_content(self, account_id):
        """指定したアカウントからランダムなコンテンツを取得"""
        content_ids = self.get_account_content_ids(account_id)
        if not content_ids:
            return None
        
        # ランダム選択
        content_id = random.choice(content_ids)
        return self.get_content(account_id, content_id)
    
    def get_content(self, account_id, content_id):
        """指定したコンテンツの情報を取得"""
        content_dir = os.path.join(self.base_dir, account_id, "contents", content_id)
        if not os.path.exists(content_dir):
            return None
        
        result = {
            "id": content_id,
            "account_id": account_id
        }
        
        # メインテキスト読み込み
        main_text_path = os.path.join(content_dir, "main.txt")
        if os.path.exists(main_text_path):
            with open(main_text_path, 'r', encoding='utf-8') as f:
                result["main_text"] = f.read()
        
        # メタデータ読み込み
        metadata_path = os.path.join(content_dir, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                result.update(metadata)
        
        # 画像情報を取得
        result["images"] = self._get_content_images(content_dir)
        
        # アフィリエイト情報
        affiliate_path = os.path.join(content_dir, "affiliate.txt")
        if os.path.exists(affiliate_path):
            with open(affiliate_path, 'r', encoding='utf-8') as f:
                result["affiliate_text"] = f.read()
            
            # アフィリエイトメタデータ
            aff_metadata_path = os.path.join(content_dir, "affiliate_metadata.json")
            if os.path.exists(aff_metadata_path):
                with open(aff_metadata_path, 'r', encoding='utf-8') as f:
                    result["affiliate_metadata"] = json.load(f)
        
        return result
    
    def _get_content_images(self, content_dir):
        """コンテンツディレクトリから画像情報を取得"""
        images = []
        
        # メイン画像
        main_image = None
        for ext in ['.jpg', '.JPG', '.png', '.PNG']:
            path = os.path.join(content_dir, f"image_main{ext}")
            if os.path.exists(path):
                main_image = {
                    "type": "main",
                    "path": path,
                    "filename": os.path.basename(path)
                }
                break
        
        if main_image:
            images.append(main_image)
        
        # 追加画像
        for i in range(1, 10):  # 最大9枚の追加画像
            for ext in ['.jpg', '.JPG', '.png', '.PNG']:
                path = os.path.join(content_dir, f"image_{i}{ext}")
                if os.path.exists(path):
                    images.append({
                        "type": "carousel",
                        "index": i,
                        "path": path,
                        "filename": os.path.basename(path)
                    })
                    break
        
        return images
    
    def get_post_type(self, content):
        """コンテンツの投稿タイプを判定"""
        if not content:
            return "unknown"
        
        images = content.get("images", [])
        if not images:
            return "text"
        elif len(images) == 1:
            return "single_image"
        else:
            return "carousel"
    
    def increment_usage_count(self, account_id, content_id):
        """使用回数をインクリメント"""
        content_dir = os.path.join(self.base_dir, account_id, "contents", content_id)
        metadata_path = os.path.join(content_dir, "metadata.json")
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                metadata["usage_count"] = metadata.get("usage_count", 0) + 1
                metadata["updated_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                return True
            except Exception as e:
                print(f"❌ 使用回数更新エラー: {e}")
        
        return False

# モジュールとしてインポートされた場合の動作確認
if __name__ == "__main__":
    # テスト用コード
    manager = ThreadsAccountManager()
    accounts = manager.get_account_ids()
    print(f"アカウント数: {len(accounts)}")
    for account in accounts:
        print(f"- {account}")