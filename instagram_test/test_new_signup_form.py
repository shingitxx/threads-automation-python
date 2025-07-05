from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

print("=== 新しいサインアップフォーム調査 ===")

# IPRoyalのセッション（使用済みのものを使用）
proxy_host = "iproyal-aisa.hellworld.io"
proxy_port = "12322"
proxy_user = "C9kNyNmY"
proxy_pass = "fiWduY3n-country-jp_session-16u7hbrf_lifetime-4h"

# Chrome設定
options = Options()
options.add_argument("--lang=ja")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')

print(f"\nプロキシ設定: {proxy_host}:{proxy_port}")
print(f"認証情報を手動入力してください")

# ブラウザ起動
driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

try:
    # Google経由で認証
    driver.get("https://www.google.com")
    time.sleep(3)
    
    print(f"\n認証情報:")
    print(f"ユーザー名: {proxy_user}")
    print(f"パスワード: {proxy_pass}")
    input("\n認証完了後、Enterキーを押してください...")
    
    # Instagramサインアップページへ
    print("\nInstagramサインアップページを分析中...")
    driver.get("https://www.instagram.com/accounts/emailsignup/")
    time.sleep(5)
    
    # すべての入力フィールドを探す
    print("\n=== 入力フィールド検索 ===")
    
    # input要素をすべて取得
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"\n見つかった入力フィールド: {len(inputs)}個")
    
    for i, inp in enumerate(inputs):
        try:
            if inp.is_displayed():
                inp_type = inp.get_attribute("type") or "text"
                placeholder = inp.get_attribute("placeholder") or ""
                name = inp.get_attribute("name") or ""
                aria_label = inp.get_attribute("aria-label") or ""
                
                print(f"\nInput #{i+1}:")
                print(f"  Type: {inp_type}")
                print(f"  Placeholder: {placeholder}")
                print(f"  Name: {name}")
                print(f"  Aria-label: {aria_label}")
                
                # 最初の入力欄を特定
                if i == 0:
                    print("  → これがメール/電話番号入力欄の可能性が高い")
        except:
            pass
    
    # select要素（生年月日）を探す
    selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"\n見つかったセレクトボックス: {len(selects)}個")
    
    # ボタンを探す
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"\n見つかったボタン: {len(buttons)}個")
    
    for i, btn in enumerate(buttons):
        try:
            if btn.is_displayed():
                btn_text = btn.text
                btn_type = btn.get_attribute("type") or ""
                print(f"\nButton #{i+1}:")
                print(f"  Text: {btn_text}")
                print(f"  Type: {btn_type}")
        except:
            pass
    
    # テスト入力
    print("\n=== テスト入力を開始 ===")
    if inputs:
        # 最初の入力欄（メール）にテスト入力
        test_email = "test123@example.com"
        inputs[0].clear()
        inputs[0].send_keys(test_email)
        print(f"✅ メール入力: {test_email}")
        time.sleep(2)
    
    # スクリーンショット保存
    driver.save_screenshot('instagram_data/temp/new_signup_form.png')
    print("\n📸 スクリーンショット保存: new_signup_form.png")
    
    input("\n調査完了。Enterキーで終了...")
    
except Exception as e:
    print(f"\nエラー: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()