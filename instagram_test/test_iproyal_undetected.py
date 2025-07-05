import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

print("=== IPRoyal プロキシテスト (検出回避版) ===")

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

# undetected-chromedriverのオプション
options = uc.ChromeOptions()
options.add_argument("--lang=ja")

# プロキシ設定（認証なし）
proxy_url = f"{proxy_host}:{proxy_port}"
options.add_argument(f'--proxy-server=http://{proxy_url}')

print(f"\nプロキシ設定:")
print(f"  Host: {proxy_host}")
print(f"  Port: {proxy_port}")
print(f"  認証情報は手動で入力が必要です")

# ブラウザ起動
print("\nブラウザ起動中...")
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 20)

try:
    # まずdata:ページを開く（認証ダイアログ対策）
    driver.get("data:,")
    time.sleep(2)
    
    print("\n⚠️ プロキシ認証ダイアログが表示されたら:")
    print(f"  ユーザー名: {proxy_user}")
    print(f"  パスワード: {proxy_pass}")
    print("\n手動で入力してください。")
    
    # テストページへ
    print("\nIPアドレス確認ページへアクセス中...")
    driver.get("https://api.ipify.org")
    
    # 認証待機
    time.sleep(5)
    
    try:
        current_ip = driver.find_element(By.TAG_NAME, "body").text
        print(f"\n✅ 現在のIP: {current_ip}")
        
        # Instagram確認
        print("\nInstagramサインアップページにアクセス中...")
        driver.get("https://www.instagram.com/accounts/emailsignup/")
        time.sleep(5)
        
        try:
            email_input = wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone")))
            print("\n✅ 成功！サインアップページにアクセスできました！")
            print("プロキシ経由でのアクセスに成功しました。")
            
            # スクリーンショット
            driver.save_screenshot('instagram_data/temp/proxy_undetected_success.png')
            print("📸 スクリーンショット保存: proxy_undetected_success.png")
            
        except:
            page_text = driver.find_element(By.TAG_NAME, "body").text[:500]
            print("\n❌ サインアップページが表示されていません")
            print(f"ページ内容: {page_text}")
            
    except Exception as e:
        print(f"\n認証が完了していない可能性があります: {e}")
        print("認証ダイアログに入力してから、もう一度お試しください")
    
    input("\nテスト完了。Enterキーで終了...")
    
except Exception as e:
    print(f"\n❌ エラー: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()