"""
強制実投稿テスト - テストモードを無効化
"""

import sys
import os
sys.path.append('.')

# 強制的にテストモードを無効化
os.environ['TEST_MODE'] = 'False'

try:
    from image_posting_system import ThreadsImagePostingSystem
    from src.core.threads_api import ThreadsAPI, Account
    from config.settings import settings
    print("✅ インポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)

def force_real_image_posting():
    """強制実際の画像投稿テスト"""
    print("🚀 強制実投稿テスト開始")
    print("=" * 50)
    
    # システム初期化（テストモード強制無効化）
    image_system = ThreadsImagePostingSystem()
    image_system.test_mode = False  # 強制的にFalseに設定
    
    print(f"🧪 テストモード: {image_system.test_mode}")
    print(f"🌐 Cloudinaryテストモード: {image_system.cloudinary}")
    
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
    print(f"🔑 トークン: {real_account.access_token[:20]}...")
    
    # テスト画像URL（小さなテスト画像）
    test_image_url = "https://httpbin.org/image/jpeg"
    
    print(f"\n🧪 実際の1枚画像投稿テスト")
    print(f"🖼️ テスト画像: {test_image_url}")
    
    # 最終確認
    proceed = input("🚀 【実際に】Threadsに画像投稿しますか？ (y/n): ")
    
    if proceed.lower() == 'y':
        print("📡 実際の画像投稿実行中...")
        print("⚠️ これは実際のThreads投稿です！")
        
        try:
            # 実際の1枚画像投稿
            result = image_system.create_single_image_post(
                account=real_account,
                text="🎉 Python画像投稿システム完成記念投稿！🖼️\n\n✨ 機能:\n- 1枚画像投稿 ✅\n- 2枚画像投稿 ✅\n- Cloudinary連携 ✅\n- 自動アップロード ✅\n\n#Python #自動投稿 #画像投稿 #開発完了",
                image_source=test_image_url
            )
            
            print(f"\n📊 実際の投稿結果:")
            print(f"成功: {result.success}")
            
            if result.success:
                print(f"🎉 実際の画像投稿成功！")
                print(f"✅ 投稿ID: {result.post_id}")
                print(f"🖼️ 画像URL: {result.image_url}")
                print(f"🔗 実際の投稿URL: https://threads.net/@{real_account.username}/post/{result.post_id}")
                
                # GAS版データとの統合テスト提案
                gas_test = input("\n🔥 実際のGAS版データで画像投稿もテストしますか？ (y/n): ")
                if gas_test.lower() == 'y':
                    test_with_gas_data(image_system, real_account)
                    
            else:
                print(f"❌ 投稿失敗: {result.error}")
                print("💡 エラー詳細を確認して設定を見直してください")
                
        except Exception as e:
            print(f"❌ 例外エラー: {e}")
            
    else:
        print("⏸️ テストをキャンセルしました")
    
    print("\n✅ 強制実投稿テスト完了")

def test_with_gas_data(image_system, account):
    """GAS版データとの統合テスト"""
    print("\n🔥 GAS版データ統合テスト")
    print("=" * 40)
    
    try:
        from test_real_gas_data_system_v2 import RealGASDataSystemV2
        
        # GAS版データシステム
        gas_system = RealGASDataSystemV2()
        
        # 画像使用コンテンツを確認
        image_contents = [
            content for content in gas_system.main_contents.values() 
            if content.get('image_usage', '').upper() == 'YES'
        ]
        
        print(f"🖼️ 画像使用コンテンツ: {len(image_contents)}件")
        
        if image_contents:
            # ランダムに1つ選択
            import random
            selected_content = random.choice(image_contents)
            
            print(f"📝 選択されたコンテンツ: {selected_content['id']}")
            print(f"📄 投稿内容: {selected_content['main_text'][:50]}...")
            
            # 対応するアフィリエイト取得
            affiliate = gas_system.get_affiliate_for_content(selected_content['id'], account.id)
            
            if affiliate:
                affiliate_text = gas_system.format_affiliate_reply_text(affiliate)
                
                print(f"\n📋 実際のGAS版コンテンツで画像投稿:")
                print(f"🔹 メイン投稿: {selected_content['main_text']}")
                print(f"🔹 リプライ: {affiliate_text}")
                
                final_confirm = input("\n🚀 この内容で実際に画像投稿しますか？ (y/n): ")
                
                if final_confirm.lower() == 'y':
                    # 実際のGAS版データで画像付きツリー投稿
                    result = image_system.create_image_tree_post(
                        account=account,
                        main_text=selected_content['main_text'],
                        image_sources="https://httpbin.org/image/jpeg",
                        reply_text=affiliate_text
                    )
                    
                    if result["success"]:
                        print(f"🎉 GAS版データでの画像付きツリー投稿成功！")
                        print(f"📱 メイン投稿: {result['main_post_id']}")
                        print(f"💬 リプライ: {result['reply_post_id']}")
                        print(f"🔗 投稿URL: https://threads.net/@{account.username}/post/{result['main_post_id']}")
                    else:
                        print(f"❌ ツリー投稿失敗: {result['error']}")
            else:
                print("❌ 対応するアフィリエイトが見つかりません")
        else:
            print("❌ 画像使用コンテンツが見つかりません")
            
    except Exception as e:
        print(f"❌ GAS版データテストエラー: {e}")

if __name__ == "__main__":
    force_real_image_posting()