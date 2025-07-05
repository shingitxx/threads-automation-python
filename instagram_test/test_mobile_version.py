from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

print("=== Instagram モバイル版アクセステスト ===")

# Chrome設定（モバイルエミュレーション）
options = Options()
options.add_argument("--lang=ja")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# モバイルデバイスとしてエミュレート
mobile_emulation = {"deviceName": "iPhone 12 Pro"}
options.add_experimental_option("mobileEmulation", mobile_emulation)

# User-Agentを設定
options.add_argument('user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1')

print("モバイル版としてアクセスします...")

driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

try:
    # Instagramモバイル版にアクセス
    driver.get("https://www.instagram.com/accounts/emailsignup/")
    time.sleep(5)
    
    # 要素確認
    print("\n要素を確認中...")
    
    # 通常のセレクタで要素を探す
    try:
        email_input = driver.find_element(By.NAME, "emailOrPhone")
        print("✅ 旧フォーム検出！emailOrPhone要素が見つかりました")
        
        # その他の要素も確認
        fullname = driver.find_element(By.NAME, "fullName")
        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        
        print("✅ すべての必要な要素が見つかりました")
        print("旧画面でのアクセスに成功しました！")
        
    except:
        print("❌ 旧フォームの要素が見つかりません")
        print("新しいフォーマットが表示されているようです")
    
    # スクリーンショット
    driver.save_screenshot('instagram_data/temp/mobile_version.png')
    print("\n📸 スクリーンショット保存: mobile_version.png")
    
    input("\nEnterキーで終了...")
    
except Exception as e:
    print(f"エラー: {e}")
    
finally:
    driver.quit()