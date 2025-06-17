#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.envファイル修復用スクリプト
"""

import os
import re
import shutil

def fix_env_file():
    """
    .envファイルのCLOUDINARY_API_SECRETとTOKEN_ACCOUNT_009の問題を修正
    """
    print("🔧 .envファイル修正を開始します...")
    
    env_file = ".env"
    
    # ファイルが存在しない場合はエラー
    if not os.path.exists(env_file):
        print(f"❌ {env_file} が見つかりません。")
        return False
    
    # バックアップ作成
    backup_file = f"{env_file}.backup"
    shutil.copy2(env_file, backup_file)
    print(f"✅ バックアップを作成しました: {backup_file}")
    
    try:
        # ファイル内容を読み込み
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 問題のパターンを探す
        pattern = r"CLOUDINARY_API_SECRET=([a-zA-Z0-9]+)TOKEN_ACCOUNT_009=(.*)"
        match = re.search(pattern, content)
        
        if match:
            # 分割すべき値を取得
            secret_value = match.group(1)
            token_value = match.group(2)
            
            # 置換
            new_content = content.replace(
                f"CLOUDINARY_API_SECRET={secret_value}TOKEN_ACCOUNT_009={token_value}",
                f"CLOUDINARY_API_SECRET={secret_value}\nTOKEN_ACCOUNT_009={token_value}"
            )
            
            # 書き戻し
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print("✅ CLOUDINARY_API_SECRETとTOKEN_ACCOUNT_009の問題を修正しました。")
            
            # 修正後の内容を表示
            print("\n=== 修正後の環境変数 ===")
            with open(env_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("CLOUDINARY_API_SECRET="):
                        print(f"CLOUDINARY_API_SECRET=***（値は秘密）")
                    elif line.startswith("TOKEN_ACCOUNT_"):
                        account_id = line.split("=")[0].replace("TOKEN_ACCOUNT_", "")
                        print(f"TOKEN_ACCOUNT_{account_id}=***（値は秘密）")
                    elif line.startswith("THREADS_ACCESS_TOKEN="):
                        print("THREADS_ACCESS_TOKEN=***（値は秘密）")
                    else:
                        print(line.strip())
            
            return True
        else:
            # 問題がなければそのまま環境変数ファイルを整理
            print("🔍 CLOUDINARY_API_SECRETとTOKEN_ACCOUNT_009の連結問題は見つかりませんでした。")
            return reorganize_env_file()
    
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        print("🔄 バックアップから復元します...")
        shutil.copy2(backup_file, env_file)
        print("✅ バックアップから復元しました。")
        return False

def reorganize_env_file():
    """環境変数ファイルを整理して見やすくする"""
    print("\n🔄 環境変数ファイルを整理します...")
    
    env_file = ".env"
    
    try:
        # 既存ファイル読み込み
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 行単位に分割
        lines = [line.strip() for line in content.split('\n')]
        
        # セクション分け
        sections = {
            "THREADS": [],
            "INSTAGRAM": [],
            "ACCOUNT": [],
            "CLOUDINARY": [],
            "OTHER": []
        }
        
        # 行を分類
        for line in lines:
            if not line or line.startswith("#"):
                continue
            
            if line.startswith("THREADS_ACCESS_TOKEN="):
                sections["THREADS"].append(line)
            elif line.startswith("INSTAGRAM_USER_ID"):
                sections["INSTAGRAM"].append(line)
            elif line.startswith("TOKEN_ACCOUNT_"):
                sections["ACCOUNT"].append(line)
            elif line.startswith("CLOUDINARY_"):
                sections["CLOUDINARY"].append(line)
            else:
                sections["OTHER"].append(line)
        
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
        
        print("✅ 環境変数ファイルを整理しました。")
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        return False

def manual_fix_instructions():
    """手動修正の手順を表示"""
    print("\n📋 === 手動修正手順 ===")
    print("環境変数ファイル (.env) を手動で修正するには:")
    print("1. テキストエディタで .env ファイルを開きます")
    print("2. 以下のような行を探します:")
    print("   CLOUDINARY_API_SECRET=e7qWzubCbY8iJI2C8b1UvFcTsQUTOKEN_ACCOUNT_009=...")
    print("3. この行を2行に分割します:")
    print("   CLOUDINARY_API_SECRET=e7qWzubCbY8iJI2C8b1UvFcTsQU")
    print("   TOKEN_ACCOUNT_009=...")
    print("4. ファイルを保存して閉じます")
    print("5. final_system.py を実行して動作確認します")

if __name__ == "__main__":
    print("=================================================")
    print("🛠️ .envファイル修復ツール")
    print("=================================================")
    print("1. 自動修復を実行")
    print("2. 手動修復手順を表示")
    print("0. 終了")
    print("-------------------------------------------------")
    
    choice = input("選択してください (0-2): ")
    
    if choice == "1":
        if fix_env_file():
            print("\n✅ 修復が完了しました。final_system.py を実行して動作確認してください。")
        else:
            print("\n⚠️ 修復が失敗または不要でした。")
            manual_fix_instructions()
    elif choice == "2":
        manual_fix_instructions()
    elif choice == "0":
        print("終了します")
    else:
        print("無効な選択です")