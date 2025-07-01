"""
Threads自動いいね機能
おすすめフィードの投稿に自動でいいねを行う
"""
import os
import json
import time
import pickle
from datetime import datetime
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from proxy.proxy_manager import ProxyManager


# ロガー設定
logger = logging.getLogger('threads-auto-like')

class ThreadsAutoLike:
    """Threads自動いいね機能クラス"""
    
    def __init__(self):
        """初期化"""
        self.driver = None
        self.wait = None
        self.session_dir = "sessions"
        self.liked_posts_file = "liked_posts.json"
        self.liked_posts = self.load_liked_posts()
        self.proxy_manager = ProxyManager()
        
        os.makedirs(self.session_dir, exist_ok=True)

        
        # セッションディレクトリ作成
        os.makedirs(self.session_dir, exist_ok=True)
        
    def load_liked_posts(self) -> Dict[str, List[str]]:
        """いいね済み投稿の履歴を読み込み"""
        if os.path.exists(self.liked_posts_file):
            try:
                with open(self.liked_posts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_liked_posts(self):
        """いいね済み投稿の履歴を保存"""
        with open(self.liked_posts_file, 'w', encoding='utf-8') as f:
            json.dump(self.liked_posts, f, ensure_ascii=False, indent=2)
    
    def setup_driver(self, account_id: str, headless: bool = False):
        """Seleniumドライバーのセットアップ（プロキシ対応版）"""
        options = webdriver.ChromeOptions()
        
        # セッションデータの保存先
        user_data_dir = os.path.join(os.getcwd(), self.session_dir, account_id)
        options.add_argument(f'user-data-dir={user_data_dir}')
        
        # プロキシ設定を追加
        proxy_url = self.proxy_manager.get_proxy_for_selenium(account_id)
        if proxy_url:
            self.logger.info(f"[{account_id}] プロキシを使用: {proxy_url[:30]}...")
            
            # プロキシ認証が必要な場合の処理
            if '@' in proxy_url:
                # Selenium Wireなどの拡張が必要な場合はここで処理
                # 基本的なプロキシ設定
                options.add_argument(f'--proxy-server={proxy_url}')
            else:
                options.add_argument(f'--proxy-server={proxy_url}')
        
        # その他のオプション
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if headless:
            options.add_argument('--headless')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-gpu')
        
        # 日本語対応
        options.add_argument('--lang=ja')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        
        # User-Agentを設定
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def login(self, account_id: str, manual: bool = True) -> bool:
        """Threadsにログイン"""
        try:
            print(f"🔐 {account_id} でログイン処理を開始します...")
            
            # Threadsのログインページへ
            self.driver.get("https://www.threads.net/login")
            time.sleep(3)
            
            # 既存のセッションをチェック
            if self.check_logged_in():
                print(f"✅ {account_id} は既にログイン済みです")
                return True
            
            if manual:
                print("\n⚠️ 手動でログインしてください")
                print("1. ブラウザでログイン情報を入力")
                print("2. ログインが完了したらEnterキーを押してください")
                input("\nログイン完了後、Enterキーを押してください...")
                
                if self.check_logged_in():
                    print("✅ ログイン成功！セッションを保存しました")
                    return True
                else:
                    print("❌ ログインが確認できませんでした")
                    return False
            else:
                # 自動ログイン（セッションが保存されている場合）
                time.sleep(5)
                if self.check_logged_in():
                    print(f"✅ {account_id} 自動ログイン成功")
                    return True
                else:
                    print(f"❌ {account_id} 自動ログイン失敗。手動ログインが必要です")
                    return False
                    
        except Exception as e:
            print(f"❌ ログインエラー: {e}")
            logger.error(f"ログインエラー: {e}", exc_info=True)
            return False
    
    def check_logged_in(self) -> bool:
        """ログイン状態を確認"""
        try:
            # URLでログイン状態を判定
            current_url = self.driver.current_url
            if "login" not in current_url and "threads.net" in current_url:
                return True
                
            # ログイン後の要素を探す（複数の可能性を試す）
            possible_selectors = [
                '[aria-label="ホーム"]',
                '[aria-label="Home"]',
                'svg[aria-label="ホーム"]',
                'a[href="/"]',
                '[role="navigation"]',
                'nav'
            ]
            
            for selector in possible_selectors:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, selector)
                    return True
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"ログイン確認エラー: {e}")
        
        return False

    def navigate_to_home(self) -> bool:
        """ホーム（おすすめフィード）へ移動"""
        try:
            print("🏠 ホームフィードへ移動中...")
            
            # 既にホームにいる可能性をチェック
            current_url = self.driver.current_url
            if current_url == "https://www.threads.net/" or current_url == "https://www.threads.net":
                print("✅ 既にホームフィードにいます")
            else:
                self.driver.get("https://www.threads.net/")
            
            # ページ読み込み待機（より柔軟に）
            time.sleep(5)  # 固定待機時間を増やす
            
            # 投稿要素の存在を確認（複数の可能性を試す）
            post_found = False
            possible_selectors = [
                'article',
                'div[role="article"]',
                '[data-pressable-container="true"]',
                'div[role="main"]',
                'main',
                # 投稿コンテナの可能性があるクラス
                'div.x1ypdohk',
                'div[class*="x1ypdohk"]'
            ]
            
            for selector in possible_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ 投稿要素を検出しました（{selector}）: {len(elements)}個")
                        post_found = True
                        break
                except:
                    continue
            
            if not post_found:
                # スクリーンショットを撮って状況を確認
                print("⚠️ 投稿要素が見つかりません。ページの状態を確認中...")
                
                # ページソースの一部を確認（デバッグ用）
                page_source = self.driver.page_source[:1000]
                if "ログイン" in page_source or "login" in page_source.lower():
                    print("❌ まだログインページにいるようです")
                    return False
            
            print("✅ ホームフィードに到着")
            return True
            
        except Exception as e:
            print(f"❌ ホームフィード移動エラー: {e}")
            logger.error(f"ホームフィード移動エラー: {e}", exc_info=True)
            
            # 現在のURLを表示（デバッグ用）
            try:
                print(f"📍 現在のURL: {self.driver.current_url}")
            except:
                pass
                
            return False
    
    def navigate_to_user_profile(self, username: str) -> bool:
        """特定ユーザーのプロフィールページへ移動"""
        try:
            print(f"👤 @{username} のプロフィールへ移動中...")
            
            # ユーザープロフィールのURLに直接アクセス
            profile_url = f"https://www.threads.net/@{username}"
            self.driver.get(profile_url)
            time.sleep(5)  # ページ読み込み待機
            
            # プロフィールページの読み込みを確認
            profile_loaded = False
            
            # プロフィール要素の確認
            profile_selectors = [
                '[data-pressable-container="true"]',
                'article',
                'div[role="article"]',
                f'[aria-label*="{username}"]',
                'div[role="main"]'
            ]
            
            for selector in profile_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        profile_loaded = True
                        print(f"✅ 投稿要素を検出しました（{selector}）: {len(elements)}個")
                        break
                except:
                    continue
            
            if profile_loaded:
                print(f"✅ @{username} のプロフィールページに到着")
                return True
            else:
                print(f"❌ @{username} のプロフィールページが見つかりません")
                return False
                
        except Exception as e:
            print(f"❌ プロフィール移動エラー: {e}")
            logger.error(f"プロフィール移動エラー: {e}", exc_info=True)
            return False
    
    def find_like_buttons(self) -> List[Dict]:
        """いいねボタンを検出"""
        like_buttons = []
        
        try:
            # まず、ページに投稿があるか確認
            print("🔍 投稿を検索中...")
            
            # いいねボタンのSVGを探す（複数のパターンを試す）
            svg_selectors = [
                'svg[aria-label="「いいね！」"]',
                'svg[aria-label="いいね"]',
                'svg[aria-label="Like"]',
                # パスで探す場合
                'svg path[d*="M1.34375 7.53125"]'  # いいねボタンのパスの一部
            ]
            
            svg_elements = []
            for selector in svg_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        svg_elements.extend(elements)
                        print(f"✅ いいねボタン要素を検出: {len(elements)}個（{selector}）")
                        break
                except:
                    continue
            
            if not svg_elements:
                print("⚠️ いいねボタンが見つかりません")
                # デバッグ: SVG要素をすべて取得
                all_svgs = self.driver.find_elements(By.TAG_NAME, 'svg')
                print(f"📊 ページ内のSVG要素数: {len(all_svgs)}")
                
                # aria-labelを持つSVGを確認
                for svg in all_svgs[:5]:  # 最初の5個だけ確認
                    try:
                        aria_label = svg.get_attribute('aria-label')
                        if aria_label:
                            print(f"  - SVG aria-label: {aria_label}")
                    except:
                        pass
            
            # いいね済みカウンター
            already_liked_count = 0
            
            for svg in svg_elements:
                try:
                    # SVGの親要素（クリック可能なボタン）を取得
                    button = svg.find_element(By.XPATH, './ancestor::div[@role="button"]')
                    
                    # すでにいいね済みかチェック（より厳密に）
                    path = svg.find_element(By.TAG_NAME, 'path')
                    
                    # pathの属性を詳細にチェック
                    stroke_width = path.get_attribute('stroke-width')
                    fill = path.get_attribute('fill')
                    d_attribute = path.get_attribute('d')
                    
                    # いいね済みの判定条件を強化
                    # 1. stroke-widthがない（塗りつぶされている）
                    # 2. fillが設定されている（transparentやnone以外）
                    # 3. pathのd属性が異なる（いいね済みは別のパス形状の場合がある）
                    is_liked = False
                    
                    # stroke-widthがない、またはfillが設定されている場合はいいね済み
                    if not stroke_width or (fill and fill not in ['transparent', 'none', '']):
                        is_liked = True
                        already_liked_count += 1
                    
                    # ボタンのクラスや親要素でもチェック（いいね済みは色が変わる場合がある）
                    try:
                        button_classes = button.get_attribute('class')
                        # いいね済みの場合、特定のクラスが追加される可能性
                        if button_classes and any(cls in button_classes for cls in ['liked', 'active', 'selected']):
                            is_liked = True
                    except:
                        pass
                    
                    if not is_liked:
                        # 投稿の識別情報を取得（より詳細に）
                        post_container = button.find_element(By.XPATH, './ancestor::article | ./ancestor::div[@data-pressable-container="true"]')
                        
                        # 投稿のテキストや時間などから一意のIDを生成
                        post_text = ""
                        try:
                            text_elements = post_container.find_elements(By.CSS_SELECTOR, 'span[dir="auto"]')
                            if text_elements:
                                post_text = text_elements[0].text[:30]  # 最初の30文字
                        except:
                            pass
                        
                        # より一意性の高いpost_idを生成
                        post_id = f"post_{hash(post_text)}_{len(like_buttons)}_{int(time.time())}"
                        
                        like_buttons.append({
                            'button': button,
                            'post_id': post_id,
                            'svg': svg,
                            'post_text': post_text
                        })
                        
                except Exception as e:
                    # 個別のボタン処理エラーは無視
                    logger.debug(f"ボタン処理エラー: {e}")
                    continue
            
            print(f"📊 {len(like_buttons)}個のいいね可能な投稿を検出（{already_liked_count}個は既にいいね済み）")
            return like_buttons
            
        except Exception as e:
            print(f"❌ いいねボタン検出エラー: {e}")
            logger.error(f"いいねボタン検出エラー: {e}", exc_info=True)
            return []

    def _like_posts_on_page(self, account_id: str, target_count: int, results: Dict, is_target_user: bool = False) -> int:
        """現在のページで投稿にいいねを実行（内部メソッド）"""
        liked_count = 0
        scroll_count = 0
        max_scrolls = 10 if not is_target_user else 5  # 特定ユーザーページでは少なめ
        consecutive_no_new_posts = 0  # 新しい投稿が見つからない連続回数
        
        # このセッションでいいねした投稿のIDを記録
        session_liked_posts = set()
        
        while liked_count < target_count and scroll_count < max_scrolls:
            # いいねボタンを検出
            like_buttons = self.find_like_buttons()
            
            # 新しくいいね可能な投稿をフィルタリング
            new_like_buttons = []
            for btn in like_buttons:
                if btn['post_id'] not in session_liked_posts and btn['post_id'] not in self.liked_posts.get(account_id, []):
                    new_like_buttons.append(btn)
            
            if not new_like_buttons:
                consecutive_no_new_posts += 1
                if consecutive_no_new_posts >= 3:  # 3回連続で新しい投稿がない場合は終了
                    print("⚠️ 新しい投稿が見つかりません。処理を終了します。")
                    break
                    
                if scroll_count >= max_scrolls - 1:
                    break
                print("⏬ 新しい投稿を読み込むためにスクロール...")
                self.driver.execute_script("window.scrollBy(0, 800)")
                time.sleep(3)  # スクロール後の待機時間を増やす
                scroll_count += 1
                continue
            else:
                consecutive_no_new_posts = 0  # リセット
            
            # 各投稿にいいね
            for btn_info in new_like_buttons:
                if liked_count >= target_count:
                    break
                
                try:
                    post_id = btn_info['post_id']
                    
                    # 二重チェック：すでにいいね済みかチェック
                    if post_id in session_liked_posts or post_id in self.liked_posts.get(account_id, []):
                        results['already_liked'] += 1
                        continue
                    
                    # ボタンまでスクロール
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_info['button'])
                    time.sleep(1.5)  # スクロール後の待機時間を増やす
                    
                    # いいねボタンの状態を再確認
                    try:
                        svg = btn_info['svg']
                        path = svg.find_element(By.TAG_NAME, 'path')
                        stroke_width = path.get_attribute('stroke-width')
                        fill = path.get_attribute('fill')
                        
                        # 再度いいね済みチェック
                        if not stroke_width or (fill and fill not in ['transparent', 'none', '']):
                            print(f"⏭️ 既にいいね済みの投稿をスキップ")
                            results['already_liked'] += 1
                            continue
                    except:
                        pass
                    
                    # いいねを実行
                    btn_info['button'].click()
                    
                    # クリック後の待機（状態変化を待つ）
                    time.sleep(1)
                    
                    # 成功をカウント
                    liked_count += 1
                    results['success'] += 1
                    results['posts'].append(post_id)
                    session_liked_posts.add(post_id)  # セッション内でも記録
                    self.liked_posts[account_id].append(post_id)
                    
                    total_likes = results['success']
                    if btn_info.get('post_text'):
                        print(f"💗 [{total_likes}/{target_count}] いいね完了: {btn_info['post_text'][:20]}...")
                    else:
                        print(f"💗 [{total_likes}/{target_count}] いいね完了")
                    
                    # レート制限対策（2-4秒のランダム待機）
                    import random
                    time.sleep(random.uniform(20, 40))
                    
                except Exception as e:
                    results['failed'] += 1
                    print(f"❌ いいねエラー: {str(e)[:100]}")
                    logger.error(f"いいねエラー: {e}")
                    # エラー後は少し長めに待機
                    time.sleep(3)
                    continue
            
            # 次のバッチのためにスクロール
            if liked_count < target_count:
                print("⏬ 追加の投稿を読み込み中...")
                self.driver.execute_script("window.scrollBy(0, 800)")
                time.sleep(3)
                scroll_count += 1
        
        return liked_count
    
    def like_home_feed_posts(self, account_id: str, target_count: int) -> Dict:
        """ホームフィード（おすすめ）の投稿にいいねを実行"""
        print("🏠 おすすめの投稿にいいねします")
        results = {
            'success': 0,
            'failed': 0,
            'already_liked': 0,
            'posts': []
        }
        
        try:
            # アカウントの履歴を初期化
            if account_id not in self.liked_posts:
                self.liked_posts[account_id] = []
            
            # ホームフィードへ移動
            if not self.navigate_to_home():
                print("❌ ホームフィードへの移動に失敗しました")
                return results
            
            # いいね実行
            liked_count = self._like_posts_on_page(
                account_id, 
                target_count, 
                results,
                is_target_user=False
            )
            
            # 履歴を保存
            self.save_liked_posts()
            
            print(f"\n✅ おすすめ投稿へのいいね処理完了")
            print(f"💗 成功: {results['success']}件")
            print(f"⏭️ スキップ（いいね済み）: {results['already_liked']}件")
            print(f"❌ 失敗: {results['failed']}件")
            
            return results
            
        except Exception as e:
            print(f"❌ いいね処理エラー: {e}")
            logger.error(f"いいね処理エラー: {e}", exc_info=True)
            return results
    
    def like_user_posts(self, account_id: str, target_user: str, target_count: int) -> Dict:
        """特定ユーザーの投稿にいいねを実行"""
        print(f"👤 @{target_user} の投稿にいいねします")
        results = {
            'success': 0,
            'failed': 0,
            'already_liked': 0,
            'posts': [],
            'target_user': target_user
        }
        
        try:
            # アカウントの履歴を初期化
            if account_id not in self.liked_posts:
                self.liked_posts[account_id] = []
            
            # 特定ユーザーのプロフィールへ移動
            if not self.navigate_to_user_profile(target_user):
                print(f"❌ @{target_user} のプロフィールが見つかりません")
                return results
            
            # いいね実行
            liked_count = self._like_posts_on_page(
                account_id, 
                target_count, 
                results,
                is_target_user=True
            )
            
            # 履歴を保存
            self.save_liked_posts()
            
            print(f"\n✅ @{target_user} への いいね処理完了")
            print(f"💗 成功: {results['success']}件")
            print(f"⏭️ スキップ（いいね済み）: {results['already_liked']}件")
            print(f"❌ 失敗: {results['failed']}件")
            
            return results
            
        except Exception as e:
            print(f"❌ いいね処理エラー: {e}")
            logger.error(f"いいね処理エラー: {e}", exc_info=True)
            return results
    
    def like_posts(self, account_id: str, target_count: int, target_user: Optional[str] = None) -> Dict:
        """投稿にいいねを実行（互換性のため残す・非推奨）"""
        if target_user:
            return self.like_user_posts(account_id, target_user, target_count)
        else:
            return self.like_home_feed_posts(account_id, target_count)
    
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()
            self.driver = None