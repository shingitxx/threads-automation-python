# proxy/proxy_manager.py
"""
プロキシ管理システム
アカウント別プロキシ管理とプロバイダー抽象化を提供
"""
import os
import json
import time
import random
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

# ロガー設定
logger = logging.getLogger('proxy-manager')

@dataclass
class ProxyConfig:
    """プロキシ設定データクラス"""
    provider: str
    endpoint: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_url(self) -> str:
        """プロキシURLを生成"""
        if self.username and self.password:
            return f"http://{self.username}:{self.password}@{self.endpoint}:{self.port}"
        return f"http://{self.endpoint}:{self.port}"

class ProxyManager:
    """プロキシ管理クラス"""
    
    def __init__(self, test_mode: bool = None):
        """初期化
        
        Args:
            test_mode: テストモード（プロキシを使用しない）
        """
        self.config_file = Path(__file__).parent / 'proxy_config.json'
        self.config = self._load_config()
        
        # テストモードの設定（環境変数優先）
        if test_mode is None:
            self.test_mode = os.getenv('PROXY_TEST_MODE', 'true').lower() == 'true'
        else:
            self.test_mode = test_mode
            
        # プロバイダーの設定
        self.provider = os.getenv('PROXY_PROVIDER', self.config.get('default_provider', 'mock'))
        
        # プロキシ使用の有効/無効
        self.enabled = os.getenv('PROXY_ENABLED', 'false').lower() == 'true'
        
        # 使用履歴
        self.usage_history = []
        
        # セッション管理
        self.sessions = {}
        
        logger.info(f"ProxyManager初期化: provider={self.provider}, test_mode={self.test_mode}, enabled={self.enabled}")
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"設定ファイルが見つかりません: {self.config_file}")
                return {}
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
            return {}
    
    def get_proxy_for_account(self, account_id: str) -> Optional[Dict[str, str]]:
        """アカウント用のプロキシを取得
        
        Args:
            account_id: アカウントID (例: ACCOUNT_001)
            
        Returns:
            プロキシ辞書 {'http': 'http://...', 'https': 'http://...'} または None
        """
        # テストモードまたは無効の場合
        if self.test_mode or not self.enabled:
            logger.debug(f"[{account_id}] プロキシ未使用 (test_mode={self.test_mode}, enabled={self.enabled})")
            return None
        
        try:
            # プロキシ設定を取得
            proxy_config = self._get_account_proxy_config(account_id)
            if not proxy_config:
                logger.warning(f"[{account_id}] プロキシ設定が見つかりません")
                return None
            
            # プロキシURLを生成
            proxy_url = proxy_config.to_url()
            
            # 使用履歴に記録
            self._record_usage(account_id, proxy_url)
            
            logger.info(f"[{account_id}] プロキシ使用: {self._mask_proxy_url(proxy_url)}")
            
            return {
                'http': proxy_url,
                'https': proxy_url
            }
            
        except Exception as e:
            logger.error(f"[{account_id}] プロキシ取得エラー: {e}")
            return None
    
    def get_proxy_for_selenium(self, account_id: str) -> Optional[str]:
        """Selenium用のプロキシ設定を取得
        
        Args:
            account_id: アカウントID
            
        Returns:
            プロキシ文字列 (例: "http://user:pass@proxy.com:8080") または None
        """
        proxy_dict = self.get_proxy_for_account(account_id)
        if proxy_dict:
            return proxy_dict.get('http')
        return None
    
    def _get_account_proxy_config(self, account_id: str) -> Optional[ProxyConfig]:
        """アカウント固有のプロキシ設定を取得"""
        # 環境変数から個別設定を確認
        proxy_url = os.getenv(f'PROXY_{account_id}')
        if proxy_url:
            return self._parse_proxy_url(proxy_url)
        
        # プロバイダー設定から生成
        provider_config = self.config.get('providers', {}).get(self.provider, {})
        if not provider_config:
            return None
        
        # 環境変数から認証情報を取得
        username = os.getenv(f'PROXY_USERNAME_{self.provider.upper()}', 
                            os.getenv('PROXY_USERNAME'))
        password = os.getenv(f'PROXY_PASSWORD_{self.provider.upper()}',
                            os.getenv('PROXY_PASSWORD'))
        
        if not username or not password:
            logger.error(f"プロキシ認証情報が設定されていません: {self.provider}")
            return None
        
        # セッションID生成（必要な場合）
        session_id = None
        if self.provider == 'brightdata':
            session_id = f"{account_id}_{int(time.time())}"
            username = username.replace('{session}', session_id)
        
        return ProxyConfig(
            provider=self.provider,
            endpoint=provider_config.get('endpoint', ''),
            port=provider_config.get('port', 8080),
            username=username,
            password=password,
            session_id=session_id
        )
    
    def _parse_proxy_url(self, url: str) -> Optional[ProxyConfig]:
        """プロキシURLをパース"""
        try:
            # 簡易パーサー (http://user:pass@host:port)
            if '://' in url:
                url = url.split('://', 1)[1]
            
            if '@' in url:
                auth, host_port = url.split('@', 1)
                username, password = auth.split(':', 1)
            else:
                username, password = None, None
                host_port = url
            
            if ':' in host_port:
                host, port = host_port.rsplit(':', 1)
                port = int(port)
            else:
                host = host_port
                port = 8080
            
            return ProxyConfig(
                provider='custom',
                endpoint=host,
                port=port,
                username=username,
                password=password
            )
        except Exception as e:
            logger.error(f"プロキシURL解析エラー: {url} - {e}")
            return None
    
    def _record_usage(self, account_id: str, proxy_url: str):
        """プロキシ使用を記録"""
        self.usage_history.append({
            'timestamp': datetime.now().isoformat(),
            'account_id': account_id,
            'proxy': self._mask_proxy_url(proxy_url),
            'provider': self.provider
        })
        
        # ログファイルに記録（必要に応じて）
        if self.config.get('monitoring', {}).get('log_usage', True):
            log_dir = Path('logs/proxy')
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / f"usage_{datetime.now().strftime('%Y%m%d')}.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} - {account_id} - {self._mask_proxy_url(proxy_url)}\n")
    
    def _mask_proxy_url(self, url: str) -> str:
        """プロキシURLの認証情報をマスク"""
        if '@' in url:
            protocol, rest = url.split('://', 1) if '://' in url else ('http', url)
            auth, host = rest.split('@', 1)
            if ':' in auth:
                user, _ = auth.split(':', 1)
                return f"{protocol}://{user}:****@{host}"
        return url
    
    def test_proxy(self, account_id: str) -> bool:
        """プロキシの接続テスト
        
        Args:
            account_id: テスト対象のアカウントID
            
        Returns:
            接続成功の場合True
        """
        import requests
        
        proxy = self.get_proxy_for_account(account_id)
        if not proxy:
            logger.info(f"[{account_id}] プロキシなしでテスト")
            return True
        
        try:
            # IPアドレス確認サービスでテスト
            response = requests.get(
                'https://api.ipify.org?format=json',
                proxies=proxy,
                timeout=10
            )
            
            if response.status_code == 200:
                ip_info = response.json()
                logger.info(f"[{account_id}] プロキシテスト成功: IP={ip_info.get('ip')}")
                return True
            else:
                logger.error(f"[{account_id}] プロキシテスト失敗: status={response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"[{account_id}] プロキシテストエラー: {e}")
            return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """使用統計を取得"""
        stats = {
            'total_requests': len(self.usage_history),
            'accounts': {},
            'provider': self.provider,
            'test_mode': self.test_mode,
            'enabled': self.enabled
        }
        
        # アカウント別の使用回数
        for record in self.usage_history:
            account_id = record['account_id']
            if account_id not in stats['accounts']:
                stats['accounts'][account_id] = 0
            stats['accounts'][account_id] += 1
        
        return stats


# モック用のプロキシマネージャー（開発・テスト用）
class MockProxyManager(ProxyManager):
    """開発・テスト用のモックプロキシマネージャー"""
    
    def __init__(self):
        super().__init__(test_mode=True)
        self.provider = 'mock'
        self.failure_rate = 0.1  # 10%の確率でエラーをシミュレート
    
    def get_proxy_for_account(self, account_id: str) -> Optional[Dict[str, str]]:
        """モックプロキシを返す（実際には直接接続）"""
        # 使用履歴に記録
        self._record_usage(account_id, "mock://proxy")
        
        # エラーシミュレーション
        if random.random() < self.failure_rate:
            logger.warning(f"[MOCK] {account_id}: プロキシエラーをシミュレート")
            raise Exception("Mock proxy connection error")
        
        logger.info(f"[MOCK] {account_id}: モックプロキシ使用（実際は直接接続）")
        return None  # 実際にはプロキシを使用しない