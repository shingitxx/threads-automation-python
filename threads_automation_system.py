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
from pathlib import Path
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
            print("-"*40)
            print("11. 📝 特定アカウント投稿（リプライなし）")  # 新機能
            print("12. 🔄 アカウントコンテンツ同期")  # 新機能
            print("-"*40)
            print("0. 🚪 終了")
            print("-"*50)
            print("🤖 項目2は画像ファイルの存在を自動判定します")
            print("-"*50)
            
            try:
                choice = input("選択してください (0-12): ").strip()
                
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
                    self.post_specific_account_no_reply()
                elif choice == "12":
                    print("\n🔄 === アカウントコンテンツ同期メニュー ===")
                    print("1. 特定アカウントのコンテンツを同期")
                    print("2. 全アカウントのコンテンツを同期")
                    print("0. 戻る")
                    
                    sync_choice = input("選択してください: ").strip()
                    
                    if sync_choice == "1":
                        # アカウント一覧表示
                        accounts = self.account_manager.get_account_ids()
                        print("\n📊 利用可能なアカウント:")
                        for i, acc in enumerate(accounts, 1):
                            print(f"{i}. {acc}")
                        
                        try:
                            selection = int(input("同期するアカウントの番号を入力してください: "))
                            if 1 <= selection <= len(accounts):
                                account_id = accounts[selection - 1]
                                force = input("既存のデータを上書きしますか？ (y/n): ").lower() == 'y'
                                self.sync_account_contents(account_id, force)
                            else:
                                print("❌ 無効な選択です")
                        except ValueError:
                            print("❌ 数値を入力してください")
                    
                    elif sync_choice == "2":
                        force = input("既存のデータを上書きしますか？ (y/n): ").lower() == 'y'
                        self.sync_account_contents(None, force)
                    
                    elif sync_choice == "0":
                        continue
                    
                    else:
                        print("❌ 無効な選択です")
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

    def post_specific_account_no_reply(self, account_id=None, test_mode=None, custom_text=None):
        """
        特定のアカウントでリプライなしの投稿を実行する機能
        
        Args:
            account_id (str, optional): 使用するアカウントID。指定がなければ対話式で選択
            test_mode (bool, optional): テストモードフラグ。指定がなければ対話式で選択
            custom_text (str, optional): カスタムテキスト。指定がなければ対話式で選択
            
        Returns:
            dict: 投稿結果
        """
        print("\n🎯 === 特定アカウント投稿実行（リプライなし） ===")
        logger.info("特定アカウント投稿実行（リプライなし）開始")
        
        # アカウントIDが指定されていない場合は対話式で選択
        if account_id is None:
            available_accounts = self.account_manager.get_account_ids()
            print("📊 利用可能なアカウント:")
            for i, acc in enumerate(available_accounts, 1):
                print(f"{i}. {acc}")
            
            try:
                selection = int(input("使用するアカウントの番号を入力してください: "))
                if 1 <= selection <= len(available_accounts):
                    account_id = available_accounts[selection - 1]
                    print(f"✅ 選択されたアカウント: {account_id}")
                    logger.info(f"選択されたアカウント: {account_id}")
                else:
                    print("❌ 無効な選択です")
                    logger.error("無効なアカウント選択")
                    return None
            except ValueError:
                print("❌ 数値を入力してください")
                logger.error("数値入力エラー")
                return None
        
        # テストモードの選択
        if test_mode is None:
            test_mode = input("テストモードで実行しますか？実際には投稿されません (y/n): ").lower() == 'y'
            logger.info(f"テストモード: {test_mode}")
        
        # カスタムテキストの選択
        if custom_text is None:
            use_custom = input("カスタムテキストを使用しますか？ (y/n): ").lower() == 'y'
            if use_custom:
                custom_text = input("投稿するテキストを入力してください: ")
                logger.info("カスタムテキスト使用")
        
        # 実行確認
        if not test_mode:
            confirm = input(f"🚨 {account_id} で実際に投稿を実行しますか？（リプライなし） (y/n): ").lower()
            if confirm != 'y':
                print("投稿をキャンセルしました")
                logger.info("投稿キャンセル")
                return None
        
        print(f"🚀 {account_id} で投稿実行中（リプライなし）...")
        logger.info(f"{account_id} で投稿実行中（リプライなし）...")
        
        try:
            # コンテンツを選択
            content = self.account_manager.get_random_content(account_id)
            if not content:
                print(f"❌ {account_id}: コンテンツの取得に失敗しました")
                logger.error(f"{account_id}: コンテンツの取得に失敗")
                return False
            
            content_id = content.get('id')
            print(f"📝 選択されたコンテンツ: {content_id}")
            logger.info(f"選択されたコンテンツ: {content_id}")
            
            # メインテキスト取得
            main_text = content.get('main_text', '')
            if custom_text:
                main_text = custom_text
            
            # テストモードの場合
            if test_mode:
                print("\n🧪 テストモード: 実際には投稿されません")
                print(f"📄 メインテキスト:")
                print(main_text[:200] + "..." if len(main_text) > 200 else main_text)
                
                # 画像情報
                images = content.get('images', [])
                post_type = "carousel" if len(images) > 1 else ("image" if images else "text")
                print(f"📊 投稿タイプ: {post_type}")
                
                if images:
                    print(f"🖼️ 画像数: {len(images)}枚")
                    for i, image in enumerate(images, 1):
                        print(f"  画像{i}: {image.get('path')}")
                
                print("\n✅ テストモード投稿シミュレーション完了（リプライなし）")
                logger.info("テストモード投稿シミュレーション完了（リプライなし）")
                
                return {
                    "success": True,
                    "test_mode": True,
                    "content_id": content_id,
                    "post_type": post_type,
                    "account_id": account_id
                }
            
            # 実際の投稿（リプライなし）
            print("\n📤 === 実際の投稿実行（リプライなし） ===")
            logger.info(f"{account_id}: 実際の投稿実行開始（リプライなし）")
            
            # 投稿実行（アフィリエイトリプライなし）
            result = self.direct_post.post_without_affiliate(account_id, content_id, main_text)
            
            if result and result.get("success"):
                print(f"🎉 {account_id}: 投稿完了（リプライなし）")
                logger.info(f"{account_id}: 投稿完了（リプライなし） - {result}")
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

    def sync_account_contents(self, account_id=None, force=False):
        """
        アカウントのコンテンツフォルダを読み込み、システムのキャッシュを更新
        
        Args:
            account_id (str, optional): 同期するアカウントID（Noneの場合は全アカウント）
            force (bool): 既存のデータを上書きするかどうか
            
        Returns:
            dict: 同期結果の統計
        """
        stats = {
            "total_scanned": 0,
            "added": 0,
            "updated": 0,
            "unchanged": 0,
            "errors": 0
        }
        
        print("\n🔄 === アカウントコンテンツ同期 ===")
        logger.info("アカウントコンテンツ同期開始")
        
        # 同期するアカウントのリスト
        accounts_to_sync = []
        if account_id:
            accounts_to_sync = [account_id]
            logger.info(f"同期対象: {account_id}")
        else:
            # 利用可能な全アカウントを取得
            accounts_to_sync = self.account_manager.get_account_ids()
            logger.info(f"同期対象: 全アカウント ({len(accounts_to_sync)}件)")
        
        print(f"🔄 {len(accounts_to_sync)}個のアカウントのコンテンツ同期を開始...")
        
        for acc_id in accounts_to_sync:
            print(f"\n📂 {acc_id} の同期中...")
            logger.info(f"{acc_id} の同期開始")
            
            content_dir = Path(f"accounts/{acc_id}/contents")
            
            if not content_dir.exists():
                print(f"⚠ {acc_id} のコンテンツディレクトリが見つかりません")
                logger.warning(f"{acc_id} のコンテンツディレクトリが見つかりません")
                continue
            
            # コンテンツフォルダを検索
            content_folders = [d for d in content_dir.glob(f"{acc_id}_CONTENT_*") if d.is_dir()]
            print(f"📊 {len(content_folders)}個のコンテンツフォルダを検出")
            logger.info(f"{acc_id}: {len(content_folders)}個のコンテンツフォルダを検出")
            
            # キャッシュディレクトリの作成
            cache_dir = Path(f"accounts/{acc_id}/_cache")
            cache_dir.mkdir(exist_ok=True, parents=True)
            
            # コンテンツキャッシュファイル
            cache_file = cache_dir / "contents.json"
            
            # 既存のキャッシュを読み込む
            existing_contents = {}
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        existing_contents = json.load(f)
                except Exception as e:
                    print(f"⚠ キャッシュファイル読み込みエラー: {e}")
                    logger.warning(f"キャッシュファイル読み込みエラー: {e}")
            
            # 新しいコンテンツデータ
            new_contents = {}
            
            for folder in content_folders:
                stats["total_scanned"] += 1
                content_id = folder.name
                metadata_file = folder / "metadata.json"
                
                if not metadata_file.exists():
                    print(f"⚠ {content_id}: メタデータファイルがありません")
                    logger.warning(f"{content_id}: メタデータファイルがありません")
                    stats["errors"] += 1
                    continue
                
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    if "text" not in metadata:
                        print(f"⚠ {content_id}: テキストデータがありません")
                        logger.warning(f"{content_id}: テキストデータがありません")
                        stats["errors"] += 1
                        continue
                    
                    # コンテンツデータの作成
                    content_data = {
                        "main_text": metadata["text"],
                        "id": content_id,
                        "account_id": acc_id,
                        "from_folder": True,
                        "original_content_id": metadata.get("original_content_id", ""),
                        "created_at": metadata.get("created_at", "")
                    }
                    
                    # 画像ファイルの検出
                    image_files = list(folder.glob("image_*.jpg"))
                    if image_files:
                        images = []
                        for i, img_file in enumerate(sorted(image_files)):
                            img_info = {
                                "path": str(img_file),
                                "index": i,
                                "id": f"{content_id}_IMG_{i}"
                            }
                            images.append(img_info)
                        content_data["images"] = images
                    
                    # 既存データとの比較
                    if content_id in existing_contents and not force:
                        existing_data = existing_contents[content_id]
                        if existing_data.get("main_text") == content_data["main_text"]:
                            print(f"ℹ {content_id}: 変更なし")
                            logger.info(f"{content_id}: 変更なし")
                            new_contents[content_id] = existing_data
                            stats["unchanged"] += 1
                        else:
                            new_contents[content_id] = content_data
                            print(f"✅ {content_id}: 更新")
                            logger.info(f"{content_id}: 更新")
                            stats["updated"] += 1
                    else:
                        new_contents[content_id] = content_data
                        print(f"✅ {content_id}: 追加")
                        logger.info(f"{content_id}: 追加")
                        stats["added"] += 1
                
                except Exception as e:
                    print(f"❌ {content_id}: エラー - {e}")
                    logger.error(f"{content_id}: エラー - {e}", exc_info=True)
                    stats["errors"] += 1
            
            # キャッシュファイルに保存
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(new_contents, f, ensure_ascii=False, indent=2)
                print(f"✅ コンテンツキャッシュを保存しました: {len(new_contents)}件")
                logger.info(f"コンテンツキャッシュを保存: {len(new_contents)}件")
            except Exception as e:
                print(f"❌ キャッシュ保存エラー: {e}")
                logger.error(f"キャッシュ保存エラー: {e}")
            
        # 結果の表示
        print("\n===== 同期結果 =====")
        print(f"スキャンされたフォルダ: {stats['total_scanned']}")
        print(f"追加されたコンテンツ: {stats['added']}")
        print(f"更新されたコンテンツ: {stats['updated']}")
        print(f"変更なし: {stats['unchanged']}")
        print(f"エラー: {stats['errors']}")
        logger.info(f"同期完了 - 追加: {stats['added']}件, 更新: {stats['updated']}件, 変更なし: {stats['unchanged']}件, エラー: {stats['errors']}件")
        
        return stats

def main():
    """メイン実行関数"""
    print("🚀 Python版Threads自動投稿システム v5.0")
    print("=" * 50)
    print("🎉 フォルダ構造最適化 + 完全自動判定機能付き")
    print("=" * 50)
    logger.info("Python版Threads自動投稿システム v5.0 起動")
    
    try:
        # コマンドライン引数を解析
        import argparse
        parser = argparse.ArgumentParser(description='Python版Threads自動投稿システム')
        subparsers = parser.add_subparsers(dest='command', help='実行するコマンド')
        
        # no-reply コマンド
        no_reply_parser = subparsers.add_parser('no-reply', help='特定アカウント投稿（リプライなし）')
        no_reply_parser.add_argument('--account', help='アカウントID（指定なしの場合は対話的に選択）')
        no_reply_parser.add_argument('--test', action='store_true', help='テストモード（実際には投稿しない）')
        no_reply_parser.add_argument('--text', help='カスタムテキスト（指定なしの場合は対話的に入力）')
        
        # sync コマンド
        sync_parser = subparsers.add_parser('sync', help='アカウントコンテンツ同期')
        sync_parser.add_argument('--account', help='同期するアカウントID（指定なしの場合は全アカウント）')
        sync_parser.add_argument('--force', action='store_true', help='既存データを上書き')
        
        args = parser.parse_args()
        
        # システム初期化
        system = ThreadsAutomationSystem()
        
        if args.command == 'no-reply':
            # 特定アカウント投稿（リプライなし）
            system.post_specific_account_no_reply(
                account_id=args.account,
                test_mode=args.test,
                custom_text=args.text
            )
        elif args.command == 'sync':
            # アカウントコンテンツ同期
            system.sync_account_contents(
                account_id=args.account,
                force=args.force
            )
        else:
            # コマンドが指定されていない場合は対話型メニュー起動
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

if __name__ == "__main__":
    sys.exit(main())