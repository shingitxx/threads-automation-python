from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random

print("=== Instagram 旧フォーム表示テスト ===")

# User-Agentのリスト（古いバージョンを使用）
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

selected_ua = random.choice(user_agents)
print(f"使用するUser-Agent: {selected_ua[:50]}...")

# Chrome設定
options = Options()

# 言語設定（英語版を試す）
options.add_argument("--lang=en-US")
options.add_argument("--accept-lang=en-US,en;q=0.9")

# 検出回避
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# User-Agent設定
options.add_argument(f'user-agent={selected_ua}')

# その他のオプション
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

print("\nブラウザ起動中...")
driver = webdriver.Chrome(options=options)

# JavaScript実行で追加の設定
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

try:
    # 最初にaboutページにアクセス
    driver.get("about:blank")
    time.sleep(1)
    
    # Instagramサインアップページへ（emailsignupを明示）
    print("\nInstagramサインアップページにアクセス中...")
    driver.get("https://www.instagram.com/accounts/emailsignup/")
    time.sleep(5)
    
    # 要素確認
    print("\n要素を確認中...")
    
    # 旧フォームの要素を探す
    try:
        email_input = driver.find_element(By.NAME, "emailOrPhone")
        fullname_input = driver.find_element(By.NAME, "fullName")
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        
        print("\n✅ 旧フォーム検出成功！")
        print("以下の要素が見つかりました:")
        print("- emailOrPhone (メールアドレス)")
        print("- fullName (フルネーム)")
        print("- username (ユーザー名)")
        print("- password (パスワード)")
        
        # スクリーンショット
        driver.save_screenshot('instagram_data/temp/old_form_success.png')
        print("\n📸 スクリーンショット保存: old_form_success.png")
        
    except:
        print("\n❌ 旧フォームが見つかりません")
        
        # ページ内容確認
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\n入力フィールド数: {len(inputs)}")
        
        # 新フォームかチェック
        page_text = driver.find_element(By.TAG_NAME, "body").text
        if "携帯電話番号" in page_text:
            print("⚠️ 新フォーム（日本語版）が表示されています")
        elif "phone number" in page_text.lower():
            print("⚠️ 新フォーム（英語版）が表示されています")
        else:
            print("⚠️ 不明なフォーマットです")
    
    input("\nEnterキーで終了...")
    
except Exception as e:
    print(f"\nエラー: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()