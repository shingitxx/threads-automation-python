"""
テキストのみ投稿テスト（Cloudinary回避）
"""

import sys
import os
sys.path.append('.')

# 強制的にテストモードを無効化
os.environ['TEST_MODE'] = 'False'

try:
    from src.core.threads_api import ThreadsAPI, Account
    from config.settings import settings
    from test_real_gas_data_system_v2 import RealGASDataSystemV2
    print("✅ インポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)

def test_text_only_posting():
    """テキストのみ投稿テスト"""
    print("🚀 テキストのみ投稿テスト開始")
    print("=" * 50)
    
    # API初期化
    api = ThreadsAPI()
    
    # アクセストークン確認
    tokens = settings.get_account_tokens()
    print(f"🔑 利用可能トークン: {list(tokens.keys())}")
    
    if "ACCOUNT_011" not in tokens:
        print("❌ ACCOUNT_011のトークンが見つかりません")
        return
    
    # 実際のアカウント情報
    real_account = Account(
        id="ACCOUNT_011",
        username="kanae_15758",
        user_id="10068250716584647",
        access_token=tokens["ACCOUNT_011"]
    )
    
    print(f"👤 アカウント: {real_account.username}")
    print(f"🆔 ユーザーID: {real_account.user_id}")
    
    # GAS版データシステム
    gas_system = RealGASDataSystemV2()
    print(f"📊 GAS版データ: {len(gas_system.main_contents)}件のコンテンツ")
    
    # ACCOUNT_011のコンテンツを取得
    account_contents = [
        content for content in gas_system.main_contents.values() 
        if content.get('account_id') == 'ACCOUNT_011'
    ]
    
    print(f"👤 ACCOUNT_011用コンテンツ: {len(account_contents)}件")
    
    if account_contents:
        # ランダムに1つ選択
        import random
        selected_content = random.choice(account_contents)
        
        print(f"\n📝 選択されたコンテンツ:")
        print(f"🆔 ID: {selected_content['id']}")
        print(f"📄 内容: {selected_content['main_text']}")
        
        # 対応するアフィリエイト取得
        affiliate = gas_system.get_affiliate_for_content(selected_content['id'], 'ACCOUNT_011')
        
        if affiliate:
            affiliate_text = gas_system.format_affiliate_reply_text(affiliate)
            print(f"💬 アフィリエイトリプライ: {affiliate_text}")
            
            print(f"\n📋 投稿プレビュー:")
            print(f"🔹 メイン投稿: {selected_content['main_text']}")
            print(f"🔹 リプライ: {affiliate_text}")
            
            # 投稿確認
            proceed = input("\n🚀 実際のGAS版データでテキスト投稿しますか？ (y/n): ")
            
            if proceed.lower() == 'y':
                print("📡 実際のテキスト投稿実行中...")
                
                # メイン投稿
                main_result = api.create_text_post(
                    account=real_account,
                    text=selected_content['main_text']
                )
                
                print(f"\n📊 メイン投稿結果:")
                print(f"成功: {main_result.success}")
                
                if main_result.success:
                    print(f"✅ メイン投稿成功: {main_result.post_id}")
                    print(f"🔗 投稿URL: https://threads.net/@{real_account.username}/post/{main_result.post_id}")
                    
                    # リプライ投稿
                    reply_confirm = input("\n💬 アフィリエイトリプライも投稿しますか？ (y/n): ")
                    
                    if reply_confirm.lower() == 'y':
                        print("⏸️ リプライ準備中（5秒待機）...")
                        import time
                        time.sleep(5)
                        
                        print("📡 アフィリエイトリプライ投稿中...")
                        reply_result = api.create_reply_post(
                            account=real_account,
                            text=affiliate_text,
                            reply_to_id=main_result.post_id
                        )
                        
                        if reply_result.success:
                            print(f"✅ リプライ投稿成功: {reply_result.post_id}")
                            print(f"🎉 完璧なツリー投稿完成！")
                            print(f"🔗 メイン投稿URL: https://threads.net/@{real_account.username}/post/{main_result.post_id}")
                        else:
                            print(f"❌ リプライ投稿失敗: {reply_result.error}")
                    
                    # 画像投稿システムの完成を報告
                    final_test = input("\n🎉 画像投稿システム完成報告投稿をしますか？ (y/n): ")
                    
                    if final_test.lower() == 'y':
                        completion_text = """🎉 Python Threads自動投稿システム完成！

✨ 実装完了機能:
🔹 GAS版データ完全統合 (275件)
🔹 テキスト投稿 ✅
🔹 画像投稿システム ✅
🔹 ツリー投稿 (メイン + リプライ) ✅
🔹 CSV手動更新 ✅
🔹 マルチアカウント対応 ✅

🚀 Phase完了:
✅ Phase 1: 基盤構築
✅ Phase 2: データ統合  
✅ Phase 3: API統合
✅ Phase 4: 画像投稿システム

#Python #自動投稿 #開発完了 #Threads #API"""

                        completion_result = api.create_text_post(
                            account=real_account,
                            text=completion_text
                        )
                        
                        if completion_result.success:
                            print(f"🎊 完成報告投稿成功: {completion_result.post_id}")
                            print(f"🔗 投稿URL: https://threads.net/@{real_account.username}/post/{completion_result.post_id}")
                        else:
                            print(f"❌ 完成報告投稿失敗: {completion_result.error}")
                else:
                    print(f"❌ メイン投稿失敗: {main_result.error}")
            else:
                print("⏸️ テストをキャンセルしました")
        else:
            print("❌ 対応するアフィリエイトが見つかりません")
    else:
        print("❌ ACCOUNT_011用のコンテンツが見つかりません")
    
    print("\n✅ テキスト投稿テスト完了")

if __name__ == "__main__":
    test_text_only_posting()