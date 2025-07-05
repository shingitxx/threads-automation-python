from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

print("=== IPRoyal プロキシテスト (ステルスモード) ===")

# IPRoyalのセッション
sessions = [
    "w0sc3hsf_lifetime-2h",
    "3icgignj_lifetime-9h", 
    "16u7hbrf_lifetime-4h",
    "ohxfhr7l_lifetime-15h",
    "uchw0mfn_lifetime-14h"
]

selected_session = random.choice(sessions)
print(f"選択されたセッション: {selected_session}")

# プロキシ情報
proxy_host = "iproyal-aisa.hellworld.io"
proxy_port = "12322"
proxy_user = "C9kNyNmY"
proxy_pass = f"fiWduY3n-country-jp_session-{selected_session}"

# Chrome オプション（検出回避設定）
options = Options()
options.add_argument("--lang=ja")

# 検出回避の設定
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# User-Agentを設定
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# プロキシ設定
proxy_url = f"{proxy_host}:{proxy_port}"
options.add_argument(f'--proxy-server=http://{proxy_url}')

print(f"\nプロキシ設定:")
print(f"  Host: {proxy_host}")
print(f"  Port: {proxy_port}")
print(f"  認証情報は手動で入力が必要です")

# ブラウザ起動
print("\nブラウザ起動中...")
driver = webdriver.Chrome(options=options)

# JavaScriptで追加の検出回避
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd('Network.setUserAgentOverride', {
    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

wait = WebDriverWait(driver, 20)

try:
    print("\n⚠️ プロキシ認証ダイアログが表示されたら:")
    print(f"  ユーザー名: {proxy_user}")
    print(f"  パスワード: {proxy_pass}")
    print("\n手動で入力してください。")
    
    # まず簡単なページへ
    driver.get("https://www.google.com")
    time.sleep(3)
    
    input("\n認証を完了したらEnterキーを押してください...")
    
    # IPアドレス確認
    print("\nIPアドレス確認中...")
    driver.get("https://api.ipify.org")
    time.sleep(3)
    
    try:
        current_ip = driver.find_element(By.TAG_NAME, "body").text
        print(f"✅ 現在のIP: {current_ip}")
        
        # Instagram確認
        print("\nInstagramサインアップページにアクセス中...")
        driver.get("https://www.instagram.com/accounts/emailsignup/")
        time.sleep(5)
        
        # 検出チェック
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        if "自動テストソフトウェア" in page_text:
            print("⚠️ まだ検出されています")
        else:
            try:
                email_input = driver.find_element(By.NAME, "emailOrPhone")
                print("\n✅ 成功！サインアップページにアクセスできました！")
                
                # スクリーンショット
                driver.save_screenshot('instagram_data/temp/proxy_stealth_success.png')
                print("📸 スクリーンショット保存: proxy_stealth_success.png")
                
            except:
                print("\n❌ フォームが見つかりません")
                print(f"ページ内容: {page_text[:200]}")
        
    except Exception as e:
        print(f"\nエラー: {e}")
    
    input("\nテスト完了。Enterキーで終了...")
    
except Exception as e:
    print(f"\n❌ エラー: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()