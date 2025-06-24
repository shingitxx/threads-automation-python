#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
【アカウント初期設定】
Threads自動投稿システム - 新規アカウント追加専用ツール

使用方法:
1. 新しいアカウントのThreads APIアクセストークンを取得
2. setup_new_account() 関数にアクセストークンと希望のアカウントIDを設定
3. 実行してアカウント追加完了

作成日: 2025年6月16日
"""

import os
import sys
import json
import requests
import pandas as pd
import re
import shutil
from dotenv import load_dotenv

# ロガー設定の修正（エンコーディング問題対応）
import logging
import io

# Windows環境でのロガーエンコーディング問題を解決
class EncodingStreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        if stream is None:
            stream = sys.stdout
        super().__init__(stream)
        
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            # Windows環境でエンコードできない文字は置換する
            try:
                stream.write(msg + self.terminator)
            except UnicodeEncodeError:
                # 絵文字を含む場合、安全な文字に置換
                safe_msg = ''.join(c if ord(c) < 0x10000 else '?' for c in msg)
                stream.write(safe_msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# ロガー設定を上書き
logger = logging.getLogger('threads-automation')
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
handler = EncodingStreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# プロジェクトルートをパスに追加
sys.path.append('.')

# 設定
CONFIG = {
    "THREADS_API_BASE": "https://graph.threads.net/v1.0",
    "CSV_FILES": {
        "ACCOUNTS": "accounts.csv"  # アカウント管理CSVファイル
    }
}

# ==============================================
# 【メイン機能】新規アカウントセットアップ
# ==============================================

def setup_new_account(new_account_token=None, account_id=None):
    """
    【推奨】新規アカウント追加 - 自動設定版
    使用方法: アクセストークンを設定して実行するだけ
    """
    print('🚀 === 新規アカウント追加開始 ===')
    
    # 引数が指定されていない場合は対話形式で入力を受け付ける
    if new_account_token is None:
        new_account_token = input("⭐ 新しいアカウントのアクセストークンを入力: ")
    
    if account_id is None:
        account_id = input("⭐ アカウントIDを指定（例: ACCOUNT_012）: ")
    
    if new_account_token == '' or new_account_token == 'YOUR_ACCESS_TOKEN_HERE':
        print('❌ アクセストークンを設定してください')
        return {"success": False, "error": "アクセストークン未設定"}
    
    print(f"🔧 アカウントID: {account_id}")
    print(f"🔑 トークン長: {len(new_account_token)} 文字")
    print(f"🔑 先頭10文字: {new_account_token[:10]}...")
    
    try:
        # Step 1: ユーザー情報取得
        print('\n📡 Step 1: ユーザー情報取得...')
        user_info = get_threads_user_info(new_account_token)
        
        if not user_info["success"]:
            print(f'❌ ユーザー情報取得失敗: {user_info["error"]}')
            display_troubleshooting(user_info.get("response_code"))
            return user_info
        
        print('✅ ユーザー情報取得成功!')
        print(f"   ユーザーID: {user_info['user_id']}")
        print(f"   ユーザー名: {user_info['username']}")
        print(f"   表示名: {user_info['display_name']}")
        
        # Step 2: アクセストークン保存
        print('\n🔐 Step 2: アクセストークン保存...')
        set_account_token(account_id, new_account_token)
        print('✅ アクセストークン保存完了')
        
        # Step 2.5: ユーザーID保存（新規追加）
        print('\n🔐 Step 2.5: ユーザーID保存...')
        set_env_variable(f"INSTAGRAM_USER_ID_{account_id}", user_info['user_id'])
        print(f"✅ ユーザーID保存完了: {user_info['user_id']}")
        
        # Step 3: CSVに追加
        print('\n📊 Step 3: CSVに追加...')
        add_result = add_account_to_csv_safe(account_id, user_info['username'], user_info['user_id'])
        
        if add_result["success"]:
            print('✅ CSV追加完了')
        else:
            print(f"⚠️ {add_result['message']}")
            display_manual_instructions(account_id, user_info)
        
        # Step 4: 設定確認・テスト
        print('\n🔍 Step 4: 設定確認...')
        verify_account_setup(account_id)
        
        print('\n🎉 === 新規アカウント追加完了! ===')
        print(f'🧪 テスト投稿: python final_system.py で起動してメニュー1を選択')
        print(f'🤖 自動投稿: python scheduler_system.py')
        
        return {
            "success": True,
            "account_id": account_id,
            "user_info": user_info
        }
        
    except Exception as error:
        print(f'❌ セットアップエラー: {str(error)}')
        return {"success": False, "error": str(error)}

def bulk_setup_accounts():
    """複数アカウント一括追加"""
    print('🚀 === 複数アカウント一括セットアップ ===')
    
    # ⭐ ここに複数アカウントの情報を設定 ⭐
    accounts_to_add = [
        {
            "id": "ACCOUNT_031",
            "token": "THAAkIds0IIlZABUVJMaFdyUklGQk0xSnpZAWGdYb1dSeFJISU5ic0syUlhXRml2SmR2ZAmpnUHlQLWdiMUNnVlNlSGtuamI2N2s0S3dySHNsdm11SDlyTEV5enV2c3ZAWbjZAXYlRMdzFLVFVaXzBmaE1YQm1pQ0RoUWxtY0ZAwU3FaZA3I2ZAXhCODVpdTZAOd2VQbmMZD",
        },
        {
            "id": "ACCOUNT_032",
            "token": "THAAkIds0IIlZABUVFydWRCZADA2d084S1RNMkNBZAUx6M2tTSFVCdXNUeFZAiYThnRWVPYk5CbTY4dkFqMDY1YWtkQ2pLTm5HR1g2dDV2cmFRMkV3SEVDY1g1YzBrTWlsRWlhZAURUMHBuNW9DempZAOE1aTzV5cVdkaUVMYktJaUFlbnlyUF9fRDNnZAElIeEIyNzQZD",
        },
        {
            "id": "ACCOUNT_033",
            "token": "THAAkIds0IIlZABUVN6QXdFUENnRkZAYRjAyRXNnMFN1ZAEpvaUhrY3J0OERGVm1OUUxaNG1rRzlvTDdqUGNFc1NXN1NxRk15UkEzMHJlTnNEMTNyaFhQc2luby1oMzN4M3lWUzRfeUI2c2s4TzB4TnZAYNl8xeVVDNFo3T1JKV2VWMjhvU2FjQlR5cGtLUjBnaUkZD",
        },
        {
            "id": "ACCOUNT_034",
            "token": "THAAkIds0IIlZABUVNlUDRkTlJhc1lKWThWMVcwWXlZAZA3p4RnVaRlpBcHRleWhQZAE1pbmIwR1BFdktGbFdqN19tS0pJY0lvN2pBajlCVXdxdXVCUHZAOa1lWazMtS2RmbTk1THFJemxsbmJ6Q1ZALSVktYUZAOd1pCWjZAIdEVIMksxOUUyVkJfVTVhRU9TRF9DWUUZD",
        },
        {
            "id": "ACCOUNT_035",
            "token": "THAAkIds0IIlZABUVNUbGY0Y2pwS09YYmtHSXk1XzBFRzBKQUJvNC1HN2RQM25yT1VlUnJ3QWxhSFVIRkttdXJXSEE1RnZAvLUluVEdtRk9feFBzZAHluM3JOa040NF90Vko3ZAEdwcE5kUXo2QkFLVnZAyOXhTU1dQRng0QTQwYWNSa1E0T3NuY2VYZAlFONnJPNTAZD",
        },
        {
            "id": "ACCOUNT_036",
            "token": "THAAkIds0IIlZABUVNnaUhHRFpzWXJ3bW5mMkZAkTFJja3hSOEpWcmdlWEJsWHdrdnlmeHZATOVZAVeXhwQm9ob1lzZAVBrWFJMZAHZA1d1NqNW54SjVRYXBDU05ra0JUN1NRbDRKUEJqQzZAad0xPTmxRVGtTR083NXd2dmpFWG9TOVUwUlhuS1ppUWpZAeUF5c3lwVUUZD",
        }
        # 必要に応じて追加...
    ]
    
    success_count = 0
    fail_count = 0
    
    for i, account in enumerate(accounts_to_add):
        print(f"\n🔄 {i + 1}/{len(accounts_to_add)}: {account['id']} 処理中...")
        
        if account["token"] == "YOUR_TOKEN_HERE":
            print(f"⚠️ {account['id']}: トークンが未設定")
            fail_count += 1
            continue
        
        result = setup_account_with_token(account["id"], account["token"])
        
        if result["success"]:
            print(f"✅ {account['id']}: 成功")
            success_count += 1
        else:
            print(f"❌ {account['id']}: 失敗")
            fail_count += 1
        
        # API制限を避けるため待機
        if i < len(accounts_to_add) - 1:
            import time
            time.sleep(2)
    
    print('\n📊 === 一括セットアップ結果 ===')
    print(f"✅ 成功: {success_count} アカウント")
    print(f"❌ 失敗: {fail_count} アカウント")
    if success_count + fail_count > 0:
        print(f"📈 成功率: {round(success_count / (success_count + fail_count) * 100)}%")

# ==============================================
# 【ユーティリティ】アカウント情報取得
# ==============================================

def get_threads_user_info(access_token):
    """Threads APIからユーザー情報取得"""
    try:
        if not access_token:
            return {"success": False, "error": "アクセストークンが指定されていません"}

        response = requests.get(
            f"{CONFIG['THREADS_API_BASE']}/me?fields=id,username,name,threads_profile_picture_url,threads_biography",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        response_code = response.status_code
        response_text = response.text

        print(f"📡 API応答コード: {response_code}")

        if response_code == 200:
            user_data = response.json()
            
            return {
                "success": True,
                "user_id": user_data.get("id"),
                "username": user_data.get("username"),
                "display_name": user_data.get("name", ""),
                "profile_picture_url": user_data.get("threads_profile_picture_url", ""),
                "biography": user_data.get("threads_biography", ""),
                "full_response": user_data
            }
            
        else:
            print(f"❌ API呼び出し失敗: {response_code}")
            print(f"エラー詳細: {response_text}")
            
            return {
                "success": False,
                "error": f"API呼び出し失敗: {response_code} - {response_text}",
                "response_code": response_code
            }

    except Exception as error:
        print(f"❌ ユーザー情報取得エラー: {str(error)}")
        return {
            "success": False,
            "error": str(error)
        }

def setup_account_with_token(account_id, access_token):
    """汎用アカウントセットアップ関数"""
    if access_token == "YOUR_TOKEN_HERE":
        print(f"❌ {account_id} のアクセストークンを設定してください")
        return {"success": False, "error": "アクセストークン未設定"}
    
    print(f"🔧 {account_id} セットアップ開始...")
    
    user_info = get_threads_user_info(access_token)
    if not user_info["success"]:
        print(f"❌ {account_id} のユーザー情報取得失敗: {user_info['error']}")
        return user_info
    
    # トークン保存 - 直接環境変数ファイルに追加（問題箇所修正）
    token_key = f"TOKEN_{account_id}"
    set_direct_env_value(token_key, access_token)
    print(f"✅ {account_id} のトークンを直接設定しました")
    
    # ユーザーIDを環境変数に保存（新規追加）
    user_id = user_info["user_id"]
    set_env_variable(f"INSTAGRAM_USER_ID_{account_id}", user_id)
    print(f"✅ {account_id} 用のユーザーID保存完了: {user_id}")
    
    # CSV追加
    add_result = add_account_to_csv_safe(account_id, user_info["username"], user_info["user_id"])
    
    if add_result["success"]:
        print(f"✅ {account_id} ({user_info['username']}) 追加完了")
        verify_account_setup(account_id)
        return {"success": True, "account_id": account_id, "user_info": user_info}
    else:
        print(f"⚠️ {add_result['message']}")
        display_manual_instructions(account_id, user_info)
        return {"success": False, "error": add_result["message"]}

# ==============================================
# 【CSVファイル操作】
# ==============================================

def add_account_to_csv_safe(account_id, username, user_id):
    """安全なアカウント追加（重複チェック付き）"""
    try:
        accounts_file = CONFIG["CSV_FILES"]["ACCOUNTS"]
        
        # CSVファイルが存在するか確認
        if not os.path.exists(accounts_file):
            # 新規作成
            df = pd.DataFrame({
                "account_id": [account_id],
                "username": [username],
                "app_id": ["2542581129421398"],
                "user_id": [user_id],
                "last_post_time": [""],
                "daily_post_count": [0],
                "status": ["アクティブ"]
            })
            df.to_csv(accounts_file, index=False)
            return {"success": True, "message": f"新規作成: {account_id} を追加しました"}
        
        # 既存ファイル読み込み
        df = pd.read_csv(accounts_file)
        
        # 重複チェック
        if account_id in df["account_id"].values:
            return {"success": False, "message": f"アカウントID {account_id} は既に存在します"}
        
        if username in df["username"].values:
            return {"success": False, "message": f"ユーザー名 {username} は既に存在します"}
        
        # 新規追加
        new_row = pd.DataFrame({
            "account_id": [account_id],
            "username": [username],
            "app_id": ["2542581129421398"],
            "user_id": [user_id],
            "last_post_time": [""],
            "daily_post_count": [0],
            "status": ["アクティブ"]
        })
        
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(accounts_file, index=False)
        
        return {"success": True, "message": f"{account_id} を追加しました"}
        
    except Exception as error:
        print(f"CSV追加エラー: {str(error)}")
        return {"success": False, "message": f"エラー: {str(error)}"}

# ==============================================
# 【環境変数操作】
# ==============================================

def set_direct_env_value(key, value):
    """環境変数を直接設定する関数（問題箇所対応用）"""
    try:
        env_file = ".env"
        
        # .envファイルが存在するか確認
        if os.path.exists(env_file):
            # 既存ファイル読み込み
            with open(env_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # 該当キーがあれば置換、なければ追加
            key_found = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{key}="):
                    lines[i] = f"{key}={value}\n"
                    key_found = True
                    break
            
            if not key_found:
                # アカウントトークンセクションを探す
                account_section_index = -1
                for i, line in enumerate(lines):
                    if line.strip() == "# アカウントトークン":
                        account_section_index = i
                        break
                
                if account_section_index >= 0:
                    # アカウントトークンセクションの最後に追加
                    end_index = account_section_index + 1
                    while end_index < len(lines):
                        if lines[end_index].strip() == "" or lines[end_index].strip().startswith("#"):
                            break
                        end_index += 1
                    
                    lines.insert(end_index, f"{key}={value}\n")
                else:
                    # セクションが見つからない場合は末尾に追加
                    lines.append(f"\n# アカウントトークン\n{key}={value}\n")
            
            # ファイルに書き戻し
            with open(env_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
            
            print(f"✅ 環境変数 {key} を直接設定しました")
            
            # ファイル内容を確認
            debug_env_file()
            
            return True
        else:
            # ファイルがない場合は新規作成
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"{key}={value}\n")
            
            print(f"✅ 新規環境変数ファイルに {key} を設定しました")
            return True
            
    except Exception as error:
        print(f"❌ 環境変数設定エラー: {str(error)}")
        return False

def debug_env_file():
    """環境変数ファイルの内容を確認（デバッグ用）"""
    try:
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            print("\n=== 環境変数ファイル内容（デバッグ） ===")
            for line in content.split('\n'):
                if line.strip().startswith("TOKEN_ACCOUNT_"):
                    print(f"トークン検出: {line.strip()}")
    except Exception as e:
        print(f"デバッグ表示エラー: {str(e)}")

def set_account_token(account_id, token):
    """アカウントトークンを.envファイルに保存"""
    try:
        env_file = ".env"
        
        # .envファイルが存在するか確認
        if os.path.exists(env_file):
            # 既存ファイル読み込み
            with open(env_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # TOKEN_ACCOUNT_XXXの行があれば置換、なければ追加
            token_key = f"TOKEN_{account_id}"
            token_line = f"{token_key}={token}\n"
            
            token_found = False
            for i, line in enumerate(lines):
                if line.startswith(token_key):
                    lines[i] = token_line
                    token_found = True
                    break
            
            if not token_found:
                # アカウントトークンセクションを探す
                account_section_found = False
                for i, line in enumerate(lines):
                    if "# アカウントトークン" in line:
                        # セクションの最後に追加
                        section_end = i + 1
                        while section_end < len(lines) and not lines[section_end].strip().startswith("#") and lines[section_end].strip():
                            section_end += 1
                        lines.insert(section_end, token_line)
                        account_section_found = True
                        break
                
                if not account_section_found:
                    lines.append(token_line)
            
            # 書き戻し
            with open(env_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
        else:
            # 新規作成
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"{token_key}={token}\n")
        
        print(f"✅ {account_id} のトークンを.envファイルに保存しました")
        return True
        
    except Exception as error:
        print(f"❌ トークン保存エラー: {str(error)}")
        return False

def set_env_variable(key, value):
    """環境変数を.envファイルに保存（位置を整理して追加）"""
    try:
        env_file = ".env"
        
        # .envファイルが存在するか確認
        if os.path.exists(env_file):
            # 既存ファイル読み込み
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 行単位に分割し、各行を確実にstrip
            lines = [line.strip() for line in content.split('\n')]
            
            # キーごとにグループ化して整理
            sections = {
                "THREADS": [],   # メイントークン
                "ACCOUNT": [],   # アカウント関連
                "INSTAGRAM": [], # インスタグラムID
                "CLOUDINARY": [],  # Cloudinary設定
                "OTHER": []      # その他
            }
            
            # 既存行を分類
            for line in lines:
                if not line or line.startswith("#"):
                    continue
                    
                if line.startswith("THREADS_ACCESS_TOKEN="):
                    sections["THREADS"].append(line)
                elif line.startswith("TOKEN_ACCOUNT_"):
                    sections["ACCOUNT"].append(line)
                elif line.startswith("INSTAGRAM_USER_ID"):
                    sections["INSTAGRAM"].append(line)
                elif line.startswith("CLOUDINARY_"):
                    sections["CLOUDINARY"].append(line)
                else:
                    sections["OTHER"].append(line)
            
            # 新しい行を適切なセクションに追加
            new_line = f"{key}={value}"
            if key.startswith("TOKEN_ACCOUNT_"):
                # すでに存在するかチェック
                if new_line not in sections["ACCOUNT"]:
                    sections["ACCOUNT"].append(new_line)
            elif key.startswith("INSTAGRAM_USER_ID"):
                if new_line not in sections["INSTAGRAM"]:
                    sections["INSTAGRAM"].append(new_line)
            else:
                if new_line not in sections["OTHER"]:
                    sections["OTHER"].append(new_line)
            
            # セクション順に書き出し
            with open(env_file, "w", encoding="utf-8") as f:
                if sections["THREADS"]:
                    f.write("# Threads API設定\n")
                    for line in sections["THREADS"]:
                        f.write(f"{line}\n")
                    f.write("\n")
                
                if sections["INSTAGRAM"]:
                    f.write("# インスタグラムユーザーID\n")
                    for line in sections["INSTAGRAM"]:
                        f.write(f"{line}\n")
                    f.write("\n")
                
                if sections["ACCOUNT"]:
                    f.write("# アカウントトークン\n")
                    for line in sections["ACCOUNT"]:
                        f.write(f"{line}\n")
                    f.write("\n")
                
                if sections["CLOUDINARY"]:
                    f.write("# Cloudinary設定\n")
                    for line in sections["CLOUDINARY"]:
                        f.write(f"{line}\n")
                    f.write("\n")
                
                if sections["OTHER"]:
                    f.write("# その他設定\n")
                    for line in sections["OTHER"]:
                        f.write(f"{line}\n")
        else:
            # 新規作成
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"{key}={value}\n")
        
        print(f"✅ 環境変数 {key} を.envファイルに保存しました")
        return True
        
    except Exception as error:
        print(f"❌ 環境変数保存エラー: {str(error)}")
        return False

# ==============================================
# 【確認・テスト機能】
# ==============================================

def verify_account_setup(account_id):
    """アカウント設定確認"""
    try:
        print(f"🔍 {account_id} 設定確認中...")
        
        # .env確認
        token_exists = check_token_exists(account_id)
        
        # ユーザーID確認（新規追加）
        user_id_exists = check_user_id_exists(account_id)
        
        # CSV確認
        account_info = get_account_from_csv(account_id)
        
        if account_info:
            print(f"✅ CSV認識: {account_info['username']}")
            print(f"✅ ユーザーID: {account_info['user_id']}")
            print(f"✅ アクセストークン: {'設定済み' if token_exists else '未設定'}")
            print(f"✅ 固有ユーザーID: {'設定済み' if user_id_exists else '未設定'}")
            return True
        else:
            print(f"❌ {account_id} がCSVに見つかりません")
            return False
        
    except Exception as error:
        print(f"設定確認エラー: {str(error)}")
        return False

def check_token_exists(account_id):
    """トークンが.envに存在するか確認"""
    try:
        # .envファイル読み込み
        load_dotenv()
        token = os.getenv(f"TOKEN_{account_id}")
        return token is not None
    except:
        return False

def check_user_id_exists(account_id):
    """ユーザーIDが.envに存在するか確認"""
    try:
        # .envファイル読み込み
        load_dotenv()
        user_id = os.getenv(f"INSTAGRAM_USER_ID_{account_id}")
        return user_id is not None
    except:
        return False

def get_account_from_csv(account_id):
    """CSVからアカウント情報取得"""
    try:
        accounts_file = CONFIG["CSV_FILES"]["ACCOUNTS"]
        
        if not os.path.exists(accounts_file):
            return None
        
        df = pd.read_csv(accounts_file)
        
        account_row = df[df["account_id"] == account_id]
        if len(account_row) == 0:
            return None
        
        return {
            "account_id": account_id,
            "username": account_row["username"].values[0],
            "user_id": account_row["user_id"].values[0]
        }
    except:
        return None

# ==============================================
# 【エラー対処・ヘルプ機能】
# ==============================================

def display_troubleshooting(response_code):
    """トラブルシューティング表示"""
    print('\n🔧 === トラブルシューティング ===')
    
    if response_code == 400:
        print('🚫 400 Bad Request - リクエスト形式エラー')
        print('   対処法: アクセストークンの形式を確認')
    elif response_code == 401:
        print('🔑 401 Unauthorized - 認証エラー')
        print('   対処法1: 新しいアクセストークンを生成')
        print('   対処法2: Meta Developers でアプリ設定確認')
    elif response_code == 403:
        print('🚫 403 Forbidden - 権限不足')
        print('   対処法: Threads API の権限を有効化')
    elif response_code == 500:
        print('💥 500 Internal Server Error - サーバーエラー')
        print('   対処法1: しばらく待ってから再実行')
        print('   対処法2: Meta Developers でアプリ設定確認')
    else:
        print(f'❓ {response_code} 予期しないエラー')
        print('   対処法: Meta Developers サポートに問い合わせ')
    
    print('\n📋 共通確認事項:')
    print('   - Threads API が有効化されているか')
    print('   - アプリが「本番」モードになっているか')
    print('   - 適切な権限が設定されているか')

def display_manual_instructions(account_id, user_info):
    """手動設定手順表示"""
    print('\n📋 === 手動設定手順 ===')
    print('CSVファイル「accounts.csv」に以下を追加:')
    print('=====================================')
    print(f'アカウントID: {account_id}')
    print(f'ユーザー名: {user_info["username"]}')
    print(f'アプリID: 2542581129421398')
    print(f'ユーザーID: {user_info["user_id"]}')
    print(f'最終投稿時間: (空欄)')
    print(f'日次投稿数: 0')
    print(f'ステータス: アクティブ')
    print('=====================================')

# ==============================================
# 【便利機能】トークン管理
# ==============================================

def list_saved_tokens():
    """保存済みトークン一覧表示"""
    print('🔍 === 保存済みトークン一覧 ===')
    
    try:
        # .envファイル読み込み
        load_dotenv()
        
        # 環境変数からTOKEN_で始まるものを抽出
        token_keys = [key for key in os.environ.keys() if key.startswith("TOKEN_")]
        
        if len(token_keys) == 0:
            print('❌ 保存されているトークンがありません')
            return
        
        for key in token_keys:
            account_id = key.replace("TOKEN_", "")
            token = os.getenv(key)
            masked_token = token[:20] + "..." if token else "未設定"
            print(f"{account_id}: {masked_token}")
        
        print(f"\n📊 合計 {len(token_keys)} 個のトークンが保存されています")
    except Exception as e:
        print(f"エラー: {str(e)}")

def remove_account_token(account_id):
    """特定アカウントのトークン削除"""
    try:
        env_file = ".env"
        
        if os.path.exists(env_file):
            # ファイル読み込み
            with open(env_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # TOKEN_ACCOUNT_XXXの行を削除
            token_key = f"TOKEN_{account_id}"
            new_lines = [line for line in lines if not line.startswith(token_key)]
            
            # 書き戻し
            with open(env_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            print(f"✅ {account_id} のトークンを削除しました")
        else:
            print("❌ .envファイルが見つかりません")
    except Exception as error:
        print(f"❌ {account_id} のトークン削除エラー: {str(error)}")

def reorganize_env_file():
    """環境変数ファイルを整理して見やすくする"""
    print("\n🔄 === 環境変数ファイルの整理 ===")
    
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"❌ {env_file} ファイルが見つかりません")
        return False
    
    try:
        # 既存ファイル読み込み
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 行単位に分割し、各行を確実にstrip
        lines = [line.strip() for line in content.split('\n')]
        
        # 空でない行のみ抽出
        valid_lines = [line for line in lines if line and not line.startswith("#")]
        
        # セクションごとに分類
        sections = {
            "THREADS": [],   # メイントークン
            "INSTAGRAM": [], # インスタグラムID
            "ACCOUNT": [],   # アカウント関連
            "CLOUDINARY": [],  # Cloudinary設定
            "OTHER": []      # その他
        }
        
        # 既存行を分類
        for line in valid_lines:
            if line.startswith("THREADS_ACCESS_TOKEN="):
                sections["THREADS"].append(line)
            elif line.startswith("TOKEN_ACCOUNT_"):
                sections["ACCOUNT"].append(line)
            elif line.startswith("INSTAGRAM_USER_ID"):
                sections["INSTAGRAM"].append(line)
            elif line.startswith("CLOUDINARY_"):
                sections["CLOUDINARY"].append(line)
            elif line.startswith("TEST_MODE="):
                sections["OTHER"].append(line)
            else:
                sections["OTHER"].append(line)
        
        # バックアップを作成
        backup_file = f"{env_file}.bak"
        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 元の.envファイルをバックアップしました: {backup_file}")
        
        # 整理して書き出し
        with open(env_file, "w", encoding="utf-8") as f:
            if sections["THREADS"]:
                f.write("# Threads API設定\n")
                for line in sections["THREADS"]:
                    f.write(f"{line}\n")
                f.write("\n")
            
            if sections["INSTAGRAM"]:
                f.write("# インスタグラムユーザーID\n")
                for line in sections["INSTAGRAM"]:
                    f.write(f"{line}\n")
                f.write("\n")
            
            if sections["ACCOUNT"]:
                f.write("# アカウントトークン\n")
                sections["ACCOUNT"].sort()  # アカウントを番号順に整列
                for line in sections["ACCOUNT"]:
                    f.write(f"{line}\n")
                f.write("\n")
            
            if sections["CLOUDINARY"]:
                f.write("# Cloudinary設定\n")
                for line in sections["CLOUDINARY"]:
                    f.write(f"{line}\n")
                f.write("\n")
            
            if sections["OTHER"]:
                f.write("# その他設定\n")
                for line in sections["OTHER"]:
                    f.write(f"{line}\n")
        
        print(f"✅ 環境変数ファイルを整理しました")
        
        # トークン確認
        debug_env_file()
        
        return True
        
    except Exception as error:
        print(f"❌ 環境変数ファイル整理エラー: {str(error)}")
        return False

def repair_existing_accounts():
    """既存のアカウントを修復してユーザーIDを設定"""
    print("\n🔧 === 既存アカウント修復 ===")
    
    # 環境変数から既存のトークンを読み込む
    load_dotenv()
    
    # トークンキーを検索
    token_keys = [key for key in os.environ.keys() if key.startswith("TOKEN_ACCOUNT_")]
    
    if not token_keys:
        print("❌ 修復が必要なアカウントが見つかりません")
        return
    
    print(f"🔍 {len(token_keys)}個のアカウントを検出しました")
    
    success_count = 0
    fail_count = 0
    
    for token_key in token_keys:
        account_id = token_key.replace("TOKEN_", "")
        token = os.getenv(token_key)
        
        # すでにユーザーIDが設定されているかチェック
        user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
        existing_user_id = os.getenv(user_id_key)
        
        if existing_user_id:
            print(f"✅ {account_id} は既にユーザーID {existing_user_id} が設定されています")
            success_count += 1
            continue
        
        print(f"🔄 {account_id} のユーザーIDを取得中...")
        
        # ユーザー情報を取得
        user_info = get_threads_user_info(token)
        if user_info["success"]:
            user_id = user_info["user_id"]
            # ユーザーIDを設定
            set_env_variable(user_id_key, user_id)
            print(f"✅ {account_id} にユーザーID {user_id} を設定しました")
            success_count += 1
        else:
            print(f"❌ {account_id} のユーザーID取得に失敗: {user_info['error']}")
            fail_count += 1
    
    print(f"\n📊 === 修復結果 ===")
    print(f"✅ 成功: {success_count}件")
    print(f"❌ 失敗: {fail_count}件")
    
    if success_count > 0:
        print("\n💡 環境変数を変更しました。システムを再起動して変更を反映してください。")

def add_missing_token_account():
    """不足しているアカウントトークンを追加（緊急修正）"""
    print("\n🚨 === 不足アカウントトークン追加 ===")
    
    account_id = "ACCOUNT_009"
    token = "THAAkIds0IIlZABUVNzdVF6MnNVa1pfTWw5MkFNUmNOYU5hNm9kQUFKTDZAQTFBqRXVIUmZA1cVU4SmNkaFBkNVBGckItYWRPVERjcXZA1akFlWUQwaU4yZAlUwRHFnR2ZACZATBUQ0xhSVJWLWJMOUg0MkxObzNlaUl2S1c5UmNya0ZATU1U3Ujdkck9qUndrd1NJbTgZD"
    
    print(f"🔍 {account_id} のトークンを設定します...")
    
    # 既存の.envファイルを読み込み
    env_file = ".env"
    
    try:
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # すでにトークンが含まれているか確認
            token_key = f"TOKEN_{account_id}"
            if f"{token_key}=" in content:
                print(f"✅ {account_id} のトークンは既に設定されています")
                return True
            
            # アカウントトークンセクションを見つける
            lines = content.split('\n')
            account_section_index = -1
            
            for i, line in enumerate(lines):
                if line.strip() == "# アカウントトークン":
                    account_section_index = i
                    break
            
            if account_section_index >= 0:
                # セクションの末尾に追加
                end_index = account_section_index + 1
                while end_index < len(lines) and not (lines[end_index].strip() == "" or lines[end_index].strip().startswith("#")):
                    end_index += 1
                
                lines.insert(end_index, f"{token_key}={token}")
                
                # 書き戻し
                with open(env_file, "w", encoding="utf-8") as f:
                    f.write('\n'.join(lines))
                
                print(f"✅ {account_id} のトークンを追加しました")
            else:
                # セクションがなければ追加
                with open(env_file, "a", encoding="utf-8") as f:
                    f.write(f"\n# アカウントトークン\n{token_key}={token}\n")
                
                print(f"✅ {account_id} のトークンをセクションごと追加しました")
            
            return True
        else:
            print(f"❌ .envファイルが見つかりません")
            return False
    except Exception as e:
        print(f"❌ トークン追加エラー: {str(e)}")
        return False

# ==============================================
# 【環境変数修復機能 - 新規追加】
# ==============================================

def fix_env_file():
    """
    .envファイルのCLOUDINARY_API_SECRETとTOKEN_ACCOUNT_009の問題を修正
    重複するTOKEN_ACCOUNT_009エントリーも削除
    """
    print("🔧 .envファイル修正を開始します...")
    
    env_file = ".env"
    
    # ファイルが存在しない場合はエラー
    if not os.path.exists(env_file):
        print(f"❌ {env_file} が見つかりません。")
        return False
    
    # バックアップ作成
    backup_file = f"{env_file}.complete.backup"
    shutil.copy2(env_file, backup_file)
    print(f"✅ バックアップを作成しました: {backup_file}")
    
    try:
        # ファイル内容を読み込み
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # 修正したい内容
        new_lines = []
        sections = {
            "THREADS": [],
            "INSTAGRAM": [],
            "ACCOUNT": [],
            "CLOUDINARY": [],
            "OTHER": []
        }
        
        # トークンの値を保存
        account_tokens = {}
        
        # 行を解析
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # セクション見出しをスキップ
            if line.startswith("#"):
                continue
                
            # 行を分類
            if line.startswith("THREADS_ACCESS_TOKEN="):
                sections["THREADS"].append(line)
            elif line.startswith("INSTAGRAM_USER_ID"):
                sections["INSTAGRAM"].append(line)
            elif line.startswith("TOKEN_ACCOUNT_"):
                # トークン名を抽出
                parts = line.split("=", 1)
                if len(parts) == 2:
                    token_name = parts[0]
                    token_value = parts[1]
                    # まだ保存されていないトークンのみ保存
                    if token_name not in account_tokens:
                        account_tokens[token_name] = token_value
            elif line.startswith("CLOUDINARY_"):
                # CLOUDINARY_API_SECRETが連結問題を持っている場合を修正
                if line.startswith("CLOUDINARY_API_SECRET="):
                    pattern = r"CLOUDINARY_API_SECRET=([a-zA-Z0-9]+)TOKEN_ACCOUNT_"
                    match = re.search(pattern, line)
                    if match:
                        # 正しい値を取得して保存
                        secret_value = match.group(1)
                        sections["CLOUDINARY"].append(f"CLOUDINARY_API_SECRET={secret_value}")
                        
                        # 残りの部分からTOKEN_ACCOUNT_部分を抽出
                        token_part = line[line.find("TOKEN_ACCOUNT_"):]
                        token_parts = token_part.split("=", 1)
                        if len(token_parts) == 2:
                            token_name = token_parts[0]
                            token_value = token_parts[1]
                            # アカウントトークンとして保存
                            if token_name not in account_tokens:
                                account_tokens[token_name] = token_value
                    else:
                        # 連結問題がなければそのまま追加
                        sections["CLOUDINARY"].append(line)
                else:
                    # その他のCloudinary設定はそのまま追加
                    sections["CLOUDINARY"].append(line)
            else:
                sections["OTHER"].append(line)
        
        # アカウントトークンを追加
        for token_name, token_value in account_tokens.items():
            sections["ACCOUNT"].append(f"{token_name}={token_value}")
        
        # 整理して書き出し
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("# Threads API設定\n")
            for line in sections["THREADS"]:
                f.write(f"{line}\n")
            f.write("\n")
            
            f.write("# インスタグラムユーザーID\n")
            for line in sections["INSTAGRAM"]:
                f.write(f"{line}\n")
            f.write("\n")
            
            f.write("# アカウントトークン\n")
            for line in sections["ACCOUNT"]:
                f.write(f"{line}\n")
            f.write("\n")
            
            f.write("# Cloudinary設定\n")
            for line in sections["CLOUDINARY"]:
                f.write(f"{line}\n")
            f.write("\n")
            
            f.write("# その他設定\n")
            for line in sections["OTHER"]:
                f.write(f"{line}\n")
        
        print("✅ 環境変数ファイルを完全に修正しました。")
        
        # 修正後の内容を確認
        print("\n=== 修正後の環境変数 ===")
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    print(line)
                elif line.startswith("CLOUDINARY_API_SECRET="):
                    print("CLOUDINARY_API_SECRET=***（値は秘密）")
                elif line.startswith("TOKEN_ACCOUNT_"):
                    account_id = line.split("=")[0].replace("TOKEN_ACCOUNT_", "")
                    print(f"TOKEN_ACCOUNT_{account_id}=***（値は秘密）")
                elif line.startswith("THREADS_ACCESS_TOKEN="):
                    print("THREADS_ACCESS_TOKEN=***（値は秘密）")
                else:
                    print(line)
        
        # セクションごとのチェック
        verify_env_file()
        
        return True
    
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        print("🔄 バックアップから復元します...")
        shutil.copy2(backup_file, env_file)
        print("✅ バックアップから復元しました。")
        return False

def verify_env_file():
    """環境変数ファイルの整合性を検証"""
    print("\n🔍 環境変数の整合性を確認しています...")
    
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"❌ {env_file} が見つかりません。")
        return False
    
    try:
        # 各セクションのアイテム数
        counts = {
            "THREADS": 0,
            "INSTAGRAM": 0,
            "ACCOUNT": 0,
            "CLOUDINARY": 0,
            "OTHER": 0
        }
        
        # TOKEN_ACCOUNT_009の出現回数
        token_009_count = 0
        
        with open(env_file, "r", encoding="utf-8") as f:
            current_section = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # セクション見出しの検出
                if line.startswith("# Threads API"):
                    current_section = "THREADS"
                elif line.startswith("# インスタグラム"):
                    current_section = "INSTAGRAM"
                elif line.startswith("# アカウントトークン"):
                    current_section = "ACCOUNT"
                elif line.startswith("# Cloudinary"):
                    current_section = "CLOUDINARY"
                elif line.startswith("# その他"):
                    current_section = "OTHER"
                # 内容の検出
                elif not line.startswith("#") and current_section:
                    counts[current_section] += 1
                
                # TOKEN_ACCOUNT_009の検出
                if line.startswith("TOKEN_ACCOUNT_009="):
                    token_009_count += 1
        
        # 結果出力
        print("\n📊 環境変数セクション集計:")
        print(f"  Threads API設定: {counts['THREADS']}項目")
        print(f"  インスタグラムユーザーID: {counts['INSTAGRAM']}項目")
        print(f"  アカウントトークン: {counts['ACCOUNT']}項目")
        print(f"  Cloudinary設定: {counts['CLOUDINARY']}項目")
        print(f"  その他設定: {counts['OTHER']}項目")
        
        # TOKEN_ACCOUNT_009の確認
        print(f"\n🔑 TOKEN_ACCOUNT_009の出現回数: {token_009_count}")
        if token_009_count > 1:
            print("⚠️ TOKEN_ACCOUNT_009が複数回出現しています。手動での修正が必要かもしれません。")
            return False
        elif token_009_count == 0:
            print("⚠️ TOKEN_ACCOUNT_009が見つかりません。手動での追加が必要かもしれません。")
            return False
        else:
            print("✅ TOKEN_ACCOUNT_009は正しく1回だけ出現しています。")
            return True
    
    except Exception as e:
        print(f"❌ 検証中にエラーが発生しました: {str(e)}")
        return False

def manual_fix_instructions():
    """手動修正の手順を表示"""
    print("\n📋 === 手動修正手順 ===")
    print("環境変数ファイル (.env) を手動で修正するには:")
    print("1. テキストエディタで .env ファイルを開きます")
    print("2. 以下のような構造になっているか確認します:")
    print("\n# Threads API設定")
    print("THREADS_ACCESS_TOKEN=...")
    print("\n# インスタグラムユーザーID")
    print("INSTAGRAM_USER_ID=...")
    print("INSTAGRAM_USER_ID_ACCOUNT_009=...")
    print("\n# アカウントトークン")
    print("TOKEN_ACCOUNT_009=...")
    print("TOKEN_ACCOUNT_011=...")
    print("\n# Cloudinary設定")
    print("CLOUDINARY_CLOUD_NAME=...")
    print("CLOUDINARY_API_KEY=...")
    print("CLOUDINARY_API_SECRET=...")
    print("\n# その他設定")
    print("TEST_MODE=...")
    print("\n3. 特に以下の点を確認してください:")
    print("   - CLOUDINARY_API_SECRETが単独で存在しているか")
    print("   - TOKEN_ACCOUNT_009が1回だけ出現し、アカウントトークンセクションにあるか")
    print("4. 問題があれば修正し、ファイルを保存して閉じます")
    print("5. final_system.py を実行して動作確認します")

def fix_all_env_issues():
    """環境変数ファイルのすべての問題を修復"""
    print("\n🔧 === 環境変数ファイルの問題を修復 ===")
    success = fix_env_file()
    if success:
        print("\n✅ 環境変数ファイルの修復に成功しました。")
    else:
        print("\n⚠️ 環境変数ファイルの修復に失敗または不完全な修復です。")
        manual_fix_instructions()
    return success

# ==============================================
# 【メイン実行】
# ==============================================

def main():
    """メインメニュー"""
    print('=================================================')
    print('🚀 Threads新規アカウント追加ツール')
    print('=================================================')
    print('1. 新規アカウント追加')
    print('2. 複数アカウント一括追加')
    print('3. 保存済みトークン一覧表示')
    print('4. アカウント設定確認')
    print('5. トークン削除')
    print('6. 環境変数ファイル整理')
    print('7. 既存アカウント修復')
    print('8. ACCOUNT_009トークン緊急追加')
    print('9. 環境変数ファイル完全修復') # 新しいメニュー項目を追加
    print('0. 終了')
    print('-------------------------------------------------')
    
    choice = input('選択してください (0-9): ')
    
    if choice == '1':
        setup_new_account()
    elif choice == '2':
        bulk_setup_accounts()
    elif choice == '3':
        list_saved_tokens()
    elif choice == '4':
        account_id = input('確認するアカウントIDを入力: ')
        verify_account_setup(account_id)
    elif choice == '5':
        account_id = input('削除するアカウントIDを入力: ')
        remove_account_token(account_id)
    elif choice == '6':
        reorganize_env_file()
    elif choice == '7':
        repair_existing_accounts()
    elif choice == '8':
        add_missing_token_account()
    elif choice == '9':
        fix_all_env_issues()  # 新しい関数を呼び出し
    elif choice == '0':
        print('終了します')
        return
    else:
        print('無効な選択です')
    
    # 続けるか確認
    if input('\n続けますか？ (y/n): ').lower() == 'y':
        main()

if __name__ == "__main__":
    main()