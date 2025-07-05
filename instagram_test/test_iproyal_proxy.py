from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import os

print("=== IPRoyal プロキシテスト ===")

# IPRoyalのセッションリスト
sessions = [
    "w0sc3hsf_lifetime-2h",
    "3icgignj_lifetime-9h", 
    "16u7hbrf_lifetime-4h",
    "ohxfhr7l_lifetime-15h",
    "uchw0mfn_lifetime-14h"
]

# ランダムにセッションを選択
selected_session = random.choice(sessions)
print(f"選択されたセッション: {selected_session}")

# プロキシ情報
proxy_host = "iproyal-aisa.hellworld.io"
proxy_port = "12322"
proxy_user = "C9kNyNmY"
proxy_pass = f"fiWduY3n-country-jp_session-{selected_session}"

# 認証なしプロキシとして設定（Seleniumの制限）
proxy_url = f"{proxy_host}:{proxy_port}"

# Chrome設定
options = Options()
options.add_argument("--lang=ja")
options.add_argument(f'--proxy-server=http://{proxy_url}')

# 認証情報を環境変数に設定（ProxyManagerが使用）
os.environ['PROXY_USERNAME_IPROYAL'] = proxy_user
os.environ['PROXY_PASSWORD_IPROYAL'] = proxy_pass

print(f"\nプロキシ設定:")
print(f"  Host: {proxy_host}")
print(f"  Port: {proxy_port}")
print(f"  User: {proxy_user}")
print(f"  Pass: {proxy_pass[:20]}...")

# ブラウザ起動
print("\nブラウザ起動中...")
driver = webdriver.Chrome(options=options)

try:
    # 認証ポップアップが出る場合の処理
    print("\n⚠️ 認証ポップアップが表示された場合:")
    print(f"  ユーザー名: {proxy_user}")
    print(f"  パスワード: {proxy_pass}")
    print("\n手動で入力してください。")
    
    input("認証を完了したらEnterキーを押してください...")
    
    # IPアドレス確認
    print("\nIPアドレス確認中...")
    driver.get("https://api.ipify.org")
    time.sleep(3)
    current_ip = driver.find_element(By.TAG_NAME, "body").text
    print(f"✅ 現在のIP: {current_ip}")
    
    # 日本のIPか確認
    driver.get("https://ipinfo.io/json")
    time.sleep(3)
    ip_info = driver.find_element(By.TAG_NAME, "body").text
    print(f"IP情報: {ip_info[:100]}...")
    
    # Instagramアクセステスト
    print("\nInstagramサインアップページにアクセス中...")
    driver.get("https://www.instagram.com/accounts/emailsignup/")
    time.sleep(5)
    
    # ページ確認
    try:
        email_input = driver.find_element(By.NAME, "emailOrPhone")
        print("\n✅ サインアップページに正常にアクセスできました！")
        print("プロキシ経由でのアクセスに成功しました。")
        
        # スクリーンショット
        driver.save_screenshot('instagram_data/temp/proxy_success.png')
        print("📸 スクリーンショット保存: proxy_success.png")
        
    except:
        page_text = driver.find_element(By.TAG_NAME, "body").text[:500]
        print("\n❌ サインアップページが表示されていません")
        print(f"ページ内容: {page_text}")
        
        if "公開プロキシ" in page_text or "flagged" in page_text.lower():
            print("\n⚠️ このプロキシはブロックされている可能性があります")
            print("別のセッションを試してください")
    
    input("\nテスト完了。Enterキーで終了...")
    
except Exception as e:
    print(f"\n❌ エラー: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()