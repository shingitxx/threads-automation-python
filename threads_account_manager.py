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
        """特定のコンテンツ情報を取得（tree_post対応版）"""
        try:
            # パスの構築
            content_path = os.path.join(self.base_dir, account_id, "contents", content_id)
            
            if not os.path.exists(content_path):
                print(f"❌ コンテンツパスが存在しません: {content_path}")
                return None
            
            # 基本情報
            result = {
                "id": content_id,
                "account_id": account_id
            }
            
            # main.txtを読み込み
            main_txt_path = os.path.join(content_path, 'main.txt')
            if os.path.exists(main_txt_path):
                with open(main_txt_path, 'r', encoding='utf-8') as f:
                    result["main_text"] = f.read().strip()
            else:
                result["main_text"] = ""
            
            # metadata.jsonを読み込み
            metadata_path = os.path.join(content_path, 'metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    result.update(metadata)
            
            # tree_post関連の情報を確実に設定
            if "tree_post" not in result:
                result["tree_post"] = "NO"
            if "tree_text" not in result:
                result["tree_text"] = ""
            if "quote_account" not in result:
                result["quote_account"] = ""
            
            # 画像情報を取得
            result["images"] = self._get_content_images(content_path)
            
            # 旧形式のaffiliate_text互換性（もし存在する場合）
            if "affiliate_text" in result and result.get("tree_post") == "NO":
                # 旧データでtree_postが設定されていない場合、affiliate_textをtree_textとして使用
                result["tree_post"] = "YES"
                result["tree_text"] = result["affiliate_text"]
            
            return result
            
        except Exception as e:
            print(f"❌ コンテンツ取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
    
    def add_new_account(self, account_id, access_token, user_id):
        """新規アカウントを追加する（Cloudinary更新なし）"""
        if not account_id.startswith('ACCOUNT_'):
            account_id = f'ACCOUNT_{account_id}'
        
        try:
            # 1. 環境変数に追加
            self._add_account_env_vars(account_id, access_token, user_id)
            
            # 2. フォルダ構造を作成
            self._create_account_folders(account_id)
            
            # 3. アカウント設定を初期化
            self._initialize_account_settings(account_id)
            
            # 4. アカウント情報を再読み込み
            self.load_accounts()
            
            return {
                'success': True,
                'account_id': account_id,
                'message': f'アカウント {account_id} が正常に追加されました'
            }
        except Exception as e:
            return {
                'success': False,
                'account_id': account_id,
                'message': str(e)
            }

    def _add_account_env_vars(self, account_id, access_token, user_id):
        """環境変数ファイルにアカウント情報を追加"""
        # .envファイルを読み込む
        env_path = '.env'
        lines = []
        
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # アカウントセクションを探す
        account_section_found = False
        user_id_section_found = False
        
        for i, line in enumerate(lines):
            if '# アカウントトークン' in line:
                account_section_found = True
            elif '# インスタグラムユーザーID' in line:
                user_id_section_found = True
        
        # 変更するための新しい行
        token_line = f'TOKEN_{account_id}={access_token}\n'
        user_id_line = f'INSTAGRAM_USER_ID_{account_id}={user_id}\n'
        
        # セクションが見つかった場合、そのセクションに追加
        if account_section_found:
            for i, line in enumerate(lines):
                if '# アカウントトークン' in line:
                    # セクション内の最後に追加
                    j = i + 1
                    while j < len(lines) and lines[j].strip() and not lines[j].startswith('#'):
                        j += 1
                    lines.insert(j, token_line)
                    break
        else:
            # セクションが見つからない場合、ファイルの最後に追加
            lines.append('\n# アカウントトークン\n')
            lines.append(token_line)
        
        if user_id_section_found:
            for i, line in enumerate(lines):
                if '# インスタグラムユーザーID' in line:
                    # セクション内の最後に追加
                    j = i + 1
                    while j < len(lines) and lines[j].strip() and not lines[j].startswith('#'):
                        j += 1
                    lines.insert(j, user_id_line)
                    break
        else:
            # セクションが見つからない場合、ファイルの最後に追加
            lines.append('\n# インスタグラムユーザーID\n')
            lines.append(user_id_line)
        
        # 更新された内容を書き込む
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # 環境変数をメモリに読み込む
        os.environ[f'TOKEN_{account_id}'] = access_token
        os.environ[f'INSTAGRAM_USER_ID_{account_id}'] = user_id

    def _create_account_folders(self, account_id):
        """アカウント用のフォルダ構造を作成"""
        # ベースディレクトリ
        base_dir = os.path.join('accounts', account_id)
        os.makedirs(base_dir, exist_ok=True)
        
        # コンテンツディレクトリ
        contents_dir = os.path.join(base_dir, 'contents')
        os.makedirs(contents_dir, exist_ok=True)
        
        # 設定ディレクトリ
        settings_dir = os.path.join(base_dir, 'settings')
        os.makedirs(settings_dir, exist_ok=True)
        
        # 初期設定ファイル
        settings_file = os.path.join(settings_dir, 'account_settings.json')
        if not os.path.exists(settings_file):
            initial_settings = {
                'account_id': account_id,
                'created_at': datetime.now().isoformat(),
                'status': 'active',
                'content_count': 0
            }
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(initial_settings, f, ensure_ascii=False, indent=2)

    def _initialize_account_settings(self, account_id):
        """アカウントの初期設定を行う"""
        # キャッシュディレクトリの作成
        cache_dir = os.path.join('accounts', '_cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # アカウントキャッシュファイル
        cache_file = os.path.join(cache_dir, f'{account_id}_cache.json')
        if not os.path.exists(cache_file):
            initial_cache = {
                'account_id': account_id,
                'last_updated': datetime.now().isoformat(),
                'content_ids': [],
                'cloudinary_resources': {}
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(initial_cache, f, ensure_ascii=False, indent=2)

    def load_account_tokens(self):
        """アカウントトークンを環境変数から読み込み（add_new_accountで参照されるため追加）"""
        # この実装では環境変数は既に読み込まれているため、特に処理は不要
        # ただし、メソッドが存在しないとエラーになるため空実装を提供
        pass

# モジュールとしてインポートされた場合の動作確認
if __name__ == "__main__":
    # テスト用コード
    manager = ThreadsAccountManager()
    accounts = manager.get_account_ids()
    print(f"アカウント数: {len(accounts)}")
    for account in accounts:
        print(f"- {account}")