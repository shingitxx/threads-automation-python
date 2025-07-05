from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def test_instagram_access():
    """Instagramサインアップページへのアクセステスト"""
    
    print("=== Instagram アクセステスト ===")
    
    # Chrome オプション設定
    options = Options()
    options.add_argument("--lang=ja")
    
    # ブラウザ起動
    print("ブラウザを起動中...")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Instagramサインアップページにアクセス
        print("Instagramサインアップページにアクセス中...")
        driver.get("https://www.instagram.com/accounts/emailsignup/")
        
        # ページ読み込み待機
        time.sleep(3)
        
        # ページタイトル確認
        print(f"ページタイトル: {driver.title}")
        
        # 10秒間表示（手動確認用）
        print("\n10秒間ページを表示します。フォームを確認してください...")
        time.sleep(10)
        
        print("✅ テスト成功！")
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
    
    finally:
        driver.quit()
        print("ブラウザを終了しました。")

if __name__ == "__main__":
    test_instagram_access()