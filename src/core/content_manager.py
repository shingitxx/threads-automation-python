"""
コンテンツ管理システム - CSV ベース実装
CSVファイルからメイン投稿とアフィリエイト内容を読み込み、投稿管理を行う
"""

import csv
import json
import os
import random
import chardet
from config.settings import (
    MAIN_CONTENT_CSV, 
    AFFILIATE_CONTENT_CSV, 
    CONTENT_CACHE_JSON,
    ENCODING_CANDIDATES,
    logger
)

class ContentManager:
    """投稿コンテンツを管理するクラス"""
    
    def __init__(self):
        self.main_csv = MAIN_CONTENT_CSV
        self.affiliate_csv = AFFILIATE_CONTENT_CSV
        self.cache_file = CONTENT_CACHE_JSON
        self.content = self.load_content()
        
    def detect_encoding(self, file_path):
        """ファイルのエンコーディングを検出"""
        # 一部を読み込んでエンコーディングを推測
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            detected = result['encoding']
            
        # 検出されたエンコーディングが未知の場合は候補から試す
        if not detected or detected.lower() == 'ascii':
            for encoding in ENCODING_CANDIDATES:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.read(100)
                        return encoding
                except UnicodeDecodeError:
                    continue
            
            # どのエンコーディングも合わない場合はデフォルト
            return 'utf-8'
        
        return detected
    
    def load_csv(self, file_path):
        """CSVファイルを読み込む（エンコーディング自動判定）"""
        try:
            encoding = self.detect_encoding(file_path)
            logger.info(f"CSVエンコーディング検出: {encoding} - {file_path}")
            
            data = []
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # IDフィールドの標準化（CSVのコンテンツIDをidフィールドとしても追加）
                    if 'コンテンツID' in row and not row.get('id'):
                        row['id'] = row['コンテンツID']
                    if 'アフィリエイトID' in row and not row.get('id'):
                        row['id'] = row['アフィリエイトID']
                    data.append(row)
            
            logger.info(f"CSVデータ読み込み完了: {len(data)}件 - {file_path}")
            return data
        except Exception as e:
            logger.error(f"CSV読み込みエラー ({file_path}): {str(e)}")
            return []
    
    def load_content(self):
        """コンテンツデータを読み込む（キャッシュがあればそれを使用）"""
        try:
            # キャッシュが存在すればそれを使用
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    logger.info(f"キャッシュからコンテンツを読み込みました: {len(content.get('main', []))}件のメイン, {len(content.get('affiliate', []))}件のアフィリエイト")
                    return content
            
            # CSVから読み込み
            main_data = self.load_csv(self.main_csv)
            affiliate_data = self.load_csv(self.affiliate_csv)
            
            content = {
                "main": main_data,
                "affiliate": affiliate_data,
                "posted": [],  # 投稿済みID管理
                "history": []  # 投稿履歴
            }
            
            # キャッシュとして保存
            self.save_content(content)
            
            return content
        except Exception as e:
            logger.error(f"コンテンツ読み込みエラー: {str(e)}")
            return {"main": [], "affiliate": [], "posted": [], "history": []}
    
    def save_content(self, content=None):
        """コンテンツデータをキャッシュとして保存"""
        try:
            if content is None:
                content = self.content
            
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=4)
            
            logger.info("コンテンツをキャッシュに保存しました")
            return True
        except Exception as e:
            logger.error(f"コンテンツ保存エラー: {str(e)}")
            return False
    
    def get_random_post(self, exclude_ids=None):
        """ランダムなメイン投稿を選択（既投稿を除外）"""
        if not self.content["main"]:
            logger.warning("メイン投稿データが空です")
            return None
        
        if exclude_ids is None:
            exclude_ids = self.content.get("posted", [])
        
        # 未投稿のコンテンツをフィルタリング
        available_posts = [
            post for post in self.content["main"] 
            if (post.get("id") not in exclude_ids) and 
               (post.get("コンテンツID") not in exclude_ids)
        ]
        
        # 全て投稿済みの場合はリセット
        if not available_posts:
            logger.info("全投稿が完了したため、投稿履歴をリセットします")
            self.content["posted"] = []
            available_posts = self.content["main"]
        
        # ランダムに選択
        selected_post = random.choice(available_posts)
        
        # 投稿済みに追加
        post_id = selected_post.get("id") or selected_post.get("コンテンツID")
        if post_id:
            self.content["posted"].append(post_id)
            self.save_content()
        
        return selected_post
    
    def get_matching_affiliate(self, main_post):
        """メイン投稿に対応するアフィリエイト投稿を取得"""
        if not self.content["affiliate"]:
            logger.warning("アフィリエイトデータが空です")
            return None
        
        # 優先順位でIDを取得
        post_id = main_post.get("id") or main_post.get("コンテンツID")
        
        if not post_id:
            logger.warning("メイン投稿のIDが見つかりません")
            return random.choice(self.content["affiliate"])
        
        # IDが一致するアフィリエイトを検索（複数のフィールド名に対応）
        matching_affiliates = [
            aff for aff in self.content["affiliate"] 
            if (aff.get("id") == post_id) or 
               (aff.get("コンテンツID") == post_id)
        ]
        
        if matching_affiliates:
            return matching_affiliates[0]
        
        # なければランダムに選択
        return random.choice(self.content["affiliate"])
    
    def add_to_history(self, post_data):
        """投稿履歴に追加"""
        try:
            self.content["history"].append(post_data)
            self.save_content()
            return True
        except Exception as e:
            logger.error(f"履歴追加エラー: {str(e)}")
            return False
    
    def get_posts_for_account(self, account_id):
        """アカウントIDに対応するポストを取得"""
        return [
            post for post in self.content["main"]
            if post.get("アカウントID") == account_id
        ]
    
    def get_affiliates_for_account(self, account_id):
        """アカウントIDに対応するアフィリエイトを取得"""
        return [
            aff for aff in self.content["affiliate"]
            if aff.get("アカウントID") == account_id
        ]
    
    def get_stats(self):
        """コンテンツ統計情報を取得"""
        # アカウント別のコンテンツ数
        account_stats = {}
        for post in self.content["main"]:
            account_id = post.get("アカウントID")
            if account_id:
                if account_id not in account_stats:
                    account_stats[account_id] = {"main": 0, "affiliate": 0}
                account_stats[account_id]["main"] += 1
        
        for aff in self.content["affiliate"]:
            account_id = aff.get("アカウントID")
            if account_id:
                if account_id not in account_stats:
                    account_stats[account_id] = {"main": 0, "affiliate": 0}
                account_stats[account_id]["affiliate"] += 1
        
        return {
            "total_main": len(self.content["main"]),
            "total_affiliate": len(self.content["affiliate"]),
            "account_stats": account_stats,
            "posted_count": len(self.content.get("posted", [])),
            "history_count": len(self.content.get("history", []))
        }

# グローバルインスタンス（他のモジュールでの使用を簡素化）
content_manager = ContentManager()