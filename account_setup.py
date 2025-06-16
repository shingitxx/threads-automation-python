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
from dotenv import load_dotenv

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
            "id": "ACCOUNT_009",
            "token": "THAAkIds0IIlZABUVNzdVF6MnNVa1pfTWw5MkFNUmNOYU5hNm9kQUFKTDZAQTFBqRXVIUmZA1cVU4SmNkaFBkNVBGckItYWRPVERjcXZA1akFlWUQwaU4yZAlUwRHFnR2ZACZATBUQ0xhSVJWLWJMOUg0MkxObzNlaUl2S1c5UmNya0ZATU1U3Ujdkck9qUndrd1NJbTgZD"
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
    
    # トークン保存
    set_account_token(account_id, access_token)
    
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
                lines.append(token_line)
            
            # 書き戻し
            with open(env_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
        else:
            # 新規作成
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"TOKEN_{account_id}={token}\n")
        
        print(f"✅ {account_id} のトークンを.envファイルに保存しました")
        return True
        
    except Exception as error:
        print(f"❌ トークン保存エラー: {str(error)}")
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
        
        # CSV確認
        account_info = get_account_from_csv(account_id)
        
        if account_info:
            print(f"✅ CSV認識: {account_info['username']}")
            print(f"✅ ユーザーID: {account_info['user_id']}")
            print(f"✅ アクセストークン: {'設定済み' if token_exists else '未設定'}")
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
    print('0. 終了')
    print('-------------------------------------------------')
    
    choice = input('選択してください (0-5): ')
    
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