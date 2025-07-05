from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

class InstagramUITester:
    def __init__(self):
        # Chromeオプション設定
        self.options = Options()
        self.options.add_argument("--lang=ja")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        
        # ステルス設定の追加
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = None
        
    def start_browser(self):
        """ブラウザを起動"""
        print("ブラウザを起動中...")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def check_signup_page(self):
        """サインアップページの要素を確認"""
        print("\n=== Instagram サインアップページ要素確認 ===")
        
        try:
            # サインアップページにアクセス
            print("1. サインアップページにアクセス中...")
            self.driver.get("https://www.instagram.com/accounts/emailsignup/")
            
            # ページ読み込み待機
            time.sleep(3)
            
            # 要素を探す
            print("\n2. 入力フィールドを検索中...")
            
            elements_found = {}
            
            # よく使われるセレクタパターン
            selectors = {
                "email": [
                    "input[name='emailOrPhone']",
                    "input[aria-label*='メール']",
                    "input[aria-label*='email']",
                    "input[type='email']",
                    "input[placeholder*='メール']"
                ],
                "fullname": [
                    "input[name='fullName']",
                    "input[aria-label*='氏名']",
                    "input[aria-label*='name']",
                    "input[placeholder*='氏名']"
                ],
                "username": [
                    "input[name='username']",
                    "input[aria-label*='ユーザーネーム']",
                    "input[aria-label*='username']",
                    "input[placeholder*='ユーザーネーム']"
                ],
                "password": [
                    "input[name='password']",
                    "input[type='password']",
                    "input[aria-label*='パスワード']",
                    "input[placeholder*='パスワード']"
                ],
                "submit_button": [
                    "button[type='submit']",
                    "button:contains('登録')",
                    "button:contains('Sign up')",
                    "button:contains('次へ')"
                ]
            }
            
            # 各要素を検索
            for element_name, selector_list in selectors.items():
                print(f"\n   {element_name} を検索中...")
                for selector in selector_list:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if element:
                            elements_found[element_name] = {
                                "selector": selector,
                                "found": True,
                                "visible": element.is_displayed(),
                                "enabled": element.is_enabled()
                            }
                            print(f"   ✅ 見つかりました: {selector}")
                            break
                    except:
                        continue
                
                if element_name not in elements_found:
                    print(f"   ❌ 見つかりませんでした")
            
            # すべての入力フィールドを探す
            print("\n3. すべての入力フィールドを列挙...")
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"   入力フィールド総数: {len(all_inputs)}")
            
            for i, input_elem in enumerate(all_inputs):
                try:
                    name = input_elem.get_attribute("name") or "なし"
                    type_ = input_elem.get_attribute("type") or "text"
                    placeholder = input_elem.get_attribute("placeholder") or "なし"
                    aria_label = input_elem.get_attribute("aria-label") or "なし"
                    
                    print(f"\n   Input #{i+1}:")
                    print(f"     - name: {name}")
                    print(f"     - type: {type_}")
                    print(f"     - placeholder: {placeholder}")
                    print(f"     - aria-label: {aria_label}")
                except:
                    pass
            
            # ボタンを探す
            print("\n4. ボタンを検索中...")
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"   ボタン総数: {len(buttons)}")
            
            for i, button in enumerate(buttons):
                try:
                    text = button.text
                    if text:
                        print(f"   Button #{i+1}: {text}")
                except:
                    pass
            
            # 結果を保存
            with open('instagram_data/temp/instagram_elements.json', 'w', encoding='utf-8') as f:
                json.dump(elements_found, f, ensure_ascii=False, indent=2)
            
            print("\n✅ 要素情報を保存しました: instagram_data/temp/instagram_elements.json")
            
            # スクリーンショットを保存
            self.driver.save_screenshot('instagram_data/temp/signup_page.png')
            print("✅ スクリーンショットを保存しました: instagram_data/temp/signup_page.png")
            
            # 手動確認のため少し待機
            print("\n⏸️  10秒間ページを表示します...")
            time.sleep(10)
            
        except Exception as e:
            print(f"\n❌ エラー発生: {e}")
            import traceback
            traceback.print_exc()
            
    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()
            print("\nブラウザを終了しました。")

if __name__ == "__main__":
    tester = InstagramUITester()
    try:
        tester.start_browser()
        tester.check_signup_page()
    finally:
        tester.close()