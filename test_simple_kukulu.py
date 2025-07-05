# test_simple_kukulu_fixed.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

class KukuluMailGenerator:
    def __init__(self):
        self.driver = None
        self.email = None
        self.generated_email_count = 0
        
    def setup_driver(self):
        """ブラウザの設定"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--lang=ja')
        
        # 検出回避設定
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def handle_cloudflare_challenge(self):
        """Cloudflareチャレンジを処理"""
        time.sleep(3)
        
        current_url = self.driver.current_url
        page_source = self.driver.page_source.lower()
        
        # Cloudflareチャレンジの検出
        if ("challenge-platform" in page_source or 
            "cf-turnstile" in page_source or
            "cloudflare" in self.driver.title.lower()):
            
            print("🛡️ Cloudflareチャレンジを検出しました")
            print("\n🤖 手動でチャレンジを解決してください:")
            print("1. ブラウザでチャレンジを完了してください")
            print("2. kuku.luのページが表示されたらEnterキーを押してください")
            input("\nEnterキーを押して続行...")
            
            if "kuku.lu" in self.driver.current_url:
                print("✅ チャレンジが解決されました！")
                return True
                
        return True
        
    def get_existing_emails(self):
        """既存のメールアドレスリストを取得"""
        existing_emails = []
        try:
            # テーブル内のメールアドレスを収集
            email_cells = self.driver.find_elements(By.CSS_SELECTOR, "td a[href*='mailto:']")
            for cell in email_cells:
                email = cell.text.strip()
                if "@" in email:
                    existing_emails.append(email)
                    
            # リストアイテムからも収集
            list_items = self.driver.find_elements(By.CSS_SELECTOR, "li a")
            for item in list_items:
                text = item.text.strip()
                if "@" in text and text not in existing_emails:
                    existing_emails.append(text)
                    
            print(f"📋 既存のメールアドレス: {existing_emails}")
            
        except Exception as e:
            print(f"⚠️ 既存メール取得エラー: {e}")
            
        return existing_emails
        
    def generate_email(self):
        """メールアドレスを生成"""
        print("=== kuku.lu メール生成 ===")
        
        self.setup_driver()
        
        try:
            # kuku.luにアクセス
            print("🔍 kuku.luにアクセス中...")
            self.driver.get("https://m.kuku.lu/")
            time.sleep(3)
            
            # Cloudflareチャレンジを処理
            if not self.handle_cloudflare_challenge():
                return None
            
            # 生成前の既存メールアドレスを記録
            existing_emails_before = self.get_existing_emails()
            
            # メールアドレス生成
            print("\n📧 メールアドレス生成ボタンを探しています...")
            
            # ボタンをクリック
            try:
                add_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "link_addMailAddrByAuto"))
                )
                print("✅ ボタン発見！クリックします...")
                
                # クリック前のスクリーンショット
                self.driver.save_screenshot("before_click.png")
                
                add_button.click()
                time.sleep(2)
                
                self.generated_email_count += 1
                
            except Exception as e:
                print(f"⚠️ ボタンクリックエラー: {e}")
                
            # 利用規約に同意
            try:
                confirm_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "area-confirm-dialog-button-ok"))
                )
                confirm_button.click()
                print("✅ 利用規約に同意しました")
                time.sleep(3)
            except:
                print("ℹ️ 利用規約ダイアログは表示されませんでした")
            
            # 新しく生成されたメールアドレスを取得
            self.email = self.extract_new_email_address(existing_emails_before)
            
            if self.email:
                print(f"\n✅ メールアドレス取得成功: {self.email}")
                return self.email
            else:
                print("❌ メールアドレスが自動取得できませんでした")
                
                # 手動入力オプション
                print("\n🤔 ブラウザでメールアドレスが表示されているか確認してください")
                print("黄色い背景に表示されている最新のメールアドレスを入力してください")
                manual_email = input("メールアドレス: ").strip()
                
                if manual_email and "@" in manual_email:
                    self.email = manual_email
                    print(f"✅ 手動入力されたメール: {self.email}")
                    return self.email
                    
                return None
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            self.driver.save_screenshot("kukulu_error.png")
            return None
            
    def extract_new_email_address(self, existing_emails_before):
        """新しく生成されたメールアドレスを抽出"""
        print("\n📧 新しく生成されたメールアドレスを探しています...")
        
        # 生成後のスクリーンショット
        self.driver.save_screenshot("after_generation.png")
        
        # 黄色い通知エリアから最新のメールアドレスを取得
        try:
            # 方法1: 通知エリア（黄色い背景）から取得
            print("🔍 通知エリアから検索...")
            
            # JavaScriptで黄色い背景の要素を探す
            yellow_elements = self.driver.execute_script("""
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
            
            # 最新のメールアドレスパターン
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            
            for elem in yellow_elements:
                text = elem.text
                if text and "@" in text:
                    # すべてのメールアドレスを抽出
                    matches = re.findall(email_pattern, text)
                    
                    # 新しいメールアドレスを探す
                    for email in matches:
                        if email not in existing_emails_before:
                            print(f"✅ 新しいメールアドレス発見: {email}")
                            return email
                            
        except Exception as e:
            print(f"⚠️ 通知エリア検索エラー: {e}")
        
        # 方法2: ページ内の最新メールアドレスを取得
        try:
            print("🔍 ページ全体から最新のメールアドレスを検索...")
            
            # 現在のすべてのメールアドレスを取得
            current_emails = []
            
            # リンクから
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='mailto:']")
            for link in links:
                email = link.text.strip()
                if "@" in email and email not in current_emails:
                    current_emails.append(email)
            
            # 新しく追加されたメールアドレスを特定
            for email in current_emails:
                if email not in existing_emails_before:
                    print(f"✅ 新規追加メールアドレス: {email}")
                    return email
                    
        except Exception as e:
            print(f"⚠️ ページ検索エラー: {e}")
        
        # 方法3: 最上部のメールアドレスを取得（通常は最新）
        try:
            print("🔍 最上部のメールアドレスを確認...")
            
            # テーブルの最初の行を確認
            first_email_cell = self.driver.find_element(By.CSS_SELECTOR, "table tr:first-child td a[href*='mailto:']")
            if first_email_cell:
                email = first_email_cell.text.strip()
                if email and email not in existing_emails_before:
                    print(f"✅ 最上部の新規メール: {email}")
                    return email
                    
        except:
            pass
        
        return None
        
    def check_for_verification_code_safe(self, timeout=300):
        """認証コードを安全にチェック（Cloudflareを回避）"""
        if not self.driver or not self.email:
            return None
            
        print(f"\n📬 {self.email} の認証コードを待機中...")
        print("⚠️ 注意: ページをリフレッシュするとCloudflareチャレンジが発生する可能性があります")
        
        start_time = time.time()
        last_check_time = 0
        check_interval = 30  # 30秒ごとにチェック
        
        while time.time() - start_time < timeout:
            current_time = time.time()
            
            # インターバルチェック
            if current_time - last_check_time < check_interval:
                remaining = check_interval - (current_time - last_check_time)
                print(f"⏳ 次のチェックまで {int(remaining)} 秒待機中...")
                time.sleep(1)
                continue
                
            try:
                print(f"\n🔄 メールをチェック中... ({int(current_time - start_time)}秒経過)")
                
                # 現在のURLを保存
                current_url = self.driver.current_url
                
                # メールリストページに戻る（リフレッシュではなくナビゲーション）
                if "#" in current_url:
                    # アンカーを削除してメインページに戻る
                    base_url = current_url.split("#")[0]
                    self.driver.get(base_url)
                    time.sleep(3)
                
                # Cloudflareチャレンジが出た場合の処理
                if "cloudflare" in self.driver.title.lower():
                    print("⚠️ Cloudflareチャレンジが再発生しました")
                    if not self.handle_cloudflare_challenge():
                        print("❌ チャレンジ解決に失敗しました")
                        break
                
                # メール一覧を確認
                mail_found = False
                mail_items = self.driver.find_elements(By.CSS_SELECTOR, f"a[href*='mailto:{self.email}']")
                
                if mail_items:
                    # 該当メールの行を探す
                    for item in mail_items:
                        try:
                            # 親要素（tr）を取得
                            row = item.find_element(By.XPATH, "./ancestor::tr")
                            
                            # 件名を確認
                            subject_cells = row.find_elements(By.TAG_NAME, "td")
                            for cell in subject_cells:
                                if "Instagram" in cell.text or "確認" in cell.text or "認証" in cell.text:
                                    print(f"📧 Instagramからのメールを検出！")
                                    
                                    # メールをクリック
                                    row.click()
                                    time.sleep(3)
                                    
                                    # メール本文から認証コードを探す
                                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                                    
                                    # 認証コードパターン
                                    patterns = [
                                        r'\b(\d{6})\b',
                                        r'認証コード[:：]\s*(\d{4,6})',
                                        r'verification code[:：]\s*(\d{4,6})',
                                    ]
                                    
                                    for pattern in patterns:
                                        match = re.search(pattern, body_text, re.IGNORECASE)
                                        if match:
                                            code = match.group(1)
                                            print(f"\n✅ 認証コード発見: {code}")
                                            return code
                                    
                                    mail_found = True
                                    break
                                    
                        except:
                            continue
                
                if not mail_found:
                    print(f"ℹ️ {self.email} 宛のInstagramメールはまだ届いていません")
                
                last_check_time = current_time
                
            except Exception as e:
                print(f"⚠️ メールチェック中にエラー: {e}")
                
        print("\n❌ タイムアウト: 認証コードが見つかりませんでした")
        return None
        
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()

def main():
    generator = KukuluMailGenerator()
    
    try:
        # メールアドレス生成
        email = generator.generate_email()
        
        if email:
            print(f"\n✅ メールアドレス生成成功！")
            print(f"📧 メールアドレス: {email}")
            
            # 認証コードを待つか確認
            print("\n⚠️ 認証コード確認時の注意:")
            print("- ページリフレッシュによりCloudflareチャレンジが発生する可能性があります")
            print("- 30秒ごとに自動チェックします")
            
            choice = input("\n認証コードを待ちますか？ (y/n): ")
            if choice.lower() == 'y':
                code = generator.check_for_verification_code_safe()
                if code:
                    print(f"\n✅ 認証コード: {code}")
                    
                    # コードをクリップボードにコピー（オプション）
                    try:
                        import pyperclip
                        pyperclip.copy(code)
                        print("📋 認証コードをクリップボードにコピーしました")
                    except:
                        pass
                    
        else:
            print("\n❌ メールアドレス生成失敗")
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        
    finally:
        input("\n何かキーを押すとブラウザを閉じます...")
        generator.close()

if __name__ == "__main__":
    main()