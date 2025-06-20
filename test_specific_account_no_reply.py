#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
特定アカウントでのThreads投稿テスト用スクリプト（リプライなし版）
"""
import sys
import traceback
from final_system import ThreadsAutomationSystem

def test_specific_account_no_reply():
    """特定アカウントでテスト投稿を実行（リプライなし）"""
    try:
        # システム初期化
        print("🚀 システム初期化中...")
        system = ThreadsAutomationSystem()
        
        # 利用可能なアカウント表示
        print("\n📊 利用可能なアカウント:")
        tokens = system.tokens
        if not tokens:
            print("❌ 利用可能なアカウントがありません")
            return 1
        
        for i, account_id in enumerate(tokens.keys(), 1):
            print(f"{i}. {account_id}")
        
        # アカウント選択
        try:
            selection = input("\n使用するアカウントの番号を入力してください: ").strip()
            selection_idx = int(selection) - 1
            
            if selection_idx < 0 or selection_idx >= len(tokens):
                print("❌ 無効な選択です")
                return 1
            
            account_id = list(tokens.keys())[selection_idx]
            print(f"✅ 選択されたアカウント: {account_id}")
            
            # テストモード選択
            test_mode_input = input("テストモードで実行しますか？実際には投稿されません (y/n): ").strip().lower()
            test_mode = test_mode_input == 'y'
            
            # カスタムテキスト入力
            custom_text_option = input("カスタムテキストを使用しますか？ (y/n): ").strip().lower()
            custom_text = None
            
            if custom_text_option == 'y':
                print("📝 カスタムテキストを入力してください (終了するには空行を入力):")
                lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    lines.append(line)
                custom_text = "\n".join(lines)
                print(f"📝 入力されたテキスト:")
                print(custom_text)
            
            # 確認
            if test_mode:
                confirm = input(f"🧪 {account_id} でテストモード投稿を実行しますか？（リプライなし） (y/n): ")
            else:
                confirm = input(f"🚨 {account_id} で実際に投稿を実行しますか？（リプライなし） (y/n): ")
            
            if confirm.lower() != 'y':
                print("❌ キャンセルされました")
                return 0
            
            # リプライなしで投稿実行
            print(f"\n🚀 {account_id} で投稿実行中（リプライなし）...")
            result = system.single_post_without_reply(
                account_id=account_id,
                test_mode=test_mode,
                custom_text=custom_text
            )
            
            if result and (result is True or (isinstance(result, dict) and result.get("success"))):
                print(f"✅ {account_id}: 投稿成功")
                if isinstance(result, dict):
                    post_id = result.get("main_post_id")
                    post_type = result.get("post_type", "unknown")
                    
                    print(f"📊 投稿情報:")
                    print(f"  投稿ID: {post_id}")
                    print(f"  投稿タイプ: {post_type}")
                    
                    # 投稿URLを表示（実際の投稿の場合）
                    if not test_mode and post_id:
                        username = account_id.lower()
                        print(f"🔗 投稿URL: https://threads.net/@{username}/post/{post_id}")
                
                return 0
            else:
                print(f"❌ {account_id}: 投稿失敗")
                return 1
                
        except ValueError:
            print("❌ 数値を入力してください")
            return 1
            
    except KeyboardInterrupt:
        print("\n👋 スクリプトを終了します")
        return 0
    except Exception as e:
        print(f"❌ スクリプトエラー: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_specific_account_no_reply())