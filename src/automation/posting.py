import time
import datetime
from config.settings import logger, settings
from src.core.threads_api import ThreadsAPI, threads_api
from src.core.account_manager import account_manager
from src.core.content_manager import ContentManager
from src.core.cloudinary_util import CloudinaryUtil

class PostingManager:
    """投稿の実行を管理するクラス"""
    
    def __init__(self):
        self.threads_api = threads_api
        self.account_manager = account_manager
        self.content_manager = ContentManager()
        self.cloudinary_util = CloudinaryUtil()
    
    def create_single_post(self, account_id="main_account", content=None):
        """単一の投稿を作成"""
        try:
            # アカウント取得
            account = self.account_manager.get_account_by_id(account_id)
            if not account:
                logger.error(f"アカウント '{account_id}' が見つかりません")
                return None
            
            # コンテンツが指定されていない場合はランダム選択
            if content is None:
                content = self.content_manager.get_random_post()
            
            if not content:
                logger.error("投稿用コンテンツが取得できませんでした")
                return None
            
            # 投稿内容
            post_text = content.get("text", "")
            
            # 投稿実行
            result = self.threads_api.create_text_post(account, post_text)
            
            if result:
                # 投稿記録を更新
                self.account_manager.update_last_post_time(account_id)
                
                # 履歴に追加
                post_info = {
                    "post_id": result.get("id"),
                    "content_id": content.get("id"),
                    "text": post_text,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "text",
                    "account": account_id
                }
                self.content_manager.add_to_history(post_info)
            
            return result
        except Exception as e:
            logger.error(f"投稿作成エラー: {str(e)}")
            return None
    
    def create_tree_post(self, account_id="main_account", with_affiliate=True):
        """ツリー投稿（メイン + アフィリエイト）を作成"""
        try:
            # アカウント取得
            account = self.account_manager.get_account_by_id(account_id)
            if not account:
                logger.error(f"アカウント '{account_id}' が見つかりません")
                return None
            
            # メイン投稿用コンテンツ取得
            main_content = self.content_manager.get_random_post()
            if not main_content:
                logger.error("メイン投稿用コンテンツが取得できませんでした")
                return None
            
            # メイン投稿実行
            main_result = self.threads_api.create_text_post(
                account, main_content.get("text", "")
            )
            
            if not main_result:
                logger.error("メイン投稿に失敗しました")
                return None
            
            main_post_id = main_result.get("id")
            
            # 投稿記録を更新
            self.account_manager.update_last_post_time(account_id)
            
            # 履歴に追加
            post_info = {
                "post_id": main_post_id,
                "content_id": main_content.get("id"),
                "text": main_content.get("text", ""),
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "text",
                "account": account_id
            }
            self.content_manager.add_to_history(post_info)
            
            # アフィリエイト投稿が不要な場合は終了
            if not with_affiliate:
                return main_result
            
            # APIリクエスト間隔を空ける
            delay = settings.posting.reply_delay_minutes * 60
            if delay > 0:
                logger.info(f"アフィリエイト投稿待機中... {delay}秒")
                time.sleep(delay)
            
            # アフィリエイト投稿用コンテンツ取得
            affiliate_content = self.content_manager.get_matching_affiliate(main_content)
            if not affiliate_content:
                logger.warning("アフィリエイト投稿用コンテンツが取得できませんでした")
                return main_result
            
            # アフィリエイトリプライ投稿実行
            affiliate_result = self.threads_api.create_reply_post(
                account, 
                affiliate_content.get("text", ""), 
                main_post_id
            )
            
            if affiliate_result:
                # 履歴に追加
                reply_info = {
                    "post_id": affiliate_result.get("id"),
                    "parent_id": main_post_id,
                    "content_id": affiliate_content.get("id"),
                    "text": affiliate_content.get("text", ""),
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "reply",
                    "account": account_id
                }
                self.content_manager.add_to_history(reply_info)
            
            return {
                "main": main_result,
                "affiliate": affiliate_result
            }
        except Exception as e:
            logger.error(f"ツリー投稿作成エラー: {str(e)}")
            return None
    
    def create_image_post(self, account_id="main_account", content=None, image_path=None):
        """画像付き投稿を作成"""
        try:
            # アカウント取得
            account = self.account_manager.get_account_by_id(account_id)
            if not account:
                logger.error(f"アカウント '{account_id}' が見つかりません")
                return None
            
            # コンテンツが指定されていない場合はランダム選択
            if content is None:
                content = self.content_manager.get_random_post()
            
            if not content:
                logger.error("投稿用コンテンツが取得できませんでした")
                return None
            
            # 投稿内容
            post_text = content.get("text", "")
            
            # 画像がない場合はテキスト投稿に切り替え
            if not image_path:
                logger.warning("画像が指定されていないため、テキスト投稿を実行します")
                return self.create_single_post(account_id, content)
            
            # 画像アップロード
            image_url = self.cloudinary_util.upload_image(image_path)
            if not image_url:
                logger.error("画像アップロードに失敗したため、テキスト投稿を実行します")
                return self.create_single_post(account_id, content)
            
            # 画像投稿実行
            result = self.threads_api.create_image_post(account, post_text, image_url)
            
            if result:
                # 投稿記録を更新
                self.account_manager.update_last_post_time(account_id)
                
                # 履歴に追加
                post_info = {
                    "post_id": result.get("id"),
                    "content_id": content.get("id"),
                    "text": post_text,
                    "image": image_url,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "image",
                    "account": account_id
                }
                self.content_manager.add_to_history(post_info)
            
            return result
        except Exception as e:
            logger.error(f"画像投稿作成エラー: {str(e)}")
            return None
    
    def create_multi_image_post(self, account_id="main_account", content=None, image_paths=None):
        """複数画像付き投稿を作成"""
        try:
            # アカウント取得
            account = self.account_manager.get_account_by_id(account_id)
            if not account:
                logger.error(f"アカウント '{account_id}' が見つかりません")
                return None
            
            # コンテンツが指定されていない場合はランダム選択
            if content is None:
                content = self.content_manager.get_random_post()
            
            if not content:
                logger.error("投稿用コンテンツが取得できませんでした")
                return None
            
            # 投稿内容
            post_text = content.get("text", "")
            
            # 画像がない場合はテキスト投稿に切り替え
            if not image_paths or len(image_paths) == 0:
                logger.warning("画像が指定されていないため、テキスト投稿を実行します")
                return self.create_single_post(account_id, content)
            
            # 画像アップロード
            image_urls = []
            for path in image_paths:
                img_url = self.cloudinary_util.upload_image(path)
                if img_url:
                    image_urls.append(img_url)
            
            if not image_urls:
                logger.error("すべての画像アップロードに失敗したため、テキスト投稿を実行します")
                return self.create_single_post(account_id, content)
            
            # 複数画像投稿実行
            result = self.threads_api.create_multi_image_post(account, post_text, image_urls)
            
            if result:
                # 投稿記録を更新
                self.account_manager.update_last_post_time(account_id)
                
                # 履歴に追加
                post_info = {
                    "post_id": result.get("id"),
                    "content_id": content.get("id"),
                    "text": post_text,
                    "images": image_urls,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "multi_image",
                    "account": account_id
                }
                self.content_manager.add_to_history(post_info)
            
            return result
        except Exception as e:
            logger.error(f"複数画像投稿作成エラー: {str(e)}")
            return None

# グローバルインスタンス
posting_manager = PostingManager()