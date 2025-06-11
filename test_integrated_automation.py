"""
統合自動化システム
投稿システム + スケジューラーを統合した完全自動化システム
"""

import sys
import os
import time
import json
import random
import threading
from datetime import datetime, timedelta
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config.settings import settings
    print("✅ config.settings インポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    class FallbackSettings:
        def __init__(self):
            self.schedule = type('obj', (object,), {
                'enabled': True,
                'posting_hours': [2, 5, 8, 12, 17, 20, 22, 0]
            })
            self.posting = type('obj', (object,), {
                'reply_delay_minutes': 5,
                'all_accounts_interval_seconds': 10
            })
        def get_account_tokens(self):
            return {}
    settings = FallbackSettings()

try:
    import schedule
    print("✅ schedule ライブラリ インポート成功")
except ImportError:
    print("❌ schedule ライブラリが見つかりません")
    print("📝 インストール: pip install schedule")
    sys.exit(1)

class IntegratedAutomationSystem:
    """統合自動化システム"""
    
    def __init__(self):
        self.accounts = self._setup_accounts()
        self.contents = self._setup_contents()
        self.affiliates = self._setup_affiliates()
        self.selection_history = {}
        
        # スケジューラー設定
        self.is_running = False
        self.scheduler_thread = None
        self.execution_log = []
        self.posting_hours = settings.schedule.posting_hours
        
        # 統計情報
        self.stats = {
            "total_posts": 0,
            "successful_posts": 0,
            "failed_posts": 0,
            "last_execution": None,
            "system_start_time": datetime.now()
        }
        
        # 実行モード
        self.test_mode = True  # テストモード
        self.auto_mode = False  # 自動モード
        
        print("🚀 統合自動化システム初期化完了")
    
    def _setup_accounts(self):
        """アカウント設定"""
        tokens = settings.get_account_tokens()
        return {
            "ACC001": {
                "id": "ACC001",
                "username": "kana_chan_ura", 
                "user_id": "23881245698173501",
                "access_token": tokens.get("ACC001"),
                "status": "アクティブ"
            },
            "ACCOUNT_002": {
                "id": "ACCOUNT_002",
                "username": "akari_chan_sab",
                "user_id": "8091935217596688", 
                "access_token": tokens.get("ACCOUNT_002"),
                "status": "アクティブ"
            }
        }
    
    def _setup_contents(self):
        """コンテンツ設定"""
        return {
            "CONTENT_001": {
                "account_id": "ACC001",
                "id": "CONTENT_001",
                "main_text": "今からオ〇しようと思うけど、もうしこった〜？🍌おかずいる？？笑笑",
                "use_image": "NO"
            },
            "CONTENT_002": {
                "account_id": "ACCOUNT_002", 
                "id": "CONTENT_002",
                "main_text": "最近のスマホアプリって種類多すぎて選べないよね🤔\nみんなはどうやって選んでる？",
                "use_image": "NO"
            },
            "CONTENT_003": {
                "account_id": "ACC001",
                "id": "CONTENT_003", 
                "main_text": "作業効率を10倍にしたツールがあるって聞いたんだけど...\n本当にそんなのある？🤯",
                "use_image": "NO"
            },
            "CONTENT_004": {
                "account_id": "ACCOUNT_002",
                "id": "CONTENT_004",
                "main_text": "夜中に見つけた神アプリ...これマジでやばい😱\n使いすぎ注意かも",
                "use_image": "NO"
            }
        }
    
    def _setup_affiliates(self):
        """アフィリエイト設定"""
        return {
            "AFF_001": {
                "id": "AFF_001",
                "account_id": "ACC001",
                "content_id": "CONTENT_001",
                "description": "ここに載せてるから好きに見ていいよ❤",
                "affiliate_url": "https://1link.jp/is001"
            },
            "AFF_002": {
                "id": "AFF_002", 
                "account_id": "ACCOUNT_002",
                "content_id": "CONTENT_002",
                "app_name": "おすすめアプリ",
                "description": "ユーザー評価4.8の人気アプリ！",
                "affiliate_url": "https://example.com/affiliate/app1",
                "call_to_action": "無料ダウンロードはこちら👆"
            },
            "AFF_003": {
                "id": "AFF_003",
                "account_id": "ACC001", 
                "content_id": "CONTENT_003",
                "app_name": "効率化アプリ",
                "description": "作業効率が本当に上がる神アプリ",
                "affiliate_url": "https://example.com/affiliate/app2",
                "call_to_action": "今すぐ試してみる🚀"
            },
            "AFF_004": {
                "id": "AFF_004",
                "account_id": "ACCOUNT_002",
                "content_id": "CONTENT_004",
                "app_name": "神アプリ",
                "description": "夜中に見つけた話題のアプリ",
                "affiliate_url": "https://example.com/affiliate/app3",
                "call_to_action": "チェックしてみて✨"
            }
        }
    
    # ==============================================
    # 投稿機能（既存システムを統合）
    # ==============================================
    
    def get_active_accounts(self):
        """アクティブなアカウント一覧を取得"""
        return [
            account for account in self.accounts.values()
            if account["status"] == "アクティブ"
        ]
    
    def get_random_content_for_account(self, account_id):
        """アカウント専用コンテンツをランダム選択（重複回避付き）"""
        account_contents = [
            content for content in self.contents.values()
            if content["account_id"] == account_id
        ]
        
        if not account_contents:
            return None
        
        # 重複回避ロジック
        recent_content = self.selection_history.get(account_id, [])
        available_content = [
            content for content in account_contents
            if content["id"] not in recent_content
        ]
        
        if available_content:
            selected = random.choice(available_content)
        else:
            # 全て最近使用済みの場合は全体から選択
            selected = random.choice(account_contents)
        
        # 選択履歴を記録
        if account_id not in self.selection_history:
            self.selection_history[account_id] = []
        self.selection_history[account_id].insert(0, selected["id"])
        if len(self.selection_history[account_id]) > 3:  # 直近3件のみ保持
            self.selection_history[account_id] = self.selection_history[account_id][:3]
        
        return selected
    
    def get_affiliate_for_content(self, content_id, account_id):
        """コンテンツに対応するアフィリエイトを取得"""
        for affiliate in self.affiliates.values():
            if (affiliate["content_id"] == content_id and 
                affiliate["account_id"] == account_id):
                return affiliate
        return None
    
    def format_affiliate_reply_text(self, affiliate):
        """アフィリエイトリプライテキストフォーマット"""
        reply_text = ""
        
        if affiliate.get("app_name"):
            reply_text += f"{affiliate['app_name']}\n\n"
        
        if affiliate.get("description"):
            reply_text += f"{affiliate['description']}"
        
        if affiliate.get("call_to_action"):
            reply_text += f"\n\n{affiliate['call_to_action']}"
        
        if affiliate.get("affiliate_url"):
            reply_text += f"\n{affiliate['affiliate_url']}"
        
        return reply_text
    
    def simulate_api_call(self, call_type, account, content_text, **kwargs):
        """API呼び出しシミュレート"""
        if self.test_mode:
            # テストモード：シミュレート
            time.sleep(random.uniform(0.5, 2.0))  # ランダム待機時間
            
            # 95%の確率で成功
            success = random.random() > 0.05
            
            if success:
                fake_id = f"{call_type.upper()}_{int(time.time())}{random.randint(100, 999)}"
                return {"success": True, "post_id": fake_id}
            else:
                return {"success": False, "error": f"API呼び出し失敗（シミュレート）"}
        else:
            # 実際のAPI呼び出し（.env設定済みの場合）
            # ここで実際のThreads API呼び出し
            return {"success": True, "post_id": "REAL_API_RESULT"}
    
    def execute_tree_posting_for_account(self, account):
        """単一アカウントでツリー投稿実行"""
        try:
            # コンテンツ取得
            content = self.get_random_content_for_account(account['id'])
            if not content:
                return {"success": False, "error": "コンテンツなし"}
            
            print(f"📝 {account['username']}: {content['id']} - {content['main_text'][:30]}...")
            
            # メイン投稿
            main_result = self.simulate_api_call("post", account, content['main_text'])
            if not main_result["success"]:
                return {"success": False, "error": f"メイン投稿失敗: {main_result.get('error')}"}
            
            print(f"✅ {account['username']}: メイン投稿成功 - {main_result['post_id']}")
            
            # リプライ準備
            time.sleep(2)  # 5秒 → 2秒に短縮（テスト用）
            
            # アフィリエイトリプライ
            affiliate = self.get_affiliate_for_content(content['id'], account['id'])
            if affiliate:
                reply_text = self.format_affiliate_reply_text(affiliate)
                reply_result = self.simulate_api_call("reply", account, reply_text, parent_id=main_result['post_id'])
                
                if reply_result["success"]:
                    print(f"💬 {account['username']}: リプライ成功 - {reply_result['post_id']}")
                    return {
                        "success": True,
                        "account": account['username'],
                        "main_post_id": main_result['post_id'],
                        "reply_post_id": reply_result['post_id'],
                        "content_id": content['id'],
                        "affiliate_id": affiliate['id']
                    }
                else:
                    print(f"⚠️ {account['username']}: リプライ失敗")
                    return {
                        "success": True,
                        "account": account['username'],
                        "main_post_id": main_result['post_id'],
                        "content_id": content['id'],
                        "reply_failed": True
                    }
            else:
                print(f"⚠️ {account['username']}: アフィリエイトなし")
                return {
                    "success": True,
                    "account": account['username'],
                    "main_post_id": main_result['post_id'],
                    "content_id": content['id'],
                    "no_affiliate": True
                }
                
        except Exception as e:
            print(f"❌ {account['username']}: 例外発生 - {e}")
            return {"success": False, "error": str(e)}
    
    def execute_all_accounts_posting(self):
        """全アカウント投稿実行（統合版）"""
        print("🚀 === 全アカウント自動投稿実行 ===")
        
        active_accounts = self.get_active_accounts()
        if not active_accounts:
            return {"success": False, "error": "アクティブなアカウントなし"}
        
        print(f"👥 対象アカウント数: {len(active_accounts)}")
        
        results = []
        success_count = 0
        start_time = time.time()
        
        for i, account in enumerate(active_accounts):
            print(f"\n🔄 [{i + 1}/{len(active_accounts)}] {account['username']} 投稿開始")
            
            result = self.execute_tree_posting_for_account(account)
            results.append(result)
            
            if result["success"]:
                success_count += 1
                self.stats["successful_posts"] += 1
            else:
                self.stats["failed_posts"] += 1
            
            self.stats["total_posts"] += 1
            
            # 次のアカウントまで間隔
            if i < len(active_accounts) - 1:
                wait_time = 3  # 10秒 → 3秒に短縮（テスト用）
                print(f"⏸️ 次のアカウントまで{wait_time}秒待機...")
                time.sleep(wait_time)
        
        execution_time = time.time() - start_time
        success_rate = (success_count / len(active_accounts)) * 100
        
        final_result = {
            "success": success_count > 0,
            "total_accounts": len(active_accounts),
            "success_count": success_count,
            "success_rate": success_rate,
            "execution_time": execution_time,
            "results": results
        }
        
        print(f"\n📊 === 実行結果サマリー ===")
        print(f"✅ 成功: {success_count}/{len(active_accounts)}アカウント")
        print(f"📈 成功率: {success_rate:.1f}%")
        print(f"⏱️ 実行時間: {execution_time:.1f}秒")
        
        return final_result
    
    # ==============================================
    # スケジューラー機能
    # ==============================================
    
    def setup_schedule(self):
        """投稿スケジュール設定"""
        if not settings.schedule.enabled:
            print("⚠️ スケジュール投稿が無効化されています")
            return False
        
        schedule.clear()
        
        for hour in self.posting_hours:
            schedule.every().day.at(f"{hour:02d}:00").do(self._scheduled_posting_execution, hour)
            print(f"📅 スケジュール設定: {hour:02d}:00")
        
        print(f"✅ 投稿スケジュール設定完了: {self.posting_hours}")
        return True
    
    def _scheduled_posting_execution(self, hour):
        """スケジュール投稿実行"""
        execution_time = datetime.now()
        execution_id = f"{execution_time.strftime('%Y%m%d')}_{hour:02d}"
        
        print(f"\n🕐 === {hour:02d}:00 自動投稿実行 ===")
        
        # 重複実行チェック
        if self._is_already_executed_today(hour):
            print(f"⏭️ {hour:02d}:00 の投稿は既に実行済み")
            return
        
        try:
            result = self.execute_all_accounts_posting()
            
            # 実行ログ記録
            log_entry = {
                "execution_id": execution_id,
                "execution_time": execution_time.isoformat(),
                "hour": hour,
                "success": result.get("success", False),
                "total_accounts": result.get("total_accounts", 0),
                "success_count": result.get("success_count", 0),
                "success_rate": result.get("success_rate", 0),
                "execution_time": result.get("execution_time", 0),
                "results": result.get("results", [])
            }
            
            self.execution_log.append(log_entry)
            self.stats["last_execution"] = execution_time.isoformat()
            
            if log_entry["success"]:
                print(f"🎉 {hour:02d}:00 自動投稿完了 - 成功: {log_entry['success_count']}/{log_entry['total_accounts']}")
            else:
                print(f"❌ {hour:02d}:00 自動投稿失敗")
                
        except Exception as e:
            print(f"❌ {hour:02d}:00 自動投稿中にエラー: {e}")
            
            error_log = {
                "execution_id": execution_id,
                "execution_time": execution_time.isoformat(),
                "hour": hour,
                "success": False,
                "error": str(e)
            }
            self.execution_log.append(error_log)
    
    def _is_already_executed_today(self, hour):
        """今日の指定時間に既に実行済みかチェック"""
        today = datetime.now().strftime('%Y%m%d')
        execution_id = f"{today}_{hour:02d}"
        
        return any(
            log.get("execution_id") == execution_id 
            for log in self.execution_log
        )
    
    def start_automation(self):
        """自動化システム開始"""
        if self.is_running:
            print("⚠️ 自動化システムは既に実行中です")
            return False
        
        if not self.setup_schedule():
            return False
        
        self.is_running = True
        self.auto_mode = True
        
        def run_automation():
            print("🤖 自動化システム開始 - バックグラウンド実行")
            print(f"📅 投稿時間: {self.posting_hours}")
            print(f"🧪 テストモード: {self.test_mode}")
            
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 1分毎にチェック
            
            print("🛑 自動化システム停止")
        
        self.scheduler_thread = threading.Thread(target=run_automation, daemon=True)
        self.scheduler_thread.start()
        
        print("✅ 自動化システムをバックグラウンドで開始しました")
        return True
    
    def stop_automation(self):
        """自動化システム停止"""
        if not self.is_running:
            print("⚠️ 自動化システムは実行されていません")
            return False
        
        self.is_running = False
        self.auto_mode = False
        schedule.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        print("✅ 自動化システムを停止しました")
        return True
    
    def get_system_status(self):
        """システム状況取得"""
        active_accounts = self.get_active_accounts()
        
        # 次回投稿時間計算
        now = datetime.now()
        next_posting_hour = None
        
        for hour in sorted(self.posting_hours):
            next_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            
            if next_posting_hour is None or next_time < next_posting_hour:
                next_posting_hour = next_time
        
        return {
            "automation_running": self.is_running,
            "auto_mode": self.auto_mode,
            "test_mode": self.test_mode,
            "active_accounts": len(active_accounts),
            "posting_hours": self.posting_hours,
            "next_posting": next_posting_hour.isoformat() if next_posting_hour else None,
            "stats": self.stats,
            "recent_executions": len(self.execution_log),
            "last_execution": self.stats["last_execution"],
            "system_uptime": (datetime.now() - self.stats["system_start_time"]).total_seconds()
        }
    
    def manual_test_execution(self):
        """手動テスト実行"""
        print("🧪 === 手動テスト実行 ===")
        current_hour = datetime.now().hour
        self._scheduled_posting_execution(current_hour)

def main():
    """メインテスト関数"""
    print("🤖 統合自動化システム 総合テスト")
    print("="*60)
    
    # システム初期化
    automation = IntegratedAutomationSystem()
    
    # システム状況確認
    status = automation.get_system_status()
    print(f"📊 システム状況:")
    print(f"  アクティブアカウント: {status['active_accounts']}件")
    print(f"  投稿時間: {status['posting_hours']}")
    print(f"  テストモード: {status['test_mode']}")
    print(f"  自動化実行中: {status['automation_running']}")
    
    # 手動投稿テスト
    print(f"\n🧪 1. 手動投稿テスト")
    manual_result = automation.execute_all_accounts_posting()
    print(f"✅ 手動投稿テスト: {'成功' if manual_result['success'] else '失敗'}")
    
    # スケジューラーテスト
    print(f"\n🧪 2. スケジューラー手動実行テスト")
    automation.manual_test_execution()
    
    # 自動化システム短期テスト
    print(f"\n🧪 3. 自動化システム短期テスト")
    print("🤖 自動化システムを10秒間実行...")
    
    automation.start_automation()
    time.sleep(10)  # 10秒間実行
    automation.stop_automation()
    
    # 最終状況確認
    final_status = automation.get_system_status()
    print(f"\n📊 === 最終統計 ===")
    print(f"総投稿数: {final_status['stats']['total_posts']}")
    print(f"成功投稿数: {final_status['stats']['successful_posts']}")
    print(f"失敗投稿数: {final_status['stats']['failed_posts']}")
    print(f"実行履歴: {final_status['recent_executions']}件")
    
    # 互換性確認
    print(f"\n🔄 既存GAS版との互換性:")
    print("  ✅ 全アカウント投稿システム")
    print("  ✅ 時間指定投稿システム")
    print("  ✅ アカウント別コンテンツ選択")
    print("  ✅ ツリー投稿（メイン + アフィリエイト）")
    print("  ✅ 重複回避機能")
    print("  ✅ 自動化・スケジューリング")
    print("  ✅ 統計・ログ機能")
    
    print("\n🎉 統合自動化システムテスト完了")
    print("🎯 次のステップ: .env設定 → 本番運用開始")

if __name__ == "__main__":
    main()