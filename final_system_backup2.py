"""
🎉 Python版Threads自動投稿システム - 最終統合版
GAS版完全互換 + 画像投稿 + スケジューラー
"""
import os
import sys
import time
import random
import traceback
from datetime import datetime
from typing import Dict, List, Optional

# プロジェクトルートをパスに追加
sys.path.append('.')

try:
    from config.settings import settings
    from test_real_gas_data_system_v2 import RealGASDataSystemV2
    from src.core.threads_api import ThreadsAPI, Account, threads_api
    from src.core.cloudinary_util import get_cloudinary_image_url, cloudinary_util
    print("✅ 全システムインポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)

class DirectPost:
    """直接投稿機能（APIを直接使用）"""
    
    @staticmethod
    def post_text(account_id, text):
        """テキスト投稿を直接実行"""
        try:
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": settings.INSTAGRAM_USER_ID
            }
            
            # 投稿実行
            print(f"📡 APIを呼び出して投稿中...")
            result = threads_api.create_text_post(account_data, text)
            
            return result
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            return None
    
    @staticmethod
    def post_reply(account_id, text, reply_to_id):
        """リプライ投稿を直接実行"""
        try:
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": settings.INSTAGRAM_USER_ID
            }
            
            # リプライ実行
            print(f"📡 APIを呼び出してリプライ中...")
            result = threads_api.create_reply_post(account_data, text, reply_to_id)
            
            return result
        except Exception as e:
            print(f"❌ リプライエラー: {e}")
            return None
    
    @staticmethod
    def post_image(account_id, text, image_url):
        """画像投稿を直接実行"""
        try:
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": settings.INSTAGRAM_USER_ID
            }
            
            # 画像投稿実行
            print(f"📡 APIを呼び出して画像投稿中...")
            result = threads_api.create_image_post(account_data, text, image_url)
            
            return result
        except Exception as e:
            print(f"❌ 画像投稿エラー: {e}")
            return None
    
    @staticmethod
    def post_image_reply(account_id, text, image_url, reply_to_id):
        """画像リプライ投稿を直接実行"""
        try:
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": settings.INSTAGRAM_USER_ID
            }
            
            # 画像リプライ実行
            print(f"📡 APIを呼び出して画像リプライ中...")
            result = threads_api.create_image_reply_post(account_data, text, image_url, reply_to_id)
            
            return result
        except Exception as e:
            print(f"❌ 画像リプライエラー: {e}")
            return None
    
    @staticmethod
    def post_carousel(account_id, text, image_urls):
        """カルーセル投稿（複数画像）を直接実行"""
        try:
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": settings.INSTAGRAM_USER_ID
            }
            
            # カルーセル投稿実行
            print(f"📡 APIを呼び出してカルーセル投稿中...")
            result = threads_api.create_carousel_post(account_data, text, image_urls)
            
            return result
        except Exception as e:
            print(f"❌ カルーセル投稿エラー: {e}")
            return None

class ThreadsAutomationSystem:
    """完全自動投稿システム"""
    
    def __init__(self):
        """初期化"""
        print("🚀 Python版Threads自動投稿システム起動中...")
        
        # コアシステム初期化
        self.content_system = RealGASDataSystemV2()
        self.api = ThreadsAPI()
        
        # 設定確認
        self.tokens = settings.get_account_tokens()
        
        print("🎉 システム初期化完了")
        print(f"📊 利用可能アカウント: {list(self.tokens.keys())}")
        print(f"📊 メインコンテンツ: {len(self.content_system.main_contents)}件")
        print(f"📊 アフィリエイト: {len(self.content_system.affiliates)}件")
    
    def select_account(self):
        """アカウントを選択"""
        if not self.tokens:
            print("❌ 利用可能なアカウントがありません")
            return None
        
        # 最初のアカウントを選択（通常は1つしかないため）
        return list(self.tokens.keys())[0]
    
    def single_post(self, account_id=None, test_mode=False, custom_text=None):
        """単発投稿実行"""
        print("\n🎯 === 単発投稿実行 ===")
        
        if not account_id:
            # デフォルトアカウントを使用
            account_id = self.select_account()
            if not account_id:
                print("❌ 利用可能なアカウントがありません")
                return False
        
        # カスタムテキストの場合は直接APIを使用
        if custom_text and not test_mode:
            print(f"📝 カスタムテキスト投稿:")
            print(custom_text)
            result = DirectPost.post_text(account_id, custom_text)
            return result
        
        # 通常の投稿処理
        try:
            # 1. コンテンツを選択
            main_content = self.content_system.get_random_main_content_for_account(account_id)
            if not main_content:
                print(f"❌ {account_id}: 利用可能なコンテンツがありません")
                return False
            
            print(f"📝 選択されたコンテンツ: {main_content['id']} - {main_content['main_text'][:50]}...")
            
            # 2. 対応するアフィリエイトを取得
            affiliate = self.content_system.get_affiliate_for_content(main_content["id"], account_id)
            if not affiliate:
                print(f"❌ {account_id}: コンテンツID {main_content['id']} に対応するアフィリエイトが見つかりません")
                return False
            
            print(f"🔗 対応するアフィリエイト: {affiliate['id']} - {affiliate['reply_text'][:30]}...")
            
            # 3. メイン投稿テキストを整形
            main_text = self.content_system.format_main_post_text(main_content)
            print(f"📝 メイン投稿テキスト:")
            print(main_text[:200] + "..." if len(main_text) > 200 else main_text)
            
            # 4. 画像URLを取得（もし画像付き投稿の場合）
            image_url = None
            if main_content.get('use_image') == 'YES' or main_content.get('use_image') is True:
                print(f"🖼️ 画像付きコンテンツのため、画像URL取得中...")
                cloud_result = get_cloudinary_image_url(main_content['id'])
                
                if cloud_result and cloud_result.get('success') and cloud_result.get('image_url'):
                    image_url = cloud_result.get('image_url')
                    print(f"✅ 画像URL取得成功: {image_url}")
                else:
                    print("⚠️ 画像が見つからないか、アップロードに失敗したため、テキストのみで投稿します")
            
            # テストモードの場合はシミュレーションのみ
            if test_mode:
                main_post_id = f"POST_{random.randint(1000000000, 9999999999)}"
                if image_url:
                    print(f"🧪 画像投稿シミュレーション: {image_url}")
                print(f"✅ メイン投稿成功（シミュレーション）: {main_post_id}")
                
                # リプライもシミュレーション
                reply_text = self.content_system.format_affiliate_reply_text(affiliate)
                print(f"💬 リプライテキスト:")
                print(reply_text[:200] + "..." if len(reply_text) > 200 else reply_text)
                
                reply_post_id = f"REPLY_{random.randint(1000000000, 9999999999)}"
                print(f"✅ リプライ投稿成功（シミュレーション）: {reply_post_id}")
                
                print(f"🎉 {account_id}: ツリー投稿完了（シミュレーション）")
                
                return {
                    "success": True,
                    "test_mode": True,
                    "main_post_id": main_post_id,
                    "reply_post_id": reply_post_id,
                    "main_content": main_content,
                    "affiliate": affiliate
                }
            
            # 実際の投稿処理
            # 5. メイン投稿を実行（テキストまたは画像）
            if image_url:
                main_result = DirectPost.post_image(account_id, main_text, image_url)
            else:
                main_result = DirectPost.post_text(account_id, main_text)
            
            if not main_result:
                print(f"❌ {account_id}: メイン投稿に失敗しました")
                return False
            
            main_post_id = main_result.get('id')
            print(f"✅ 投稿成功: {main_post_id}")
            
            # 6. リプライ投稿を準備
            print(f"⏸️ リプライ準備中（5秒待機）...")
            time.sleep(5)
            
            # 7. リプライテキストを整形
            reply_text = self.content_system.format_affiliate_reply_text(affiliate)
            print(f"💬 リプライテキスト:")
            print(reply_text[:200] + "..." if len(reply_text) > 200 else reply_text)
            
            # 8. リプライ投稿を実行
            reply_result = DirectPost.post_reply(account_id, reply_text, main_post_id)
            
            if not reply_result:
                print(f"❌ リプライ失敗: None")
                return {
                    "success": False,
                    "main_post_id": main_post_id,
                    "error": "リプライ投稿に失敗しました"
                }
            
            reply_post_id = reply_result.get('id')
            print(f"✅ リプライ成功: {reply_post_id}")
            
            print(f"🎉 {account_id}: ツリー投稿完了")
            
            return {
                "success": True,
                "main_post_id": main_post_id,
                "reply_post_id": reply_post_id,
                "main_content": main_content,
                "affiliate": affiliate
            }
                
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            traceback.print_exc()
            return False
    
    def all_accounts_post(self, test_mode=False):
        """全アカウント投稿実行"""
        print("\n🚀 === 全アカウント投稿実行 ===")
        
        if not self.tokens:
            print("❌ 利用可能なアカウントがありません")
            return {"success": 0, "failed": 0, "accounts": []}
        
        results = {"success": 0, "failed": 0, "accounts": []}
        total_accounts = len(self.tokens)
        
        for i, account_id in enumerate(self.tokens.keys(), 1):
            try:
                print(f"🔄 [{i}/{total_accounts}] {account_id} 投稿開始")
                
                result = self.single_post(
                    account_id=account_id,
                    test_mode=test_mode
                )
                
                if result and (result is True or (isinstance(result, dict) and result.get("success"))):
                    results["success"] += 1
                    results["accounts"].append({
                        "account_id": account_id,
                        "status": "success",
                        "main_post_id": result.get("main_post_id") if isinstance(result, dict) else None,
                        "reply_post_id": result.get("reply_post_id") if isinstance(result, dict) else None
                    })
                    print(f"✅ {account_id}: 投稿成功")
                else:
                    results["failed"] += 1
                    results["accounts"].append({
                        "account_id": account_id,
                        "status": "failed",
                        "error": str(result) if result else "Unknown error"
                    })
                    print(f"❌ {account_id}: 投稿失敗")
                
                # アカウント間の間隔
                if i < total_accounts:
                    interval = settings.posting.account_interval_seconds
                    print(f"⏸️ 次のアカウントまで{interval}秒待機...")
                    time.sleep(interval)
                    
            except Exception as e:
                results["failed"] += 1
                print(f"❌ {account_id} エラー: {e}")
        
        # 結果サマリー
        success_rate = (results["success"] / total_accounts) * 100 if total_accounts > 0 else 0
        print(f"\n📊 === 全アカウント投稿結果 ===")
        print(f"✅ 成功: {results['success']}/{total_accounts}")
        print(f"❌ 失敗: {results['failed']}/{total_accounts}")
        print(f"📈 成功率: {success_rate:.1f}%")
        
        return results
    
    def update_data(self):
        """データ更新"""
        print("\n🔄 === データ更新実行 ===")
        
        try:
            result = self.content_system.update_from_csv()
            
            if result and result.get("success"):
                print("✅ データ更新成功")
                print(f"📊 メインコンテンツ: {len(self.content_system.main_contents)}件")
                print(f"📊 アフィリエイト: {len(self.content_system.affiliates)}件")
                return True
            else:
                print("❌ データ更新失敗")
                return False
                
        except Exception as e:
            print(f"❌ データ更新エラー: {e}")
            return False
    
    def system_status(self):
        """システム状況確認"""
        print("\n📊 === システム状況 ===")
        
        # 基本情報
        print(f"📁 プロジェクトルート: {os.getcwd()}")
        print(f"🐍 Python版本: {sys.version.split()[0]}")
        print(f"⏰ 現在時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # データ状況
        print(f"\n📊 データ状況:")
        print(f"  メインコンテンツ: {len(self.content_system.main_contents)}件")
        print(f"  アフィリエイト: {len(self.content_system.affiliates)}件")
        
        # アカウント状況
        print(f"\n👥 アカウント状況:")
        if self.tokens:
            for account_id in self.tokens.keys():
                print(f"  ✅ {account_id}: トークン設定済み")
        else:
            print("  ❌ 設定済みアカウントなし")
        
        # 設定状況
        print(f"\n⚙️ 設定状況:")
        print(f"  投稿時間: {settings.schedule.posting_hours}")
        print(f"  テストモード: {os.getenv('TEST_MODE', 'False')}")
        print(f"  Cloudinary: 設定済み")
        
        # Cloudinary接続テスト
        try:
            cloud_test = cloudinary_util.test_cloudinary_connection()
            if cloud_test:
                print(f"  ☁️ Cloudinary接続: ✅ 成功")
            else:
                print(f"  ☁️ Cloudinary接続: ❌ 失敗")
        except Exception:
            print(f"  ☁️ Cloudinary接続: ❌ エラー")
    
    def test_image_post(self, test_mode=True):
        """画像投稿テスト"""
        try:
            print("\n🖼️ === 画像投稿テスト ===")
            
            # アカウント選択
            account_id = self.select_account()
            if not account_id:
                print("❌ アカウントが見つかりません")
                return False
            
            # テスト用テキスト
            test_text = "これは画像投稿のテストです📷 #テスト"
            
            # テスト用コンテンツID（実際のIDを指定）
            content_id = input("📝 テスト用コンテンツID（例: CONTENT_001）を入力: ").strip()
            
            # CloudinaryからURLを取得
            print(f"🔍 コンテンツID {content_id} の画像を検索中...")
            cloud_result = get_cloudinary_image_url(content_id)
            
            if not cloud_result or not cloud_result.get('success'):
                print("❌ 画像が見つからないか、アップロードに失敗しました")
                return False
            
            image_url = cloud_result.get('image_url')
            print(f"✅ 画像URL取得成功: {image_url}")
            
            # 投稿実行
            print("📡 APIを呼び出して画像投稿中...")
            
            if test_mode:
                print("🧪 テストモード: 実際には投稿されません")
                print(f"📝 投稿テキスト: {test_text}")
                print(f"🖼️ 画像URL: {image_url}")
                result = {"id": f"test_image_post_{int(time.time())}"}
            else:
                result = DirectPost.post_image(account_id, test_text, image_url)
            
            if result:
                print(f"✅ 画像投稿成功: {result.get('id')}")
                return True
            else:
                print("❌ 画像投稿失敗")
                return False
                
        except Exception as e:
            print(f"❌ 画像投稿テストエラー: {e}")
            traceback.print_exc()
            return False
    
    def test_carousel_post(self, test_mode=True):
        """カルーセル投稿（複数画像）テスト"""
        try:
            print("\n🎠 === カルーセル投稿テスト ===")
            
            # アカウント選択
            account_id = self.select_account()
            if not account_id:
                print("❌ アカウントが見つかりません")
                return False
            
            # テスト用テキスト
            test_text = "これはカルーセル投稿（複数画像）のテストです📷🖼️ #テスト"
            
            # 複数のコンテンツID入力
            print("📝 複数のコンテンツIDをカンマ区切りで入力してください（例: CONTENT_001,CONTENT_002）")
            content_ids_input = input("コンテンツID: ").strip()
            content_ids = [cid.strip() for cid in content_ids_input.split(",")]
            
            if not content_ids:
                print("❌ コンテンツIDが指定されていません")
                return False
            
            # 各コンテンツIDから画像URLを取得
            image_urls = []
            for content_id in content_ids:
                print(f"🔍 コンテンツID {content_id} の画像を検索中...")
                cloud_result = get_cloudinary_image_url(content_id)
                
                if cloud_result and cloud_result.get('success'):
                    image_url = cloud_result.get('image_url')
                    image_urls.append(image_url)
                    print(f"✅ 画像URL取得成功: {image_url}")
                else:
                    print(f"⚠️ コンテンツID {content_id} の画像取得失敗")
            
            if not image_urls:
                print("❌ 画像URLが取得できませんでした")
                return False
            
            print(f"📊 取得した画像URL数: {len(image_urls)}")
            
            # カルーセル投稿実行
            print("📡 APIを呼び出してカルーセル投稿中...")
            
            if test_mode:
                print("🧪 テストモード: 実際には投稿されません")
                print(f"📝 投稿テキスト: {test_text}")
                print(f"🖼️ 画像URL数: {len(image_urls)}")
                result = {"id": f"test_carousel_{int(time.time())}"}
            else:
                result = DirectPost.post_carousel(account_id, test_text, image_urls)
            
            if result:
                print(f"✅ カルーセル投稿成功: {result.get('id')}")
                return True
            else:
                print("❌ カルーセル投稿失敗")
                return False
                
        except Exception as e:
            print(f"❌ カルーセル投稿テストエラー: {e}")
            traceback.print_exc()
            return False
    
    def start_scheduler_menu(self):
        """スケジューラーメニュー"""
        print("\n⏰ === スケジューラーシステム ===")
        print("注意: スケジューラーは別途 scheduler_system.py で起動してください")
        print("1. scheduler_system.py の実行")
        print("2. バックグラウンド実行での24時間自動投稿")
        print("3. 投稿時間: [2, 5, 8, 12, 17, 20, 22, 0]時")
        
        choice = input("スケジューラーを起動しますか？ (y/n): ")
        if choice.lower() == 'y':
            try:
                os.system("python scheduler_system.py")
            except Exception as e:
                print(f"❌ スケジューラー起動エラー: {e}")
                print("💡 手動で 'python scheduler_system.py' を実行してください")
    
    def completion_celebration(self):
        """完成記念投稿"""
        print("\n🎉 === 完成記念投稿 ===")
        
        celebration_text = """🎉 Python版Threads自動投稿システム完成！

✅ GAS版からの完全移行成功
✅ 275件のデータ統合完了  
✅ 画像投稿機能実装
✅ スケジューラー機能完成
✅ 全自動化システム完成

#Python #自動化 #Threads #開発完了"""
        
        print("📝 完成記念投稿内容:")
        print(celebration_text)
        
        confirm = input("\n🚀 完成記念投稿を実際に投稿しますか？ (y/n): ")
        if confirm.lower() == 'y':
            try:
                account_id = self.select_account()
                if account_id:
                    # カスタムテキストで投稿
                    result = self.single_post(
                        account_id=account_id,
                        test_mode=False,
                        custom_text=celebration_text
                    )
                    
                    if result and result.get("success"):
                        post_id = result.get("post_id") or result.get("main_post_id")
                        print(f"🎊 完成記念投稿成功: {post_id}")
                        username = account_id.lower()
                        print(f"🔗 投稿URL: https://threads.net/@{username}/post/{post_id}")
                    else:
                        # フォールバック：通常の投稿システムを使用
                        print("⚠️ カスタムテキスト投稿に失敗、通常投稿を実行...")
                        fallback_result = self.single_post(
                            account_id=account_id,
                            test_mode=False
                        )
                        if fallback_result and fallback_result.get("success"):
                            print("🎉 システム完成を記念した投稿が完了しました！")
                        else:
                            print(f"❌ 投稿失敗")
                else:
                    print("❌ 利用可能なアカウントがありません")
                    
            except Exception as e:
                print(f"❌ 記念投稿エラー: {e}")
                print("💡 代替案：メニューの '2. 🚀 単発投稿（実際の投稿）' で記念投稿を実行してください")
    
    def interactive_menu(self):
        """対話型メニュー"""
        while True:
            print("\n" + "="*50)
            print("🎯 Python版Threads自動投稿システム")
            print("="*50)
            print("1. 📱 単発投稿（テストモード）")
            print("2. 🚀 単発投稿（実際の投稿）")
            print("3. 👥 全アカウント投稿（テストモード）")
            print("4. 🌟 全アカウント投稿（実際の投稿）")
            print("5. 🔄 データ更新（CSV読み込み）")
            print("6. 📊 システム状況確認")
            print("7. ⏰ スケジューラー起動")
            print("8. 🎉 完成記念投稿")
            print("9. 🖼️ 画像投稿テスト（テストモード）")
            print("10. 📷 画像投稿テスト（実際の投稿）")
            print("11. 🎠 カルーセル投稿テスト（テストモード）")
            print("12. 🌄 カルーセル投稿テスト（実際の投稿）")
            print("0. 🚪 終了")
            print("-"*50)
            
            try:
                choice = input("選択してください (0-12): ").strip()
                
                if choice == "0":
                    print("👋 システムを終了します")
                    break
                elif choice == "1":
                    self.single_post(test_mode=True)
                elif choice == "2":
                    confirm = input("🚨 実際にThreadsに投稿します。続行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        self.single_post(test_mode=False)
                elif choice == "3":
                    self.all_accounts_post(test_mode=True)
                elif choice == "4":
                    confirm = input("🚨 全アカウントで実際にThreadsに投稿します。続行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        self.all_accounts_post(test_mode=False)
                elif choice == "5":
                    self.update_data()
                elif choice == "6":
                    self.system_status()
                elif choice == "7":
                    self.start_scheduler_menu()
                elif choice == "8":
                    self.completion_celebration()
                elif choice == "9":
                    self.test_image_post(test_mode=True)
                elif choice == "10":
                    confirm = input("🚨 実際に画像投稿します。続行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        self.test_image_post(test_mode=False)
                elif choice == "11":
                    self.test_carousel_post(test_mode=True)
                elif choice == "12":
                    confirm = input("🚨 実際にカルーセル投稿します。続行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        self.test_carousel_post(test_mode=False)
                else:
                    print("❌ 無効な選択です")
                    
            except KeyboardInterrupt:
                print("\n👋 システムを終了します")
                break
            except Exception as e:
                print(f"❌ エラー: {e}")

def main():
    """メイン実行関数"""
    print("🚀 Python版Threads自動投稿システム")
    print("=" * 50)
    print("🎉 GAS版完全互換 + 画像投稿 + スケジューラー")
    print("=" * 50)
    
    try:
        # システム初期化
        system = ThreadsAutomationSystem()
        
        # 対話型メニュー起動
        system.interactive_menu()
        
    except KeyboardInterrupt:
        print("\n👋 システムを終了しました")
    except Exception as e:
        print(f"❌ システムエラー: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())