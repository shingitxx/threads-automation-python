from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random

print("=== IPRoyal 自動認証プロキシテスト ===")

# セッションリスト
sessions = [
    "w0sc3hsf_lifetime-2h",
    "3icgignj_lifetime-9h", 
    "16u7hbrf_lifetime-4h",
    "ohxfhr7l_lifetime-15h",
    "uchw0mfn_lifetime-14h"
]

# ランダム選択
selected_session = random.choice(sessions)

# プロキシ設定
proxy_options = {
    'proxy': {
        'http': f'http://C9kNyNmY:fiWduY3n-country-jp_session-{selected_session}@iproyal-aisa.hellworld.io:12322',
        'https': f'http://C9kNyNmY:fiWduY3n-country-jp_session-{selected_session}@iproyal-aisa.hellworld.io:12322',
        'no_proxy': 'localhost,127.0.0.1'
    }
}

print(f"セッション: {selected_session}")

# Chrome設定
chrome_options = Options()
chrome_options.add_argument("--lang=ja")

# ブラウザ起動（selenium-wire）
driver = webdriver.Chrome(
    options=chrome_options,
    seleniumwire_options=proxy_options
)

try:
    # IPアドレス確認
    print("\nIPアドレス確認中...")
    driver.get("https://api.ipify.org")
    time.sleep(3)
    current_ip = driver.find_element(By.TAG_NAME, "body").text
    print(f"✅ 現在のIP: {current_ip} (日本)")
    
    # Instagram確認
    print("\nInstagramアクセス中...")
    driver.get("https://www.instagram.com/accounts/emailsignup/")
    time.sleep(5)
    
    try:
        driver.find_element(By.NAME, "emailOrPhone")
        print("✅ 成功！プロキシ経由でアクセスできました！")
    except:
        print("❌ アクセスできませんでした")
    
    input("\nEnterキーで終了...")
    
except Exception as e:
    print(f"エラー: {e}")
    
finally:
    driver.quit()