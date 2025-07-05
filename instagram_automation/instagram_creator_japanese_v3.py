# instagram_automation/instagram_creator_japanese_v3.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import undetected_chromedriver as uc
import time
import random
import string
import json
import os
import re
from datetime import datetime
import requests
import zipfile
import shutil

class InstagramCreatorJapaneseV3:
    def __init__(self, use_proxy=False, sms_api_key=None, captcha_api_key=None):
        """
        初期化
        SMS認証・CAPTCHA対応 + kuku.lu捨てメアド版
        """
        self.use_proxy = use_proxy
        self.sms_api_key = sms_api_key or "d7549f9386e4dc5349dAde541f83df6c"
        self.captcha_api_key = captcha_api_key or "6c900aee84f21e9923a34d1432022e2a"
        
        # ブラウザインスタンス
        self.driver = None
        self.mail_driver = None  # メール用の別ブラウザ
        
        # アカウント情報
        self.email_account = None
        self.user_info = None
        self.created_account = None
        
        # プロキシセッションをファイルから読み込む
        self.sessions = self.load_proxy_sessions()
        
        # 使用済みプロキシの管理
        self.used_sessions_file = "used_proxy_sessions.json"
        self.used_sessions = self.load_used_sessions()
        
        # 利用可能なセッションから選択
        self.proxy_session = self.select_proxy_session() if use_proxy else None
        
        # Chrome オプション
        self.options = Options()
        
    def get_random_user_agent(self):
        """ランダムなUser-Agentを生成"""
        user_agents = [
            # Windows Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            # Mac Chrome
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            # Windows Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
            # Windows Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        ]
        return random.choice(user_agents)
    
    def create_proxy_extension(self):
        """プロキシ認証用の拡張機能を作成（改善版）"""
        if not self.proxy_session:
            return None
            
        # プロキシ情報を解析
        parts = self.proxy_session.split(':')
        if len(parts) < 4:
            print("❌ プロキシ形式が正しくありません")
            return None
            
        proxy_host = parts[0]
        proxy_port = parts[1]
        proxy_user = parts[2]
        proxy_password = ':'.join(parts[3:])
        
        # 拡張機能のディレクトリを作成
        extension_dir = os.path.join(os.getcwd(), "proxy_extension")
        if os.path.exists(extension_dir):
            shutil.rmtree(extension_dir)
        os.makedirs(extension_dir)
        
        # manifest.json (Manifest V2を使用)
        manifest = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy Auth Extension",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version": "22.0.0"
        }
        
        # background.js
        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: parseInt({proxy_port})
                }},
                bypassList: ["localhost", "127.0.0.1"]
            }}
        }};

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_user}",
                    password: "{proxy_password}"
                }}
            }};
        }}

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """
        
        # ファイルを作成
        with open(os.path.join(extension_dir, "manifest.json"), 'w') as f:
            json.dump(manifest, f, indent=2)
            
        with open(os.path.join(extension_dir, "background.js"), 'w') as f:
            f.write(background_js)
            
        print(f"✅ プロキシ拡張機能を作成: {extension_dir}")
        return extension_dir
    
    def enhance_stealth_advanced(self):
        """より高度な検出回避"""
        # WebRTC漏洩対策とCanvas Fingerprinting対策
        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    // webdriver検出を回避
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false
                    });
                    
                    // Chrome検出を回避
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                    
                    // permissions検出を回避
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    // plugins検出を回避
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [
                            {
                                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                                description: "Portable Document Format",
                                filename: "internal-pdf-viewer",
                                length: 1,
                                name: "Chrome PDF Plugin"
                            }
                        ]
                    });
                    
                    // languages検出を回避
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['ja-JP', 'ja', 'en-US', 'en']
                    });
                    
                    // WebRTC IPリーク対策
                    const config = {
                        iceServers: [{urls: ['stun:stun.l.google.com:19302']}],
                        iceCandidatePoolSize: 0
                    };
                    const pc = new RTCPeerConnection(config);
                    
                    // Canvas Fingerprinting対策
                    const originalGetContext = HTMLCanvasElement.prototype.getContext;
                    HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                        if (type === '2d') {
                            const context = originalGetContext.apply(this, [type, ...args]);
                            const originalGetImageData = context.getImageData;
                            context.getImageData = function(...args) {
                                const imageData = originalGetImageData.apply(this, args);
                                for (let i = 0; i < imageData.data.length; i += 4) {
                                    imageData.data[i] = imageData.data[i] + (Math.random() * 2 - 1);
                                    imageData.data[i + 1] = imageData.data[i + 1] + (Math.random() * 2 - 1);
                                    imageData.data[i + 2] = imageData.data[i + 2] + (Math.random() * 2 - 1);
                                }
                                return imageData;
                            };
                            return context;
                        }
                        return originalGetContext.apply(this, [type, ...args]);
                    };
                    
                    // WebGL Fingerprinting対策
                    const getParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) {
                            return 'Intel Inc.';
                        }
                        if (parameter === 37446) {
                            return 'Intel Iris OpenGL Engine';
                        }
                        return getParameter.call(this, parameter);
                    };
                    
                    // Battery API無効化
                    delete navigator.getBattery;
                    
                    // Notification API偽装
                    window.Notification = function() {
                        return {
                            permission: 'default',
                            requestPermission: () => Promise.resolve('default')
                        };
                    };
                    window.Notification.permission = 'default';
                    window.Notification.requestPermission = () => Promise.resolve('default');
                '''
            })
        except Exception as e:
            print(f"⚠️ スクリプト注入エラー: {e}")
        
    def load_proxy_sessions(self):
        """proxies.txtからプロキシセッションを読み込む"""
        proxy_file = "proxies.txt"
        
        # まず instagram_automation ディレクトリ内を確認
        if not os.path.exists(proxy_file):
            # 親ディレクトリも確認
            parent_proxy_file = os.path.join("..", proxy_file)
            if os.path.exists(parent_proxy_file):
                proxy_file = parent_proxy_file
        
        try:
            with open(proxy_file, 'r', encoding='utf-8') as f:
                sessions = [line.strip() for line in f.readlines() if line.strip()]
            print(f"✅ プロキシリスト読み込み成功: {len(sessions)}個のプロキシ")
            return sessions
        except FileNotFoundError:
            print(f"❌ {proxy_file} が見つかりません")
            print("   proxies.txt を以下のいずれかの場所に配置してください:")
            print("   - instagram_automation/proxies.txt")
            print("   - threads-automation-python/proxies.txt")
            return []
        except Exception as e:
            print(f"❌ プロキシリスト読み込みエラー: {e}")
            return []
            
    def load_used_sessions(self):
        """使用済みセッションを読み込む"""
        try:
            with open(self.used_sessions_file, 'r') as f:
                return json.load(f)
        except:
            return []
        
    def save_used_sessions(self):
        """使用済みセッションを保存"""
        try:
            with open(self.used_sessions_file, 'w') as f:
                json.dump(self.used_sessions, f, indent=2)
        except Exception as e:
            print(f"⚠️ 使用済みセッション保存エラー: {e}")
            
    def select_proxy_session(self):
        """未使用のプロキシセッションを選択"""
        if not self.sessions:
            print("❌ プロキシリストが空です")
            return None
            
        # 利用可能なセッションを抽出
        available_sessions = [s for s in self.sessions if s not in self.used_sessions]
        
        if available_sessions:
            selected = random.choice(available_sessions)
            print(f"🌐 選択されたプロキシ: {selected}")
            print(f"📊 利用可能: {len(available_sessions)}個 / 全体: {len(self.sessions)}個")
            return selected
        else:
            print("⚠️ すべてのプロキシが使用済みです。リストをリセットします。")
            self.used_sessions = []
            self.save_used_sessions()
            if self.sessions:
                selected = random.choice(self.sessions)
                print(f"🌐 リセット後に選択されたプロキシ: {selected}")
                return selected
            else:
                print("❌ 利用可能なプロキシがありません")
                return None
            
    def mark_session_as_used(self):
        """現在のセッションを使用済みとしてマーク"""
        if self.proxy_session and self.proxy_session not in self.used_sessions:
            self.used_sessions.append(self.proxy_session)
            self.save_used_sessions()
            print(f"✅ プロキシを使用済みとしてマーク: {self.proxy_session}")
            
    def create_mail_account_kukulu(self):
        """
        kuku.luで捨てメアドを作成
        """
        print("\n📧 捨てメアドアカウント作成中...")
        
        try:
            # メール用ブラウザの設定
            mail_options = Options()
            mail_options.add_argument('--no-sandbox')
            mail_options.add_argument('--disable-dev-shm-usage')
            mail_options.add_argument('--lang=ja')
            mail_options.add_argument('--disable-blink-features=AutomationControlled')
            mail_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            mail_options.add_experimental_option('useAutomationExtension', False)
            
            self.mail_driver = webdriver.Chrome(options=mail_options)
            self.mail_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # kuku.luにアクセス
            print("🔍 kuku.luにアクセス中...")
            self.mail_driver.get("https://m.kuku.lu/")
            time.sleep(3)
            
            # Cloudflareチャレンジの処理
            if self.handle_cloudflare_challenge(self.mail_driver):
                # 既存のメールアドレスを記録
                existing_emails = self.get_existing_emails_kukulu()
                
                # メールアドレス生成ボタンをクリック
                print("📧 メールアドレス生成ボタンを探しています...")
                add_button = WebDriverWait(self.mail_driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "link_addMailAddrByAuto"))
                )
                add_button.click()
                time.sleep(2)
                
                # 利用規約に同意
                try:
                    confirm_button = WebDriverWait(self.mail_driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "area-confirm-dialog-button-ok"))
                    )
                    confirm_button.click()
                    print("✅ 利用規約に同意しました")
                    time.sleep(3)
                except:
                    print("ℹ️ 利用規約ダイアログは表示されませんでした")
                
                # 新しく生成されたメールアドレスを取得
                email = self.extract_new_email_kukulu(existing_emails)
                
                if email:
                    self.email_account = {
                        "email": email,
                        "provider": "kuku.lu",
                        "created_at": datetime.now().isoformat()
                    }
                    print(f"✅ 捨てメアドアカウント作成成功: {email}")
                    return True
                else:
                    # 手動入力オプション
                    print("\n🤔 ブラウザでメールアドレスが表示されているか確認してください")
                    manual_email = input("メールアドレスを入力してください: ").strip()
                    
                    if manual_email and "@" in manual_email:
                        self.email_account = {
                            "email": manual_email,
                            "provider": "kuku.lu",
                            "created_at": datetime.now().isoformat()
                        }
                        print(f"✅ 手動入力されたメール: {manual_email}")
                        return True
                        
        except Exception as e:
            print(f"❌ メールアカウント作成エラー: {e}")
            if self.mail_driver:
                self.mail_driver.save_screenshot("kukulu_error.png")
                
        return False
        
    def handle_cloudflare_challenge(self, driver):
        """Cloudflareチャレンジを処理"""
        time.sleep(3)
        
        page_source = driver.page_source.lower()
        
        if ("challenge-platform" in page_source or 
            "cf-turnstile" in page_source or
            "cloudflare" in driver.title.lower()):
            
            print("🛡️ Cloudflareチャレンジを検出しました")
            print("\n🤖 手動でチャレンジを解決してください:")
            print("1. ブラウザでチャレンジを完了してください")
            print("2. kuku.luのページが表示されたらEnterキーを押してください")
            input("\nEnterキーを押して続行...")
            
            if "kuku.lu" in driver.current_url:
                print("✅ チャレンジが解決されました！")
                return True
                
        return True
        
    def get_existing_emails_kukulu(self):
        """既存のメールアドレスリストを取得"""
        existing_emails = []
        try:
            email_cells = self.mail_driver.find_elements(By.CSS_SELECTOR, "td a[href*='mailto:']")
            for cell in email_cells:
                email = cell.text.strip()
                if "@" in email:
                    existing_emails.append(email)
        except:
            pass
        return existing_emails
        
    def extract_new_email_kukulu(self, existing_emails):
        """新しく生成されたメールアドレスを抽出"""
        print("📧 新しく生成されたメールアドレスを探しています...")
        
        # 黄色い通知エリアから取得
        try:
            yellow_elements = self.mail_driver.execute_script("""
                var elements = document.querySelectorAll('*');
                var yellowElements = [];
                for (var i = 0; i < elements.length; i++) {
                    var bgColor = window.getComputedStyle(elements[i]).backgroundColor;
                    if (bgColor === 'rgb(255, 248, 220)' || bgColor === 'rgb(255, 255, 224)') {
                        yellowElements.push(elements[i]);
                    }
                }
                return yellowElements;
            """)
            
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            
            for elem in yellow_elements:
                text = elem.text
                if text and "@" in text:
                    matches = re.findall(email_pattern, text)
                    for email in matches:
                        if email not in existing_emails:
                            return email
        except:
            pass
            
        return None
        
    def generate_user_info(self):
        """ユーザー情報を生成（日本人向け）"""
        print("\n👤 ユーザー情報生成中...")
        
        # 日本人の名前リスト
        first_names_romaji = ["yuki", "haruto", "yui", "sota", "mei", "riku", "sakura", "kaito", 
                             "hina", "ren", "aoi", "minato", "koharu", "daiki", "miu", "sora"]
        last_names_romaji = ["tanaka", "suzuki", "takahashi", "watanabe", "ito", "yamamoto", 
                            "nakamura", "sato", "kobayashi", "saito", "kato", "yoshida"]
        
        first_names_kanji = ["優希", "陽斗", "結衣", "蒼太", "芽衣", "陸", "さくら", "海斗",
                            "陽菜", "蓮", "葵", "湊", "心春", "大輝", "美羽", "空"]
        last_names_kanji = ["田中", "鈴木", "高橋", "渡辺", "伊藤", "山本", "中村", "佐藤",
                           "小林", "斎藤", "加藤", "吉田"]
        
        # ランダムに選択
        first_name_idx = random.randint(0, len(first_names_romaji) - 1)
        last_name_idx = random.randint(0, len(last_names_romaji) - 1)
        
        # タイムスタンプとランダム文字列でユニークなユーザー名を生成
        timestamp = datetime.now().strftime("%H%M%S")
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        username = f"{first_names_romaji[first_name_idx]}_{timestamp}_{random_str}"
        
        # パスワード生成（強力なもの）
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + "!@#"
        
        # 誕生日（18-35歳）
        age = random.randint(18, 35)
        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        
        self.user_info = {
            "username": username,
            "password": password,
            "full_name": f"{last_names_kanji[last_name_idx]} {first_names_kanji[first_name_idx]}",
            "full_name_romaji": f"{last_names_romaji[last_name_idx]} {first_names_romaji[first_name_idx]}",
            "birth_year": birth_year,
            "birth_month": birth_month,
            "birth_day": birth_day
        }
        
        print(f"✅ ユーザー情報生成完了:")
        print(f"   ユーザー名: {username}")
        print(f"   フルネーム: {self.user_info['full_name']}")
        print(f"   誕生日: {birth_year}年{birth_month}月{birth_day}日")
        
        return True
        
    def start_browser(self):
        """ブラウザ起動（undetected-chromedriver + プロキシ拡張機能）"""
        print("\n🌐 Instagram用ブラウザ起動中...")
        
        try:
            # Chrome オプション
            chrome_options = uc.ChromeOptions()
            chrome_options.add_argument('--lang=ja')
            chrome_options.add_argument(f'user-agent={self.get_random_user_agent()}')
            
            # 検出回避設定
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # プロファイル設定
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--no-service-autorun')
            chrome_options.add_argument('--password-store=basic')
            
            # GPU無効化
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--no-sandbox')
            
            # ウィンドウサイズを設定
            chrome_options.add_argument('--window-size=1366,768')
            
            # プロキシ拡張機能を追加
            if self.use_proxy and self.proxy_session:
                extension_dir = self.create_proxy_extension()
                if extension_dir:
                    chrome_options.add_argument(f'--load-extension={extension_dir}')
            
            # undetected-chromedriverで起動
            self.driver = uc.Chrome(options=chrome_options, version_main=None)
            print("✅ undetected-chromedriver起動成功")
            
            # 追加のJavaScript実行
            self.enhance_stealth_advanced()
            
        except Exception as e:
            print(f"⚠️ undetected-chromedriver失敗: {e}")
            print("通常のChromeDriverを使用します")
            
            # 通常のChromeDriverで再試行
            chrome_options = Options()
            chrome_options.add_argument('--lang=ja')
            chrome_options.add_argument(f'user-agent={self.get_random_user_agent()}')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # プロキシ拡張機能を追加
            if self.use_proxy and self.proxy_session:
                extension_dir = self.create_proxy_extension()
                if extension_dir:
                    chrome_options.add_argument(f'--load-extension={extension_dir}')
                    
            self.driver = webdriver.Chrome(options=chrome_options)
            self.enhance_stealth_advanced()
        
        self.wait = WebDriverWait(self.driver, 20)
        print("✅ ブラウザ起動完了")
            
    def slow_type(self, element, text, delay=0.1):
        """より人間らしい入力速度"""
        element.clear()
        
        # ランダムな待機を追加
        time.sleep(random.uniform(0.5, 1.0))
        
        for char in text:
            element.send_keys(char)
            # よりランダムな入力速度
            time.sleep(delay + random.uniform(0.05, 0.2))
            
            # たまに長い待機を入れる
            if random.random() < 0.1:
                time.sleep(random.uniform(0.5, 1.0))
            
    def create_instagram_account(self):
        """Instagramアカウント作成のメインプロセス"""
        try:
            print("\n📝 Instagramアカウント作成開始...")
            
            # プロキシの動作確認
            if self.use_proxy:
                print("🔍 プロキシ接続を確認中...")
                self.driver.get("https://httpbin.org/ip")
                time.sleep(3)
                ip_info = self.driver.find_element(By.TAG_NAME, "body").text
                print(f"✅ 現在のIP情報: {ip_info}")
                time.sleep(2)
            
            # ランダムな待機時間
            time.sleep(random.uniform(3, 7))
            
            # Instagramにアクセス
            self.driver.get("https://www.instagram.com/")
            time.sleep(random.uniform(5, 10))
            
            # サインアップページへの遷移
            self.driver.get("https://www.instagram.com/accounts/emailsignup/")
            time.sleep(random.uniform(3, 7))
            
            # 基本情報入力
            if self.fill_basic_info():
                # 誕生日入力
                if self.fill_birthday():
                    # 認証コード処理
                    if self.handle_verification():
                        print("\n✅ アカウント作成成功！")
                        self.save_account_info()
                        return True
                        
        except Exception as e:
            print(f"❌ アカウント作成エラー: {e}")
            self.driver.save_screenshot("instagram_error.png")
            
        return False
        
    def fill_basic_info(self):
        """基本情報入力"""
        print("\n[STEP 1] 基本情報入力...")
        
        try:
            # メールアドレス入力
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "emailOrPhone"))
            )
            self.slow_type(email_input, self.email_account["email"])
            print(f"   メール: {self.email_account['email']}")
            
            # フルネーム入力
            fullname_input = self.driver.find_element(By.NAME, "fullName")
            self.slow_type(fullname_input, self.user_info["full_name"])
            print(f"   氏名: {self.user_info['full_name']}")
            
            # ユーザー名入力
            username_input = self.driver.find_element(By.NAME, "username")
            self.slow_type(username_input, self.user_info["username"])
            print(f"   ユーザー名: {self.user_info['username']}")
            
            # パスワード入力
            password_input = self.driver.find_element(By.NAME, "password")
            self.slow_type(password_input, self.user_info["password"])
            print(f"   パスワード: {'*' * len(self.user_info['password'])}")
            
            time.sleep(2)
            
            # CAPTCHAチェック
            self.detect_and_solve_captcha()
            
            # 登録ボタンをクリック
            print("   登録ボタンを探しています...")
            signup_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '登録') or contains(text(), 'Sign up')]")
            
            # ユーザー名の重複チェック
            if self.check_and_fix_username_error():
                # 再度登録ボタンを取得
                signup_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '登録') or contains(text(), 'Sign up')]")
                
            # 複数の方法でクリックを試行
            try:
                signup_button.click()
            except:
                self.driver.execute_script("arguments[0].click();", signup_button)
                
            print("   ✅ 基本情報送信完了")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"   ❌ 基本情報入力エラー: {e}")
            return False
            
    def check_and_fix_username_error(self):
        """ユーザー名エラーをチェックして修正"""
        try:
            # エラーメッセージを探す
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, "span[role='alert'], .coreSpriteInputError")
            
            for elem in error_elements:
                if elem.is_displayed():
                    error_text = elem.text
                    if "ユーザーネーム" in error_text or "username" in error_text.lower():
                        print("   ⚠️ ユーザー名エラーを検出")
                        
                        # おすすめボタンを探す
                        suggestion_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[type='button']")
                        
                        for button in suggestion_buttons:
                            button_text = button.text.strip()
                            if button_text and len(button_text) > 3 and "_" in button_text:
                                print(f"   📝 おすすめユーザー名を選択: {button_text}")
                                button.click()
                                time.sleep(2)
                                self.user_info["username"] = button_text
                                return True
                                
                        # おすすめボタンが見つからない場合は新しいユーザー名を生成
                        new_username = f"{self.user_info['username']}_{random.randint(100, 999)}"
                        username_input = self.driver.find_element(By.NAME, "username")
                        username_input.clear()
                        self.slow_type(username_input, new_username)
                        self.user_info["username"] = new_username
                        print(f"   📝 新しいユーザー名: {new_username}")
                        time.sleep(2)
                        return True
                        
        except:
            pass
            
        return False
        
    def fill_birthday(self):
        """誕生日入力"""
        print("\n[STEP 2] 誕生日入力...")
        
        try:
            # 誕生日入力画面を待つ
            time.sleep(3)
            
            # 月のセレクトボックス
            month_select = Select(self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[title*='月']"))
            ))
            month_select.select_by_value(str(self.user_info["birth_month"]))
            time.sleep(1)
            
            # 日のセレクトボックス
            day_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[title*='日']"))
            day_select.select_by_value(str(self.user_info["birth_day"]))
            time.sleep(1)
            
            # 年のセレクトボックス
            year_select = Select(self.driver.find_element(By.CSS_SELECTOR, "select[title*='年']"))
            year_select.select_by_value(str(self.user_info["birth_year"]))
            time.sleep(1)
            
            print(f"   誕生日: {self.user_info['birth_year']}年{self.user_info['birth_month']}月{self.user_info['birth_day']}日")
            
            # 次へボタンをクリック
            next_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '次へ') or contains(text(), 'Next')]")
            next_button.click()
            
            print("   ✅ 誕生日入力完了")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"   ❌ 誕生日入力エラー: {e}")
            return False
            
    def handle_verification(self):
        """認証コード処理"""
        print("\n[STEP 3] 認証コード処理...")
        
        try:
            # 認証コード入力画面を待つ
            time.sleep(5)
            
            # 電話番号認証が要求された場合
            if self.check_phone_verification_required():
                if not self.handle_phone_verification():
                    return False
            
            # メール認証コードを取得
            print("   📧 認証コードメールを待っています...")
            
            verification_code = self.get_verification_code_from_kukulu()
            
            if verification_code:
                print(f"   🔢 認証コード取得: {verification_code}")
                
                # まず6つの個別入力欄を確認（Instagram特有のパターン）
                try:
                    single_digit_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[maxlength='1']")
                    if len(single_digit_inputs) == 6:
                        print("   📝 6つの個別入力欄を検出")
                        # 既存の入力をクリア
                        for inp in single_digit_inputs:
                            inp.clear()
                        # 1文字ずつ入力
                        for i, digit in enumerate(verification_code):
                            single_digit_inputs[i].send_keys(digit)
                            time.sleep(0.2)
                        print(f"   ✅ 認証コード入力完了: {verification_code}")
                        
                        # 送信ボタンを探す
                        time.sleep(2)
                        try:
                            submit_button = self.driver.find_element(By.XPATH, "//button[@type='button' and not(@disabled)]")
                            submit_button.click()
                            print("   ✅ 送信ボタンをクリック")
                        except:
                            # ボタンが見つからない場合は最後の入力欄でEnter
                            single_digit_inputs[-1].send_keys(Keys.RETURN)
                            print("   ✅ Enterキーで送信")
                        
                        time.sleep(5)
                        
                        # 成功確認
                        if "welcome" in self.driver.current_url.lower() or "accounts/onetap" in self.driver.current_url:
                            print("   ✅ 認証成功！")
                            return True
                        else:
                            print(f"   📍 現在のURL: {self.driver.current_url}")
                            self.driver.save_screenshot("after_6digit_submit.png")
                except Exception as e:
                    print(f"   ⚠️ 6桁入力エラー: {e}")
                
                # 6桁入力欄がない場合は通常の入力欄を探す
                code_input = None
                
                # 方法1: name属性で探す
                try:
                    code_input = self.wait.until(
                        EC.presence_of_element_located((By.NAME, "confirmationCode"))
                    )
                    print("   ✅ 認証コード入力欄を発見（name属性）")
                except:
                    pass
                
                # 方法2: input要素から探す
                if not code_input:
                    try:
                        inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='number']")
                        for inp in inputs:
                            placeholder = inp.get_attribute("placeholder") or ""
                            aria_label = inp.get_attribute("aria-label") or ""
                            
                            if any(keyword in placeholder.lower() + aria_label.lower() 
                                for keyword in ["code", "コード", "認証", "confirm", "確認"]):
                                code_input = inp
                                print("   ✅ 認証コード入力欄を発見（placeholder/aria-label）")
                                break
                    except:
                        pass
                
                # 方法3: 最も可能性の高い入力欄を使用
                if not code_input:
                    try:
                        visible_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input:not([type='hidden'])")
                        
                        for inp in visible_inputs:
                            if inp.is_displayed() and inp.is_enabled():
                                input_type = inp.get_attribute("type") or ""
                                name = inp.get_attribute("name") or ""
                                
                                if input_type not in ["password", "email"] and name not in ["password", "emailOrPhone"]:
                                    code_input = inp
                                    print("   ✅ 認証コード入力欄を推定")
                                    break
                    except:
                        pass
                
                if code_input:
                    # スクリーンショットを保存
                    self.driver.save_screenshot("before_code_input.png")
                    
                    # 入力欄をクリアして入力
                    code_input.clear()
                    self.slow_type(code_input, verification_code)
                    print(f"   ✅ 認証コード入力完了: {verification_code}")
                    
                    time.sleep(2)
                    
                    # 確認ボタンを探してクリック
                    confirm_success = False
                    
                    # 方法1: テキストでボタンを探す
                    try:
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            button_text = button.text.lower()
                            if any(keyword in button_text for keyword in ["確認", "次へ", "confirm", "next", "送信", "submit"]):
                                if button.is_displayed() and button.is_enabled():
                                    button.click()
                                    print(f"   ✅ ボタンクリック: {button.text}")
                                    confirm_success = True
                                    break
                    except:
                        pass
                    
                    # 方法2: Enterキーを送信
                    if not confirm_success:
                        try:
                            code_input.send_keys(Keys.RETURN)
                            print("   ✅ Enterキーで送信")
                            confirm_success = True
                        except:
                            pass
                    
                    # 方法3: フォームをsubmit
                    if not confirm_success:
                        try:
                            form = code_input.find_element(By.XPATH, "./ancestor::form")
                            self.driver.execute_script("arguments[0].submit();", form)
                            print("   ✅ フォームを送信")
                            confirm_success = True
                        except:
                            pass
                    
                    time.sleep(5)
                    
                    # 成功確認
                    if "welcome" in self.driver.current_url.lower() or "accounts/onetap" in self.driver.current_url:
                        print("   ✅ 認証成功！")
                        return True
                    else:
                        print(f"   📍 現在のURL: {self.driver.current_url}")
                        self.driver.save_screenshot("after_code_submit.png")
                        
                else:
                    print("   ❌ 認証コード入力欄が見つかりません")
                    self.driver.save_screenshot("code_input_not_found.png")
                    
                    # 手動入力オプション
                    print("\n   🤖 手動での対応が必要です:")
                    print("   1. ブラウザで認証コード入力欄を確認してください")
                    print(f"   2. 認証コード: {verification_code} を手動で入力してください")
                    print("   3. 確認ボタンをクリックしてください")
                    input("   完了したらEnterキーを押してください...")
                    
                    time.sleep(3)
                    
                    # 手動入力後の確認
                    if "welcome" in self.driver.current_url.lower() or "accounts/onetap" in self.driver.current_url:
                        print("   ✅ 手動認証成功！")
                        return True
            
            else:
                print("   ❌ 認証コードが取得できませんでした")
                
                # 手動入力オプション
                manual_code = input("   手動で認証コードを入力してください: ").strip()
                if manual_code:
                    # 上記と同じ処理を実行
                    pass
                    
        except Exception as e:
            print(f"   ❌ 認証処理エラー: {e}")
            self.driver.save_screenshot("verification_error.png")
            
            # 手動対応オプション
            print("\n   🤖 手動での対応をお試しください:")
            print("   1. ブラウザで認証作業を完了してください")
            input("   2. 完了したらEnterキーを押してください...")
            
            # 手動完了後の確認
            if "welcome" in self.driver.current_url.lower() or "accounts/onetap" in self.driver.current_url:
                return True
        
        return False
        
    def get_verification_code_from_kukulu(self):
        """kuku.luから認証コードを取得"""
        if not self.mail_driver:
            return None
            
        print("   📬 認証コードを確認中...")
        
        start_time = time.time()
        timeout = 300  # 5分
        check_interval = 20  # 20秒ごとに変更
        last_check = 0
        
        while time.time() - start_time < timeout:
            current_time = time.time()
            
            if current_time - last_check < check_interval:
                remaining = check_interval - (current_time - last_check)
                print(f"   ⏳ 次のチェックまで {int(remaining)} 秒待機中...")
                time.sleep(1)
                continue
                
            try:
                print(f"   🔄 メールをチェック中... ({int(current_time - start_time)}秒経過)")
                
                # まず、受信トレイを開く
                print(f"   📥 {self.email_account['email']} の受信トレイを開きます...")
                
                # 方法1: メールアドレスのリンクをクリック
                email_found = False
                try:
                    # メールアドレス一覧から自分のアドレスを探す
                    email_links = self.mail_driver.find_elements(By.CSS_SELECTOR, "a")
                    for link in email_links:
                        link_text = link.text.strip()
                        if link_text == self.email_account['email']:
                            print(f"   📧 メールアドレスリンクをクリック: {link_text}")
                            link.click()
                            time.sleep(3)
                            email_found = True
                            break
                    
                    # テーブル内のメールアドレスも確認
                    if not email_found:
                        table_cells = self.mail_driver.find_elements(By.CSS_SELECTOR, "td")
                        for cell in table_cells:
                            if self.email_account['email'] in cell.text:
                                # クリック可能な要素を探す
                                clickable = cell.find_elements(By.CSS_SELECTOR, "a")
                                if clickable:
                                    clickable[0].click()
                                else:
                                    cell.click()
                                time.sleep(3)
                                email_found = True
                                break
                                
                except Exception as e:
                    print(f"   ⚠️ メールアドレスクリックエラー: {e}")
                
                if not email_found:
                    print(f"   ❌ {self.email_account['email']} が見つかりません")
                    # 手動でナビゲート
                    print("   📍 URLで直接アクセスを試みます...")
                    # URLパターンは #p数字 のような形式
                    # 既存のURLから推測する必要がある
                    
                # 受信トレイが開いたら、メール一覧を確認
                print("   📨 受信メール一覧を確認中...")
                time.sleep(2)
                
                # 受信トレイ内のメールを探す
                # 複数の方法でメール一覧を取得
                mail_found = False
                
                # 方法1: テーブル内の行を確認
                try:
                    rows = self.mail_driver.find_elements(By.CSS_SELECTOR, "table tr, tbody tr")
                    print(f"   📧 受信メール数: {len(rows)}件")
                    
                    for row in rows:
                        try:
                            row_text = row.text
                            
                            # Instagramからのメールを探す
                            if any(keyword in row_text for keyword in ["Instagram", "インスタグラム", "認証", "確認", "verify", "confirm"]):
                                print("   ✅ Instagramからのメールを発見！")
                                
                                # 行をクリックしてメールを開く
                                clickable = row.find_elements(By.CSS_SELECTOR, "td, a")
                                for elem in clickable:
                                    if elem.is_displayed() and elem.is_enabled():
                                        try:
                                            elem.click()
                                            time.sleep(3)
                                            mail_found = True
                                            break
                                        except:
                                            continue
                                
                                if mail_found:
                                    break
                                    
                        except Exception as e:
                            print(f"   ⚠️ 行処理エラー: {e}")
                            continue
                            
                except Exception as e:
                    print(f"   ⚠️ テーブル検索エラー: {e}")
                
                # 方法2: リンクから探す
                if not mail_found:
                    try:
                        links = self.mail_driver.find_elements(By.CSS_SELECTOR, "a")
                        for link in links:
                            link_text = link.text
                            if any(keyword in link_text for keyword in ["Instagram", "認証", "確認"]):
                                print("   ✅ Instagramメールリンクを発見！")
                                link.click()
                                time.sleep(3)
                                mail_found = True
                                break
                    except:
                        pass
                
                # メールが開いたら認証コードを探す
                if mail_found:
                    print("   🔍 メール本文から認証コードを検索中...")
                    
                    # ページ全体のテキストを取得
                    page_text = self.mail_driver.find_element(By.TAG_NAME, "body").text
                    
                    # 認証コードパターンを検索
                    patterns = [
                        r'(\d{6})',  # 6桁の数字
                        r'(\d{5})',  # 5桁の数字  
                        r'(\d{4})',  # 4桁の数字
                        r'認証コード[:：\s]*(\d{4,6})',
                        r'確認コード[:：\s]*(\d{4,6})',
                        r'verification code[:：\s]*(\d{4,6})',
                        r'code[:：\s]*(\d{4,6})',
                        r'は\s*(\d{4,6})\s*です',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, page_text, re.IGNORECASE | re.MULTILINE)
                        if matches:
                            # Instagramの認証コードは通常6桁
                            for code in matches:
                                if len(code) == 6 and code.isdigit():
                                    print(f"   ✅ 認証コード発見: {code}")
                                    return code
                            
                            # 6桁が見つからない場合は4-5桁も許可
                            for code in matches:
                                if len(code) >= 4 and code.isdigit():
                                    print(f"   ✅ 認証コード発見: {code}")
                                    return code
                    
                    # メール本文の一部を表示（デバッグ用）
                    print("   📄 メール本文の一部:")
                    print(page_text[:500] + "...")
                    
                    # メールリストに戻る
                    self.mail_driver.back()
                    time.sleep(2)
                
                else:
                    print(f"   ℹ️ Instagramからのメールがまだ届いていません")
                
                # 受信トレイから戻る（必要な場合）
                if email_found:
                    try:
                        # メールアドレス一覧に戻る
                        back_links = self.mail_driver.find_elements(By.CSS_SELECTOR, "a[href*='#']")
                        for link in back_links:
                            if "戻る" in link.text or "一覧" in link.text:
                                link.click()
                                break
                    except:
                        pass
                
                last_check = current_time
                
            except Exception as e:
                print(f"   ⚠️ メールチェック中にエラー: {e}")
                self.mail_driver.save_screenshot(f"mail_check_error_{int(time.time())}.png")
        
        print("   ❌ タイムアウト: 認証コードが見つかりませんでした")
        
        # 最後に手動入力オプションを提供
        print("\n   🤔 メールブラウザで認証コードが表示されているか確認してください")
        print(f"   1. {self.email_account['email']} をクリック")
        print("   2. 受信トレイでInstagramからのメールを開く")
        print("   3. メール内の6桁の認証コードを確認")
        
        manual_code = input("   認証コードを手動で入力してください: ").strip()
        
        if manual_code and manual_code.isdigit() and len(manual_code) >= 4:
            print(f"   ✅ 手動入力された認証コード: {manual_code}")
            return manual_code
            
        return None
        
    def check_phone_verification_required(self):
        """電話番号認証が必要かチェック"""
        try:
            phone_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='tel'], input[name='phoneNumber']")
            return len(phone_inputs) > 0
        except:
            return False
            
    def handle_phone_verification(self):
        """電話番号認証を処理（SMS-Activate使用）"""
        print("   📱 電話番号認証が必要です...")
        
        try:
            # SMS-Activateから番号を取得
            phone_number = self.get_phone_number()
            if not phone_number:
                return False
                
            # 電話番号入力
            phone_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='tel'], input[name='phoneNumber']")
            phone_input.clear()
            self.slow_type(phone_input, phone_number)
            
            # 送信ボタンをクリック
            send_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '送信') or contains(text(), 'Send')]")
            send_button.click()
            
            time.sleep(5)
            
            # SMSコードを取得
            sms_code = self.get_sms_code()
            if sms_code:
                code_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='confirmationCode']")
                self.slow_type(code_input, sms_code)
                
                confirm_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '確認') or contains(text(), 'Confirm')]")
                confirm_button.click()
                
                return True
                
        except Exception as e:
            print(f"   ❌ 電話番号認証エラー: {e}")
            
        return False
        
    def get_phone_number(self):
        """SMS-Activateから電話番号を取得"""
        # SMS-Activate実装（既存のコードから）
        # ここでは省略
        return None
        
    def get_sms_code(self):
        """SMS-ActivateからSMSコードを取得"""
        # SMS-Activate実装（既存のコードから）
        # ここでは省略
        return None
        
    def detect_and_solve_captcha(self):
        """CAPTCHAを検出して解決"""
        try:
            # reCAPTCHAの検出
            captcha_elements = self.driver.find_elements(By.CSS_SELECTOR, ".g-recaptcha, iframe[src*='recaptcha']")
            
            if captcha_elements:
                print("   🔐 CAPTCHAを検出しました...")
                # 2captcha実装（既存のコードから）
                
        except:
            pass
            
    def save_account_info(self):
        """アカウント情報を保存"""
        print("\n💾 アカウント情報を保存中...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        account_id = f"IG_JP_{timestamp}"
        
        self.created_account = {
            "account_id": account_id,
            "instagram": {
                "username": self.user_info["username"],
                "password": self.user_info["password"],
                "email": self.email_account["email"],
                "fullname": self.user_info["full_name"],
                "birth_year": self.user_info["birth_year"],
                "birth_month": self.user_info["birth_month"],
                "birth_day": self.user_info["birth_day"]
            },
            "email": self.email_account,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "language": "japanese",
            "proxy_used": self.proxy_session if self.use_proxy else None
        }
        
        # ディレクトリ作成
        save_dir = os.path.join("instagram_accounts", account_id)
        os.makedirs(save_dir, exist_ok=True)
        
        # JSON保存
        json_path = os.path.join(save_dir, "account_info.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.created_account, f, ensure_ascii=False, indent=2)
            
        # スクリーンショット保存
        screenshot_path = os.path.join(save_dir, "final_screen.png")
        self.driver.save_screenshot(screenshot_path)
        
        print(f"✅ アカウント情報を保存しました: {json_path}")
        
        # 成功情報を表示
        print("\n" + "="*50)
        print("🎉 Instagramアカウント作成成功！")
        print("="*50)
        print(f"ユーザー名: {self.user_info['username']}")
        print(f"メール: {self.email_account['email']}")
        print(f"パスワード: {self.user_info['password']}")
        print("="*50)
        
# プロキシを使用済みとしてマーク
        if self.use_proxy:
            self.mark_session_as_used()
        
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()
        if self.mail_driver:
            self.mail_driver.quit()

# メイン実行部分
def main():
    print("=== Instagram自動アカウント作成システム（kuku.lu版） ===")
    print("プロキシ拡張機能対応版")
    
    # undetected-chromedriverのインストール確認
    try:
        import undetected_chromedriver as uc
        print("✅ undetected-chromedriver: インストール済み")
    except ImportError:
        print("❌ undetected-chromedriverがインストールされていません")
        print("以下のコマンドでインストールしてください:")
        print("pip install undetected-chromedriver")
        return
    
    # プロキシ使用の選択
    use_proxy_input = input("\nプロキシを使用しますか？ (y/n): ")
    use_proxy = use_proxy_input.lower() == 'y'
    
    if use_proxy:
        print("\n🌐 プロキシ: 有効")
    else:
        print("\n🌐 プロキシ: 無効（直接接続）")
    
    max_attempts = 3
    
    for attempt in range(max_attempts):
        print(f"\n{'='*50}")
        print(f"試行 {attempt + 1}/{max_attempts}")
        print(f"{'='*50}")
        
        creator = InstagramCreatorJapaneseV3(use_proxy=use_proxy)
        
        try:
            # メールアカウント作成
            if creator.create_mail_account_kukulu():
                # ユーザー情報生成
                if creator.generate_user_info():
                    # ブラウザ起動
                    creator.start_browser()
                    
                    # Instagramアカウント作成
                    if creator.create_instagram_account():
                        print("\n✅ アカウント作成完了！")
                        time.sleep(10)
                        break
                    else:
                        print("\n❌ アカウント作成失敗")
            else:
                print("\n❌ メールアカウント作成失敗")
                
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # ブラウザを閉じる
            creator.close()
            
        if attempt < max_attempts - 1:
            # より長い待機時間
            wait_time = random.randint(600, 900)  # 10-15分
            print(f"\n⏳ {wait_time//60}分後に再試行します...")
            time.sleep(wait_time)
            
    print("\n処理完了")

if __name__ == "__main__":
    main()