#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
【全データ削除ツール】
Threads自動投稿システム用 - メインコンテンツとアフィリエイトデータの削除

使用方法:
1. このスクリプトを実行するだけで全データが削除されます
2. 既存のJSONファイルは自動的にバックアップされます
3. 実行後はfinal_system.pyを起動してデータを確認してください

作成日: 2025年6月19日
"""

import json
import os
import shutil
from datetime import datetime
import sys
import traceback

def clear_all_data():
    """メインコンテンツとアフィリエイトデータを削除して空のJSONに置き換える"""
    print("🔄 === 全データ削除ツール ===")
    
    try:
        # JSONファイルのパス
        main_json_path = "src/data/main_contents.json"
        affiliate_json_path = "src/data/affiliates.json"
        
        # バックアップディレクトリを作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"json_backup_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # メインコンテンツをバックアップして削除
        if os.path.exists(main_json_path):
            shutil.copy2(main_json_path, f"{backup_dir}/{os.path.basename(main_json_path)}")
            print(f"✅ {main_json_path} をバックアップしました: {backup_dir}/{os.path.basename(main_json_path)}")
            
            # 空のJSONファイルを作成
            with open(main_json_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            print(f"✅ メインコンテンツを削除しました: {main_json_path}")
        
        # アフィリエイトをバックアップして削除
        if os.path.exists(affiliate_json_path):
            shutil.copy2(affiliate_json_path, f"{backup_dir}/{os.path.basename(affiliate_json_path)}")
            print(f"✅ {affiliate_json_path} をバックアップしました: {backup_dir}/{os.path.basename(affiliate_json_path)}")
            
            # 空のJSONファイルを作成
            with open(affiliate_json_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            print(f"✅ アフィリエイトデータを削除しました: {affiliate_json_path}")
        
        print("\n🎉 全データの削除が完了しました!")
        print("次のステップ:")
        print("1. final_system.py を起動")
        print("2. メニューから「6. 📊 システム状況確認」を選択")
        print("3. メインコンテンツとアフィリエイトの件数が0件になっていることを確認")
        print("4. メニューから「5. 🔄 データ更新（CSV読み込み）」を選択してデータを再読み込み")
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        traceback.print_exc()
        return False

def main():
    """メイン関数"""
    print("📋 === 全データ削除ツール ===")
    print("このツールはメインコンテンツとアフィリエイトデータを完全に削除します。")
    print("続行すると、既存のデータは全て削除されます（バックアップは作成されます）。")
    print("続行しますか？ (y/n): ", end="")
    
    choice = input().strip().lower()
    
    if choice == "y" or choice == "yes":
        clear_all_data()
    else:
        print("操作をキャンセルしました。")

if __name__ == "__main__":
    main()