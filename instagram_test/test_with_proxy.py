from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 既存のプロキシマネージャーをインポート
try:
    from proxy.proxy_manager import ProxyManager
    proxy_available = True
except:
    print("⚠️ プロキシマネージャーが見つかりません")
    proxy_available = False

print("=== Instagram プロキシ経由アクセステスト ===")

# Chrome設定
options = Options()
options.add_argument("--lang=ja")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# プロキシ設定
if proxy_available:
    try:
        # ProxyManagerを使用
        proxy_manager = ProxyManager()
        proxy_config = proxy_manager.get_proxy_for_account("INSTAGRAM_TEST")
        
        if proxy_config:
            proxy_string = f"{proxy_config['host']}:{proxy_config['port']}"
            
            # 認証が必要な場合
            if proxy_config.get('username'):
                # Seleniumでの認証付きプロキシは拡張機能が必要
                print(f"✅ プロキシ設定: {proxy_config['host']}:{proxy_config['port']}")
                options.add_argument(f'--proxy-server={proxy_string}')
            else:
                options.add_argument(f'--proxy-server={proxy_string}')
        else:
            print("⚠️ プロキシ設定が取得できませんでした")
    except Exception as e:
        print(f"❌ プロキシ設定エラー: {e}")

# ブラウザ起動
print("\nブラウザ起動中...")
driver = webdriver.Chrome(options=options)

try:
    # IPアドレス確認
    print("\n現在のIPアドレスを確認中...")
    driver.get("https://api.ipify.org?format=text")
    time.sleep(2)
    current_ip = driver.find_element(By.TAG_NAME, "body").text
    print(f"現在のIP: {current_ip}")
    
    # Instagramアクセステスト
    print("\nInstagramサインアップページにアクセス中...")
    driver.get("https://www.instagram.com/accounts/emailsignup/")
    time.sleep(5)
    
    # エラーメッセージの確認
    page_text = driver.find_element(By.TAG_NAME, "body").text
    
    if "公開プロキシ" in page_text or "flagged" in page_text.lower():
        print("\n❌ IPアドレスがブロックされています")
        print("プロキシを変更する必要があります")
    else:
        print("\n✅ 正常にアクセスできました")
        
        # フォームの存在確認
        try:
            email_input = driver.find_element(By.NAME, "emailOrPhone")
            print("✅ サインアップフォームが表示されています")
        except:
            print("⚠️ サインアップフォームが見つかりません")
    
    # スクリーンショット
    driver.save_screenshot('instagram_data/temp/proxy_test.png')
    print("\n📸 スクリーンショット保存: proxy_test.png")
    
    input("\nエンターキーでブラウザを閉じます...")
    
except Exception as e:
    print(f"\n❌ エラー: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()