# test_proxy_loading.py
import json

def test_proxy_loading():
    """プロキシファイルの読み込みテスト"""
    print("=== プロキシファイル読み込みテスト ===")
    
    try:
        # proxies.txt を読み込む
        with open('proxies.txt', 'r', encoding='utf-8') as f:
            sessions = [line.strip() for line in f.readlines() if line.strip()]
        
        print(f"✅ プロキシ数: {len(sessions)}個")
        print(f"📋 最初の5個:")
        for i, session in enumerate(sessions[:5]):
            print(f"   {i+1}. {session}")
        
        print(f"📋 最後の5個:")
        for i, session in enumerate(sessions[-5:]):
            print(f"   {len(sessions)-4+i}. {session}")
            
        # プロキシフォーマットの確認
        print("\n📊 プロキシフォーマット分析:")
        sample = sessions[0] if sessions else ""
        if "_lifetime-" in sample:
            parts = sample.split("_lifetime-")
            print(f"   セッションID部分: {parts[0]}")
            print(f"   有効期限部分: lifetime-{parts[1] if len(parts) > 1 else '?'}")
        else:
            print(f"   サンプル: {sample}")
            
    except FileNotFoundError:
        print("❌ proxies.txt が見つかりません")
        print("   現在のディレクトリにproxies.txtを配置してください")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    test_proxy_loading()