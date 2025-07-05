import requests
import json
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os
from datetime import datetime

class ProxyIPChecker:
    def __init__(self):
        self.proxy_sessions = [
            "7i7zey36_lifetime-12h",
            "wm6xvyww_lifetime-20h",
            "mtt1eo7g_lifetime-3h",
            "9drxv6m2_lifetime-5h",
            "lh8pnld8_lifetime-3h",
            "mqc7uh51_lifetime-4h",
            "2h9g1e99_lifetime-8h",
            "apqlpfsx_lifetime-19h",
            "3ya3z213_lifetime-7h",
            "p86tr9m9_lifetime-11h",
            "8csylzl9_lifetime-6h",
            "kojybfeg_lifetime-18h",
            "46q75oht_lifetime-19h",
            "5saamfkt_lifetime-23h",
            "83ucpem7_lifetime-11h",
            "3oe6umil_lifetime-1h",
            "yhxc9z9a_lifetime-18h",
            "0kuyd286_lifetime-19h",
            "dlxnwrmo_lifetime-8h",
            "jlvw6yi1_lifetime-15h",
            "spizi9ob_lifetime-18h",
            "32ijg4d3_lifetime-11h",
            "ie0x3zhk_lifetime-4h",
            "kqvrjtvg_lifetime-19h",
            "76w5dgtn_lifetime-3h",
            "axsa828b_lifetime-17h",
            "zt2evsnl_lifetime-1h",
            "xwawqy31_lifetime-2h",
            "i6yfyn5i_lifetime-13h",
            "avzy9puv_lifetime-13h",
            "3n7obiq5_lifetime-14h",
            "iad9w0w3_lifetime-7h",
            "9hg6gcs0_lifetime-3h",
            "wsjn7oqe_lifetime-9h",
            "oi5rklpf_lifetime-18h",
            "n0pld22u_lifetime-20h",
            "6ycs64ml_lifetime-16h",
            "avq3ax1e_lifetime-9h",
            "qqbvsoc7_lifetime-9h",
            "ezru8kd7_lifetime-8h",
            "sz51a0hg_lifetime-13h",
            "x8uuy3uv_lifetime-12h",
            "cpmhpg72_lifetime-3h",
            "aaq48ybf_lifetime-5h",
            "omh5z7rc_lifetime-20h",
            "0cmalxet_lifetime-10h",
            "y107zwat_lifetime-22h",
            "p5sp90x7_lifetime-5h",
            "j0i18jre_lifetime-23h",
            "jjaqh2fg_lifetime-1h",
            "0xj098hi_lifetime-17h",
            "g5yayhh9_lifetime-5h",
            "lq5sm4gi_lifetime-13h",
            "6g2saf2z_lifetime-21h",
            "ikcw0mge_lifetime-24h",
            "usvmx2zw_lifetime-13h",
            "3a13etyw_lifetime-24h",
            "ftbok5s5_lifetime-23h",
            "2uim18jl_lifetime-1h",
            "cbj4ffee_lifetime-12h",
            "9wdar843_lifetime-19h",
            "ekstrx6d_lifetime-1h",
            "ivl4ij9o_lifetime-15h",
            "4x9hu5kt_lifetime-23h",
            "nedlmrf3_lifetime-3h",
            "7xnfc1zp_lifetime-10h",
            "j36q15ad_lifetime-15h",
            "gsbti5oq_lifetime-20h",
            "gkemc9u8_lifetime-23h",
            "0luspoji_lifetime-19h",
            "4jegucjy_lifetime-7h",
            "ausrjyv9_lifetime-1h",
            "ws55v7da_lifetime-24h",
            "tnjbux2i_lifetime-1h",
            "iju48eql_lifetime-20h",
            "f9sy3ofp_lifetime-22h",
            "3rmv63gb_lifetime-4h",
            "zaf17ynz_lifetime-6h",
            "zy6ys01u_lifetime-17h",
            "bm26ck7m_lifetime-2h",
            "31w3ntib_lifetime-6h",
            "8c9u5dql_lifetime-23h",
            "x9sd3efq_lifetime-11h",
            "uzypjm4r_lifetime-1h",
            "ln35tikn_lifetime-15h",
            "2x6qewbt_lifetime-9h",
            "7q0g3y21_lifetime-2h",
            "szqmotah_lifetime-8h",
            "xsogos8y_lifetime-6h",
            "08xauabf_lifetime-15h",
            "yukokn95_lifetime-23h",
            "ikslow23_lifetime-22h",
            "ybt8m68i_lifetime-19h",
            "4uy3a7ki_lifetime-2h",
            "pj88zupo_lifetime-10h",
            "ilquxg24_lifetime-11h",
            "rtj76mh9_lifetime-8h",
            "ww8phio3_lifetime-16h",
            "4j8bygzb_lifetime-14h",
            "93s4ewn1_lifetime-10h",
            "molfzvog_lifetime-9h",
            "vy88whxq_lifetime-19h",
            "mim4q1wl_lifetime-7h",
            "njm3lvwl_lifetime-13h",
            "rql0l4b8_lifetime-6h",
            "7f6rnlrt_lifetime-16h",
            "safm64jt_lifetime-17h",
            "o5bsxfwk_lifetime-21h",
            "ichs74e2_lifetime-9h",
            "3jr9wiof_lifetime-10h"
        ]
        
        self.old_sessions = [
            "w0sc3hsf_lifetime-2h",
            "3icgignj_lifetime-9h", 
            "16u7hbrf_lifetime-4h",
            "ohxfhr7l_lifetime-15h",
            "uchw0mfn_lifetime-14h"
        ]
        
        self.proxy_host = "iproyal-aisa.hellworld.io"
        self.proxy_port = "12322"
        self.proxy_user = "C9kNyNmY"
        
        # ログディレクトリ作成
        os.makedirs("proxy_logs", exist_ok=True)
        
    def check_ip_with_requests(self, session_name=None):
        """requestsライブラリを使用してIPアドレスを確認"""
        print("\n" + "="*50)
        print("📡 Requestsライブラリでプロキシ確認")
        print("="*50)
        
        # 直接接続でのIP確認
        try:
            print("\n1. 直接接続（プロキシなし）:")
            response = requests.get("https://api.ipify.org?format=json", timeout=10)
            direct_ip = response.json()['ip']
            print(f"   📍 あなたの実際のIP: {direct_ip}")
            
            # IP情報の詳細取得
            ip_info = requests.get(f"https://ipapi.co/{direct_ip}/json/", timeout=10).json()
            print(f"   📍 場所: {ip_info.get('city', 'N/A')}, {ip_info.get('country_name', 'N/A')}")
            print(f"   📍 ISP: {ip_info.get('org', 'N/A')}")
        except Exception as e:
            print(f"   ❌ エラー: {e}")
        
        # プロキシ経由でのIP確認
        if session_name:
            session = session_name
        else:
            session = random.choice(self.proxy_sessions)
            
        proxy_password = f"fiWduY3n-country-jp_session-{session}"
        
        proxies = {
            'http': f'http://{self.proxy_user}:{proxy_password}@{self.proxy_host}:{self.proxy_port}',
            'https': f'http://{self.proxy_user}:{proxy_password}@{self.proxy_host}:{self.proxy_port}'
        }
        
        print(f"\n2. プロキシ経由（セッション: {session}）:")
        
        try:
            response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=20)
            proxy_ip = response.json()['ip']
            print(f"   📍 プロキシIP: {proxy_ip}")
            
            # プロキシIPの詳細情報
            ip_info = requests.get(f"https://ipapi.co/{proxy_ip}/json/", proxies=proxies, timeout=20).json()
            print(f"   📍 場所: {ip_info.get('city', 'N/A')}, {ip_info.get('country_name', 'N/A')}")
            print(f"   📍 ISP: {ip_info.get('org', 'N/A')}")
            
            # IPが変更されているか確認
            if proxy_ip != direct_ip:
                print(f"   ✅ IPアドレスが正しく変更されています！")
            else:
                print(f"   ❌ IPアドレスが変更されていません！")
                
            return {
                'session': session,
                'proxy_ip': proxy_ip,
                'location': f"{ip_info.get('city', 'N/A')}, {ip_info.get('country_name', 'N/A')}",
                'isp': ip_info.get('org', 'N/A'),
                'status': 'working'
            }
            
        except Exception as e:
            print(f"   ❌ プロキシエラー: {e}")
            return {
                'session': session,
                'status': 'error',
                'error': str(e)
            }
    
    def check_ip_with_selenium(self, session_name=None):
        """Seleniumを使用してブラウザ経由でIPアドレスを確認"""
        print("\n" + "="*50)
        print("🌐 Seleniumブラウザでプロキシ確認")
        print("="*50)
        
        if session_name:
            session = session_name
        else:
            session = random.choice(self.proxy_sessions)
            
        proxy_password = f"fiWduY3n-country-jp_session-{session}"
        
        # Chrome設定
        options = Options()
        options.add_argument("--lang=ja")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'--proxy-server=http://{self.proxy_host}:{self.proxy_port}')
        
        driver = None
        try:
            print(f"\nセッション: {session}")
            print(f"プロキシ認証情報:")
            print(f"  ユーザー名: {self.proxy_user}")
            print(f"  パスワード: {proxy_password}")
            
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("\n⚠️ ブラウザでプロキシ認証ダイアログが表示されたら、")
            print("上記の認証情報を入力してください。")
            input("\n認証完了後、Enterキーを押してください...")
            
            # IPアドレス確認サイトにアクセス
            print("\nIPアドレスを確認中...")
            driver.get("https://whatismyipaddress.com/")
            time.sleep(3)
            
            # スクリーンショット保存
            screenshot_path = f"proxy_logs/ip_check_{session}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 スクリーンショット保存: {screenshot_path}")
            
            # Instagramにアクセス可能か確認
            print("\nInstagramへのアクセスを確認中...")
            driver.get("https://www.instagram.com/")
            time.sleep(5)
            
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            if "公開プロキシ" in page_text or "flagged" in page_text.lower():
                print("❌ このプロキシはInstagramにブロックされています！")
                status = "blocked"
            else:
                print("✅ Instagramに正常にアクセスできました！")
                status = "working"
            
            # スクリーンショット保存
            screenshot_path = f"proxy_logs/instagram_{session}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Instagramスクリーンショット: {screenshot_path}")
            
            return {
                'session': session,
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {
                'session': session,
                'status': 'error',
                'error': str(e)
            }
        finally:
            if driver:
                driver.quit()
    
    def check_all_proxies(self, sample_size=5):
        """複数のプロキシをランダムにチェック"""
        print("\n" + "="*70)
        print("🔍 プロキシ一括チェック")
        print("="*70)
        
        results = []
        
        # 古いセッションをチェック
        print("\n【古いセッション（制限される可能性）】")
        for session in self.old_sessions[:2]:  # 最初の2つだけテスト
            result = self.check_ip_with_requests(session)
            results.append(result)
            time.sleep(2)
        
        # 新しいセッションをチェック
        print("\n【新しいセッション】")
        sample_sessions = random.sample(self.proxy_sessions, min(sample_size, len(self.proxy_sessions)))
        
        for i, session in enumerate(sample_sessions):
            print(f"\nテスト {i+1}/{len(sample_sessions)}")
            result = self.check_ip_with_requests(session)
            results.append(result)
            time.sleep(2)
        
        # 結果をファイルに保存
        log_file = f"proxy_logs/proxy_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 チェック結果を保存しました: {log_file}")
        
        # サマリー表示
        print("\n" + "="*70)
        print("📊 チェック結果サマリー")
        print("="*70)
        
        working = [r for r in results if r.get('status') == 'working']
        errors = [r for r in results if r.get('status') == 'error']
        
        print(f"✅ 正常動作: {len(working)}/{len(results)}")
        print(f"❌ エラー: {len(errors)}/{len(results)}")
        
        if working:
            print("\n正常動作しているプロキシ:")
            for proxy in working[:5]:  # 最初の5つだけ表示
                print(f"  - {proxy['session']}: {proxy.get('proxy_ip', 'N/A')} ({proxy.get('location', 'N/A')})")
    
    def compare_old_and_new(self):
        """古いプロキシと新しいプロキシを比較"""
        print("\n" + "="*70)
        print("🔄 新旧プロキシ比較")
        print("="*70)
        
        print("\n【古いプロキシ（制限される可能性）】")
        old_result = self.check_ip_with_requests(self.old_sessions[0])
        
        print("\n【新しいプロキシ】")
        new_result = self.check_ip_with_requests(self.proxy_sessions[0])
        
        print("\n" + "="*70)
        print("📋 比較結果")
        print("="*70)
        
        if old_result.get('status') == 'error' and new_result.get('status') == 'working':
            print("✅ 新しいプロキシは正常に動作しています！")
            print("✅ 古いプロキシから正しく切り替わっています！")
        elif old_result.get('status') == 'working' and new_result.get('status') == 'working':
            print("⚠️ 両方のプロキシが動作しています")
            print("   古いプロキシ: " + old_result.get('proxy_ip', 'N/A'))
            print("   新しいプロキシ: " + new_result.get('proxy_ip', 'N/A'))
        else:
            print("❌ 問題が発生している可能性があります")

def main():
    print("=== プロキシIPチェッカー ===")
    print("1. requestsでクイックチェック（単一プロキシ）")
    print("2. Seleniumでブラウザチェック（Instagram確認付き）")
    print("3. 複数プロキシの一括チェック")
    print("4. 新旧プロキシの比較")
    print("5. すべてのテストを実行")
    
    choice = input("\n選択してください (1-5): ")
    
    checker = ProxyIPChecker()
    
    if choice == "1":
        checker.check_ip_with_requests()
    elif choice == "2":
        checker.check_ip_with_selenium()
    elif choice == "3":
        sample = int(input("チェックするプロキシ数を入力 (1-10): "))
        checker.check_all_proxies(sample)
    elif choice == "4":
        checker.compare_old_and_new()
    elif choice == "5":
        print("\n全テスト実行中...")
        checker.check_ip_with_requests()
        time.sleep(2)
        checker.compare_old_and_new()
        time.sleep(2)
        checker.check_all_proxies(3)
    else:
        print("無効な選択です")

if __name__ == "__main__":
    main()