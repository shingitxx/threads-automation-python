# test_proxy_gradual.py
"""
プロキシの段階的テストスクリプト
安全にプロキシ機能をテストする
"""
import os
import json
from datetime import datetime
from proxy.proxy_manager import ProxyManager
from threads_automation_system import ThreadsAutomationSystem

def test_phase1_mock():
    """Phase 1: モックプロキシでテスト"""
    print("🧪 === Phase 1: モックプロキシテスト ===")
    
    # 設定を確認
    os.environ['PROXY_ENABLED'] = 'true'
    os.environ['PROXY_TEST_MODE'] = 'true'
    os.environ['PROXY_PROVIDER'] = 'mock'
    
    proxy_manager = ProxyManager()
    print(f"設定: enabled={proxy_manager.enabled}, test_mode={proxy_manager.test_mode}")
    
    # テスト投稿（実際には投稿されない）
    system = ThreadsAutomationSystem()
    result = system.single_post(test_mode=True)
    
    if result:
        print("✅ Phase 1: 成功")
    else:
        print("❌ Phase 1: 失敗")
    
    return result is not None

def test_phase2_real_proxy():
    """Phase 2: 実プロキシでテスト（投稿はしない）"""
    print("\n🧪 === Phase 2: 実プロキシ接続テスト ===")
    
    # 実プロキシ設定（まだ投稿はしない）
    os.environ['PROXY_ENABLED'] = 'true'
    os.environ['PROXY_TEST_MODE'] = 'false'
    # プロバイダーは.envで設定されているものを使用
    
    proxy_manager = ProxyManager()
    
    # 接続テストのみ
    test_account = "ACCOUNT_001"
    success = proxy_manager.test_proxy(test_account)
    
    if success:
        print("✅ Phase 2: プロキシ接続成功")
    else:
        print("❌ Phase 2: プロキシ接続失敗")
    
    return success

def test_phase3_real_post():
    """Phase 3: 実プロキシで実際に投稿"""
    print("\n🧪 === Phase 3: 実プロキシで投稿テスト ===")
    print("⚠️  警告: 実際にThreadsに投稿されます")
    
    confirm = input("続行しますか？ (yes/no): ")
    if confirm.lower() != 'yes':
        print("テストを中止しました")
        return False
    
    # 実投稿
    system = ThreadsAutomationSystem()
    result = system.single_post(test_mode=False)
    
    if result:
        print("✅ Phase 3: 投稿成功")
        print(f"投稿結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print("❌ Phase 3: 投稿失敗")
    
    return result is not None

def main():
    """段階的テストのメイン処理"""
    print("🚀 プロキシ段階的テスト開始")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Phase 1
    if not test_phase1_mock():
        print("\n❌ Phase 1で失敗しました。修正が必要です。")
        return
    
    # Phase 2（プロキシ設定がある場合のみ）
    if os.getenv('PROXY_USERNAME'):
        if not test_phase2_real_proxy():
            print("\n❌ Phase 2で失敗しました。プロキシ設定を確認してください。")
            return
    else:
        print("\n⏭️  Phase 2をスキップ（プロキシ認証情報が未設定）")
    
    # Phase 3（オプション）
    print("\n" + "=" * 50)
    run_phase3 = input("Phase 3（実投稿テスト）を実行しますか？ (y/n): ")
    if run_phase3.lower() == 'y':
        test_phase3_real_post()
    
    print("\n✅ 段階的テスト完了")

if __name__ == "__main__":
    main()