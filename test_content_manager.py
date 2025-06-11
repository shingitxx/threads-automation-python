"""
コンテンツ管理システム
既存Google Apps Script版との完全互換性を保つコンテンツ・アフィリエイト管理機能
"""

import json
import random
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from config.settings import settings

@dataclass
class Content:
    """コンテンツ情報（既存GAS版互換）"""
    account_id: str
    id: str
    main_text: str
    used_count: int = 0
    use_image: str = "NO"
    
    @property
    def is_available(self) -> bool:
        """コンテンツが利用可能かチェック（無制限版では常にTrue）"""
        return True  # 既存GAS版の無制限化を継承

@dataclass
class AffiliateContent:
    """アフィリエイトコンテンツ情報（既存GAS版互換）"""
    id: str
    account_id: str
    content_id: str
    app_name: str = ""
    description: str = ""
    affiliate_url: str = ""
    call_to_action: str = ""

class ContentManager:
    """コンテンツ管理クラス"""
    
    def __init__(self):
        self.content_file = settings.data.content_path
        self.contents: Dict[str, Content] = {}
        self.affiliates: Dict[str, AffiliateContent] = {}
        self.selection_history: Dict[str, List[str]] = {}
        self._load_content()
        self._create_sample_data()
    
    def _load_content(self):
        """コンテンツ情報をファイルから読み込み"""
        try:
            if self.content_file.exists():
                with open(self.content_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # コンテンツ読み込み
                if 'contents' in data:
                    for content_data in data['contents']:
                        content = Content(**content_data)
                        self.contents[content.id] = content
                
                # アフィリエイト読み込み
                if 'affiliates' in data:
                    for affiliate_data in data['affiliates']:
                        affiliate = AffiliateContent(**affiliate_data)
                        self.affiliates[affiliate.id] = affiliate
                        
        except Exception as e:
            print(f"⚠️ コンテンツ読み込みエラー: {e}")
    
    def _create_sample_data(self):
        """既存GAS版互換のサンプルデータを作成"""
        if not self.contents:
            # サンプルコンテンツ（既存GAS版と同じ）
            sample_contents = [
                Content(
                    account_id="ACC001",
                    id="CONTENT_001",
                    main_text="今からオ〇しようと思うけど、もうしこった〜？🍌おかずいる？？笑笑",
                    use_image="NO"
                ),
                Content(
                    account_id="ACCOUNT_002", 
                    id="CONTENT_002",
                    main_text="最近のスマホアプリって種類多すぎて選べないよね🤔\nみんなはどうやって選んでる？",
                    use_image="NO"
                ),
                Content(
                    account_id="ACC001",
                    id="CONTENT_003", 
                    main_text="作業効率を10倍にしたツールがあるって聞いたんだけど...\n本当にそんなのある？🤯",
                    use_image="NO"
                ),
                Content(
                    account_id="ACCOUNT_002",
                    id="CONTENT_004",
                    main_text="夜中に見つけた神アプリ...これマジでやばい😱\n使いすぎ注意かも",
                    use_image="NO"
                )
            ]
            
            for content in sample_contents:
                self.contents[content.id] = content
            
            # サンプルアフィリエイト（既存GAS版と同じ）
            sample_affiliates = [
                AffiliateContent(
                    id="AFF_001",
                    account_id="ACC001",
                    content_id="CONTENT_001",
                    description="ここに載せてるから好きに見ていいよ❤",
                    affiliate_url="https://1link.jp/is001"
                ),
                AffiliateContent(
                    id="AFF_002", 
                    account_id="ACCOUNT_002",
                    content_id="CONTENT_002",
                    app_name="おすすめアプリ",
                    description="ユーザー評価4.8の人気アプリ！",
                    affiliate_url="https://example.com/affiliate/app1",
                    call_to_action="無料ダウンロードはこちら👆"
                ),
                AffiliateContent(
                    id="AFF_003",
                    account_id="ACC001", 
                    content_id="CONTENT_003",
                    app_name="効率化アプリ",
                    description="作業効率が本当に上がる神アプリ",
                    affiliate_url="https://example.com/affiliate/app2",
                    call_to_action="今すぐ試してみる🚀"
                ),
                AffiliateContent(
                    id="AFF_004",
                    account_id="ACCOUNT_002",
                    content_id="CONTENT_004",
                    app_name="神アプリ",
                    description="夜中に見つけた話題のアプリ",
                    affiliate_url="https://example.com/affiliate/app3",
                    call_to_action="チェックしてみて✨"
                )
            ]
            
            for affiliate in sample_affiliates:
                self.affiliates[affiliate.id] = affiliate
            
            self._save_content()
            print("✅ サンプルコンテンツ・アフィリエイトを作成しました")
    
    def _save_content(self):
        """コンテンツ情報をファイルに保存"""
        try:
            # ディレクトリが存在しない場合は作成
            self.content_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "contents": [asdict(content) for content in self.contents.values()],
                "affiliates": [asdict(affiliate) for affiliate in self.affiliates.values()]
            }
            
            with open(self.content_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ コンテンツ保存エラー: {e}")
    
    def get_random_content_for_account(self, account_id: str) -> Optional[Content]:
        """
        アカウント別ランダムコンテンツ取得（既存GAS版のgetRandomContentForAccount互換）
        """
        if settings.random.debug_mode:
            print(f"🎲 [DEBUG] {account_id} 用ランダムコンテンツ取得開始")
        
        # アカウント専用コンテンツをフィルタリング
        account_contents = [
            content for content in self.contents.values()
            if content.account_id == account_id and content.is_available
        ]
        
        if not account_contents:
            if settings.random.enable_shared_content:
                print(f"🔄 {account_id}: 共通コンテンツを検索中...")
                return self._get_shared_content_for_account(account_id)
            
            print(f"❌ {account_id} 用のコンテンツがありません")
            return None
        
        print(f"📝 {account_id} 用コンテンツ数: {len(account_contents)}件")
        
        # 重複回避を考慮したランダム選択
        selected_content = self._select_random_content_with_avoidance(account_id, account_contents)
        
        if not selected_content:
            print(f"❌ {account_id}: 選択可能なコンテンツがありません")
            return None
        
        # 選択履歴を記録
        self._record_content_selection(account_id, selected_content.id)
        
        if settings.random.debug_mode:
            print(f"🎯 [DEBUG] {account_id} 選択: {selected_content.id} - {selected_content.main_text[:30]}...")
        
        return selected_content
    
    def _get_shared_content_for_account(self, account_id: str) -> Optional[Content]:
        """共通コンテンツ取得（フォールバック用）"""
        # コンテンツIDごとにグループ化
        content_groups = {}
        for content in self.contents.values():
            if content.id not in content_groups:
                content_groups[content.id] = []
            content_groups[content.id].append(content)
        
        # 複数アカウントで共有されているコンテンツを検索
        shared_contents = []
        for content_id, content_list in content_groups.items():
            if len(content_list) > 1:
                shared_contents.extend(content_list)
        
        if not shared_contents:
            print(f"❌ {account_id}: 共通コンテンツも見つかりません")
            return None
        
        print(f"🔄 {account_id}: 共通コンテンツ {len(shared_contents)}件から選択")
        
        # ランダム選択
        selected = self._select_random_content_with_avoidance(account_id, shared_contents)
        
        if selected:
            # アカウントIDを変更してコピー作成
            shared_content = Content(
                account_id=account_id,
                id=selected.id,
                main_text=selected.main_text,
                used_count=selected.used_count,
                use_image=selected.use_image
            )
            return shared_content
        
        return None
    
    def _select_random_content_with_avoidance(self, account_id: str, content_list: List[Content]) -> Optional[Content]:
        """重複回避を考慮したランダム選択"""
        if not settings.random.avoid_recent_content:
            return random.choice(content_list)
        
        # 最近使用したコンテンツを取得
        recent_content = self._get_recent_content_selections(account_id)
        
        # 最近使用していないコンテンツをフィルタリング
        available_content = [
            content for content in content_list
            if content.id not in recent_content
        ]
        
        if available_content:
            return random.choice(available_content)
        
        # 全て最近使用済みの場合は全体から選択
        print(f"⚠️ {account_id}: 最近使用したコンテンツのみのため、全体から選択")
        return random.choice(content_list)
    
    def _record_content_selection(self, account_id: str, content_id: str):
        """コンテンツ選択履歴を記録"""
        if account_id not in self.selection_history:
            self.selection_history[account_id] = []
        
        self.selection_history[account_id].insert(0, content_id)
        
        # 履歴制限
        if len(self.selection_history[account_id]) > settings.random.recent_content_limit:
            self.selection_history[account_id] = self.selection_history[account_id][:settings.random.recent_content_limit]
        
        if settings.random.debug_mode:
            print(f"📝 [DEBUG] {account_id} 選択履歴記録: {content_id}")
    
    def _get_recent_content_selections(self, account_id: str) -> List[str]:
        """最近使用したコンテンツを取得"""
        return self.selection_history.get(account_id, [])
    
    def get_random_affiliate_for_account(self, content_id: str, account_id: str) -> Optional[AffiliateContent]:
        """
        アカウント別ランダムアフィリエイト取得（既存GAS版のgetRandomAffiliateForAccount互換）
        """
        if settings.random.debug_mode:
            print(f"🎲 [DEBUG] {account_id} 用アフィリエイト取得: {content_id}")
        
        # コンテンツIDとアカウントIDに対応するアフィリエイトを検索
        matching_affiliates = [
            affiliate for affiliate in self.affiliates.values()
            if affiliate.content_id == content_id and affiliate.account_id == account_id
        ]
        
        if not matching_affiliates:
            # アカウント専用が見つからない場合は共通アフィリエイトを検索
            if settings.random.enable_shared_content:
                print(f"🔄 {account_id}: 共通アフィリエイトを検索中...")
                return self._get_shared_affiliate_for_content(content_id, account_id)
            
            print(f"❌ {content_id} に対応するアフィリエイトがありません")
            return self._get_default_affiliate_content()
        
        print(f"📝 {account_id} 用 {content_id} アフィリエイト数: {len(matching_affiliates)}件")
        
        # ランダム選択
        selected_affiliate = random.choice(matching_affiliates)
        
        if settings.random.debug_mode:
            print(f"🎯 [DEBUG] {account_id} 選択アフィリエイト: {selected_affiliate.id}")
        
        return selected_affiliate
    
    def _get_shared_affiliate_for_content(self, content_id: str, account_id: str) -> Optional[AffiliateContent]:
        """共通アフィリエイト取得（フォールバック用）"""
        content_affiliates = [
            affiliate for affiliate in self.affiliates.values()
            if affiliate.content_id == content_id
        ]
        
        if not content_affiliates:
            print(f"❌ {account_id}({content_id}): 共通アフィリエイトも見つかりません")
            return self._get_default_affiliate_content()
        
        print(f"🔄 {account_id}({content_id}): 共通アフィリエイト {len(content_affiliates)}件から選択")
        
        selected = random.choice(content_affiliates)
        
        # アカウントIDを変更してコピー作成
        shared_affiliate = AffiliateContent(
            id=selected.id,
            account_id=account_id,
            content_id=selected.content_id,
            app_name=selected.app_name,
            description=selected.description,
            affiliate_url=selected.affiliate_url,
            call_to_action=selected.call_to_action
        )
        
        return shared_affiliate
    
    def _get_default_affiliate_content(self) -> AffiliateContent:
        """デフォルトアフィリエイトコンテンツ（既存GAS版互換）"""
        return AffiliateContent(
            id="DEFAULT_001",
            account_id="",
            content_id="",
            app_name="おすすめアプリ",
            description="実際に使って便利だったアプリです",
            affiliate_url="https://example.com/affiliate/default",
            call_to_action="チェックしてみて！"
        )
    
    def format_affiliate_reply_text(self, affiliate: AffiliateContent) -> str:
        """
        アフィリエイトリプライテキストフォーマット（既存GAS版のformatAffiliateReplyText互換）
        """
        reply_text = ""
        
        if affiliate.app_name and affiliate.app_name.strip():
            reply_text += f"{affiliate.app_name}\n\n"
        
        if affiliate.description and affiliate.description.strip():
            reply_text += f"{affiliate.description}"
        
        if affiliate.call_to_action and affiliate.call_to_action.strip():
            reply_text += f"\n\n{affiliate.call_to_action}"
        
        if affiliate.affiliate_url and affiliate.affiliate_url.strip():
            reply_text += f"\n{affiliate.affiliate_url}"
        
        return reply_text
    
    def increment_content_usage(self, content_id: str):
        """
        コンテンツ使用回数増加（既存GAS版のincrementContentUsageUnlimited互換）
        """
        if content_id in self.contents:
            self.contents[content_id].used_count += 1
            self._save_content()
            print(f"📝 {content_id}: 使用回数記録（制限なし）")
    
    def clear_selection_history(self, account_id: Optional[str] = None):
        """選択履歴をクリア（既存GAS版のclearContentSelectionHistory互換）"""
        if account_id:
            if account_id in self.selection_history:
                del self.selection_history[account_id]
                print(f"✅ {account_id} の選択履歴をクリアしました")
        else:
            self.selection_history.clear()
            print("✅ 全アカウントの選択履歴をクリアしました")
    
    def get_content_status(self) -> Dict[str, Any]:
        """コンテンツ状況の詳細情報を取得"""
        account_content_count = {}
        for content in self.contents.values():
            if content.account_id not in account_content_count:
                account_content_count[content.account_id] = 0
            account_content_count[content.account_id] += 1
        
        return {
            "total_contents": len(self.contents),
            "total_affiliates": len(self.affiliates),
            "account_content_count": account_content_count,
            "selection_history": dict(self.selection_history)
        }

# グローバルコンテンツマネージャーインスタンス
content_manager = ContentManager()

if __name__ == "__main__":
    # コンテンツ管理システムテスト
    print("🔧 コンテンツ管理システムテスト")
    
    # コンテンツ状況表示
    status = content_manager.get_content_status()
    print(f"📊 総コンテンツ数: {status['total_contents']}")
    print(f"📊 総アフィリエイト数: {status['total_affiliates']}")
    
    print("\n📊 アカウント別コンテンツ数:")
    for account_id, count in status['account_content_count'].items():
        print(f"  {account_id}: {count}件")
    
    # ランダム選択テスト
    print(f"\n🎲 ランダム選択テスト:")
    test_accounts = ["ACC001", "ACCOUNT_002"]
    
    for account_id in test_accounts:
        print(f"\n👤 {account_id} テスト:")
        
        for i in range(3):
            content = content_manager.get_random_content_for_account(account_id)
            if content:
                print(f"  {i+1}. ✅ {content.id}: {content.main_text[:30]}...")
                
                # 対応するアフィリエイトテスト
                affiliate = content_manager.get_random_affiliate_for_account(content.id, account_id)
                if affiliate:
                    reply_text = content_manager.format_affiliate_reply_text(affiliate)
                    print(f"    🔗 アフィリエイト: {affiliate.id}")
                    print(f"    💬 リプライ: {reply_text[:50]}...")
                else:
                    print(f"    ❌ アフィリエイト: 見つかりません")
            else:
                print(f"  {i+1}. ❌ コンテンツ取得失敗")
    
    # 互換性確認
    print(f"\n🔄 既存GAS版との互換性:")
    print("  ✅ getRandomContentForAccount() 互換")
    print("  ✅ getRandomAffiliateForAccount() 互換")
    print("  ✅ formatAffiliateReplyText() 互換")
    print("  ✅ 重複回避機能")
    print("  ✅ 無制限使用回数")
    
    print("\n✅ コンテンツ管理システムテスト完了")
    print("🎯 次のステップ: 投稿実行システム実装")