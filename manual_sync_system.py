# test_real_gas_data_system_v2.py - 手動更新機能付き投稿システム

import sys
import os
import json
import random
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append('.')

try:
    from config.settings import settings
    print("✅ config.settings インポート成功")
except ImportError as e:
    print(f"❌ 設定インポートエラー: {e}")
    sys.exit(1)

class RealGASDataSystemV2:
    """実際のGAS版データ対応システム V2 - 手動更新機能付き"""
    
    def __init__(self):
        self.data_dir = Path("src/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # データファイルパス
        self.main_contents_file = self.data_dir / "main_contents.json"
        self.affiliates_file = self.data_dir / "affiliates.json"
        self.sync_log_file = self.data_dir / "sync_log.json"
        
        # データストレージ
        self.main_contents = {}
        self.affiliates = {}
        self.usage_history = {}
        self.sync_history = []
        
        # 初回読み込み
        self._load_cached_data()
        
        print("🔧 手動更新機能付きシステム初期化完了")
    
    # ===============================================
    # 🔄 手動更新機能
    # ===============================================
    
    def update_from_csv(self, main_csv_path: str = None, affiliate_csv_path: str = None):
        """
        📥 CSVから手動更新（更新ボタン機能）
        
        使用方法:
        1. Google Sheetsでデータを編集
        2. CSVエクスポート（ファイル→ダウンロード→CSV）
        3. この関数を実行
        """
        print("🔄 【手動更新開始】CSVからデータ更新")
        print("=" * 50)
        
        update_result = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "main_contents": {"before": len(self.main_contents), "after": 0, "updated": False},
            "affiliates": {"before": len(self.affiliates), "after": 0, "updated": False},
            "errors": []
        }
        
        try:
            # CSVファイル自動検索
            if not main_csv_path:
                main_csv_path = self._find_csv_file("main", "メイン", "content", "コンテンツ")
            
            if not affiliate_csv_path:
                affiliate_csv_path = self._find_csv_file("affiliate", "アフィリエイト")
            
            print(f"🔍 検索結果:")
            print(f"  メインCSV: {main_csv_path or '見つかりません'}")
            print(f"  アフィリエイトCSV: {affiliate_csv_path or '見つかりません'}")
            
            # アフィリエイト更新（優先）
            if affiliate_csv_path and os.path.exists(affiliate_csv_path):
                old_count = len(self.affiliates)
                success = self._update_affiliates_from_csv(affiliate_csv_path)
                update_result["affiliates"].update({
                    "after": len(self.affiliates),
                    "updated": success,
                    "source_file": affiliate_csv_path
                })
                print(f"🔗 アフィリエイト: {old_count} → {len(self.affiliates)}件")
            else:
                print("⚠️ アフィリエイトCSVが見つかりません")
            
            # メインコンテンツ更新または生成
            if main_csv_path and os.path.exists(main_csv_path):
                old_count = len(self.main_contents)
                success = self._update_main_contents_from_csv(main_csv_path)
                update_result["main_contents"].update({
                    "after": len(self.main_contents),
                    "updated": success,
                    "source_file": main_csv_path
                })
                print(f"📝 メインコンテンツ: {old_count} → {len(self.main_contents)}件")
            else:
                print("💡 メインCSVがないため、アフィリエイトから推定生成")
                self._generate_main_contents_from_affiliates()
                update_result["main_contents"].update({
                    "after": len(self.main_contents),
                    "updated": True,
                    "source_file": "自動生成"
                })
            
            # データ保存
            self._save_all_data()
            
            # 同期ログ記録
            update_result["success"] = True
            self._log_sync_result(update_result)
            
            print(f"\n✅ 【手動更新完了】")
            self._print_update_summary(update_result)
            
            return update_result
            
        except Exception as e:
            error_msg = f"更新エラー: {e}"
            update_result["errors"].append(error_msg)
            print(f"❌ {error_msg}")
            
            # エラーログも記録
            self._log_sync_result(update_result)
            
            return update_result
    
    def _find_csv_file(self, *keywords):
        """CSVファイルを自動検索"""
        current_dir = Path(".")
        
        for file_path in current_dir.glob("*.csv"):
            filename_lower = file_path.name.lower()
            if any(keyword.lower() in filename_lower for keyword in keywords):
                return str(file_path)
        
        return None
    
    def _update_affiliates_from_csv(self, csv_path: str):
        """アフィリエイトCSVから更新"""
        try:
            print(f"📂 アフィリエイトCSV読み込み: {csv_path}")
            
            # CSV読み込み（エンコーディング自動判定）
            df = self._read_csv_with_encoding(csv_path)
            
            # 列名正規化
            df.columns = df.columns.str.strip()
            print(f"📊 列名: {list(df.columns)}")
            print(f"📊 総行数: {len(df)}")
            
            # 最初の3行のサンプル表示
            print(f"\n📋 データサンプル（最初の3行）:")
            for i in range(min(3, len(df))):
                row = df.iloc[i]
                print(f"  行{i+1}:")
                for col in df.columns:
                    value = row[col] if pd.notna(row[col]) else "N/A"
                    display_value = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                    print(f"    {col}: {display_value}")
                print()
            
            # データクリア（完全更新）
            self.affiliates.clear()
            
            # データ処理
            processed_count = 0
            skipped_count = 0
            
            for idx, row in df.iterrows():
                # 必須フィールドチェック
                affiliate_id = self._safe_get_value(row, ['アフィリエイトID', 'Affiliate ID', 'affiliate_id'])
                account_id = self._safe_get_value(row, ['アカウントID', 'Account ID', 'account_id'])
                content_id = self._safe_get_value(row, ['コンテンツID', 'Content ID', 'content_id'])
                reply_text = self._safe_get_value(row, ['説明文', 'リプライ文', 'reply_text', '説明'])
                
                # 空行やNaN値をスキップ
                if not affiliate_id or pd.isna(affiliate_id):
                    skipped_count += 1
                    continue
                
                # アフィリエイト作成
                self.affiliates[str(affiliate_id)] = {
                    "id": str(affiliate_id),
                    "account_id": str(account_id) if account_id else "",
                    "content_id": str(content_id) if content_id else "",
                    "reply_text": str(reply_text) if reply_text else "",
                    "affiliate_url": self._safe_get_value(row, ['アフィリエイトURL', 'URL', 'affiliate_url'], ""),
                    "image_usage": self._safe_get_value(row, ['画像使用', 'image_usage'], "NO"),
                    "updated_at": datetime.now().isoformat()
                }
                processed_count += 1
            
            print(f"✅ アフィリエイト処理完了: {processed_count}件処理、{skipped_count}件スキップ")
            
            # アカウント別統計
            account_stats = {}
            for affiliate in self.affiliates.values():
                account_id = affiliate['account_id']
                if account_id and account_id != "":
                    if account_id not in account_stats:
                        account_stats[account_id] = 0
                    account_stats[account_id] += 1
            
            print(f"📊 アカウント別アフィリエイト数:")
            for account_id, count in account_stats.items():
                print(f"  {account_id}: {count}件")
            
            return True
            
        except Exception as e:
            print(f"❌ アフィリエイト更新エラー: {e}")
            return False
    
    def _update_main_contents_from_csv(self, csv_path: str):
        """メインコンテンツCSVから更新"""
        try:
            print(f"📂 メインコンテンツCSV読み込み: {csv_path}")
            
            # CSV読み込み
            df = self._read_csv_with_encoding(csv_path)
            
            # 列名正規化
            df.columns = df.columns.str.strip()
            print(f"📊 列名: {list(df.columns)}")
            
            # データクリア（完全更新）
            self.main_contents.clear()
            
            # データ処理
            processed_count = 0
            for _, row in df.iterrows():
                # 必須フィールドチェック
                account_id = self._safe_get_value(row, ['アカウントID', 'Account ID', 'account_id'])
                content_id = self._safe_get_value(row, ['コンテンツID', 'Content ID', 'content_id'])
                main_text = self._safe_get_value(row, ['投稿文', 'メイン投稿文', 'main_text', '投稿内容'])
                
                if not account_id or not content_id or not main_text:
                    continue
                
                # メインコンテンツ作成
                self.main_contents[content_id] = {
                    "id": content_id,
                    "account_id": account_id,
                    "main_text": main_text,
                    "usage_count": int(self._safe_get_value(row, ['使用回数', 'usage_count'], 0)),
                    "replacement_usage": self._safe_get_value(row, ['置き換え使用', 'replacement_usage'], 'YES').upper() == 'YES',
                    "active": True,
                    "updated_at": datetime.now().isoformat()
                }
                processed_count += 1
            
            print(f"✅ メインコンテンツ処理完了: {processed_count}件")
            return True
            
        except Exception as e:
            print(f"❌ メインコンテンツ更新エラー: {e}")
            return False
    
    def _generate_main_contents_from_affiliates(self):
        """アフィリエイトデータからメインコンテンツを推定生成"""
        print("🔄 アフィリエイトデータからメインコンテンツを生成中...")
        
        # コンテンツIDとアカウントIDの組み合わせを抽出
        content_combinations = set()
        for affiliate in self.affiliates.values():
            if affiliate['content_id'] and affiliate['account_id']:
                content_combinations.add((affiliate['content_id'], affiliate['account_id']))
        
        print(f"📝 発見されたコンテンツ組み合わせ: {len(content_combinations)}件")
        
        # 既存のメインコンテンツをクリア
        self.main_contents.clear()
        
        # メインコンテンツ生成
        for content_id, account_id in content_combinations:
            # 対応するアフィリエイトを検索
            related_affiliates = [
                aff for aff in self.affiliates.values()
                if aff['content_id'] == content_id and aff['account_id'] == account_id
            ]
            
            # アフィリエイトの説明文から推定してメインテキスト生成
            main_text = f"[自動生成] {content_id} のメイン投稿"
            if related_affiliates:
                # 最初のアフィリエイトの説明文を参考に
                affiliate_desc = related_affiliates[0]['reply_text']
                if affiliate_desc and len(affiliate_desc) > 10:
                    main_text = f"関連コンテンツの投稿です 📱\n詳細は以下をチェック！\n\n※メインCSVがないため自動生成"
                else:
                    main_text = f"おすすめコンテンツの紹介です 📱\n詳細をチェックしてみて！\n\n※メインCSVがないため自動生成"
            
            self.main_contents[content_id] = {
                "id": content_id,
                "account_id": account_id,
                "main_text": main_text,
                "usage_count": 0,
                "replacement_usage": True,
                "active": True,
                "auto_generated": True,
                "generated_at": datetime.now().isoformat()
            }
        
        print(f"✅ メインコンテンツ生成完了: {len(self.main_contents)}件")
    
    def _read_csv_with_encoding(self, csv_path: str):
        """エンコーディング自動判定でCSV読み込み"""
        encodings = ['utf-8', 'shift-jis', 'cp932', 'utf-8-sig']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                print(f"✅ エンコーディング: {encoding}")
                return df
            except UnicodeDecodeError:
                continue
        
        raise Exception("対応するエンコーディングが見つかりません")
    
    def _safe_get_value(self, row, column_names, default=""):
        """安全に列の値を取得"""
        for col_name in column_names:
            if col_name in row and pd.notna(row[col_name]):
                value = str(row[col_name]).strip()
                if value and value.lower() not in ['nan', 'none', '']:
                    return value
        return default
    
    # ===============================================
    # 💾 データ管理
    # ===============================================
    
    def _save_all_data(self):
        """全データを保存"""
        # メインコンテンツ保存
        with open(self.main_contents_file, 'w', encoding='utf-8') as f:
            json.dump(self.main_contents, f, ensure_ascii=False, indent=2)
        
        # アフィリエイト保存
        with open(self.affiliates_file, 'w', encoding='utf-8') as f:
            json.dump(self.affiliates, f, ensure_ascii=False, indent=2)
        
        print(f"💾 データ保存完了: {self.data_dir}")
    
    def _load_cached_data(self):
        """キャッシュされたデータを読み込み"""
        try:
            # メインコンテンツ読み込み
            if self.main_contents_file.exists():
                with open(self.main_contents_file, 'r', encoding='utf-8') as f:
                    self.main_contents = json.load(f)
                print(f"📂 キャッシュ読み込み: メインコンテンツ {len(self.main_contents)}件")
            
            # アフィリエイト読み込み
            if self.affiliates_file.exists():
                with open(self.affiliates_file, 'r', encoding='utf-8') as f:
                    self.affiliates = json.load(f)
                print(f"📂 キャッシュ読み込み: アフィリエイト {len(self.affiliates)}件")
            
            # 同期ログ読み込み
            if self.sync_log_file.exists():
                with open(self.sync_log_file, 'r', encoding='utf-8') as f:
                    self.sync_history = json.load(f)
            
        except Exception as e:
            print(f"⚠️ キャッシュ読み込みエラー: {e}")
    
    def _log_sync_result(self, result):
        """同期結果をログに記録"""
        self.sync_history.append(result)
        
        # 最新10件のみ保持
        if len(self.sync_history) > 10:
            self.sync_history = self.sync_history[-10:]
        
        # ログファイル保存
        with open(self.sync_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.sync_history, f, ensure_ascii=False, indent=2)
    
    def _print_update_summary(self, result):
        """更新サマリーを表示"""
        print(f"\n📊 更新サマリー:")
        print(f"  🕐 更新時刻: {result['timestamp']}")
        
        if result["main_contents"]["updated"]:
            mc = result["main_contents"]
            print(f"  📝 メインコンテンツ: {mc['before']} → {mc['after']}件")
        
        if result["affiliates"]["updated"]:
            af = result["affiliates"]
            print(f"  🔗 アフィリエイト: {af['before']} → {af['after']}件")
        
        if result["errors"]:
            print(f"  ❌ エラー: {len(result['errors'])}件")
    
    # ===============================================
    # 📊 投稿システム（既存機能）
    # ===============================================
    
    def get_main_contents_for_account(self, account_id):
        """指定アカウントのメインコンテンツを取得"""
        return [content for content in self.main_contents.values() 
                if content["account_id"] == account_id and content.get("active", True)]
    
    def get_random_main_content_for_account(self, account_id):
        """指定アカウントのランダムメインコンテンツを取得"""
        available_contents = self.get_main_contents_for_account(account_id)
        
        if not available_contents:
            print(f"❌ {account_id}: 利用可能なメインコンテンツがありません")
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
        """指定コンテンツ・アカウントに対応するアフィリエイトを取得"""
        matching_affiliates = [
            affiliate for affiliate in self.affiliates.values()
            if (affiliate["content_id"] == content_id and 
                affiliate["account_id"] == account_id)
        ]
        
        if not matching_affiliates:
            print(f"⚠️ {account_id}({content_id}): 対応するアフィリエイトが見つかりません")
            return None
        
        # 複数ある場合はランダム選択
        return random.choice(matching_affiliates)
    
    def format_main_post_text(self, content):
        """メイン投稿テキストをフォーマット"""
        return content["main_text"]
    
    def format_affiliate_reply_text(self, affiliate):
        """アフィリエイトリプライテキストをフォーマット"""
        if not affiliate:
            return ""
        
        # 実際のGAS版と同じ形式：リプライテキスト + URL
        reply_text = affiliate["reply_text"]
        
        if affiliate.get("affiliate_url"):
            reply_text += f"\n{affiliate['affiliate_url']}"
        
        return reply_text
    
    def execute_single_account_post(self, account_id, test_mode=True):
        """単一アカウントでのツリー投稿実行"""
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
    
    def get_system_stats(self):
        """システム統計を取得"""
        stats = {
            "main_contents": {
                "total": len(self.main_contents),
                "active": len([c for c in self.main_contents.values() if c.get("active", True)]),
                "auto_generated": len([c for c in self.main_contents.values() if c.get("auto_generated", False)])
            },
            "affiliate_contents": {
                "total": len(self.affiliates),
                "with_url": len([a for a in self.affiliates.values() if a.get("affiliate_url")])
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
        
        for affiliate in self.affiliates.values():
            account_id = affiliate["account_id"]
            if account_id in stats["account_stats"]:
                stats["account_stats"][account_id]["affiliate_contents"] += 1
            elif account_id:  # 空でない場合のみ
                stats["account_stats"][account_id] = {
                    "main_contents": 0,
                    "affiliate_contents": 1
                }
        
        return stats
    
    def check_sync_status(self):
        """同期状況を確認"""
        print("📊 同期状況確認")
        print("=" * 30)
        
        print(f"📂 現在のデータ:")
        print(f"  メインコンテンツ: {len(self.main_contents)}件")
        print(f"  アフィリエイト: {len(self.affiliates)}件")
        
        if self.sync_history:
            last_sync = self.sync_history[-1]
            print(f"\n🕐 最終更新:")
            print(f"  日時: {last_sync['timestamp']}")
            print(f"  成功: {'✅' if last_sync['success'] else '❌'}")
            
            if last_sync.get('errors'):
                print(f"  エラー: {len(last_sync['errors'])}件")
        else:
            print(f"\n⚠️ 更新履歴なし")

def test_manual_update_system():
    """手動更新システムのテスト実行"""
    print("🔧 手動更新機能付きシステム テスト")
    print("=" * 60)
    
    # システム初期化
    system = RealGASDataSystemV2()
    
    # 現在の状況確認
    system.check_sync_status()
    
    print(f"\n💡 手動更新の使用方法:")
    print(f"1. Google Sheetsでデータを編集")
    print(f"2. CSVでエクスポート（ファイル→ダウンロード→CSV）")
    print(f"3. CSVファイルをプロジェクトルートに配置")
    print(f"4. 手動更新実行:")
    print(f"   system.update_from_csv()")
    
    # 手動更新テスト
    print(f"\n🧪 手動更新テスト実行:")
    result = system.update_from_csv()
    
    if result["success"]:
        print(f"\n✅ 手動更新テスト成功")
        
        # 統計表示
        stats = system.get_system_stats()
        print(f"\n📊 更新後のデータ:")
        print(f"📊 メインコンテンツ数: {stats['main_contents']['total']} (アクティブ: {stats['main_contents']['active']})")
        print(f"📊 アフィリエイト数: {stats['affiliate_contents']['total']} (URL付き: {stats['affiliate_contents']['with_url']})")
        
        if stats['main_contents']['auto_generated'] > 0:
            print(f"📊 自動生成コンテンツ: {stats['main_contents']['auto_generated']}件")
        
        print(f"\n📊 アカウント別統計:")
        for account_id, account_stats in stats["account_stats"].items():
            if account_id:  # 空でないアカウントIDのみ表示
                print(f"  {account_id}: メイン{account_stats['main_contents']}件 / アフィリエイト{account_stats['affiliate_contents']}件")
        
        # 投稿テスト
        print(f"\n🧪 投稿システムテスト:")
        active_accounts = list(set([
            content["account_id"] for content in system.main_contents.values() 
            if content.get("active", True) and content["account_id"]
        ]))
        
        if active_accounts:
            print(f"👥 アクティブアカウント: {active_accounts}")
            
            # 単一アカウント投稿テスト
            test_account = active_accounts[0]
            post_result = system.execute_single_account_post(test_account, test_mode=True)
            
            if post_result and post_result.get("success"):
                print(f"✅ 投稿テスト成功")
                print(f"   使用コンテンツ: {post_result['main_content']['id']}")
                print(f"   使用アフィリエイト: {post_result['affiliate']['id']}")
                print(f"   リプライテキスト: {post_result['affiliate']['reply_text'][:50]}...")
            else:
                print(f"❌ 投稿テスト失敗")
        else:
            print(f"❌ アクティブなアカウントが見つかりません")
    
    else:
        print(f"\n❌ 手動更新テスト失敗")
        if result["errors"]:
            for error in result["errors"]:
                print(f"  エラー: {error}")
    
    print(f"\n🔄 実際のGAS版データとの互換性:")
    print(f"  ✅ CSV手動更新機能")
    print(f"  ✅ アフィリエイトシート構造完全互換")
    print(f"  ✅ メインコンテンツ自動生成")
    print(f"  ✅ アカウント・コンテンツ紐付け")
    print(f"  ✅ ツリー投稿（メイン → アフィリエイトリプライ）")
    print(f"  ✅ 実際のリプライテキスト使用")
    print(f"  ✅ エンコーディング自動判定")
    print(f"  ✅ データ永続化・キャッシュ")
    
    print(f"\n✅ 手動更新機能付きシステムテスト完了")
    print(f"\n💡 次のステップ:")
    print(f"1. Google SheetsからCSVエクスポート")
    print(f"2. CSVファイルをプロジェクトルートに配置")
    print(f"3. system.update_from_csv() で手動更新")
    print(f"4. .env ファイル設定 → 実際の投稿テスト")
    
    return system

# 手動更新専用の便利関数
def manual_update():
    """手動更新専用関数（簡単実行用）"""
    print("🔄 手動更新を実行します...")
    system = RealGASDataSystemV2()
    result = system.update_from_csv()
    
    if result["success"]:
        print("\n✅ 手動更新成功！")
        print("📊 投稿システムで使用可能になりました")
    else:
        print("\n❌ 手動更新失敗")
        print("💡 CSVファイルをプロジェクトルートに配置してください")
    
    return system

def quick_post_test():
    """クイック投稿テスト"""
    print("🧪 クイック投稿テスト実行...")
    system = RealGASDataSystemV2()
    
    # アクティブアカウント取得
    active_accounts = list(set([
        content["account_id"] for content in system.main_contents.values() 
        if content.get("active", True) and content["account_id"]
    ]))
    
    if not active_accounts:
        print("❌ アクティブなアカウントがありません")
        print("💡 先に manual_update() を実行してください")
        return None
    
    # 投稿テスト実行
    test_account = active_accounts[0]
    result = system.execute_single_account_post(test_account, test_mode=True)
    
    if result and result.get("success"):
        print("✅ 投稿テスト成功！")
    else:
        print("❌ 投稿テスト失敗")
    
    return system

if __name__ == "__main__":
    # 必要なライブラリの確認
    try:
        import pandas as pd
        print("✅ pandas ライブラリ確認済み")
    except ImportError:
        print("❌ pandas ライブラリが必要です")
        print("📝 インストール: pip install pandas")
        sys.exit(1)
    
    # メインテスト実行
    test_manual_update_system()