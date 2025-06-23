"""
🎉 Python版Threads自動投稿システム - 最終統合版
GAS版完全互換 + 画像投稿 + 真のカルーセル投稿 + スケジューラー
✨ 完全自動判定機能付き ✨
"""
import os
import sys
import time
import random
import json
import traceback
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

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

# 新規アカウント追加機能のインポート
try:
    from account_setup import setup_new_account, verify_account_setup, bulk_setup_accounts
    ACCOUNT_SETUP_AVAILABLE = True
except ImportError:
    ACCOUNT_SETUP_AVAILABLE = False
    print("⚠️ account_setup.py が見つかりません。新規アカウント追加機能は無効です。")

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
            # アカウント固有のユーザーIDを取得（修正版）
            user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
            instagram_user_id = os.getenv(user_id_key, os.getenv("INSTAGRAM_USER_ID"))
            print(f"DEBUG: アカウント {account_id} のユーザーID: {instagram_user_id}")
            
            # アカウント固有のアクセストークンを取得
            token_key = f"TOKEN_{account_id}"
            access_token = os.getenv(token_key, os.getenv("THREADS_ACCESS_TOKEN"))
            
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": instagram_user_id,
                "access_token": access_token
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
            # アカウント固有のユーザーIDを取得（修正版）
            user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
            instagram_user_id = os.getenv(user_id_key, os.getenv("INSTAGRAM_USER_ID"))
            print(f"DEBUG: アカウント {account_id} のユーザーID: {instagram_user_id}")
            
            # アカウント固有のアクセストークンを取得
            token_key = f"TOKEN_{account_id}"
            access_token = os.getenv(token_key, os.getenv("THREADS_ACCESS_TOKEN"))
            
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": instagram_user_id,
                "access_token": access_token
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
            # アカウント固有のユーザーIDを取得（修正版）
            user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
            instagram_user_id = os.getenv(user_id_key, os.getenv("INSTAGRAM_USER_ID"))
            print(f"DEBUG: アカウント {account_id} のユーザーID: {instagram_user_id}")
            
            # アカウント固有のアクセストークンを取得
            token_key = f"TOKEN_{account_id}"
            access_token = os.getenv(token_key, os.getenv("THREADS_ACCESS_TOKEN"))
            
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": instagram_user_id,
                "access_token": access_token
            }
            
            # 画像投稿実行
            print(f"📡 APIを呼び出して画像投稿中...")
            print(f"🔍 画像URL: {image_url}")
            print(f"🔍 アカウント情報: {account_data}")
            result = threads_api.create_image_post(account_data, text, image_url)
            
            return result
        except Exception as e:
            print(f"❌ 画像投稿エラー: {e}")
            traceback.print_exc()  # スタックトレース表示
            return None
    
    @staticmethod
    def post_image_reply(account_id, text, image_url, reply_to_id):
        """画像リプライ投稿を直接実行"""
        try:
            # アカウント固有のユーザーIDを取得
            user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
            instagram_user_id = os.getenv(user_id_key, os.getenv("INSTAGRAM_USER_ID"))
            
            # アカウント固有のアクセストークンを取得
            token_key = f"TOKEN_{account_id}"
            access_token = os.getenv(token_key, os.getenv("THREADS_ACCESS_TOKEN"))
            
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": instagram_user_id,
                "access_token": access_token
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
        """カルーセル投稿（複数画像）を直接実行 - リプライチェーン方式"""
        try:
            # 環境変数から直接ユーザーIDを取得
            user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
            instagram_user_id = os.getenv(user_id_key, os.getenv("INSTAGRAM_USER_ID"))
            
            # アカウント固有のアクセストークンを取得
            token_key = f"TOKEN_{account_id}"
            access_token = os.getenv(token_key, os.getenv("THREADS_ACCESS_TOKEN"))
            
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": instagram_user_id,
                "access_token": access_token
            }
            
            # カルーセル投稿実行
            print(f"📡 APIを呼び出してカルーセル投稿中...")
            result = threads_api.create_carousel_post(account_data, text, image_urls)
            
            return result
        except Exception as e:
            print(f"❌ カルーセル投稿エラー: {e}")
            return None
    
    @staticmethod
    def post_true_carousel(account_id, text, image_urls):
        """真のカルーセル投稿（1つの投稿内で複数画像をスワイプ可能）を直接実行"""
        try:
            # アカウント固有のユーザーIDを取得
            user_id_key = f"INSTAGRAM_USER_ID_{account_id}"
            instagram_user_id = os.getenv(user_id_key, os.getenv("INSTAGRAM_USER_ID"))
            
            # アカウント固有のアクセストークンを取得
            token_key = f"TOKEN_{account_id}"
            access_token = os.getenv(token_key, os.getenv("THREADS_ACCESS_TOKEN"))
            
            # アカウント情報
            account_data = {
                "id": account_id,
                "username": account_id,
                "user_id": instagram_user_id,
                "access_token": access_token
            }
            
            # 真のカルーセル投稿実行
            print(f"🎠 APIを呼び出して真のカルーセル投稿中...")
            print(f"🔍 画像数: {len(image_urls)}")
            for i, url in enumerate(image_urls, 1):
                print(f"  画像{i}: {url}")
            
            result = threads_api.create_true_carousel_post(account_data, text, image_urls)
            
            return result
        except Exception as e:
            print(f"❌ 真のカルーセル投稿エラー: {e}")
            traceback.print_exc()
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
    
    def detect_carousel_images(self, main_content_id):
        """カルーセル用の複数画像を検出（画像ファイルの存在による自動判定）"""
        image_urls = []
        images_dir = "images"
        
        print(f"🔍 カルーセル用画像を検索中...")
        
        # メイン画像を取得
        main_cloud_result = get_cloudinary_image_url(main_content_id)
        if main_cloud_result and main_cloud_result.get('success'):
            image_urls.append(main_cloud_result.get('image_url'))
            print(f"✅ メイン画像: {main_cloud_result.get('image_url')}")
        else:
            print(f"❌ メイン画像の取得に失敗: {main_content_id}")
            return image_urls  # メイン画像がない場合は空のリストを返す
        
        # 追加画像を検索（CONTENT_XXX_1, CONTENT_XXX_2 などの形式）
        for i in range(1, 10):  # 最大9枚の追加画像をチェック
            additional_id = f"{main_content_id}_{i}"
            
            # 物理的なファイルの存在を確認
            potential_files = [
                os.path.join(images_dir, f"{additional_id}_image.jpg"),
                os.path.join(images_dir, f"{additional_id}_image.png"),
                os.path.join(images_dir, f"{additional_id}_image.JPG"),
                os.path.join(images_dir, f"{additional_id}_image.PNG")
            ]
            
            file_exists = any(os.path.exists(file) for file in potential_files)
            if file_exists:
                print(f"🔍 追加画像ID発見: {additional_id}")
                add_cloud_result = get_cloudinary_image_url(additional_id)
                if add_cloud_result and add_cloud_result.get('success'):
                    image_urls.append(add_cloud_result.get('image_url'))
                    print(f"✅ 追加画像{i}: {add_cloud_result.get('image_url')}")
                else:
                    print(f"⚠️ 追加画像{i}のCloudinary取得失敗: {additional_id}")
                    break  # 連続した画像が見つからない場合は終了
            else:
                break  # ファイルが見つからない場合は終了
        
        print(f"📊 検出した画像数: {len(image_urls)}")
        return image_urls
    
    def single_post(self, account_id=None, test_mode=False, custom_text=None):
        """
        単発投稿実行 - 完全自動判定版
        画像ファイルの存在に基づいて自動的に投稿タイプを決定
        """
        print("\n🎯 === 単発投稿実行（完全自動判定版） ===")
        
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
            # 1. コンテンツを選択 (修正部分)
            main_content = self.content_system.get_random_main_content_for_account(account_id)
            if not main_content:
                print(f"❌ {account_id}: コンテンツの選択に失敗 - 任意のコンテンツを試行します")
                # アカウント制限なしで任意のコンテンツを選択
                if len(self.content_system.main_contents) > 0:
                    main_content = random.choice(self.content_system.main_contents)
                else:
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
            
            # 4. 【重要】画像ファイルの存在による完全自動判定
            content_id = main_content.get('id', '')
            print(f"\n🔍 使用するコンテンツID: {content_id}")
            print(f"🤖 画像ファイルの存在を自動チェック中...")
            
            # imagesディレクトリの存在確認
            images_dir = "images"
            if not os.path.exists(images_dir):
                print(f"⚠️ 警告: {images_dir} ディレクトリが存在しません。作成します。")
                os.makedirs(images_dir)
            
            # 画像ファイルの存在チェック（CSVフラグに依存しない）
            image_urls = self.detect_carousel_images(content_id)
            
            # 投稿タイプの自動判定
            if len(image_urls) > 1:
                post_type = "真のカルーセル"
                print(f"🎠 自動判定結果: 真のカルーセル投稿（{len(image_urls)}枚の画像）")
                for i, url in enumerate(image_urls, 1):
                    print(f"  画像{i}: {url}")
            elif len(image_urls) == 1:
                post_type = "単一画像"
                print(f"📷 自動判定結果: 単一画像投稿")
                print(f"  画像: {image_urls[0]}")
            else:
                post_type = "テキスト"
                print(f"📝 自動判定結果: テキストのみ投稿（画像ファイルなし）")
            
            # テストモードの場合はシミュレーションのみ
            if test_mode:
                main_post_id = f"POST_{random.randint(1000000000, 9999999999)}"
                
                if post_type == "真のカルーセル":
                    print(f"🧪 真のカルーセル投稿シミュレーション: {len(image_urls)}枚")
                elif post_type == "単一画像":
                    print(f"🧪 画像投稿シミュレーション: {image_urls[0]}")
                else:
                    print(f"🧪 テキスト投稿シミュレーション")
                
                print(f"✅ メイン投稿成功（シミュレーション）: {main_post_id} - {post_type}")
                
                # リプライもシミュレーション（すべての投稿タイプ）
                reply_text = self.content_system.format_affiliate_reply_text(affiliate)
                print(f"💬 リプライテキスト:")
                print(reply_text[:200] + "..." if len(reply_text) > 200 else reply_text)
                
                reply_post_id = f"REPLY_{random.randint(1000000000, 9999999999)}"
                print(f"✅ リプライ投稿成功（シミュレーション）: {reply_post_id}")
                
                print(f"🎉 {account_id}: 投稿完了（シミュレーション）")
                
                return {
                    "success": True,
                    "test_mode": True,
                    "main_post_id": main_post_id,
                    "reply_post_id": reply_post_id,
                    "main_content": main_content,
                    "affiliate": affiliate,
                    "image_urls": image_urls,
                    "post_type": post_type,
                    "auto_detected": True
                }
            
            # 実際の投稿処理
            print("\n📤 === 実際の投稿実行 ===")
            
            if post_type == "真のカルーセル":
                # 真のカルーセル投稿
                print(f"🎠 真のカルーセル投稿として {len(image_urls)}枚の画像で投稿を実行します")
                main_result = DirectPost.post_true_carousel(account_id, main_text, image_urls)
            elif post_type == "単一画像":
                # 単一画像投稿
                print(f"🖼️ 画像URL: {image_urls[0]} で投稿を実行します")
                main_result = DirectPost.post_image(account_id, main_text, image_urls[0])
            else:
                # テキストのみ投稿
                print(f"📝 テキストのみで投稿を実行します")
                main_result = DirectPost.post_text(account_id, main_text)
            
            if not main_result:
                print(f"❌ {account_id}: メイン投稿に失敗しました")
                return False
            
            main_post_id = main_result.get('id')
            print(f"✅ {post_type}投稿成功: {main_post_id}")
            
            # リプライ投稿を準備（すべての投稿タイプでアフィリエイトリプライを投稿）
            
            print(f"⏸️ リプライ準備中（5秒待機）...")
            time.sleep(5)
            
            # リプライテキストを整形
            reply_text = self.content_system.format_affiliate_reply_text(affiliate)
            print(f"💬 リプライテキスト:")
            print(reply_text[:200] + "..." if len(reply_text) > 200 else reply_text)
            
            # リプライ投稿を実行
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
                "affiliate": affiliate,
                "image_urls": image_urls,
                "post_type": post_type,
                "auto_detected": True
            }
                
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            traceback.print_exc()
            return False
    
    def single_post_without_reply(self, account_id=None, test_mode=False, custom_text=None):
        """
        単発投稿実行 - ツリー投稿なし（リプライなし）
        画像ファイルの存在に基づいて自動的に投稿タイプを決定するが、アフィリエイトリプライは行わない
        """
        print("\n🎯 === 単発投稿実行（リプライなし） ===")
        
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
                print(f"❌ {account_id}: コンテンツの選択に失敗 - 任意のコンテンツを試行します")
                # アカウント制限なしで任意のコンテンツを選択
                if len(self.content_system.main_contents) > 0:
                    main_content = random.choice(self.content_system.main_contents)
                else:
                    print(f"❌ {account_id}: 利用可能なコンテンツがありません")
                    return False
            
            print(f"📝 選択されたコンテンツ: {main_content['id']} - {main_content['main_text'][:50]}...")
            
            # 2. メイン投稿テキストを整形
            main_text = self.content_system.format_main_post_text(main_content)
            print(f"📝 メイン投稿テキスト:")
            print(main_text[:200] + "..." if len(main_text) > 200 else main_text)
            
            # 3. 画像ファイルの存在による完全自動判定
            content_id = main_content.get('id', '')
            print(f"\n🔍 使用するコンテンツID: {content_id}")
            print(f"🤖 画像ファイルの存在を自動チェック中...")
            
            # imagesディレクトリの存在確認
            images_dir = "images"
            if not os.path.exists(images_dir):
                print(f"⚠️ 警告: {images_dir} ディレクトリが存在しません。作成します。")
                os.makedirs(images_dir)
            
            # 画像ファイルの存在チェック
            image_urls = self.detect_carousel_images(content_id)
            
            # 投稿タイプの自動判定
            if len(image_urls) > 1:
                post_type = "真のカルーセル"
                print(f"🎠 自動判定結果: 真のカルーセル投稿（{len(image_urls)}枚の画像）")
                for i, url in enumerate(image_urls, 1):
                    print(f"  画像{i}: {url}")
            elif len(image_urls) == 1:
                post_type = "単一画像"
                print(f"📷 自動判定結果: 単一画像投稿")
                print(f"  画像: {image_urls[0]}")
            else:
                post_type = "テキスト"
                print(f"📝 自動判定結果: テキストのみ投稿（画像ファイルなし）")
            
            # テストモードの場合はシミュレーションのみ
            if test_mode:
                main_post_id = f"POST_{random.randint(1000000000, 9999999999)}"
                
                if post_type == "真のカルーセル":
                    print(f"🧪 真のカルーセル投稿シミュレーション: {len(image_urls)}枚")
                elif post_type == "単一画像":
                    print(f"🧪 画像投稿シミュレーション: {image_urls[0]}")
                else:
                    print(f"🧪 テキスト投稿シミュレーション")
                
                print(f"✅ メイン投稿成功（シミュレーション）: {main_post_id} - {post_type}")
                print(f"ℹ️ リプライ投稿なし")
                
                print(f"🎉 {account_id}: 投稿完了（シミュレーション）")
                
                return {
                    "success": True,
                    "test_mode": True,
                    "main_post_id": main_post_id,
                    "main_content": main_content,
                    "image_urls": image_urls,
                    "post_type": post_type,
                    "auto_detected": True,
                    "no_reply": True
                }
            
            # 実際の投稿処理
            print("\n📤 === 実際の投稿実行 ===")
            
            if post_type == "真のカルーセル":
                # 真のカルーセル投稿
                print(f"🎠 真のカルーセル投稿として {len(image_urls)}枚の画像で投稿を実行します")
                main_result = DirectPost.post_true_carousel(account_id, main_text, image_urls)
            elif post_type == "単一画像":
                # 単一画像投稿
                print(f"🖼️ 画像URL: {image_urls[0]} で投稿を実行します")
                main_result = DirectPost.post_image(account_id, main_text, image_urls[0])
            else:
                # テキストのみ投稿
                print(f"📝 テキストのみで投稿を実行します")
                main_result = DirectPost.post_text(account_id, main_text)
            
            if not main_result:
                print(f"❌ {account_id}: メイン投稿に失敗しました")
                return False
            
            main_post_id = main_result.get('id')
            print(f"✅ {post_type}投稿成功: {main_post_id}")
            print(f"ℹ️ リプライ投稿なし")
            
            print(f"🎉 {account_id}: 単一投稿完了")
            
            return {
                "success": True,
                "main_post_id": main_post_id,
                "main_content": main_content,
                "image_urls": image_urls,
                "post_type": post_type,
                "auto_detected": True,
                "no_reply": True
            }
                
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            traceback.print_exc()
            return False
    
    def all_accounts_post(self, test_mode=False):
        """全アカウント投稿実行"""
        print("\n🚀 === 全アカウント投稿実行 ===")
        
        # トークンリストを再読み込み（ここを追加）
        self.tokens = settings.get_account_tokens()
        
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
                        "reply_post_id": result.get("reply_post_id") if isinstance(result, dict) else None,
                        "post_type": result.get("post_type") if isinstance(result, dict) else "unknown",
                        "auto_detected": result.get("auto_detected") if isinstance(result, dict) else False
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
    
    def all_accounts_post_without_reply(self, test_mode=False):
        """全アカウント投稿実行（リプライなし）"""
        print("\n🚀 === 全アカウント投稿実行（リプライなし） ===")
        
        # トークンリストを再読み込み
        self.tokens = settings.get_account_tokens()
        
        if not self.tokens:
            print("❌ 利用可能なアカウントがありません")
            return {"success": 0, "failed": 0, "accounts": []}
        
        results = {"success": 0, "failed": 0, "accounts": []}
        total_accounts = len(self.tokens)
        
        for i, account_id in enumerate(self.tokens.keys(), 1):
            try:
                print(f"🔄 [{i}/{total_accounts}] {account_id} 投稿開始")
                
                result = self.single_post_without_reply(
                    account_id=account_id,
                    test_mode=test_mode
                )
                
                if result and (result is True or (isinstance(result, dict) and result.get("success"))):
                    results["success"] += 1
                    results["accounts"].append({
                        "account_id": account_id,
                        "status": "success",
                        "main_post_id": result.get("main_post_id") if isinstance(result, dict) else None,
                        "post_type": result.get("post_type") if isinstance(result, dict) else "unknown",
                        "auto_detected": result.get("auto_detected") if isinstance(result, dict) else False,
                        "no_reply": True
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
        print(f"\n📊 === 全アカウント投稿結果（リプライなし） ===")
        print(f"✅ 成功: {results['success']}/{total_accounts}")
        print(f"❌ 失敗: {results['failed']}/{total_accounts}")
        print(f"📈 成功率: {success_rate:.1f}%")
        
        return results
    
    def update_data(self):
        """データ更新とCloudinary画像アップロード"""
        print("\n🔄 === データ更新実行 ===")
        
        try:
            # 1. CSVデータを更新
            result = self.content_system.update_from_csv()
            
            if result and result.get("success"):
                print("✅ データ更新成功")
                print(f"📊 メインコンテンツ: {len(self.content_system.main_contents)}件")
                print(f"📊 アフィリエイト: {len(self.content_system.affiliates)}件")
                
                # 2. 画像アップロードを実行
                print("\n🖼️ === 画像アップロード処理 ===")
                self.upload_all_images()
                
                return True
            else:
                print("❌ データ更新失敗")
                return False
                    
        except Exception as e:
            print(f"❌ データ更新エラー: {e}")
            return False
    
    def upload_all_images(self):
        """全コンテンツの画像をCloudinaryにアップロード（画像ファイル存在ベース）"""
        from src.core.cloudinary_util import get_cloudinary_image_url
        
        print("🔍 === 画像ファイルの自動検出とアップロード ===")
        
        # imagesディレクトリの存在確認
        images_dir = "images"
        if not os.path.exists(images_dir):
            print(f"⚠️ {images_dir} ディレクトリが存在しません。作成します。")
            os.makedirs(images_dir)
            return
        
        # 画像ファイルを直接検索
        image_files = []
        for file in os.listdir(images_dir):
            if file.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                # ファイル名からコンテンツIDを抽出
                if '_image.' in file:
                    content_id = file.split('_image.')[0]
                    image_files.append((content_id, file))
        
        print(f"📊 検出した画像ファイル: {len(image_files)}件")
        
        success_count = 0
        fail_count = 0
        
        # 各画像ファイルをアップロード
        unique_content_ids = list(set([content_id for content_id, _ in image_files]))
        
        for content_id in unique_content_ids:
            print(f"🔄 コンテンツ {content_id} の画像処理中...")
            
            try:
                # 画像URLを取得（自動的にアップロードを実行）
                result = get_cloudinary_image_url(content_id)
                
                if result and result.get('success'):
                    print(f"✅ {content_id}: アップロード成功 - {result.get('image_url')}")
                    success_count += 1
                else:
                    print(f"❌ {content_id}: アップロード失敗")
                    if result:
                        print(f"  詳細: {result}")
                    fail_count += 1
                    
            except Exception as e:
                print(f"❌ {content_id}: エラー - {e}")
                fail_count += 1
        
        # 結果サマリー
        print(f"\n📊 === 画像アップロード結果 ===")
        print(f"✅ 成功: {success_count}件")
        print(f"❌ 失敗: {fail_count}件")
    
    def force_update_images(self):
        """imagesフォルダの画像でCloudinaryの画像を強制上書き"""
        from src.core.cloudinary_util import cloudinary_util
        
        print("\n🔄 === 画像強制更新（Cloudinary上書き） ===")
        
        # imagesディレクトリの存在確認
        images_dir = "images"
        if not os.path.exists(images_dir):
            print(f"⚠️ {images_dir} ディレクトリが存在しません。作成します。")
            os.makedirs(images_dir)
            return False
        
        # 画像ファイルを直接検索
        image_files = []
        for file in os.listdir(images_dir):
            if file.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                # ファイル名からコンテンツIDを抽出
                if '_image.' in file:
                    content_id = file.split('_image.')[0]
                    image_files.append((content_id, file))
        
        print(f"📊 検出した画像ファイル: {len(image_files)}件")
        
        if not image_files:
            print("❌ 処理対象の画像ファイルがありません")
            return False
        
        success_count = 0
        fail_count = 0
        
        # 各画像ファイルをアップロード
        unique_content_ids = list(set([content_id for content_id, _ in image_files]))
        
        for content_id in unique_content_ids:
            print(f"🔄 コンテンツ {content_id} の画像を強制更新中...")
            
            try:
                # ローカルファイルパスを取得
                local_file_path = None
                for cid, filename in image_files:
                    if cid == content_id:
                        local_file_path = os.path.join(images_dir, filename)
                        break
                
                if not local_file_path or not os.path.exists(local_file_path):
                    print(f"❌ {content_id}: ローカルファイルが見つかりません")
                    fail_count += 1
                    continue
                
                # 強制的にCloudinaryに再アップロード
                print(f"📤 {content_id}: ローカルファイル {local_file_path} を強制アップロード中...")
                
                # 既存の関数を使用してアップロード
                result = cloudinary_util.upload_to_cloudinary_with_content_id(local_file_path, content_id)
                
                if result and result.get('success'):
                    print(f"✅ {content_id}: 強制アップロード成功 - {result.get('image_url')}")
                    success_count += 1
                else:
                    print(f"❌ {content_id}: アップロード失敗")
                    if result:
                        print(f"  詳細: {result}")
                    fail_count += 1
                    
            except Exception as e:
                print(f"❌ {content_id}: エラー - {e}")
                traceback.print_exc()
                fail_count += 1
        
        # 結果サマリー
        print(f"\n📊 === 強制画像更新結果 ===")
        print(f"✅ 成功: {success_count}件")
        print(f"❌ 失敗: {fail_count}件")
        
        return success_count > 0
    
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
        
        # アカウント状況 - ここを修正
        print(f"\n👥 アカウント状況:")
        # トークンリストを再読み込み
        self.tokens = settings.get_account_tokens()
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
        print(f"  🤖 自動判定システム: 有効")
        
        # Cloudinary接続テスト
        try:
            cloud_test = cloudinary_util.test_cloudinary_connection()
            if cloud_test:
                print(f"  ☁️ Cloudinary接続: ✅ 成功")
            else:
                print(f"  ☁️ Cloudinary接続: ❌ 失敗")
        except Exception:
            print(f"  ☁️ Cloudinary接続: ❌ エラー")
        
        # imagesディレクトリ確認
        images_dir = "images"
        if os.path.exists(images_dir):
            image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'))]
            print(f"  📁 画像ファイル: {len(image_files)}件")
            
            # カルーセル用画像の確認
            carousel_image_count = 0
            main_image_count = 0
            for f in image_files:
                if '_1_image' in f or '_2_image' in f or '_3_image' in f:
                    carousel_image_count += 1
                elif '_image.' in f and not any(x in f for x in ['_1_', '_2_', '_3_']):
                    main_image_count += 1
            
            print(f"  📷 メイン画像: {main_image_count}件")
            print(f"  🎠 カルーセル用追加画像: {carousel_image_count}件")
            
            # 自動判定例の表示
            print(f"\n🤖 === 自動判定例 ===")
            content_ids = list(set([f.split('_image.')[0] for f in image_files if '_image.' in f]))[:5]
            for content_id in content_ids:
                # このコンテンツIDの画像数をチェック
                related_files = [f for f in image_files if f.startswith(content_id)]
                if len(related_files) > 1:
                    print(f"  {content_id}: 🎠 カルーセル投稿 ({len(related_files)}枚)")
                else:
                    print(f"  {content_id}: 📷 単一画像投稿")
        else:
            print(f"  📁 画像ディレクトリ: ❌ 存在しません")
    
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
            
            # 画像ファイル確認
            images_dir = "images"
            expected_image_path = os.path.join(images_dir, f"{content_id}_image.jpg")
            expected_image_path_png = os.path.join(images_dir, f"{content_id}_image.png")
            expected_image_path_JPG = os.path.join(images_dir, f"{content_id}_image.JPG")
            
            if os.path.exists(expected_image_path):
                print(f"✅ 画像ファイル発見: {expected_image_path}")
            elif os.path.exists(expected_image_path_png):
                print(f"✅ 画像ファイル発見: {expected_image_path_png}")
            elif os.path.exists(expected_image_path_JPG):
                print(f"✅ 画像ファイル発見: {expected_image_path_JPG}")
            else:
                print(f"⚠️ 警告: コンテンツID {content_id} に対応する画像ファイルが見つかりません")
                continue_anyway = input("画像ファイルがありませんが続行しますか？ (y/n): ")
                if continue_anyway.lower() != 'y':
                    return False
            
            # CloudinaryからURLを取得
            print(f"🔍 コンテンツID {content_id} の画像を検索中...")
            cloud_result = get_cloudinary_image_url(content_id)
            
            print(f"🔍 Cloudinary結果: {cloud_result}")
            
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
            
            # 画像ファイル確認
            images_dir = "images"
            for content_id in content_ids:
                expected_image_path = os.path.join(images_dir, f"{content_id}_image.jpg")
                expected_image_path_png = os.path.join(images_dir, f"{content_id}_image.png")
                expected_image_path_JPG = os.path.join(images_dir, f"{content_id}_image.JPG")
                
                if os.path.exists(expected_image_path):
                    print(f"✅ 画像ファイル発見: {expected_image_path}")
                elif os.path.exists(expected_image_path_png):
                    print(f"✅ 画像ファイル発見: {expected_image_path_png}")
                elif os.path.exists(expected_image_path_JPG):
                    print(f"✅ 画像ファイル発見: {expected_image_path_JPG}")
                else:
                    print(f"⚠️ 警告: コンテンツID {content_id} に対応する画像ファイルが見つかりません")
            
            # 各コンテンツIDから画像URLを取得
            image_urls = []
            for content_id in content_ids:
                print(f"🔍 コンテンツID {content_id} の画像を検索中...")
                cloud_result = get_cloudinary_image_url(content_id)
                
                print(f"🔍 Cloudinary結果: {cloud_result}")
                
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
    
    def test_true_carousel_post(self, test_mode=True):
        """真のカルーセル投稿テスト（1つの投稿内で複数画像をスワイプ可能）"""
        try:
            print("\n🎠 === 真のカルーセル投稿テスト ===")
            
            # アカウント選択
            account_id = self.select_account()
            if not account_id:
                print("❌ アカウントが見つかりません")
                return False
            
            # テスト用テキスト
            test_text = "これは真のカルーセル投稿のテストです🎠📷 #テスト #カルーセル"
            
            # メインコンテンツID入力
            print("📝 メインコンテンツIDを入力してください（例: CONTENT_001）")
            main_content_id = input("メインコンテンツID: ").strip()
            
            if not main_content_id:
                print("❌ コンテンツIDが指定されていません")
                return False
            
            # カルーセル用画像を検出
            print("🔍 カルーセル用画像を検索中...")
            image_urls = self.detect_carousel_images(main_content_id)
            
            if len(image_urls) < 2:
                print(f"⚠️ カルーセル投稿には最低2枚の画像が必要です。検出された画像: {len(image_urls)}枚")
                if len(image_urls) == 1:
                    print("単一画像投稿として実行しますか？")
                    continue_single = input("(y/n): ")
                    if continue_single.lower() != 'y':
                        return False
                else:
                    return False
            
            print(f"📊 検出した画像数: {len(image_urls)}")
            for i, url in enumerate(image_urls, 1):
                print(f"  画像{i}: {url}")
            
            # 真のカルーセル投稿実行
            print("🎠 APIを呼び出して真のカルーセル投稿中...")
            
            if test_mode:
                print("🧪 テストモード: 実際には投稿されません")
                print(f"📝 投稿テキスト: {test_text}")
                print(f"🖼️ 画像数: {len(image_urls)}")
                result = {"id": f"test_true_carousel_{int(time.time())}"}
            else:
                result = DirectPost.post_true_carousel(account_id, test_text, image_urls)
            
            if result:
                print(f"✅ 真のカルーセル投稿成功: {result.get('id')}")
                return True
            else:
                print("❌ 真のカルーセル投稿失敗")
                return False
                
        except Exception as e:
            print(f"❌ 真のカルーセル投稿テストエラー: {e}")
            traceback.print_exc()
            return False
    
    def start_scheduler_menu(self):
        """スケジューラーメニュー"""
        print("\n⏰ === スケジューラーシステム ===")
        print("注意: スケジューラーは別途 scheduler_system.py で起動してください")
        print("1. scheduler_system.py の実行")
        print("2. バックグラウンド実行での24時間自動投稿")
        print("3. 投稿時間: [2, 5, 8, 12, 17, 20, 22, 0]時")
        print("4. 🤖 完全自動判定システム対応")
        
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
✅ 真のカルーセル投稿機能実装
✅ 🤖 完全自動判定システム実装
✅ スケジューラー機能完成
✅ 全自動化システム完成

#Python #自動化 #Threads #開発完了 #カルーセル #AI判定"""
        
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
    
    def post_specific_account_no_reply(self, account_id=None, test_mode=None, custom_text=None):
        """
        特定のアカウントでリプライなしの投稿を実行する機能
        
        Args:
            account_id (str, optional): 使用するアカウントID。指定がなければ対話式で選択
            test_mode (bool, optional): テストモードフラグ。指定がなければ対話式で選択
            custom_text (str, optional): カスタムテキスト。指定がなければ対話式で選択
            
        Returns:
            dict: 投稿結果
        """
        print("\n🎯 === 特定アカウント投稿実行（リプライなし） ===")
        
        # アカウントIDが指定されていない場合は対話式で選択
        if account_id is None:
            # トークンリストを再読み込み
            self.tokens = settings.get_account_tokens()
            available_accounts = list(self.tokens.keys())
            
            print("📊 利用可能なアカウント:")
            for i, acc in enumerate(available_accounts, 1):
                print(f"{i}. {acc}")
            
            try:
                selection = int(input("使用するアカウントの番号を入力してください: "))
                if 1 <= selection <= len(available_accounts):
                    account_id = available_accounts[selection - 1]
                    print(f"✅ 選択されたアカウント: {account_id}")
                else:
                    print("❌ 無効な選択です")
                    return None
            except ValueError:
                print("❌ 数値を入力してください")
                return None
        
        # テストモードの選択
        if test_mode is None:
            test_mode = input("テストモードで実行しますか？実際には投稿されません (y/n): ").lower() == 'y'
        
        # カスタムテキストの選択
        if custom_text is None:
            use_custom = input("カスタムテキストを使用しますか？ (y/n): ").lower() == 'y'
            if use_custom:
                custom_text = input("投稿するテキストを入力してください: ")
        
        # 実行確認
        if not test_mode:
            confirm = input(f"🚨 {account_id} で実際に投稿を実行しますか？（リプライなし） (y/n): ").lower()
            if confirm != 'y':
                print("投稿をキャンセルしました")
                return None
        
        print(f"🚀 {account_id} で投稿実行中（リプライなし）...")
        
        # 実際の投稿処理（既存のsingle_post_without_reply関数を使用）
        return self.single_post_without_reply(account_id=account_id, test_mode=test_mode, custom_text=custom_text)

    def sync_account_contents(self, account_id=None, force=False):
        """
        アカウントのコンテンツフォルダを読み込み、システムのキャッシュを更新
        
        Args:
            account_id (str, optional): 同期するアカウントID（Noneの場合は全アカウント）
            force (bool): 既存のデータを上書きするかどうか
            
        Returns:
            dict: 同期結果の統計
        """
        stats = {
            "total_scanned": 0,
            "added": 0,
            "updated": 0,
            "unchanged": 0,
            "errors": 0
        }
        
        print("\n🔄 === アカウントコンテンツ同期 ===")
        
        # 同期するアカウントのリスト
        accounts_to_sync = []
        if account_id:
            accounts_to_sync = [account_id]
        else:
            # 利用可能な全アカウントを取得
            self.tokens = settings.get_account_tokens()
            accounts_to_sync = list(self.tokens.keys())
        
        print(f"🔄 {len(accounts_to_sync)}個のアカウントのコンテンツ同期を開始...")
        
        for acc_id in accounts_to_sync:
            print(f"\n📂 {acc_id} の同期中...")
            content_dir = Path(f"accounts/{acc_id}/contents")
            
            if not content_dir.exists():
                print(f"⚠ {acc_id} のコンテンツディレクトリが見つかりません")
                continue
            
            # コンテンツフォルダを検索
            content_folders = [d for d in content_dir.glob(f"{acc_id}_CONTENT_*") if d.is_dir()]
            print(f"📊 {len(content_folders)}個のコンテンツフォルダを検出")
            
            for folder in content_folders:
                stats["total_scanned"] += 1
                content_id = folder.name
                metadata_file = folder / "metadata.json"
                
                if not metadata_file.exists():
                    print(f"⚠ {content_id}: メタデータファイルがありません")
                    stats["errors"] += 1
                    continue
                
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    if "text" not in metadata:
                        print(f"⚠ {content_id}: テキストデータがありません")
                        stats["errors"] += 1
                        continue
                    
                    # コンテンツデータの作成
                    content_data = {
                        "main_text": metadata["text"],  # 既存のシステム形式に合わせる
                        "id": content_id,  # 既存のシステム形式に合わせる
                        "account_id": acc_id,
                        "from_folder": True,
                        "original_content_id": metadata.get("original_content_id", ""),
                        "created_at": metadata.get("created_at", "")
                    }
                    
                    # 既存のコンテンツをチェック
                    content_in_system = False
                    for existing_id, existing_content in self.content_system.main_contents.items():
                        if existing_id == content_id:
                            content_in_system = True
                            if force or existing_content.get("main_text") != content_data["main_text"]:
                                self.content_system.main_contents[content_id] = content_data
                                print(f"✅ {content_id}: 更新")
                                stats["updated"] += 1
                            else:
                                print(f"ℹ {content_id}: 変更なし")
                                stats["unchanged"] += 1
                            break
                    
                    if not content_in_system:
                        self.content_system.main_contents[content_id] = content_data
                        print(f"✅ {content_id}: 追加")
                        stats["added"] += 1
                
                except Exception as e:
                    print(f"❌ {content_id}: エラー - {e}")
                    stats["errors"] += 1        
        # キャッシュの保存
        try:
            # self.content_system.save_main_contents_cache() の代わりに
            # 直接JSONファイルに書き込む
            cache_file = 'src/data/main_contents.json'
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.content_system.main_contents, f, ensure_ascii=False, indent=2)
            print("\n✅ コンテンツキャッシュを保存しました")
        except Exception as e:
            print(f"\n❌ キャッシュ保存エラー: {e}")
        
        # 結果の表示
        print("\n===== 同期結果 =====")
        print(f"スキャンされたフォルダ: {stats['total_scanned']}")
        print(f"追加されたコンテンツ: {stats['added']}")
        print(f"更新されたコンテンツ: {stats['updated']}")
        print(f"変更なし: {stats['unchanged']}")
        print(f"エラー: {stats['errors']}")
        
        return stats
    
    def interactive_menu(self):
        """対話型メニュー"""
        while True:
            print("\n" + "="*50)
            print("🎯 Python版Threads自動投稿システム")
            print("🤖 完全自動判定機能付き")
            print("="*50)
            print("1. 📱 単発投稿（テストモード）")
            print("2. 🚀 単発投稿（実際の投稿）🤖")
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
            print("13. ✨ 真のカルーセル投稿テスト（テストモード）")
            print("14. 🌈 真のカルーセル投稿テスト（実際の投稿）")
            print("15. 📩 単発投稿（リプライなし）")
            print("16. 📨 全アカウント投稿（リプライなし）")
            print("17. 🔄 画像強制更新（Cloudinary上書き）")
            if ACCOUNT_SETUP_AVAILABLE:
                print("18. 🆕 新規アカウント追加（自動一括追加）")
            print("19. 📝 特定アカウント投稿（リプライなし）")  # 新機能
            print("20. 🔄 アカウントコンテンツ同期")  # 新機能
            print("0. 🚪 終了")
            print("-"*50)
            print("🤖 項目2は画像ファイルの存在を自動判定します")
            print("   - 複数画像 → 真のカルーセル投稿")
            print("   - 単一画像 → 画像投稿")
            print("   - 画像なし → テキスト投稿")
            print("📩 項目15-16はツリー投稿（アフィリエイトリプライ）を行いません")
            print("🔄 項目17はimagesフォルダの画像でCloudinaryを強制上書きします")
            print("📝 項目19は特定アカウントでリプライなし投稿を行います")  # 新機能の説明
            print("🔄 項目20はアカウントフォルダからコンテンツを同期します")  # 新機能の説明
            print("-"*50)
            
            try:
                choice = input("選択してください (0-20): ").strip()
                
                if choice == "0":
                    print("👋 システムを終了します")
                    break
                elif choice == "1":
                    self.single_post(test_mode=True)
                elif choice == "2":
                    confirm = input("🚨 実際にThreadsに投稿します（自動判定機能付き）。続行しますか？ (y/n): ")
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
                elif choice == "13":
                    self.test_true_carousel_post(test_mode=True)
                elif choice == "14":
                    confirm = input("🚨 実際に真のカルーセル投稿します。続行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        self.test_true_carousel_post(test_mode=False)
                elif choice == "15":
                    confirm = input("🚨 実際にThreadsに投稿します（リプライなし）。続行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        self.single_post_without_reply(test_mode=False)
                elif choice == "16":
                    confirm = input("🚨 全アカウントで実際にThreadsに投稿します（リプライなし）。続行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        self.all_accounts_post_without_reply(test_mode=False)
                elif choice == "17":
                    confirm = input("🚨 Cloudinary上の画像をimagesフォルダの画像で強制上書きします。続行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        self.force_update_images()
                # ACCOUNT_SETUP_AVAILABLE の処理を項目18に移動
                elif choice == "18" and ACCOUNT_SETUP_AVAILABLE:
                    print("\n🆕 === 新規アカウント自動一括追加 ===")
                    print("account_setup.py の accounts_to_add リストからアカウントを追加します")
                    print("💡 事前に account_setup.py を編集してください")
                    confirm = input("アカウント自動一括追加を実行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        try:
                            # 一括アカウント追加を実行（リロードして最新のコードを使用）
                            from importlib import reload
                            import account_setup
                            reload(account_setup)  # モジュールを再読み込み
                            account_setup.bulk_setup_accounts()
    
                            # 更新を反映するためにデータを再読み込み
                            self.update_data()
                            print("✅ アカウント追加後のデータを更新しました")
    
                            # 環境変数ファイル修復の確認と実行 (新規追加部分)
                            fix_env = input("環境変数ファイルの問題を修復しますか？ (y/n): ")
                            if fix_env.lower() == 'y':
                                try:
                                    # 環境変数修復を実行
                                    account_setup.fix_all_env_issues()
                                    print("✅ 環境変数ファイルの修復が完了しました")
                                except Exception as e:
                                    print(f"❌ 環境変数修復エラー: {str(e)}")
                                    
                            # 環境変数ファイルを整理（オプション）
                            organize = input("環境変数ファイルを整理しますか？ (y/n): ")
                            if organize.lower() == 'y':
                                account_setup.reorganize_env_file()
    
                        except Exception as e:
                            print(f"❌ アカウント追加エラー: {str(e)}")
                            traceback.print_exc()
                # 新機能の処理を追加
                elif choice == "19":
                    self.post_specific_account_no_reply()
                elif choice == "20":
                    print("\n🔄 === アカウントコンテンツ同期メニュー ===")
                    print("1. 特定アカウントのコンテンツを同期")
                    print("2. 全アカウントのコンテンツを同期")
                    print("0. 戻る")
                    
                    sync_choice = input("選択してください: ").strip()
                    
                    if sync_choice == "1":
                        # トークンリストを再読み込み
                        self.tokens = settings.get_account_tokens()
                        available_accounts = list(self.tokens.keys())
                        
                        print("\n📊 利用可能なアカウント:")
                        for i, acc in enumerate(available_accounts, 1):
                            print(f"{i}. {acc}")
                        
                        try:
                            selection = int(input("同期するアカウントの番号を入力してください: "))
                            if 1 <= selection <= len(available_accounts):
                                account_id = available_accounts[selection - 1]
                                force = input("既存のデータを上書きしますか？ (y/n): ").lower() == 'y'
                                self.sync_account_contents(account_id, force)
                            else:
                                print("❌ 無効な選択です")
                        except ValueError:
                            print("❌ 数値を入力してください")
                    
                    elif sync_choice == "2":
                        force = input("既存のデータを上書きしますか？ (y/n): ").lower() == 'y'
                        self.sync_account_contents(None, force)
                    
                    elif sync_choice == "0":
                        continue
                    
                    else:
                        print("❌ 無効な選択です")
                else:
                    print("❌ 無効な選択です")
                    
            except KeyboardInterrupt:
                print("\n👋 システムを終了します")
                break
            except Exception as e:
                print(f"❌ エラー: {e}")
                traceback.print_exc()

def main():
    """メイン実行関数"""
    print("🚀 Python版Threads自動投稿システム")
    print("=" * 50)
    print("🎉 GAS版完全互換 + 画像投稿 + 真のカルーセル + スケジューラー")
    print("🤖 完全自動判定機能付き")
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