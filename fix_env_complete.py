#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.envファイル完全修復用スクリプト
"""

import os
import re
import shutil

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
                sections["CLOUDINARY"].append(line)
            else:
                sections["OTHER"].append(line)
        
        # CLOUDINARY_API_SECRETが連結問題を持っている場合を修正
        for i, line in enumerate(sections["CLOUDINARY"]):
            if line.startswith("CLOUDINARY_API_SECRET="):
                pattern = r"CLOUDINARY_API_SECRET=([a-zA-Z0-9]+)TOKEN_ACCOUNT_"
                match = re.search(pattern, line)
                if match:
                    # 正しい値を取得
                    secret_value = match.group(1)
                    # 修正
                    sections["CLOUDINARY"][i] = f"CLOUDINARY_API_SECRET={secret_value}"
        
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

if __name__ == "__main__":
    print("=================================================")
    print("🛠️ .envファイル完全修復ツール")
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
            print("\n⚠️ 自動修復が失敗または不完全な場合は、手動で修正してください。")
            manual_fix_instructions()
    elif choice == "2":
        manual_fix_instructions()
    elif choice == "0":
        print("終了します")
    else:
        print("無効な選択です")