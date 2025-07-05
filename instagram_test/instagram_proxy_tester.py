import requests
import json
import random
import time
from datetime import datetime
import os

class InstagramProxyTester:
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
        os.makedirs("proxy_test_logs", exist_ok=True)
        
    def test_instagram_access(self, session_name):
        """Instagramへのアクセスをテスト"""
        proxy_password = f"fiWduY3n-country-jp_session-{session_name}"
        
        proxies = {
            'http': f'http://{self.proxy_user}:{proxy_password}@{self.proxy_host}:{self.proxy_port}',
            'https': f'http://{self.proxy_user}:{proxy_password}@{self.proxy_host}:{self.proxy_port}'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        result = {
            'session': session_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'details': {}
        }
        
        try:
            # まずIPアドレスを確認
            print(f"\n📍 セッション: {session_name}")
            ip_response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=10)
            proxy_ip = ip_response.json()['ip']
            result['proxy_ip'] = proxy_ip
            print(f"   プロキシIP: {proxy_ip}")
            
            # IPの詳細情報
            ip_info = requests.get(f"https://ipapi.co/{proxy_ip}/json/", proxies=proxies, timeout=10).json()
            result['location'] = f"{ip_info.get('city', 'N/A')}, {ip_info.get('country_name', 'N/A')}"
            result['isp'] = ip_info.get('org', 'N/A')
            print(f"   場所: {result['location']}")
            print(f"   ISP: {result['isp']}")
            
            # Instagramのサインアップページにアクセス
            print("   📱 Instagramアクセステスト中...")
            
            # 複数のURLでテスト
            test_urls = [
                "https://www.instagram.com/",
                "https://www.instagram.com/accounts/emailsignup/"
            ]
            
            for url in test_urls:
                try:
                    response = requests.get(
                        url,
                        headers=headers,
                        proxies=proxies,
                        timeout=20,
                        allow_redirects=True
                    )
                    
                    status_code = response.status_code
                    result['details'][url] = {
                        'status_code': status_code,
                        'final_url': response.url,
                        'content_length': len(response.text)
                    }
                    
                    # レスポンス内容の確認
                    content = response.text.lower()
                    
                    if status_code == 200:
                        # ブロックインジケーターのチェック
                        blocked_indicators = [
                            "suspicious activity",
                            "automated",
                            "public proxy",
                            "公開プロキシ",
                            "flagged",
                            "blocked",
                            "制限"
                        ]
                        
                        is_blocked = any(indicator in content for indicator in blocked_indicators)
                        
                        # 正常なコンテンツの確認
                        normal_indicators = [
                            "instagram",
                            "sign up",
                            "登録",
                            "アカウント",
                            "create account"
                        ]
                        
                        has_normal_content = any(indicator in content for indicator in normal_indicators)
                        
                        if is_blocked:
                            result['status'] = 'blocked'
                            print(f"   ❌ ブロックされています ({url})")
                        elif has_normal_content:
                            result['status'] = 'working'
                            print(f"   ✅ 正常にアクセス可能 ({url})")
                        else:
                            result['status'] = 'uncertain'
                            print(f"   ⚠️ 不明な状態 ({url})")
                    else:
                        result['status'] = 'error'
                        print(f"   ❌ HTTPエラー: {status_code} ({url})")
                        
                except Exception as e:
                    result['details'][url] = {'error': str(e)}
                    print(f"   ❌ アクセスエラー ({url}): {str(e)[:50]}...")
                
                time.sleep(1)
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"   ❌ エラー: {str(e)[:100]}...")
        
        return result
    
    def test_multiple_proxies(self, test_old=True, test_new=True, sample_size=5):
        """複数のプロキシをテスト"""
        print("\n" + "="*70)
        print("🔍 Instagram プロキシアクセステスト")
        print("="*70)
        
        all_results = []
        
        # 古いプロキシのテスト
        if test_old:
            print("\n【古いプロキシ（制限されている可能性）】")
            for session in self.old_sessions[:min(2, len(self.old_sessions))]:
                result = self.test_instagram_access(session)
                all_results.append(result)
                time.sleep(3)
        
        # 新しいプロキシのテスト
        if test_new:
            print("\n【新しいプロキシ】")
            # ランダムにサンプリング
            sample_sessions = random.sample(self.proxy_sessions, min(sample_size, len(self.proxy_sessions)))
            
            for i, session in enumerate(sample_sessions):
                print(f"\n[新プロキシ {i+1}/{len(sample_sessions)}]")
                result = self.test_instagram_access(session)
                all_results.append(result)
                time.sleep(3)
        
        # 結果を保存
        self.save_results(all_results)
        
        # サマリー表示
        self.show_summary(all_results)
        
        return all_results
    
    def save_results(self, results):
        """結果をJSONファイルに保存"""
        filename = f"proxy_test_logs/instagram_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 テスト結果を保存しました: {filename}")
    
    def show_summary(self, results):
        """結果のサマリーを表示"""
        print("\n" + "="*70)
        print("📊 テスト結果サマリー")
        print("="*70)
        
        # ステータス別に分類
        working = [r for r in results if r['status'] == 'working']
        blocked = [r for r in results if r['status'] == 'blocked']
        errors = [r for r in results if r['status'] == 'error']
        uncertain = [r for r in results if r['status'] == 'uncertain']
        
        print(f"\n合計テスト数: {len(results)}")
        print(f"✅ 正常動作: {len(working)}")
        print(f"❌ ブロック: {len(blocked)}")
        print(f"⚠️ 不明: {len(uncertain)}")
        print(f"💥 エラー: {len(errors)}")
        
        # 古いプロキシと新しいプロキシの比較
        old_results = [r for r in results if r['session'] in self.old_sessions]
        new_results = [r for r in results if r['session'] in self.proxy_sessions]
        
        if old_results and new_results:
            print("\n【プロキシ比較】")
            
            old_working = len([r for r in old_results if r['status'] == 'working'])
            old_blocked = len([r for r in old_results if r['status'] == 'blocked'])
            
            new_working = len([r for r in new_results if r['status'] == 'working'])
            new_blocked = len([r for r in new_results if r['status'] == 'blocked'])
            
            print(f"古いプロキシ: 正常 {old_working}/{len(old_results)}, ブロック {old_blocked}/{len(old_results)}")
            print(f"新しいプロキシ: 正常 {new_working}/{len(new_results)}, ブロック {new_blocked}/{len(new_results)}")
            
            if old_blocked > 0 and new_working > 0:
                print("\n✅ 新しいプロキシへの切り替えが有効です！")
            elif old_working > 0 and new_working > 0:
                print("\n⚠️ 古いプロキシもまだ使用可能ですが、今後ブロックされる可能性があります。")
        
        # 正常動作しているプロキシのリスト
        if working:
            print("\n【使用可能なプロキシ】")
            for proxy in working[:10]:  # 最大10個まで表示
                print(f"  ✅ {proxy['session']} - {proxy.get('proxy_ip', 'N/A')} ({proxy.get('location', 'N/A')})")
        
        # ブロックされているプロキシのリスト
        if blocked:
            print("\n【ブロックされているプロキシ】")
            for proxy in blocked[:5]:  # 最大5個まで表示
                print(f"  ❌ {proxy['session']} - {proxy.get('proxy_ip', 'N/A')} ({proxy.get('location', 'N/A')})")
    
    def quick_test(self):
        """クイックテスト（新旧1つずつ）"""
        print("\n" + "="*70)
        print("⚡ クイックテスト")
        print("="*70)
        
        results = []
        
        # 古いプロキシを1つテスト
        if self.old_sessions:
            print("\n【古いプロキシテスト】")
            result = self.test_instagram_access(self.old_sessions[0])
            results.append(result)
        
        time.sleep(3)
        
        # 新しいプロキシを1つテスト
        if self.proxy_sessions:
            print("\n【新しいプロキシテスト】")
            result = self.test_instagram_access(random.choice(self.proxy_sessions))
            results.append(result)
        
        self.show_summary(results)
        
        return results

def main():
    print("=== Instagram プロキシアクセステスター ===")
    print("1. クイックテスト（新旧1つずつ）")
    print("2. 新しいプロキシのみテスト（5個）")
    print("3. 古いプロキシのみテスト")
    print("4. 包括的テスト（新旧両方）")
    print("5. 大規模テスト（新プロキシ10個）")
    
    choice = input("\n選択してください (1-5): ")
    
    tester = InstagramProxyTester()
    
    if choice == "1":
        tester.quick_test()
    elif choice == "2":
        tester.test_multiple_proxies(test_old=False, test_new=True, sample_size=5)
    elif choice == "3":
        tester.test_multiple_proxies(test_old=True, test_new=False)
    elif choice == "4":
        tester.test_multiple_proxies(test_old=True, test_new=True, sample_size=5)
    elif choice == "5":
        tester.test_multiple_proxies(test_old=False, test_new=True, sample_size=10)
    else:
        print("無効な選択です")

if __name__ == "__main__":
    main()