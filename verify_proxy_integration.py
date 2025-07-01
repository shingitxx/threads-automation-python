# verify_proxy_integration.py
"""
プロキシ統合の確認スクリプト
すべての機能でプロキシが正しく使用されているか確認
"""
import os
import sys
from datetime import datetime
from threads_account_manager import ThreadsAccountManager
from src.core.threads_api import threads_api
from proxy.proxy_manager import ProxyManager

def check_proxy_integration():
    """プロキシ統合状況をチェック"""
    print("🔍 === プロキシ統合確認 ===")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 1. ProxyManagerの確認
    print("\n1️⃣ ProxyManager設定確認:")
    proxy_manager = ProxyManager()
    print(f"   - プロキシ有効: {proxy_manager.enabled}")
    print(f"   - テストモード: {proxy_manager.test_mode}")
    print(f"   - プロバイダー: {proxy_manager.provider}")
    
    # 2. threads_apiでのプロキシ設定確認
    print("\n2️⃣ threads_api統合確認:")
    if hasattr(threads_api, 'proxy_manager'):
        print("   ✅ proxy_managerが追加されています")
    else:
        print("   ❌ proxy_managerが見つかりません")
    
    # 3. メソッドのプロキシ対応確認
    print("\n3️⃣ APIメソッドのプロキシ対応状況:")
    
    methods_to_check = [
        'create_text_post',
        'create_reply_post',
        'create_image_post',
        'create_image_reply_post',
        'create_media_container',
        'create_carousel_container',
        'create_true_carousel_post'
    ]
    
    # コードを文字列として読み込んで確認
    api_file_path = 'src/core/threads_api.py'
    if os.path.exists(api_file_path):
        with open(api_file_path, 'r', encoding='utf-8') as f:
            api_code = f.read()
        
        for method in methods_to_check:
            # メソッドの開始位置を探す
            method_start = api_code.find(f"def {method}")
            if method_start == -1:
                print(f"   ❓ {method}: メソッドが見つかりません")
                continue
            
            # 次のメソッドまたはクラスの終わりを探す（より正確な範囲）
            method_end = api_code.find('\n    def ', method_start + 1)
            if method_end == -1:
                method_end = api_code.find('\nclass ', method_start + 1)
            if method_end == -1:
                method_end = api_code.find('\n# ', method_start + 1)
            if method_end == -1:
                method_end = len(api_code)
            
            # メソッド内のコードを取得
            method_code = api_code[method_start:method_end]
            
            # プロキシ対応をチェック（複数のパターンで確認）
            proxy_patterns = [
                'proxies=',
                'proxies =',
                'proxies= proxies',
                'proxies = proxies',
                'get_proxy_for_account'
            ]
            
            proxy_found = any(pattern in method_code for pattern in proxy_patterns)
            
            if proxy_found:
                print(f"   ✅ {method}: プロキシ対応済み")
                # デバッグ用：プロキシ設定箇所を表示
                if method == 'create_true_carousel_post':
                    lines = method_code.split('\n')
                    for i, line in enumerate(lines):
                        if any(pattern in line for pattern in proxy_patterns):
                            print(f"      └─ 行{i}: {line.strip()[:60]}...")
            else:
                print(f"   ❌ {method}: プロキシ未対応")
                # デバッグ用：メソッドの長さを表示
                print(f"      └─ メソッドのコード長: {len(method_code)}文字")
    else:
        print(f"   ❌ {api_file_path} が見つかりません")
    
    # 4. 環境変数の確認
    print("\n4️⃣ 環境変数の確認:")
    proxy_env_vars = {
        'PROXY_ENABLED': os.getenv('PROXY_ENABLED', '未設定'),
        'PROXY_TEST_MODE': os.getenv('PROXY_TEST_MODE', '未設定'),
        'PROXY_PROVIDER': os.getenv('PROXY_PROVIDER', '未設定')
    }
    
    for key, value in proxy_env_vars.items():
        print(f"   - {key}: {value}")
    
    # 5. アカウント別プロキシ設定の確認
    print("\n5️⃣ アカウント別プロキシ設定:")
    account_manager = ThreadsAccountManager()
    accounts = account_manager.get_account_ids()[:3]  # 最初の3アカウントのみ
    
    for account_id in accounts:
        proxy = proxy_manager.get_proxy_for_account(account_id)
        if proxy:
            print(f"   - {account_id}: プロキシ設定あり")
        else:
            print(f"   - {account_id}: 直接接続")
    
    # 6. 詳細な統合状況サマリー
    print("\n6️⃣ 統合状況サマリー:")
    total_methods = len(methods_to_check)
    
    # 再度チェックして統計を取る
    if os.path.exists(api_file_path):
        with open(api_file_path, 'r', encoding='utf-8') as f:
            api_code = f.read()
        
        proxy_ready_count = 0
        for method in methods_to_check:
            method_start = api_code.find(f"def {method}")
            if method_start == -1:
                continue
            
            method_end = api_code.find('\n    def ', method_start + 1)
            if method_end == -1:
                method_end = len(api_code)
            
            method_code = api_code[method_start:method_end]
            if any(pattern in method_code for pattern in ['proxies=', 'proxies =', 'get_proxy_for_account']):
                proxy_ready_count += 1
        
        print(f"   - プロキシ対応済みメソッド: {proxy_ready_count}/{total_methods}")
        print(f"   - 完成度: {(proxy_ready_count/total_methods)*100:.1f}%")
        
        if proxy_ready_count == total_methods:
            print("   ✅ すべてのAPIメソッドがプロキシに対応しています！")
        else:
            print(f"   ⚠️  {total_methods - proxy_ready_count}個のメソッドがプロキシ未対応です")
    
    print("\n" + "=" * 50)
    print("✅ プロキシ統合確認完了")

if __name__ == "__main__":
    check_proxy_integration()