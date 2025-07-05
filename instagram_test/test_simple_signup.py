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

# ユーザー情報生成
username = f"test_{random.randint(1000, 9999)}"
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
    time.sleep(1)
    
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
            
            # 認証コード確認
            print("\n認証コード入力画面を確認中...")
            
            # すべての入力欄を表示
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"入力欄数: {len(all_inputs)}")
            
            for i, inp in enumerate(all_inputs):
                if inp.is_displayed():
                    print(f"Input {i}: type={inp.get_attribute('type')}, "
                          f"placeholder={inp.get_attribute('placeholder')}")
            
            # スクリーンショット
            driver.save_screenshot('instagram_data/temp/verification_screen.png')
            print("スクリーンショット保存: verification_screen.png")
            
            # メール確認
            print("\nメール確認中...")
            headers = {"Authorization": f"Bearer {mail_account['token']}"}
            response = requests.get("https://api.mail.tm/messages", headers=headers)
            
            if response.status_code == 200:
                messages = response.json()
                print(f"メール数: {messages['hydra:totalItems']}")
                
                if messages['hydra:totalItems'] > 0:
                    for msg in messages['hydra:member']:
                        print(f"件名: {msg.get('subject', 'なし')}")
    
    print("\nテスト完了！")
    input("エンターキーでブラウザを閉じます...")
    
except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()