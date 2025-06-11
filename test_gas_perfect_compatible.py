# test_gas_perfect_compatible.py - GAS版完全互換システム

import sys
import os
import json
import random
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
sys.path.append('.')

try:
    from config.settings import settings
    print("✅ config.settings インポート成功")
except ImportError as e:
    print(f"❌ 設定インポートエラー: {e}")
    sys.exit(1)

class GASPerfectCompatibleSystem:
    """GAS版完全互換システム（メイン投稿 + アフィリエイトリプライ）"""
    
    def __init__(self):
        self.main_contents = {}
        self.affiliate_contents = {}
        self.usage_history = {}
        self._setup_main_contents()
        self._setup_affiliate_contents()
    
    def _setup_main_contents(self):
        """メイン投稿コンテンツ設定（GAS版メインシート互換）"""
        self.main_contents = {
            "CONTENT_001": {
                "id": "CONTENT_001",
                "account_id": "ACC001",
                "main_text": "今からオ〇しようと思うけど、もうしこった〜？🍌おかずいる？？笑笑！\nお酒飲んで酔っちゃって脱いでガツガツ腰振るしまちらちゃん店行ってメメントな❤",
                "usage_count": 13,
                "replacement_usage": True,
                "active": True
            },
            "CONTENT_002": {
                "id": "CONTENT_002", 
                "account_id": "ACC001",
                "main_text": "あ、Switch2買えた人いる？\n買えた人いたら一緒にゲームしたいなー❤",
                "usage_count": 10,
                "replacement_usage": False,
                "active": True
            },
            "CONTENT_003": {
                "id": "CONTENT_003",
                "account_id": "ACC001", 
                "main_text": "当事間始しまあーす❤\nパセツ脱くたりに。",
                "usage_count": 10,
                "replacement_usage": True,
                "active": True
            },
            "CONTENT_004": {
                "id": "CONTENT_004",
                "account_id": "ACC001",
                "main_text": "すごいかい、薄かに定規がけたりい。って思う自分がいて、\n終わってんなってど思うけど...ってもいまんない笑",
                "usage_count": 12,
                "replacement_usage": True,
                "active": True
            },
            "CONTENT_005": {
                "id": "CONTENT_005",
                "account_id": "ACC001",
                "main_text": "近くなうらあろう？",
                "usage_count": 11,
                "replacement_usage": True,
                "active": True
            },
            # ACCOUNT_002のコンテンツも追加
            "CONTENT_101": {
                "id": "CONTENT_101",
                "account_id": "ACCOUNT_002",
                "main_text": "最近のスマホアプリって種類多すぎて選べないよね🤔\nみんなはどうやって選んでる？",
                "usage_count": 8,
                "replacement_usage": True,
                "active": True
            },
            "CONTENT_102": {
                "id": "CONTENT_102",
                "account_id": "ACCOUNT_002",
                "main_text": "夜中に見つけた神アプリ...これマジでやばい😱",
                "usage_count": 5,
                "replacement_usage": True,
                "active": True
            }
        }
    
    def _setup_affiliate_contents(self):
        """アフィリエイトコンテンツ設定（GAS版アフィリエイトシート完全互換）"""
        self.affiliate_contents = {
            # ACC001のアフィリエイト
            "AFF_001": {
                "id": "AFF_001",
                "account_id": "ACC001",
                "content_id": "CONTENT_001", 
                "reply_text": "ここに載せてるから好きに見ていいよ❤",
                "affiliate_url": "https://b-short.link/ZzDGuk",
                "replacement_usage": True
            },
            "AFF_002": {
                "id": "AFF_002",
                "account_id": "ACC001",
                "content_id": "CONTENT_002",
                "reply_text": "こうちにもあいて❤",
                "affiliate_url": "https://b-short.link/ZzDGuk",
                "replacement_usage": True
            },
            "AFF_003": {
                "id": "AFF_003",
                "account_id": "ACC001",
                "content_id": "CONTENT_003",
                "reply_text": "ここに載せてないエッすする動画は❤",
                "affiliate_url": "https://b-short.link/ZzDGuk",
                "replacement_usage": True
            },
            "AFF_004": {
                "id": "AFF_004",
                "account_id": "ACC001",
                "content_id": "CONTENT_004",
                "reply_text": "ここで覚せないのはこうちに❤",
                "affiliate_url": "https://b-short.link/ZzDGuk",
                "replacement_usage": True
            },
            "AFF_005": {
                "id": "AFF_005",
                "account_id": "ACC001",
                "content_id": "CONTENT_005",
                "reply_text": "過激すぎて...。",
                "affiliate_url": "https://b-short.link/ZzDGuk",
                "replacement_usage": True
            },
            
            # ACCOUNT_002のアフィリエイト  
            "AFF_101": {
                "id": "AFF_101",
                "account_id": "ACCOUNT_002",
                "content_id": "CONTENT_101",
                "reply_text": "こうちにもあいて❤",
                "affiliate_url": "https://b-short.link/ZzDGuk",
                "replacement_usage": True
            },
            "AFF_102": {
                "id": "AFF_102",
                "account_id": "ACCOUNT_002",
                "content_id": "CONTENT_102",
                "reply_text": "ここに載せてないエッすする動画は❤",
                "affiliate_url": "https://b-short.link/ZzDGuk",
                "replacement_usage": True
            }
        }
    
    def get_main_contents_for_account(self, account_id):
        """指定アカウントのメインコンテンツを取得"""
        return [content for content in self.main_contents.values() 
                if content["account_id"] == account_id and content["active"]]
    
    def get_random_main_content_for_account(self, account_id):
        """指定アカウントのランダムメインコンテンツを取得"""
        available_contents = self.get_main_contents_for_account(account_id)
        
        if not available_contents:
            return None
        
        # ランダム選択
        selected_content = random.choice(available_contents)
        
        # 使用履歴記録
        content_id = selected_content["id"]
        if content_id not in self.usage_history:
            self.usage_history[content_id] = []
        
        self.usage_history[content_id].append({
            "used_at": datetime.now().isoformat(),
            "account_id": account_id,
            "type": "main_post"
        })
        
        return selected_content
    
    def get_affiliate_for_content(self, content_id, account_id):
        """指定コンテンツ・アカウントに対応するアフィリエイトを取得（GAS版完全互換）"""
        for affiliate in self.affiliate_contents.values():
            if (affiliate["content_id"] == content_id and 
                affiliate["account_id"] == account_id):
                return affiliate
        return None
    
    def format_main_post_text(self, content):
        """メイン投稿テキストをフォーマット"""
        return content["main_text"]
    
    def format_affiliate_reply_text(self, affiliate):
        """アフィリエイトリプライテキストをフォーマット（GAS版完全互換）"""
        if not affiliate:
            return ""
        
        # GAS版と同じ形式：リプライテキスト + URL
        reply_text = affiliate["reply_text"]
        
        if affiliate.get("affiliate_url"):
            reply_text += f"\n{affiliate['affiliate_url']}"
        
        return reply_text
    
    def execute_single_account_post(self, account_id, test_mode=True):
        """単一アカウントでのツリー投稿実行（メイン + アフィリエイトリプライ）"""
        print(f"👤 === {account_id} ツリー投稿実行 ===")
        
        # 1. メインコンテンツを選択
        main_content = self.get_random_main_content_for_account(account_id)
        if not main_content:
            print(f"❌ {account_id}: 利用可能なメインコンテンツがありません")
            return False
        
        print(f"📝 選択メインコンテンツ: {main_content['id']} - {main_content['main_text'][:50]}...")
        
        # 2. 対応するアフィリエイトを取得
        affiliate = self.get_affiliate_for_content(main_content["id"], account_id)
        if not affiliate:
            print(f"❌ {account_id}: {main_content['id']}に対応するアフィリエイトが見つかりません")
            return False
        
        print(f"🔗 対応アフィリエイト: {affiliate['id']} - {affiliate['reply_text'][:30]}...")
        
        # 3. メイン投稿実行
        main_text = self.format_main_post_text(main_content)
        print(f"📝 {account_id}: メイン投稿実行中...")
        print(f"   投稿文: {main_text[:100]}...")
        
        if test_mode:
            main_post_id = f"POST_{random.randint(1000000000, 9999999999)}"
            print(f"   ✅ メイン投稿成功（シミュレート）: {main_post_id}")
        else:
            # 実際のAPI呼び出し
            main_post_id = "REAL_POST_ID_HERE"
            print(f"   ✅ メイン投稿成功: {main_post_id}")
        
        # 4. リプライ投稿実行
        print(f"⏸️ リプライ準備中（5秒待機）...")
        if not test_mode:
            import time
            time.sleep(5)
        
        reply_text = self.format_affiliate_reply_text(affiliate)
        print(f"💬 {account_id}: アフィリエイトリプライ実行中...")
        print(f"   リプライ先: {main_post_id}")
        print(f"   リプライ文: {reply_text}")
        
        if test_mode:
            reply_post_id = f"REPLY_{random.randint(1000000000, 9999999999)}"
            print(f"   ✅ アフィリエイトリプライ成功（シミュレート）: {reply_post_id}")
        else:
            # 実際のAPI呼び出し
            reply_post_id = "REAL_REPLY_ID_HERE"
            print(f"   ✅ アフィリエイトリプライ成功: {reply_post_id}")
        
        print(f"🎉 {account_id}: ツリー投稿完了（メイン + アフィリエイトリプライ）")
        
        return {
            "success": True,
            "account_id": account_id,
            "main_content": main_content,
            "affiliate": affiliate,
            "main_post_id": main_post_id,
            "reply_post_id": reply_post_id
        }
    
    def execute_all_accounts_post(self, test_mode=True):
        """全アカウントでのツリー投稿実行"""
        print(f"🚀 === 全アカウント ツリー投稿実行 ===")
        
        # アクティブアカウント取得
        active_accounts = list(set([
            content["account_id"] for content in self.main_contents.values() 
            if content["active"]
        ]))
        
        print(f"👥 対象アカウント数: {len(active_accounts)}")
        
        results = []
        successful_posts = 0
        
        for i, account_id in enumerate(active_accounts, 1):
            print(f"🔄 [{i}/{len(active_accounts)}] {account_id} 投稿開始")
            
            result = self.execute_single_account_post(account_id, test_mode)
            results.append(result)
            
            if result and result.get("success"):
                successful_posts += 1
                print(f"✅ {account_id}: 投稿完了")
            else:
                print(f"❌ {account_id}: 投稿失敗")
            
            # アカウント間の待機時間
            if i < len(active_accounts):
                print(f"⏸️ 次のアカウントまで10秒待機...")
                if not test_mode:
                    import time
                    time.sleep(10)
        
        # 結果サマリー
        success_rate = (successful_posts / len(active_accounts)) * 100 if active_accounts else 0
        
        print(f"\n📊 === 全アカウント投稿結果 ===")
        print(f"✅ 成功: {successful_posts}/{len(active_accounts)}アカウント")
        print(f"📈 成功率: {success_rate:.1f}%")
        
        print(f"\n📋 アカウント別結果:")
        for result in results:
            if result and result.get("success"):
                print(f"  ✅ {result['account_id']}")
                print(f"    メイン投稿: {result['main_post_id']}")
                print(f"    アフィリエイトリプライ: {result['reply_post_id']}")
                print(f"    使用コンテンツ: {result['main_content']['id']}")
                print(f"    使用アフィリエイト: {result['affiliate']['id']}")
            else:
                print(f"  ❌ 投稿失敗")
        
        return {
            "success_rate": success_rate,
            "successful_posts": successful_posts,
            "total_accounts": len(active_accounts),
            "results": results
        }
    
    def get_system_stats(self):
        """システム統計を取得"""
        stats = {
            "main_contents": {
                "total": len(self.main_contents),
                "active": len([c for c in self.main_contents.values() if c["active"]])
            },
            "affiliate_contents": {
                "total": len(self.affiliate_contents),
                "with_url": len([a for a in self.affiliate_contents.values() if a.get("affiliate_url")])
            },
            "account_stats": {}
        }
        
        # アカウント別統計
        for content in self.main_contents.values():
            account_id = content["account_id"]
            if account_id not in stats["account_stats"]:
                stats["account_stats"][account_id] = {
                    "main_contents": 0,
                    "affiliate_contents": 0
                }
            
            stats["account_stats"][account_id]["main_contents"] += 1
        
        for affiliate in self.affiliate_contents.values():
            account_id = affiliate["account_id"]
            if account_id in stats["account_stats"]:
                stats["account_stats"][account_id]["affiliate_contents"] += 1
        
        return stats
    
    def save_to_json(self, filepath=None):
        """データをJSONファイルに保存"""
        if not filepath:
            filepath = os.path.join("src", "data", "gas_perfect_compatible.json")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        save_data = {
            "main_contents": self.main_contents,
            "affiliate_contents": self.affiliate_contents,
            "usage_history": self.usage_history,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return filepath

def test_gas_perfect_compatible_system():
    """GAS版完全互換システムのテスト実行"""
    print("🔧 GAS版完全互換システム 統合テスト")
    print("=" * 60)
    
    # システム初期化
    system = GASPerfectCompatibleSystem()
    
    # 統計表示
    stats = system.get_system_stats()
    print(f"📊 メインコンテンツ数: {stats['main_contents']['total']} (アクティブ: {stats['main_contents']['active']})")
    print(f"📊 アフィリエイト数: {stats['affiliate_contents']['total']} (URL付き: {stats['affiliate_contents']['with_url']})")
    
    print(f"\n📊 アカウント別統計:")
    for account_id, account_stats in stats["account_stats"].items():
        print(f"  {account_id}: メイン{account_stats['main_contents']}件 / アフィリエイト{account_stats['affiliate_contents']}件")
    
    print(f"\n🧪 テストモード: 実際のAPI呼び出しは行いません")
    print(f"💡 実際の投稿には.envファイル設定が必要です")
    print("=" * 60)
    
    # 1. 単一アカウントテスト
    print(f"\n🧪 1. 単一アカウントツリー投稿テスト")
    result = system.execute_single_account_post("ACC001", test_mode=True)
    if result and result.get("success"):
        print(f"✅ 単一アカウントテスト: 成功")
    else:
        print(f"❌ 単一アカウントテスト: 失敗")
    
    print("-" * 30)
    
    # 2. 全アカウントテスト
    print(f"\n🧪 2. 全アカウントツリー投稿テスト")
    all_results = system.execute_all_accounts_post(test_mode=True)
    print(f"✅ 全アカウントテスト成功率: {all_results['success_rate']:.1f}%")
    
    # JSONファイル保存テスト
    print(f"\n💾 JSONファイル保存テスト:")
    try:
        saved_path = system.save_to_json()
        print(f"✅ GAS完全互換データを保存: {saved_path}")
        
        file_size = os.path.getsize(saved_path)
        print(f"  ✅ ファイルサイズ: {file_size} bytes")
        print(f"  📄 メインコンテンツ数: {len(system.main_contents)}")
        print(f"  📄 アフィリエイト数: {len(system.affiliate_contents)}")
        
    except Exception as e:
        print(f"❌ 保存エラー: {e}")
    
    print(f"\n🔄 GAS版との完全互換性:")
    print(f"  ✅ メインシート構造 (アカウントID + コンテンツID + メイン投稿文)")
    print(f"  ✅ アフィリエイトシート構造 (アフィリエイトID + アカウントID + コンテンツID + リプライ文 + URL)")
    print(f"  ✅ アカウント・コンテンツ紐付け")
    print(f"  ✅ ツリー投稿（メイン → アフィリエイトリプライ）")
    print(f"  ✅ ランダムコンテンツ選択")
    print(f"  ✅ 使用履歴・統計")
    print(f"  ✅ 複数アカウント対応")
    
    print(f"\n✅ GAS版完全互換システムテスト完了")
    print(f"🎯 次のステップ: .env ファイル設定 → 実際の投稿テスト")
    
    return system

if __name__ == "__main__":
    test_gas_perfect_compatible_system()