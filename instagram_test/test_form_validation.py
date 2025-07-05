from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

print("=== フォームバリデーション確認テスト ===")

# 既存のアカウント情報を使用
with open('instagram_data/temp/test_account.json', 'r', encoding='utf-8') as f:
    mail_account = json.load(f)

# テスト用のユーザー情報
test_info = {
    "email": mail_account['email'],
    "password": "TestPass123!@#",  # 強力なパスワード
    "fullname": "テスト ユーザー",
    "username": f"test_unique_{int(time.time())}"  # 一意のユーザー名
}

# Chrome設定
options = Options()
options.add_argument("--lang=ja")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

try:
    # サインアップページ
    driver.get("https://www.instagram.com/accounts/emailsignup/")
    time.sleep(5)
    
    # 入力欄を取得
    inputs = driver.find_elements(By.TAG_NAME, "input")
    
    print("\n入力開始...")
    
    # 1つずつ入力して確認
    if len(inputs) >= 4:
        # メール
        print(f"1. メール入力: {test_info['email']}")
        inputs[0].clear()
        inputs[0].send_keys(test_info['email'])
        time.sleep(2)
        
        # エラーメッセージ確認
        error_msgs = driver.find_elements(By.CSS_SELECTOR, "span[role='alert'], div[role='alert'], .error")
        if error_msgs:
            for msg in error_msgs:
                if msg.text:
                    print(f"   ⚠️ エラー: {msg.text}")
        
        # パスワード
        print(f"2. パスワード入力: {'*' * len(test_info['password'])}")
        inputs[1].clear()
        inputs[1].send_keys(test_info['password'])
        time.sleep(2)
        
        # エラー確認
        error_msgs = driver.find_elements(By.CSS_SELECTOR, "span[role='alert'], div[role='alert'], .error")
        for msg in error_msgs:
            if msg.text and msg.is_displayed():
                print(f"   ⚠️ エラー: {msg.text}")
        
        # フルネーム
        print(f"3. 氏名入力: {test_info['fullname']}")
        inputs[2].clear()
        inputs[2].send_keys(test_info['fullname'])
        time.sleep(2)
        
        # ユーザー名
        print(f"4. ユーザー名入力: {test_info['username']}")
        inputs[3].clear()
        inputs[3].send_keys(test_info['username'])
        time.sleep(3)  # ユーザー名チェックに時間がかかる
        
        # 最終的なエラーチェック
        print("\n=== エラーメッセージ確認 ===")
        
        # すべてのエラー要素を探す
        error_selectors = [
            "span[role='alert']",
            "div[role='alert']",
            ".error",
            "span.x1lliihq",  # Instagramのエラークラス
            "[aria-invalid='true']"
        ]
        
        found_errors = False
        for selector in error_selectors:
            errors = driver.find_elements(By.CSS_SELECTOR, selector)
            for error in errors:
                if error.text and error.is_displayed():
                    print(f"❌ エラー発見: {error.text}")
                    found_errors = True
        
        if not found_errors:
            print("✅ エラーメッセージは見つかりませんでした")
        
        # チェックボックスを探す
        print("\n=== チェックボックス確認 ===")
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"チェックボックス数: {len(checkboxes)}")
        
        for i, checkbox in enumerate(checkboxes):
            parent = checkbox.find_element(By.XPATH, "./..")
            label_text = parent.text
            print(f"Checkbox {i+1}: {label_text[:50]}...")
            
            if not checkbox.is_selected():
                print(f"   → チェックされていません。チェックします。")
                driver.execute_script("arguments[0].click();", checkbox)
        
        # 登録ボタンの状態確認
        print("\n=== 登録ボタン確認 ===")
        register_button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(text(), '登録する')]")
        
        print(f"ボタンテキスト: {register_button.text}")
        print(f"表示状態: {register_button.is_displayed()}")
        print(f"有効状態: {register_button.is_enabled()}")
        print(f"クラス: {register_button.get_attribute('class')}")
        
        # disabled属性確認
        disabled = register_button.get_attribute('disabled')
        aria_disabled = register_button.get_attribute('aria-disabled')
        print(f"disabled属性: {disabled}")
        print(f"aria-disabled属性: {aria_disabled}")
        
        # フォーム全体の確認
        print("\n=== フォーム確認 ===")
        form = driver.find_element(By.TAG_NAME, "form")
        form_action = form.get_attribute('action')
        form_method = form.get_attribute('method')
        print(f"Form action: {form_action}")
        print(f"Form method: {form_method}")
        
        # JavaScript のコンソールエラー確認
        print("\n=== JavaScriptエラー確認 ===")
        logs = driver.get_log('browser')
        for log in logs:
            if log['level'] == 'SEVERE':
                print(f"JSエラー: {log['message']}")
        
        # スクリーンショット
        driver.save_screenshot('instagram_data/temp/validation_check.png')
        print("\n📸 スクリーンショット保存: validation_check.png")
        
    input("\nEnterキーで終了...")
    
except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()