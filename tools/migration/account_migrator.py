"""
アカウントデータ移行用クラス
"""
import os
import shutil
import json
import csv
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

class AccountMigrator:
    """アカウントデータ移行クラス"""
    
    def __init__(self):
        """初期化"""
        self.base_dir = "accounts"
        self.csv_file = "main.csv"
        self.affiliate_json = "src/data/affiliates.json"
    
    def list_available_accounts(self) -> List[str]:
        """CSVからの利用可能なアカウントリストを取得して表示"""
        accounts = self.get_available_accounts()
        
        print("\n📊 === 利用可能なアカウント ===")
        for i, account_id in enumerate(accounts, 1):
            print(f"{i}. {account_id}")
        
        print(f"\n合計: {len(accounts)}アカウント")
        return accounts
    
    def get_available_accounts(self) -> List[str]:
        """CSVからの利用可能なアカウントリストを取得"""
        accounts = set()
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    account_id = row.get('アカウントID')
                    if account_id:
                        accounts.add(account_id)
        except Exception as e:
            print(f"❌ CSV読み込みエラー: {e}")
            return []
        
        return sorted(list(accounts))
    
    def migrate_all_accounts(self, force: bool = False) -> bool:
        """全アカウントのデータを新しいフォルダ構造に移行"""
        accounts = self.get_available_accounts()
        
        if not accounts:
            print("❌ 移行可能なアカウントがありません")
            return False
        
        success_count = 0
        fail_count = 0
        
        for account_id in accounts:
            print(f"\n=== {account_id} の移行を開始 ===")
            
            if self.migrate_account(account_id, force):
                success_count += 1
            else:
                fail_count += 1
        
        print(f"\n📊 === 移行結果 ===")
        print(f"✅ 成功: {success_count}アカウント")
        print(f"❌ 失敗: {fail_count}アカウント")
        
        return fail_count == 0
    
    def migrate_account(self, account_id: str, force: bool = False) -> bool:
        """指定したアカウントのデータを新しいフォルダ構造に移行（コンテンツIDを1から振り直し）"""
        print(f"🚀 {account_id} のデータ移行を開始")
        
        # アカウントディレクトリの確認
        account_dir = os.path.join(self.base_dir, account_id)
        
        if os.path.exists(account_dir) and not force:
            print(f"⚠️ {account_dir} はすでに存在します。--force オプションを使用して上書きしてください。")
            return False
        
        # 基本ディレクトリ構造の作成
        os.makedirs(os.path.join(account_dir, "contents"), exist_ok=True)
        os.makedirs(os.path.join(account_dir, "settings"), exist_ok=True)
        
        # アカウント設定の初期化
        account_settings = {
            "id": account_id,
            "username": account_id,
            "created_at": "2025-06-21",
            "content_count": 0,
            "last_updated": "2025-06-21",
            "content_mapping": {}  # オリジナルIDと新IDのマッピング
        }
        
        # CSVからコンテンツを読み込み
        contents_for_account = []
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['アカウントID'] == account_id:
                        contents_for_account.append(row)
        except Exception as e:
            print(f"❌ CSV読み込みエラー: {e}")
            return False
        
        print(f"📊 {account_id}用コンテンツ: {len(contents_for_account)}件")
        
        # アフィリエイト情報の読み込み
        affiliates = []
        try:
            if os.path.exists(self.affiliate_json):
                with open(self.affiliate_json, 'r', encoding='utf-8') as f:
                    affiliates = json.load(f)
        except Exception as e:
            print(f"⚠️ アフィリエイト情報の読み込みに失敗: {e}")
        
        # コンテンツごとに処理（1から連番で振り直し）
        migrated_count = 0
        content_mapping = {}  # 元のIDと新IDのマッピング
        
        for index, content in enumerate(contents_for_account, 1):
            original_content_id = content['コンテンツID']
            
            # 新しいコンテンツID（3桁の連番）
            new_content_id = f"{account_id}_CONTENT_{index:03d}"
            
            # マッピングを記録
            content_mapping[original_content_id] = new_content_id
            
            result = self._migrate_content(account_id, original_content_id, new_content_id, content, affiliates)
            if result:
                migrated_count += 1
        
        # アカウント設定の更新と保存
        account_settings["content_count"] = migrated_count
        account_settings["content_mapping"] = content_mapping
        
        with open(os.path.join(account_dir, "settings", "account_settings.json"), 'w', encoding='utf-8') as f:
            json.dump(account_settings, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {account_id} の移行完了: {migrated_count}件のコンテンツを移行しました")
        print(f"📊 元のID → 新ID のマッピング:")
        for orig, new in content_mapping.items():
            print(f"  {orig} → {new}")
        
        return True
    
    def _migrate_content(self, account_id: str, original_content_id: str, prefixed_content_id: str,
                         content_data: Dict[str, Any], affiliates: List[Dict[str, Any]]) -> bool:
        """コンテンツを新しいフォルダ構造に移行"""
        print(f"🔄 コンテンツ {original_content_id} → {prefixed_content_id} の移行処理中...")
        
        # コンテンツディレクトリ作成（アカウントプレフィックス方式）
        content_dir = os.path.join(self.base_dir, account_id, "contents", prefixed_content_id)
        os.makedirs(content_dir, exist_ok=True)
        
        # メインテキスト保存
        with open(os.path.join(content_dir, "main.txt"), 'w', encoding='utf-8') as f:
            f.write(content_data['メイン投稿文'])
        
        # 画像ファイル移行（元のコンテンツIDで検索）
        found_main_image = self._migrate_images(original_content_id, content_dir)
        
        # アフィリエイト情報の処理
        affiliate_info = self._find_affiliate(original_content_id, account_id, affiliates)
        
        if affiliate_info:
            with open(os.path.join(content_dir, "affiliate.txt"), 'w', encoding='utf-8') as f:
                f.write(affiliate_info.get('reply_text', ''))
            
            # アフィリエイトメタデータ
            aff_metadata = {
                "id": f"{prefixed_content_id}_AFFILIATE",
                "original_id": affiliate_info.get('id', f"AFF_{original_content_id}"),
                "content_id": prefixed_content_id,
                "original_content_id": original_content_id,
                "account_id": account_id,
                "created_at": "2025-06-21",
                "updated_at": "2025-06-21",
                "usage_count": 0
            }
            
            with open(os.path.join(content_dir, "affiliate_metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(aff_metadata, f, ensure_ascii=False, indent=2)
        
        # メタデータファイル作成
        metadata = {
            "id": prefixed_content_id,
            "original_id": original_content_id,
            "account_id": account_id,
            "created_at": "2025-06-21",
            "updated_at": "2025-06-21",
            "usage_count": int(content_data.get('使用回数', 0)) if content_data.get('使用回数') else 0,
            "has_images": found_main_image > 0,
            "carousel_count": found_main_image - 1 if found_main_image > 1 else 0,
            "is_active": True
        }
        
        with open(os.path.join(content_dir, "metadata.json"), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return True
    
    def _migrate_images(self, content_id: str, content_dir: str) -> int:
        """画像ファイルを移行し、見つかった画像の数を返す"""
        image_count = 0
        
        # メイン画像の検索とコピー
        main_image_patterns = [
            f"images/{content_id}_image.jpg",
            f"images/{content_id}_image.JPG",
            f"images/{content_id}_image.png",
            f"images/{content_id}_image.PNG"
        ]
        
        for src_path in main_image_patterns:
            if os.path.exists(src_path):
                ext = os.path.splitext(src_path)[1]
                dest_path = os.path.join(content_dir, f"image_main{ext}")
                shutil.copy2(src_path, dest_path)
                print(f"✅ メイン画像コピー: {src_path} -> {dest_path}")
                image_count += 1
                break
        
        # 追加画像の検索とコピー (カルーセル用)
        for i in range(1, 10):  # 最大9枚の追加画像
            found = False
            
            carousel_patterns = [
                f"images/{content_id}_{i}_image.jpg",
                f"images/{content_id}_{i}_image.JPG",
                f"images/{content_id}_{i}_image.png",
                f"images/{content_id}_{i}_image.PNG"
            ]
            
            for src_path in carousel_patterns:
                if os.path.exists(src_path):
                    ext = os.path.splitext(src_path)[1]
                    dest_path = os.path.join(content_dir, f"image_{i}{ext}")
                    shutil.copy2(src_path, dest_path)
                    print(f"✅ 追加画像{i}コピー: {src_path} -> {dest_path}")
                    image_count += 1
                    found = True
                    break
            
            if not found:
                break  # 連続性がない場合は終了
        
        return image_count
    
    def _find_affiliate(self, content_id: str, account_id: str, 
                        affiliates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """アフィリエイト情報を検索"""
        for affiliate in affiliates:
            if (affiliate.get('content_id') == content_id and 
                affiliate.get('account_id') == account_id):
                return affiliate
        return None