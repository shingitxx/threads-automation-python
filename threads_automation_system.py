"""
Threads自動投稿システム
新しいフォルダ構造に対応した自動投稿機能を提供
"""
import os
import sys
import time
import json
import random
import traceback
import subprocess
import chardet  # 文字エンコーディング検出用
from datetime import datetime
from subprocess import DEVNULL
from typing import Dict, List, Optional, Any

from threads_account_manager import ThreadsAccountManager
from threads_cloudinary_manager import ThreadsCloudinaryManager
from threads_direct_post import ThreadsDirectPost

# ロガー設定
import logging
class EncodingStreamHandler(logging.StreamHandler):
    """エンコーディング問題に対応したストリームハンドラ"""
    def __init__(self, stream=None):
        super().__init__(stream)
    
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            
            # 絵文字をテキストに置換（より広範囲に対応）
            msg = msg.replace('\u2705', '[成功]').replace('\u274c', '[失敗]')
            msg = msg.replace('✅', '[成功]').replace('❌', '[失敗]')
            
            try:
                stream.write(msg + self.terminator)
            except UnicodeEncodeError:
                # それでも失敗する場合は安全なASCII文字のみに
                safe_msg = ''.join(c if ord(c) < 128 else '?' for c in msg)
                stream.write(safe_msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# ロガーの設定
def setup_logger():
    """ロガーを設定"""
    logger = logging.getLogger('threads-automation')
    logger.setLevel(logging.INFO)
    
    # ファイルハンドラ
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"automation_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # コンソールハンドラ（エンコーディング対応）
    console_handler = EncodingStreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # フォーマッタ
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # ハンドラをロガーに追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# ロガーの初期化
logger = setup_logger()

class ThreadsAutomationSystem:
    """Threads自動投稿システム"""
    
    def __init__(self):
        """初期化"""
        print("🚀 Python版Threads自動投稿システム起動中...")
        logger.info("Python版Threads自動投稿システム起動中...")
        
        # 各マネージャークラスの初期化
        self.account_manager = ThreadsAccountManager()
        self.cloudinary_manager = ThreadsCloudinaryManager()
        self.direct_post = ThreadsDirectPost()
        
        print("🎉 システム初期化完了")
        logger.info("システム初期化完了")
        print(f"📊 利用可能アカウント: {len(self.account_manager.get_account_ids())}件")
        logger.info(f"利用可能アカウント: {len(self.account_manager.get_account_ids())}件")
    
    def single_post(self, account_id=None, test_mode=False, content_id=None):
        """単発投稿実行（完全自動判定版）"""
        print("\n🎯 === 単発投稿実行（完全自動判定版） ===")
        logger.info("単発投稿実行（完全自動判定版）開始")
        
        if not account_id:
            # アカウント選択
            accounts = self.account_manager.get_account_ids()
            if not accounts:
                print("❌ 利用可能なアカウントがありません")
                logger.error("利用可能なアカウントがありません")
                return False
            account_id = accounts[0]
        
        print(f"👤 アカウント: {account_id}")
        logger.info(f"選択アカウント: {account_id}")
        
        try:
            # コンテンツ選択（指定されていない場合はランダム）
            if not content_id:
                content = self.account_manager.get_random_content(account_id)
                if not content:
                    print(f"❌ {account_id}: コンテンツの取得に失敗しました")
                    logger.error(f"{account_id}: コンテンツの取得に失敗")
                    return False
                content_id = content.get('id')
            else:
                content = self.account_manager.get_content(account_id, content_id)
                if not content:
                    print(f"❌ {account_id}: コンテンツ {content_id} が見つかりません")
                    logger.error(f"{account_id}: コンテンツ {content_id} が見つかりません")
                    return False
            
            print(f"📝 選択されたコンテンツ: {content_id}")
            logger.info(f"選択コンテンツ: {content_id}")
            
            # テストモードの場合
            if test_mode:
                # コンテンツ情報を表示
                print("\n🧪 テストモード: 実際には投稿されません")
                logger.info("テストモード: 実際には投稿されません")
                print(f"📄 メインテキスト:")
                print(content.get('main_text', '')[:200] + "..." if len(content.get('main_text', '')) > 200 else content.get('main_text', ''))
                
                # 画像情報を表示
                images = content.get('images', [])
                post_type = "carousel" if len(images) > 1 else ("image" if images else "text")
                print(f"📊 投稿タイプ: {post_type}")
                logger.info(f"投稿タイプ: {post_type}")
                
                if images:
                    print(f"🖼️ 画像数: {len(images)}枚")
                    logger.info(f"画像数: {len(images)}枚")
                    for i, image in enumerate(images, 1):
                        print(f"  画像{i}: {image.get('path')}")
                
                # アフィリエイト情報
                if "affiliate_text" in content:
                    print("\n🔗 アフィリエイトテキスト:")
                    print(content.get('affiliate_text', '')[:200] + "..." if len(content.get('affiliate_text', '')) > 200 else content.get('affiliate_text', ''))
                    logger.info("アフィリエイトテキスト: あり")
                else:
                    logger.info("アフィリエイトテキスト: なし")
                
                print("\n✅ テストモード投稿シミュレーション完了")
                logger.info("テストモード投稿シミュレーション完了")
                
                return {
                    "success": True,
                    "test_mode": True,
                    "content_id": content_id,
                    "post_type": post_type,
                    "account_id": account_id
                }
            
            # 実際の投稿
            print("\n📤 === 実際の投稿実行 ===")
            logger.info(f"{account_id}: 実際の投稿実行開始")
            result = self.direct_post.post_with_affiliate(account_id, content_id)
            
            if result and result.get("success"):
                print(f"🎉 {account_id}: 投稿完了")
                logger.info(f"{account_id}: 投稿完了 - {result}")
                return result
            else:
                print(f"❌ {account_id}: 投稿に失敗しました")
                logger.error(f"{account_id}: 投稿失敗 - {result}")
                return False
                
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            logger.error(f"投稿エラー: {e}", exc_info=True)
            traceback.print_exc()
            return False
    
    def all_accounts_post(self, test_mode=False):
        """全アカウント投稿実行"""
        print("\n🚀 === 全アカウント投稿実行 ===")
        logger.info(f"全アカウント投稿実行開始 (テストモード: {test_mode})")
        
        accounts = self.account_manager.get_account_ids()
        if not accounts:
            print("❌ 利用可能なアカウントがありません")
            logger.error("利用可能なアカウントがありません")
            return {"success": 0, "failed": 0, "accounts": []}
        
        results = {"success": 0, "failed": 0, "accounts": []}
        total_accounts = len(accounts)
        logger.info(f"投稿対象アカウント数: {total_accounts}件")
        
        for i, account_id in enumerate(accounts, 1):
            try:
                print(f"🔄 [{i}/{total_accounts}] {account_id} 投稿開始")
                logger.info(f"[{i}/{total_accounts}] {account_id} 投稿開始")
                
                result = self.single_post(
                    account_id=account_id,
                    test_mode=test_mode
                )
                
                if result and (result is True or (isinstance(result, dict) and result.get("success"))):
                    results["success"] += 1
                    results["accounts"].append({
                        "account_id": account_id,
                        "status": "success",
                        "details": result if isinstance(result, dict) else {}
                    })
                    print(f"✅ {account_id}: 投稿成功")
                    logger.info(f"{account_id}: 投稿成功")
                else:
                    results["failed"] += 1
                    results["accounts"].append({
                        "account_id": account_id,
                        "status": "failed",
                        "error": str(result) if result else "Unknown error"
                    })
                    print(f"❌ {account_id}: 投稿失敗")
                    logger.error(f"{account_id}: 投稿失敗 - {result}")
                
                # アカウント間の間隔（本番環境では適切な間隔を設定）
                if i < total_accounts:
                    interval = 10  # 秒
                    print(f"⏸️ 次のアカウントまで{interval}秒待機...")
                    logger.info(f"次のアカウントまで{interval}秒待機")
                    time.sleep(interval)
                    
            except Exception as e:
                results["failed"] += 1
                results["accounts"].append({
                    "account_id": account_id,
                    "status": "failed",
                    "error": str(e)
                })
                print(f"❌ {account_id} エラー: {e}")
                logger.error(f"{account_id} エラー: {e}", exc_info=True)
        
        # 結果サマリー
        success_rate = (results["success"] / total_accounts) * 100 if total_accounts > 0 else 0
        print(f"\n📊 === 全アカウント投稿結果 ===")
        print(f"✅ 成功: {results['success']}/{total_accounts}")
        print(f"❌ 失敗: {results['failed']}/{total_accounts}")
        print(f"📈 成功率: {success_rate:.1f}%")
        logger.info(f"全アカウント投稿完了 - 成功: {results['success']}/{total_accounts}, 失敗: {results['failed']}/{total_accounts}, 成功率: {success_rate:.1f}%")
        
        return results
    
    def system_status(self):
        """システム状況確認"""
        print("\n📊 === システム状況 ===")
        logger.info("システム状況確認実行")
        
        # 基本情報
        print(f"📁 プロジェクトルート: {os.getcwd()}")
        print(f"🐍 Python版本: {sys.version.split()[0]}")
        print(f"⏰ 現在時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # アカウント状況
        accounts = self.account_manager.get_account_ids()
        print(f"\n👥 アカウント状況:")
        print(f"  アカウント数: {len(accounts)}件")
        logger.info(f"アカウント数: {len(accounts)}件")
        
        # 各アカウントのコンテンツ数を表示
        for account_id in accounts[:5]:  # 最初の5つのみ表示
            content_ids = self.account_manager.get_account_content_ids(account_id)
            print(f"  {account_id}: {len(content_ids)}件のコンテンツ")
        
        if len(accounts) > 5:
            print(f"  ... 他{len(accounts) - 5}件のアカウント")
        
        # Cloudinary接続テスト
        try:
            cloud_test = self.cloudinary_manager.test_connection()
            if cloud_test:
                print(f"\n☁️ Cloudinary接続: ✅ 成功")
                logger.info("Cloudinary接続: 成功")
            else:
                print(f"\n☁️ Cloudinary接続: ❌ 失敗")
                logger.warning("Cloudinary接続: 失敗")
        except Exception as e:
            print(f"\n☁️ Cloudinary接続: ❌ エラー ({str(e)[:100]}...)")
            logger.error(f"Cloudinary接続エラー: {e}", exc_info=True)
        
        # フォルダ構造の確認
        print(f"\n📂 フォルダ構造:")
        accounts_dir = "accounts"
        if os.path.exists(accounts_dir):
            account_count = len([d for d in os.listdir(accounts_dir) if os.path.isdir(os.path.join(accounts_dir, d)) and not d.startswith("_")])
            print(f"  アカウントディレクトリ数: {account_count}件")
            
            # キャッシュディレクトリの確認
            cache_dir = os.path.join(accounts_dir, "_cache")
            if os.path.exists(cache_dir):
                cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
                print(f"  キャッシュファイル数: {len(cache_files)}件")
                logger.info(f"キャッシュファイル数: {len(cache_files)}件")
        else:
            print(f"  ❌ {accounts_dir}ディレクトリが見つかりません")
            logger.warning(f"{accounts_dir}ディレクトリが見つかりません")
        
        print("\n✅ システム状況確認完了")
        logger.info("システム状況確認完了")
    
    def run_scheduler(self):
        """スケジューラーを起動"""
        print("\n⏰ === スケジューラー起動 ===")
        logger.info("スケジューラー起動開始")
        
        try:
            # 状態ファイルの保存先を明示的に指定
            log_dir = os.path.join(os.getcwd(), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            status_file = os.path.join(log_dir, 'scheduler_status.json')
            
            # 既存の状態ファイルを削除
            if os.path.exists(status_file):
                try:
                    os.remove(status_file)
                    logger.info("古い状態ファイルを削除しました")
                except Exception as e:
                    logger.error(f"状態ファイル削除エラー: {e}")
            
            print("🚀 スケジューラーをバックグラウンドで起動します...")
            
            # Windowsの場合
            if os.name == 'nt':
                # バッチファイルを使用してスケジューラーを起動
                batch_content = '@echo off\n'
                batch_content += f'cd "{os.getcwd()}"\n'  # 作業ディレクトリを明示的に設定
                batch_content += f'python threads_scheduler_system.py > "{os.path.join(log_dir, "scheduler_output.log")}" 2>&1\n'
                
                # 一時的なバッチファイルを作成
                batch_file = os.path.join(os.getcwd(), 'run_scheduler.bat')
                with open(batch_file, 'w') as f:
                    f.write(batch_content)
                
                # バッチファイルを実行
                process = subprocess.Popen([batch_file], shell=True)
                pid = process.pid
                
                # 状態ファイルを直接作成
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'status': 'running',
                        'start_time': datetime.now().isoformat(),
                        'posting_hours': [2, 5, 8, 12, 17, 20, 22, 0],
                        'pid': pid
                    }, f, ensure_ascii=False)
                
                # 少し待機してプロセスが起動するのを待つ
                print("スケジューラー起動中...")
                time.sleep(2)
                
                print(f"✅ スケジューラーが起動しました (PID: {pid})")
                print("スケジューラーはバックグラウンドで実行されています")
                print("詳細はlogs/scheduler_*.logファイルを確認してください")
                logger.info(f"スケジューラーが正常に起動しました (PID: {pid})")
            
            else:
                # Linuxの場合
                # ここにLinux用の起動コードを記述
                process = subprocess.Popen(['nohup', 'python', 'threads_scheduler_system.py', '&'],
                                         shell=True, 
                                         stdout=open(os.path.join(log_dir, 'scheduler_output.log'), 'w'),
                                         stderr=subprocess.STDOUT,
                                         preexec_fn=os.setpgrp)
                
                pid = process.pid
                
                # 状態ファイルを直接作成
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'status': 'running',
                        'start_time': datetime.now().isoformat(),
                        'posting_hours': [2, 5, 8, 12, 17, 20, 22, 0],
                        'pid': pid
                    }, f, ensure_ascii=False)
                
                print(f"✅ スケジューラーが起動しました (PID: {pid})")
                print("スケジューラーはバックグラウンドで実行されています")
                print("詳細はlogs/scheduler_*.logファイルを確認してください")
                logger.info(f"スケジューラーが正常に起動しました (PID: {pid})")
                
        except Exception as e:
            print(f"❌ スケジューラー起動エラー: {e}")
            logger.error(f"スケジューラー起動エラー: {e}", exc_info=True)
            traceback.print_exc()

    def scheduler_status(self):
        """スケジューラーの状態確認"""
        print("\n⏰ === スケジューラー状態確認 ===")
        logger.info("スケジューラー状態確認開始")
        
        try:
            # 状態ファイルを確認
            status_file = os.path.join(os.getcwd(), 'logs', 'scheduler_status.json')
            
            if not os.path.exists(status_file):
                print("📊 === スケジューラー状況 ===")
                print("⚙️ ステータス: 停止中")
                print(f"⏰ 投稿時間: 02:00, 05:00, 08:00, 12:00, 17:00, 20:00, 22:00, 00:00")
                
                # アカウント情報
                accounts = self.account_manager.get_account_ids()
                print(f"👥 投稿対象アカウント: {len(accounts)}件")
                
                logger.info("スケジューラー状態確認完了: 状態ファイルがありません")
                return
                
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                
                status = status_data.get('status', '不明')
                pid = status_data.get('pid')
                start_time = None
                
                if 'start_time' in status_data:
                    try:
                        start_time = datetime.fromisoformat(status_data['start_time'])
                    except Exception:
                        pass
                        
                print("📊 === スケジューラー状況 ===")
                
                # プロセスが実際に存在するか確認
                process_running = False
                if pid:
                    try:
                        import psutil
                        process_running = psutil.pid_exists(pid)
                    except ImportError:
                        # psutilがない場合はプロセス確認をスキップ
                        process_running = True
                
                # 状態表示
                if status == 'running' and process_running:
                    print("⚙️ ステータス: 実行中")
                    if pid:
                        print(f"🔄 プロセスID: {pid}")
                    if start_time:
                        duration = datetime.now() - start_time
                        hours, remainder = divmod(duration.total_seconds(), 3600)
                        minutes, seconds = divmod(remainder, 60)
                        print(f"⏱️ 実行時間: {int(hours)}時間{int(minutes)}分{int(seconds)}秒")
                elif status == 'running' and not process_running:
                    print("⚙️ ステータス: 異常終了 (プロセスが見つかりません)")
                    print("🔄 再起動が必要です")
                elif status == 'stopped':
                    print("⚙️ ステータス: 停止中")
                else:
                    print(f"⚙️ ステータス: {status}")
                
                # 投稿時間の表示
                posting_hours = status_data.get('posting_hours', [2, 5, 8, 12, 17, 20, 22, 0])
                print(f"⏰ 投稿時間: {', '.join([f'{h:02d}:00' for h in posting_hours])}")
                
                # 次回実行時間の計算
                if status == 'running' and process_running:
                    now = datetime.now()
                    next_hour = None
                    
                    for hour in sorted(posting_hours):
                        if now.hour < hour:
                            next_hour = hour
                            break
                    
                    if next_hour is None and posting_hours:
                        next_hour = posting_hours[0]  # 翌日の最初の時間
                    
                    if next_hour is not None:
                        try:
                            next_day = now.day + (1 if now.hour >= next_hour else 0)
                            next_date = now.replace(day=next_day, hour=next_hour, minute=0, second=0, microsecond=0)
                            print(f"📅 次回投稿予定: {next_date.strftime('%Y-%m-%d %H:%M:%S')}")
                        except ValueError:
                            # 月末の問題を処理
                            next_month = now.month + 1 if now.month < 12 else 1
                            next_year = now.year + (1 if now.month == 12 else 0)
                            next_date = now.replace(year=next_year, month=next_month, day=1, 
                                                  hour=next_hour, minute=0, second=0, microsecond=0)
                            print(f"📅 次回投稿予定: {next_date.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # アカウント情報
                accounts = self.account_manager.get_account_ids()
                print(f"👥 投稿対象アカウント: {len(accounts)}件")
                
                logger.info("スケジューラー状態確認完了")
            
            except Exception as e:
                print(f"❌ 状態ファイル読み込みエラー: {e}")
                logger.error(f"状態ファイル読み込みエラー: {e}", exc_info=True)
                
                # エラー時は基本情報のみ表示
                print("📊 === スケジューラー状況 ===")
                print("⚙️ ステータス: 不明 (ファイル読み込みエラー)")
                print(f"⏰ 投稿時間: 02:00, 05:00, 08:00, 12:00, 17:00, 20:00, 22:00, 00:00")
                
                # アカウント情報
                accounts = self.account_manager.get_account_ids()
                print(f"👥 投稿対象アカウント: {len(accounts)}件")
                
        except Exception as e:
            print(f"❌ スケジューラー状態確認エラー: {e}")
            logger.error(f"スケジューラー状態確認エラー: {e}", exc_info=True)
            traceback.print_exc()

    def manual_scheduler_post(self):
        """スケジューラーのテスト実行（手動投稿）"""
        print("\n⏰ === スケジューラーテスト実行（手動投稿） ===")
        logger.info("スケジューラーテスト実行（手動投稿）開始")
        
        try:
            # スケジューラーシステムをインポート
            from threads_scheduler_system import ThreadsSchedulerSystem
            
            # スケジューラーの手動実行
            scheduler = ThreadsSchedulerSystem()
            scheduler.manual_post()
            logger.info("スケジューラーテスト実行（手動投稿）完了")
            
        except Exception as e:
            print(f"❌ スケジューラー手動実行エラー: {e}")
            logger.error(f"スケジューラー手動実行エラー: {e}", exc_info=True)
            traceback.print_exc()
    
    def add_new_account(self):
        """新規アカウントを追加（Cloudinary更新なし）"""
        print("\n🆕 === 新規アカウント追加 ===")
        logger.info("新規アカウント追加処理開始")
        
        try:
            # アカウントID入力
            account_num = input("追加するアカウント番号を入力してください (例: 021): ").strip()
            if account_num.startswith('ACCOUNT_'):
                account_id = account_num
            else:
                # 3桁のゼロ埋め
                account_num = account_num.zfill(3)
                account_id = f'ACCOUNT_{account_num}'
            
            # 既存アカウントチェック
            existing_accounts = self.account_manager.get_account_ids()
            if account_id in existing_accounts:
                confirm = input(f"⚠️ {account_id} は既に存在します。上書きしますか？ (y/n): ")
                if confirm.lower() != 'y':
                    print("❌ アカウント追加をキャンセルしました")
                    logger.info("アカウント追加キャンセル")
                    return
            
            # アクセストークン入力
            access_token = input("アクセストークンを入力してください: ").strip()
            if not access_token:
                print("❌ アクセストークンが入力されていません")
                logger.error("アクセストークンが空")
                return
            
            # ユーザーID入力
            user_id = input("インスタグラムユーザーIDを入力してください: ").strip()
            if not user_id:
                print("❌ ユーザーIDが入力されていません")
                logger.error("ユーザーIDが空")
                return
            
            # 確認
            print("\n=== 確認情報 ===")
            print(f"アカウントID: {account_id}")
            print(f"アクセストークン: {access_token[:10]}...{access_token[-10:]}")
            print(f"ユーザーID: {user_id}")
            
            confirm = input("\n情報を確認し、アカウントを追加しますか？ (y/n): ")
            if confirm.lower() != 'y':
                print("❌ アカウント追加をキャンセルしました")
                logger.info("アカウント追加キャンセル")
                return
            
            # アカウント追加
            result = self.account_manager.add_new_account(account_id, access_token, user_id)
            
            if result.get('success'):
                print(f"✅ {account_id} を追加しました")
                print("フォルダ構造を作成しました")
                print("環境変数を更新しました")
                logger.info(f"{account_id} を正常に追加しました")
            else:
                print(f"❌ {account_id} の追加に失敗しました: {result.get('message')}")
                logger.error(f"{account_id} の追加に失敗: {result.get('message')}")
            
        except Exception as e:
            print(f"❌ アカウント追加エラー: {e}")
            logger.error(f"アカウント追加エラー: {e}", exc_info=True)
            traceback.print_exc()
    
    def add_multiple_accounts(self):
        """複数アカウントを一括追加（Cloudinary更新なし）"""
        print("\n🆕 === 複数アカウント一括追加 ===")
        logger.info("複数アカウント一括追加処理開始")
        
        try:
            # 開始アカウント番号
            start_num = input("開始アカウント番号を入力してください (例: 021): ").strip()
            if start_num.startswith('ACCOUNT_'):
                start_num = start_num[8:]
            
            # 終了アカウント番号
            end_num = input("終了アカウント番号を入力してください (例: 030): ").strip()
            if end_num.startswith('ACCOUNT_'):
                end_num = end_num[8:]
            
            # 数値チェック
            try:
                start_num_int = int(start_num)
                end_num_int = int(end_num)
            except ValueError:
                print("❌ 数値を入力してください")
                logger.error("数値変換エラー")
                return
            
            if start_num_int > end_num_int:
                print("❌ 開始番号は終了番号より小さくしてください")
                logger.error("番号範囲エラー")
                return
            
            # アカウント数
            account_count = end_num_int - start_num_int + 1
            
            # 共通アクセストークン（オプション）
            use_common_token = input("すべてのアカウントに共通のアクセストークンを使用しますか？ (y/n): ").strip().lower() == 'y'
            common_token = None
            if use_common_token:
                common_token = input("共通アクセストークンを入力してください: ").strip()
                if not common_token:
                    print("❌ アクセストークンが入力されていません")
                    logger.error("アクセストークンが空")
                    return
            
            # 共通ユーザーID（オプション）
            use_common_user_id = input("すべてのアカウントに共通のユーザーIDを使用しますか？ (y/n): ").strip().lower() == 'y'
            common_user_id = None
            if use_common_user_id:
                common_user_id = input("共通ユーザーIDを入力してください: ").strip()
                if not common_user_id:
                    print("❌ ユーザーIDが入力されていません")
                    logger.error("ユーザーIDが空")
                    return
            
            # 確認
            print("\n=== 確認情報 ===")
            print(f"追加するアカウント範囲: ACCOUNT_{start_num_int:03d} ~ ACCOUNT_{end_num_int:03d}")
            print(f"アカウント数: {account_count}件")
            if use_common_token:
                print(f"共通アクセストークン: {common_token[:10]}...{common_token[-10:]}")
            if use_common_user_id:
                print(f"共通ユーザーID: {common_user_id}")
            
            confirm = input("\n上記の内容で一括追加を実行しますか？ (y/n): ")
            if confirm.lower() != 'y':
                print("❌ 一括追加をキャンセルしました")
                logger.info("一括追加キャンセル")
                return
            
            # アカウント一括追加
            success_count = 0
            failed_count = 0
            
            for num in range(start_num_int, end_num_int + 1):
                account_id = f"ACCOUNT_{num:03d}"
                
                # 個別のトークンとユーザーIDを入力（共通でない場合）
                token = common_token
                user_id = common_user_id
                
                if not token:
                    token = input(f"\n{account_id} のアクセストークンを入力してください: ").strip()
                    if not token:
                        print(f"❌ {account_id} のアクセストークンが入力されていません。このアカウントをスキップします。")
                        failed_count += 1
                        continue
                
                if not user_id:
                    user_id = input(f"\n{account_id} のユーザーIDを入力してください: ").strip()
                    if not user_id:
                        print(f"❌ {account_id} のユーザーIDが入力されていません。このアカウントをスキップします。")
                        failed_count += 1
                        continue
                
                # アカウント追加
                result = self.account_manager.add_new_account(account_id, token, user_id)
                
                if result.get('success'):
                    print(f"✅ {account_id} を追加しました")
                    logger.info(f"{account_id} を正常に追加しました")
                    success_count += 1
                else:
                    print(f"❌ {account_id} の追加に失敗しました: {result.get('message')}")
                    logger.error(f"{account_id} の追加に失敗: {result.get('message')}")
                    failed_count += 1
            
            # 結果表示
            print("\n=== 一括追加結果 ===")
            print(f"✅ 成功: {success_count}件")
            print(f"❌ 失敗: {failed_count}件")
            print(f"📈 成功率: {(success_count / account_count) * 100:.1f}%")
            logger.info(f"一括追加完了 - 成功: {success_count}件, 失敗: {failed_count}件")
            
        except Exception as e:
            print(f"❌ 一括追加エラー: {e}")
            logger.error(f"一括追加エラー: {e}", exc_info=True)
            traceback.print_exc()

    def csv_to_folder_structure_with_main_txt(self):
        """
        main.csvからアカウント別フォルダ構造とmain.txtを作成
        - Cloudinary更新なし（軽量版）
        - main.txtファイル作成（投稿システム対応）
        - アカウント別フォルダ構造（ACCOUNT_XXX_CONTENT_XXX）
        - 4カラム対応（ACCOUNT_ID, CONTENT_ID, main_text, image_usage）
        """
        try:
            import pandas as pd
            from pathlib import Path
            import json
            from collections import defaultdict
            
            print("📊 === CSV読み込み（フォルダ構造+main.txt作成） ===")
            logger.info("CSV読み込み（フォルダ構造+main.txt作成）開始")
            
            # main.csvの存在確認
            csv_path = "main.csv"
            if not os.path.exists(csv_path):
                print(f"❌ {csv_path} が見つかりません")
                logger.error(f"{csv_path} が見つかりません")
                return
            
            # CSVを読み込み
            print(f"📋 {csv_path} を読み込み中...")
            df = pd.read_csv(csv_path)
            
            # 必要なカラムの確認
            required_columns = ['ACCOUNT_ID', 'CONTENT_ID', 'main_text', 'image_usage']
            for col in required_columns:
                if col not in df.columns:
                    print(f"❌ 必要なカラム '{col}' が見つかりません")
                    print(f"📋 利用可能なカラム: {list(df.columns)}")
                    logger.error(f"必要なカラム '{col}' が見つかりません")
                    return
            
            print(f"✅ CSVファイル読み込み完了: {len(df)} 件のコンテンツ")
            logger.info(f"CSVファイル読み込み完了: {len(df)} 件のコンテンツ")
            
            # アカウント別にコンテンツをグループ化
            account_contents = defaultdict(list)
            for _, row in df.iterrows():
                account_id = row['ACCOUNT_ID']
                content_data = {
                    'content_id': row['CONTENT_ID'],
                    'main_text': row['main_text'], 
                    'image_usage': row['image_usage']
                }
                account_contents[account_id].append(content_data)
            
            # アカウント情報の表示
            print(f"📊 CSV分析結果:")
            print(f"   - 対象アカウント: {len(account_contents)}個")
            for account_id, contents in account_contents.items():
                print(f"   - {account_id}: {len(contents)}件のコンテンツ")
            
            confirm = input("📝 この設定で実行しますか？ (y/n): ").lower()
            if confirm != 'y':
                print("❌ 処理をキャンセルしました")
                logger.info("処理をキャンセルしました")
                return
            
            # アカウント別にコンテンツを作成
            total_success_count = 0
            total_accounts = len(account_contents)
            
            for account_index, (account_id, contents) in enumerate(account_contents.items(), 1):
                print(f"\n🔄 [{account_index}/{total_accounts}] {account_id} の処理中... ({len(contents)} コンテンツ)")
                logger.info(f"{account_id} の処理中... ({len(contents)} コンテンツ)")
                
                # アカウントフォルダの作成
                account_base_dir = Path(f"accounts/{account_id}/contents")
                account_base_dir.mkdir(parents=True, exist_ok=True)
                
                # コンテンツを番号順に処理
                contents.sort(key=lambda x: x['content_id'])  # CONTENT_IDでソート
                
                for content_index, content_data in enumerate(contents, 1):
                    content_id = content_data['content_id']
                    main_text = content_data['main_text']
                    image_usage = content_data['image_usage']
                    
                    # コンテンツフォルダの作成（ACCOUNT_XXX_CONTENT_XXX形式）
                    content_folder_name = f"{account_id}_{content_id}"
                    content_dir = account_base_dir / content_folder_name
                    content_dir.mkdir(exist_ok=True)
                    
                    # main.txtファイルの作成（重要！）
                    main_txt_path = content_dir / "main.txt"
                    with open(main_txt_path, "w", encoding="utf-8") as f:
                        f.write(main_text)
                    
                    # metadata.jsonファイルの作成（互換性）
                    metadata = {
                        "id": content_folder_name,
                        "original_id": content_id,
                        "account_id": account_id,
                        "created_at": "2025-06-24",
                        "updated_at": "2025-06-24",
                        "usage_count": 0,
                        "has_images": True if image_usage.upper() == "YES" else False,
                        "carousel_count": 1,  # 画像検出システムで自動判定
                        "is_active": True
                    }
                    
                    metadata_path = content_dir / "metadata.json"
                    with open(metadata_path, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    
                    print(f"   ✅ {content_folder_name} 作成完了")
                    print(f"      - main.txt: {len(main_text)} 文字")
                    print(f"      - metadata.json: 作成済み")
                    print(f"      - 画像使用: {image_usage}")
                    
                    total_success_count += 1
                
                print(f"✅ {account_id} 完了: {len(contents)} コンテンツ作成")
                logger.info(f"{account_id} 完了: {len(contents)} コンテンツ作成")
            
            print(f"\n🎉 === 処理完了 ===")
            print(f"✅ 作成完了: {total_success_count} コンテンツ")
            print(f"📁 対象アカウント: {total_accounts}個")
            print(f"📋 各フォルダに main.txt と metadata.json を作成しました")
            print(f"🚀 投稿準備完了！メニュー項目2または4で投稿できます")
            logger.info(f"処理完了 - 作成完了: {total_success_count} コンテンツ, 対象アカウント: {total_accounts}個")
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {str(e)}")
            logger.error(f"CSV読み込みエラー: {str(e)}", exc_info=True)
            traceback.print_exc()
            
    def auto_like_posts(self):
        """自動いいね機能"""
        print("\n💗 === Threads自動いいね機能 ===")
        logger.info("Threads自動いいね機能開始")
        
        try:
            from threads_auto_like import ThreadsAutoLike
            
            # いいねタイプを選択
            print("\n📋 いいねタイプを選択してください:")
            print("1. 🏠 おすすめの投稿にいいね")
            print("2. 👤 特定アカウントの投稿にいいね")
            
            like_type = input("\n選択してください (1/2): ").strip()
            if like_type not in ["1", "2"]:
                print("❌ 無効な選択です")
                return
            
            # アカウント選択
            accounts = self.account_manager.get_account_ids()
            if not accounts:
                print("❌ 利用可能なアカウントがありません")
                return
            
            print("\n📋 利用可能なアカウント:")
            for i, account_id in enumerate(accounts, 1):
                print(f"{i}. {account_id}")
            
            choice = input("\nアカウントを選択してください (番号): ").strip()
            try:
                account_index = int(choice) - 1
                if 0 <= account_index < len(accounts):
                    selected_account = accounts[account_index]
                else:
                    print("❌ 無効な番号です")
                    return
            except ValueError:
                print("❌ 数字を入力してください")
                return
            
            print(f"\n👤 選択されたアカウント: {selected_account}")
            
            # いいね数を指定
            like_count = input("何件いいねしますか？: ").strip()
            try:
                like_count = int(like_count)
                if like_count <= 0:
                    print("❌ 1以上の数を入力してください")
                    return
            except ValueError:
                print("❌ 数字を入力してください")
                return
            
            # 特定ユーザー指定（タイプ2の場合）
            target_user = None
            if like_type == "2":
                target_user = input("対象ユーザー名を入力してください (@なしで): ").strip()
                if not target_user:
                    print("❌ ユーザー名を入力してください")
                    return
                if target_user.startswith('@'):
                    target_user = target_user[1:]  # @を除去
            
            # バックグラウンド処理の選択
            background_mode = False
            bg_choice = input("\nバックグラウンド処理を使用しますか？ (y/n): ").strip().lower()
            if bg_choice == 'y':
                background_mode = True
                print("✅ バックグラウンドモードで実行します")
            else:
                print("✅ 通常モード（ブラウザ表示）で実行します")
            
            # 確認
            print(f"\n📊 === 実行内容確認 ===")
            print(f"アカウント: {selected_account}")
            print(f"いいね数: {like_count}件")
            if like_type == "1":
                print(f"対象: おすすめの投稿")
            else:
                print(f"対象: @{target_user} の投稿")
            print(f"モード: {'バックグラウンド' if background_mode else '通常（ブラウザ表示）'}")
            
            confirm = input("\n実行しますか？ (y/n): ").lower()
            if confirm != 'y':
                print("❌ キャンセルしました")
                return
            
            # 自動いいね実行
            auto_like = ThreadsAutoLike()
            
            try:
                # ドライバーセットアップ
                print("\n🌐 ブラウザを起動中...")
                auto_like.setup_driver(selected_account, headless=background_mode)
                
                # ログイン（初回は手動）
                session_file = os.path.join(auto_like.session_dir, selected_account, "Default", "Cookies")
                is_first_login = not os.path.exists(session_file)
                
                if not auto_like.login(selected_account, manual=is_first_login):
                    print("❌ ログインに失敗しました")
                    return
                
                # いいね実行
                if like_type == "1":
                    # おすすめの投稿にいいね
                    print(f"\n🚀 おすすめの投稿に{like_count}件のいいねを実行します...")
                    results = auto_like.like_home_feed_posts(selected_account, like_count)
                else:
                    # 特定ユーザーの投稿にいいね
                    print(f"\n🚀 @{target_user} の投稿に{like_count}件のいいねを実行します...")
                    results = auto_like.like_user_posts(selected_account, target_user, like_count)
                
                # 結果をログに記録
                logger.info(f"自動いいね完了 - アカウント: {selected_account}, 成功: {results['success']}, 失敗: {results['failed']}")
                
            finally:
                # ブラウザを閉じる
                auto_like.close()
                print("\n✅ 自動いいね処理が完了しました")
                
        except ImportError:
            print("❌ threads_auto_like.py が見つかりません")
            print("threads_auto_like.py ファイルを作成してください")
            logger.error("threads_auto_like.py が見つかりません")
        except Exception as e:
            print(f"❌ 自動いいねエラー: {e}")
            logger.error(f"自動いいねエラー: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            
    
    def auto_like_all_accounts(self):
        """全アカウント自動いいね機能（1アカウントずつ順番に実行）"""
        print("\n💗 === 全アカウント自動いいね機能 ===")
        logger.info("全アカウント自動いいね機能開始")
        
        try:
            from threads_auto_like import ThreadsAutoLike
            
            # いいねタイプを選択
            print("\n📋 いいねタイプを選択してください:")
            print("1. 🏠 おすすめの投稿にいいね")
            print("2. 👤 特定アカウントの投稿にいいね")
            
            like_type = input("\n選択してください (1/2): ").strip()
            if like_type not in ["1", "2"]:
                print("❌ 無効な選択です")
                return
            
            # いいね数を指定
            like_count = input("\n各アカウントで何件いいねしますか？: ").strip()
            try:
                like_count = int(like_count)
                if like_count <= 0:
                    print("❌ 1以上の数を入力してください")
                    return
            except ValueError:
                print("❌ 数字を入力してください")
                return
            
            # 特定ユーザー指定（タイプ2の場合）
            target_user = None
            if like_type == "2":
                target_user = input("対象ユーザー名を入力してください (@なしで): ").strip()
                if not target_user:
                    print("❌ ユーザー名を入力してください")
                    return
                if target_user.startswith('@'):
                    target_user = target_user[1:]  # @を除去
            
            # バックグラウンド処理の選択
            background_mode = False
            bg_choice = input("\nバックグラウンド処理を使用しますか？ (y/n): ").strip().lower()
            if bg_choice == 'y':
                background_mode = True
                print("✅ バックグラウンドモードで実行します")
            else:
                print("✅ 通常モード（ブラウザ表示）で実行します")
            
            # アカウント間の待機時間
            wait_time = input("\nアカウント間の待機時間（秒）を入力してください (推奨: 30-60): ").strip()
            try:
                wait_time = int(wait_time)
                if wait_time < 10:
                    print("⚠️ 10秒未満は推奨されません。10秒に設定します。")
                    wait_time = 10
            except ValueError:
                print("⚠️ 無効な入力です。30秒に設定します。")
                wait_time = 30
            
            # 利用可能なアカウントを取得
            accounts = self.account_manager.get_account_ids()
            if not accounts:
                print("❌ 利用可能なアカウントがありません")
                return
            
            # 確認
            print(f"\n📊 === 実行内容確認 ===")
            print(f"対象アカウント数: {len(accounts)}件")
            print(f"各アカウントのいいね数: {like_count}件")
            print(f"合計いいね予定数: {len(accounts) * like_count}件")
            if like_type == "1":
                print(f"対象: おすすめの投稿")
            else:
                print(f"対象: @{target_user} の投稿")
            print(f"モード: {'バックグラウンド' if background_mode else '通常（ブラウザ表示）'}")
            print(f"アカウント間待機時間: {wait_time}秒")
            print(f"予想所要時間: 約{(len(accounts) * (like_count * 3 + wait_time)) // 60}分")
            
            # アカウントリストを表示
            print("\n📋 実行順序:")
            for i, account_id in enumerate(accounts[:10], 1):  # 最初の10件のみ表示
                print(f"  {i}. {account_id}")
            if len(accounts) > 10:
                print(f"  ... 他 {len(accounts) - 10} アカウント")
            
            confirm = input("\n実行しますか？ (y/n): ").lower()
            if confirm != 'y':
                print("❌ キャンセルしました")
                return
            
            # 実行結果を記録
            total_results = {
                'success_accounts': 0,
                'failed_accounts': 0,
                'total_likes': 0,
                'total_failed_likes': 0,
                'account_details': []
            }
            
            # 各アカウントで順番に実行
            for index, account_id in enumerate(accounts, 1):
                print(f"\n{'='*60}")
                print(f"🔄 [{index}/{len(accounts)}] {account_id} 処理開始")
                print(f"{'='*60}")
                
                # 自動いいね実行
                auto_like = ThreadsAutoLike()
                account_result = {
                    'account_id': account_id,
                    'success': 0,
                    'failed': 0,
                    'error': None
                }
                
                try:
                    # ドライバーセットアップ
                    print(f"\n🌐 {account_id} のブラウザを起動中...")
                    auto_like.setup_driver(account_id, headless=background_mode)
                    
                    # ログイン（初回は手動）
                    session_file = os.path.join(auto_like.session_dir, account_id, "Default", "Cookies")
                    is_first_login = not os.path.exists(session_file)
                    
                    if not auto_like.login(account_id, manual=is_first_login):
                        print(f"❌ {account_id} のログインに失敗しました")
                        account_result['error'] = "ログイン失敗"
                        total_results['failed_accounts'] += 1
                    else:
                        # いいね実行
                        if like_type == "1":
                            # おすすめの投稿にいいね
                            print(f"\n🚀 {account_id}: おすすめの投稿に{like_count}件のいいねを実行します...")
                            results = auto_like.like_home_feed_posts(account_id, like_count)
                        else:
                            # 特定ユーザーの投稿にいいね
                            print(f"\n🚀 {account_id}: @{target_user} の投稿に{like_count}件のいいねを実行します...")
                            results = auto_like.like_user_posts(account_id, target_user, like_count)
                        
                        # 結果を記録
                        account_result['success'] = results.get('success', 0)
                        account_result['failed'] = results.get('failed', 0)
                        
                        if results.get('success', 0) > 0:
                            total_results['success_accounts'] += 1
                        else:
                            total_results['failed_accounts'] += 1
                        
                        total_results['total_likes'] += results.get('success', 0)
                        total_results['total_failed_likes'] += results.get('failed', 0)
                    
                except Exception as e:
                    print(f"❌ {account_id} エラー: {e}")
                    logger.error(f"{account_id} エラー: {e}", exc_info=True)
                    account_result['error'] = str(e)
                    total_results['failed_accounts'] += 1
                    
                finally:
                    # ブラウザを閉じる
                    auto_like.close()
                    
                    # 結果を追加
                    total_results['account_details'].append(account_result)
                    
                    # アカウントの結果表示
                    print(f"\n📊 {account_id} の結果:")
                    print(f"  成功: {account_result['success']}件")
                    print(f"  失敗: {account_result['failed']}件")
                    if account_result['error']:
                        print(f"  エラー: {account_result['error']}")
                    
                    # 次のアカウントまで待機（最後のアカウントは除く）
                    if index < len(accounts):
                        print(f"\n⏸️ 次のアカウントまで{wait_time}秒待機...")
                        for i in range(wait_time, 0, -10):
                            if i >= 10:
                                print(f"  残り{i}秒...")
                                time.sleep(10)
                            else:
                                time.sleep(i)
                                break
            
            # 全体の結果表示
            print(f"\n{'='*60}")
            print("📊 === 全アカウント実行結果 ===")
            print(f"{'='*60}")
            print(f"✅ 成功アカウント: {total_results['success_accounts']}/{len(accounts)}")
            print(f"❌ 失敗アカウント: {total_results['failed_accounts']}/{len(accounts)}")
            print(f"💗 総いいね成功数: {total_results['total_likes']}件")
            print(f"❌ 総いいね失敗数: {total_results['total_failed_likes']}件")
            print(f"📈 成功率: {(total_results['total_likes'] / (len(accounts) * like_count) * 100) if len(accounts) > 0 else 0:.1f}%")
            
            # 詳細結果の保存
            result_file = f"like_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(total_results, f, ensure_ascii=False, indent=2)
            print(f"\n📁 詳細結果を保存しました: {result_file}")
            
            logger.info(f"全アカウント自動いいね完了 - 成功: {total_results['success_accounts']}, 失敗: {total_results['failed_accounts']}, 総いいね数: {total_results['total_likes']}")
            
        except ImportError:
            print("❌ threads_auto_like.py が見つかりません")
            logger.error("threads_auto_like.py が見つかりません")
        except Exception as e:
            print(f"❌ 全アカウント自動いいねエラー: {e}")
            logger.error(f"全アカウント自動いいねエラー: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
    
    def interactive_menu(self):
        """対話型メニュー"""
        while True:
            print("\n" + "="*50)
            print("🎯 Python版Threads自動投稿システム v5.0")
            print("🤖 完全自動判定機能付き + 📂 フォルダ構造最適化")
            print("="*50)
            print("1. 📱 単発投稿（テストモード）")
            print("2. 🚀 単発投稿（実際の投稿）🤖")
            print("3. 👥 全アカウント投稿（テストモード）")
            print("4. 🌟 全アカウント投稿（実際の投稿）")
            print("5. 📊 システム状況確認")
            print("-"*40)
            print("6. ⏰ スケジューラー起動")
            print("7. 📅 スケジューラー状況確認")
            print("8. 🔄 スケジューラーテスト実行（手動投稿）")
            print("-"*40)
            print("9. 📝 新規アカウント追加（Cloudinary更新なし）")
            print("10. 📋 複数アカウント一括追加（Cloudinary更新なし）")
            print("11. 💗 Threads自動いいね機能（単一アカウント）")
            print("12. 💗 Threads自動いいね機能（全アカウント順次実行）")            
            print("-"*40)
            print("21. 📊 CSV読み込み（フォルダ構造+main.txt作成）")
            print("-"*40)
            print("0. 🚪 終了")
            print("-"*50)
            print("🤖 項目2は画像ファイルの存在を自動判定します")
            print("📊 項目21は main.csv から最適化フォルダ構造を作成します")
            print("-"*50)
            
            try:
                choice = input("選択してください (0-21): ").strip()
                
                if choice == "0":
                    print("👋 システムを終了します")
                    logger.info("システム終了")
                    break
                elif choice == "1":
                    self.single_post(test_mode=True)
                elif choice == "2":
                    confirm = input("🚨 実際にThreadsに投稿します（自動判定機能付き）。続行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        self.single_post(test_mode=False)
                elif choice == "3":
                    self.all_accounts_post(test_mode=True)
                elif choice == "4":
                    confirm = input("🚨 全アカウントで実際にThreadsに投稿します。続行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        self.all_accounts_post(test_mode=False)
                elif choice == "5":
                    self.system_status()
                elif choice == "6":
                    self.run_scheduler()
                elif choice == "7":
                    self.scheduler_status()
                elif choice == "8":
                    confirm = input("🚨 スケジューラーのテスト実行（手動投稿）を行います。続行しますか？ (y/n): ")
                    if confirm.lower() == 'y':
                        self.manual_scheduler_post()
                elif choice == "9":
                    self.add_new_account()
                elif choice == "10":
                    self.add_multiple_accounts()
                elif choice == "11":
                    self.auto_like_posts()
                elif choice == "12":
                    self.auto_like_all_accounts()
                elif choice == "21":
                    self.csv_to_folder_structure_with_main_txt()
                else:
                    print("❌ 無効な選択です")
                    
            except KeyboardInterrupt:
                print("\n👋 システムを終了します")
                logger.info("ユーザーによる中断でシステム終了")
                break
            except Exception as e:
                print(f"❌ エラー: {e}")
                logger.error(f"メニュー操作エラー: {e}", exc_info=True)
                traceback.print_exc()

def main():
    """メイン実行関数"""
    print("🚀 Python版Threads自動投稿システム v5.0")
    print("=" * 50)
    print("🎉 フォルダ構造最適化 + 完全自動判定機能付き")
    print("=" * 50)
    logger.info("Python版Threads自動投稿システム v5.0 起動")
    
    try:
        # システム初期化
        system = ThreadsAutomationSystem()
        
        # 対話型メニュー起動
        system.interactive_menu()
    except KeyboardInterrupt:
        print("\n👋 システムを終了しました")
        logger.info("ユーザーによる中断でシステム終了")
    except Exception as e:
        print(f"❌ システムエラー: {e}")
        logger.error(f"システムエラー: {e}", exc_info=True)
        traceback.print_exc()
        return 1
    
    return 0

def load_csv_to_folders(self, csv_file='main.csv'):
    """CSVファイルを読み込んでフォルダ構造を生成（6カラム対応版）"""
    try:
        if not os.path.exists(csv_file):
            print(f"❌ CSVファイル '{csv_file}' が見つかりません")
            return False
        
        # CSVファイルを読み込み（改行を含むテキストに対応）
        import pandas as pd
        df = pd.read_csv(csv_file, encoding='utf-8', quoting=1)  # QUOTE_ALL = 1
        
        print(f"📊 読み込まれたデータ: {len(df)}行")
        print(f"   カラム: {list(df.columns)}")
        
        # デバッグ用：最初の数行を表示
        if len(df) > 0:
            print("\n📋 データサンプル:")
            for idx, row in df.head(3).iterrows():
                print(f"   行{idx}: ACCOUNT_ID={row.get('ACCOUNT_ID', 'N/A')}, CONTENT_ID={row.get('CONTENT_ID', 'N/A')}")
        
        # 必須カラムの確認（7カラム対応）
        required_columns = ['ACCOUNT_ID', 'CONTENT_ID', 'main_text', 'image_usage', 'tree_post', 'tree_text', 'quote_account']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ CSVファイルに必須カラムがありません: {missing_columns}")
            print(f"   必須カラム: {required_columns}")
            return False
        
        # 空の値をチェックして置換
        df['ACCOUNT_ID'] = df['ACCOUNT_ID'].fillna('')
        df['CONTENT_ID'] = df['CONTENT_ID'].fillna('')
        df['main_text'] = df['main_text'].fillna('')
        df['tree_text'] = df['tree_text'].fillna('')
        
        # 空のACCOUNT_IDまたはCONTENT_IDを持つ行を除外
        df = df[(df['ACCOUNT_ID'] != '') & (df['CONTENT_ID'] != '')]
        
        if len(df) == 0:
            print(f"❌ 有効なデータがCSVファイルにありません")
            return False
        
        # アカウント別にグループ化
        grouped = df.groupby('ACCOUNT_ID')
        
        total_contents = 0
        
        for account_id, group in grouped:
            print(f"\n📁 {account_id} の処理中...")
            
            # アカウントフォルダのパス
            account_path = os.path.join('accounts', account_id)
            contents_path = os.path.join(account_path, 'contents')
            
            # フォルダが存在しない場合は作成
            os.makedirs(contents_path, exist_ok=True)
            
            # 各コンテンツを処理
            for idx, row in group.iterrows():
                # 値の存在確認
                if pd.isna(row['ACCOUNT_ID']) or pd.isna(row['CONTENT_ID']):
                    print(f"   ⚠️ 行 {idx}: ACCOUNT_IDまたはCONTENT_IDが空のためスキップ")
                    continue
                    
                account_id_str = str(row['ACCOUNT_ID']).strip()
                content_id_str = str(row['CONTENT_ID']).strip()
                
                if not account_id_str or not content_id_str:
                    print(f"   ⚠️ 行 {idx}: 無効なデータのためスキップ")
                    continue
                
                content_id = f"{account_id_str}_{content_id_str}"
                content_path = os.path.join(contents_path, content_id)
                
                # コンテンツフォルダを作成
                os.makedirs(content_path, exist_ok=True)
                
                # main.txtを作成
                main_txt_path = os.path.join(content_path, 'main.txt')
                with open(main_txt_path, 'w', encoding='utf-8') as f:
                    f.write(row['main_text'])
                
                # metadata.jsonを作成（quote_account情報を含む）
                metadata = {
                    "content_id": content_id,
                    "original_id": row['CONTENT_ID'],
                    "main_text": row['main_text'],
                    "image_usage": row['image_usage'],
                    "tree_post": row['tree_post'],
                    "tree_text": row['tree_text'] if pd.notna(row['tree_text']) else "",
                    "quote_account": row['quote_account'] if pd.notna(row['quote_account']) else "",
                    "created_at": datetime.now().isoformat(),
                    "usage_count": 0
                }
                
                metadata_path = os.path.join(content_path, 'metadata.json')
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                print(f"   ✅ {content_id} - ツリー投稿: {row['tree_post']}")
                total_contents += 1
        
        print(f"\n✅ CSV読み込み完了")
        print(f"   総コンテンツ数: {total_contents}")
        print(f"   処理アカウント数: {len(grouped)}")
        
        # キャッシュを更新
        print("\n🔄 キャッシュを更新中...")
        for account_id in grouped.groups.keys():
            self.sync_account_contents(account_id)
        
        return True
        
    except Exception as e:
        print(f"❌ CSV読み込みエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sys.exit(main())
    
