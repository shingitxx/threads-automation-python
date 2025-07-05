from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
import json
import random
import string
import requests
import re
from datetime import datetime

print("スクリプト開始")

# 既存のmail.tmアカウントを使用
with open('instagram_data/temp/test_account.json', 'r', encoding='utf-8') as f:
    mail_account = json.load(f)

print(f"使用するメール: {mail_account['email']}")

# Chrome設定
options = Options()
options.add_argument("--lang=ja")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# ブラウザ起動
print("ブラウザ起動中...")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# よりユニークなユーザー名生成
timestamp = datetime.now().strftime("%m%d%H%M")
random_str = ''.join(random.choices(string.ascii_lowercase, k=4))
username = f"jp{random_str}{timestamp}"
fullname = "テスト ユーザー"
password = "TestPass123!@"

print(f"ユーザー名: {username}")

try:
    # サインアップページ
    driver.get("https://www.instagram.com/accounts/emailsignup/")
    time.sleep(3)
    
    # 基本情報入力
    print("基本情報入力中...")
    
    # メール
    email_input = wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone")))
    email_input.clear()
    email_input.send_keys(mail_account['email'])
    time.sleep(1)
    
    # フルネーム
    fullname_input = driver.find_element(By.NAME, "fullName")
    fullname_input.clear()
    fullname_input.send_keys(fullname)
    time.sleep(1)
    
    # ユーザー名
    username_input = driver.find_element(By.NAME, "username")
    username_input.clear()
    username_input.send_keys(username)
    time.sleep(2)  # ユーザー名チェックの時間を増やす
    
    # ユーザー名のエラーチェック
    try:
        error_element = driver.find_element(By.XPATH, "//span[contains(text(), '使用できません')]")
        if error_element.is_displayed():
            print("⚠️ ユーザー名が使用できません。代替案を使用します。")
            
            # 代替案のボタンを探す
            suggestion_buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in suggestion_buttons:
                button_text = button.text
                if button_text and len(button_text) > 3 and button_text != "登録する":
                    print(f"代替案を選択: {button_text}")
                    button.click()
                    time.sleep(1)
                    break
    except:
        print("✅ ユーザー名は利用可能です")
    
    # パスワード
    password_input = driver.find_element(By.NAME, "password")
    password_input.clear()
    password_input.send_keys(password)
    time.sleep(2)
    
    # 送信ボタン
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    print(f"送信ボタン状態: {'有効' if submit_button.is_enabled() else '無効'}")
    
    if submit_button.is_enabled():
        submit_button.click()
        print("フォーム送信完了")
        time.sleep(5)
        
        # 誕生日入力
        print("誕生日入力待機...")
        selects = driver.find_elements(By.TAG_NAME, "select")
        
        if len(selects) >= 3:
            print("誕生日入力中...")
            Select(selects[0]).select_by_value("5")  # 5月
            time.sleep(0.5)
            Select(selects[1]).select_by_value("15") # 15日
            time.sleep(0.5)
            Select(selects[2]).select_by_value("2000") # 2000年
            time.sleep(1)
            
            # 次へボタン
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "次へ" in button.text:
                    button.click()
                    print("誕生日送信")
                    break
            
            time.sleep(5)
            
            # 認証コード入力画面の確認
            print("\n🔍 認証コード入力画面を確認中...")
            current_url = driver.current_url
            print(f"現在のURL: {current_url}")
            
            # すべての入力欄を詳細に確認
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"\n入力欄数: {len(all_inputs)}")
            
            visible_input = None
            for i, inp in enumerate(all_inputs):
                try:
                    if inp.is_displayed():
                        input_type = inp.get_attribute('type') or 'text'
                        placeholder = inp.get_attribute('placeholder') or ''
                        name = inp.get_attribute('name') or ''
                        aria_label = inp.get_attribute('aria-label') or ''
                        value = inp.get_attribute('value') or ''
                        
                        print(f"\nInput {i}:")
                        print(f"  - type: {input_type}")
                        print(f"  - placeholder: {placeholder}")
                        print(f"  - name: {name}")
                        print(f"  - aria-label: {aria_label}")
                        print(f"  - 表示: {inp.is_displayed()}")
                        print(f"  - 有効: {inp.is_enabled()}")
                        
                        if inp.is_displayed() and inp.is_enabled() and not value:
                            visible_input = inp
                except:
                    pass
            
            # スクリーンショット
            driver.save_screenshot('instagram_data/temp/verification_detailed.png')
            print("\n📸 スクリーンショット保存: verification_detailed.png")
            
            # メールから認証コードを取得
            print("\n📧 メール確認中...")
            headers = {"Authorization": f"Bearer {mail_account['token']}"}
            
            code_found = None
            for attempt in range(5):
                response = requests.get("https://api.mail.tm/messages", headers=headers)
                
                if response.status_code == 200:
                    messages = response.json()
                    print(f"メール数: {messages['hydra:totalItems']}")
                    
                    if messages['hydra:totalItems'] > 0:
                        for msg in messages['hydra:member']:
                            subject = msg.get('subject', '')
                            print(f"件名: {subject}")
                            
                            if 'instagram' in subject.lower():
                                msg_id = msg.get('id')
                                msg_response = requests.get(
                                    f"https://api.mail.tm/messages/{msg_id}",
                                    headers=headers
                                )
                                
                                if msg_response.status_code == 200:
                                    msg_text = msg_response.json().get('text', '')
                                    codes = re.findall(r'\b\d{6}\b', msg_text)
                                    
                                    if codes:
                                        code_found = codes[0]
                                        print(f"\n✅ 認証コード発見: {code_found}")
                                        break
                        
                        if code_found:
                            break
                
                if not code_found:
                    print(f"待機中... ({attempt + 1}/5)")
                    time.sleep(5)
            
            # 認証コードを入力
            if code_found and visible_input:
                print(f"\n💉 認証コード入力中: {code_found}")
                visible_input.clear()
                visible_input.send_keys(code_found)
                time.sleep(1)
                
                # Enterキーで送信
                visible_input.send_keys(Keys.RETURN)
                print("✅ 認証コード送信")
                
                time.sleep(5)
                
                # 結果確認
                final_url = driver.current_url
                print(f"\n最終URL: {final_url}")
                
                if "emailsignup" not in final_url:
                    print("\n🎉 アカウント作成成功の可能性があります！")
                else:
                    print("\n⚠️ まだサインアップページにいます")
    
    print("\n✅ テスト完了！")
    input("エンターキーでブラウザを閉じます...")
    
except Exception as e:
    print(f"\n❌ エラー: {e}")
    import traceback
    traceback.print_exc()
    driver.save_screenshot('instagram_data/temp/error_screenshot.png')
    
finally:
    driver.quit()