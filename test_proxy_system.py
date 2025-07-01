# test_proxy_system.py
"""
プロキシシステムのテストスクリプト
"""
import os
import sys
from proxy.proxy_manager import ProxyManager
from threads_account_manager import ThreadsAccountManager

def test_proxy_connection():
    """プロキシ接続テスト"""
    print("🧪 === プロキシシステムテスト ===")
    
    # プロキシマネージャー初期化
    proxy_manager = ProxyManager()
    
    # 現在の設定を表示
    print(f"\n📊 現在の設定:")
    print(f"  - プロキシ有効: {proxy_manager.enabled}")
    print(f"  - テストモード: {proxy_manager.test_mode}")
    print(f"  - プロバイダー: {proxy_manager.provider}")
    
    # アカウントマネージャーからアカウントを取得
    account_manager = ThreadsAccountManager()
    accounts = account_manager.get_account_ids()
    
    if not accounts:
        print("❌ テスト用アカウントが見つかりません")
        return
    
    # 最初のアカウントでテスト
    test_account = accounts[0]
    print(f"\n🔧 テストアカウント: {test_account}")
    
    # プロキシ取得テスト
    print(f"\n1️⃣ プロキシ取得テスト:")
    proxy = proxy_manager.get_proxy_for_account(test_account)
    if proxy:
        print(f"✅ プロキシ取得成功")
        print(f"   HTTP: {proxy_manager._mask_proxy_url(proxy['http'])}")
    else:
        print(f"ℹ️ プロキシなし（直接接続）")
    
    # 接続テスト
    print(f"\n2️⃣ 接続テスト:")
    if proxy_manager.test_proxy(test_account):
        print(f"✅ 接続テスト成功")
    else:
        print(f"❌ 接続テスト失敗")
    
    # 統計情報
    print(f"\n3️⃣ 使用統計:")
    stats = proxy_manager.get_usage_stats()
    print(f"  - 総リクエスト数: {stats['total_requests']}")
    print(f"  - プロバイダー: {stats['provider']}")
    print(f"  - テストモード: {stats['test_mode']}")

def test_with_actual_post():
    """実際の投稿でプロキシをテスト"""
    print("\n🚀 === 実際の投稿でプロキシテスト ===")
    
    from threads_automation_system import ThreadsAutomationSystem
    
    # システム初期化
    system = ThreadsAutomationSystem()
    
    # テストモードで単発投稿
    print("\n📝 テストモードで投稿シミュレーション:")
    result = system.single_post(test_mode=True)
    
    if result:
        print("✅ テスト投稿成功")
    else:
        print("❌ テスト投稿失敗")

if __name__ == "__main__":
    # 基本的なプロキシテスト
    test_proxy_connection()
    
    # 実際の投稿でテスト
    confirm = input("\n実際の投稿でテストしますか？ (y/n): ")
    if confirm.lower() == 'y':
        test_with_actual_post()
    
    print("\n✅ プロキシシステムテスト完了")