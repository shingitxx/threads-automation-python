"""
ThreadsのURLから投稿IDを取得するスクリプト
"""
import os
import requests
from datetime import datetime

def get_user_threads(user_id, access_token, limit=100):
    """ユーザーの投稿一覧を取得"""
    url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "fields": "id,text,timestamp,permalink",
        "limit": limit
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"エラー: {e}")
        return None

def find_post_by_url(target_url, user_id, access_token):
    """URLから投稿IDを検索"""
    # URLから短縮IDを抽出
    short_id = target_url.split("/post/")[1].split("?")[0]
    print(f"🔍 検索中の短縮ID: {short_id}")
    
    # 投稿一覧を取得
    result = get_user_threads(user_id, access_token)
    
    if not result or "data" not in result:
        print("❌ 投稿一覧の取得に失敗しました")
        return None
    
    posts = result.get("data", [])
    print(f"📊 取得した投稿数: {len(posts)}")
    
    # 各投稿をチェック
    for post in posts:
        post_id = post.get("id")
        text = post.get("text", "")[:50] + "..." if len(post.get("text", "")) > 50 else post.get("text", "")
        permalink = post.get("permalink", "")
        
        # permalinkに短縮IDが含まれているかチェック
        if short_id in permalink:
            print(f"\n✅ 見つかりました！")
            print(f"   投稿ID: {post_id}")
            print(f"   テキスト: {text}")
            print(f"   URL: {permalink}")
            return post_id
        
        # デバッグ用：すべての投稿を表示（最初の10件）
        if posts.index(post) < 10:
            print(f"\n投稿 {posts.index(post) + 1}:")
            print(f"   ID: {post_id}")
            print(f"   テキスト: {text}")
    
    print(f"\n❌ 短縮ID '{short_id}' に該当する投稿が見つかりませんでした")
    print("💡 ヒント: 投稿が古い場合は、limitパラメータを増やしてください")
    return None

def main():
    """メイン処理"""
    print("=== Threads投稿ID取得ツール ===\n")
    
    # 対象URL
    target_url = "https://www.threads.com/@mariko98909434/post/DCXs7SrJYLq"
    
    # アカウント情報を直接設定
    user_id = "24354787437458491"
    access_token = "THAAkIds0IIlZABUVE2cllhNDRiRGFzRHJzdXJmaTF3RTZAwMXpHNEVPMzJqU0Rhd1R4TkhuOTd2RjAyenRxWFZATbUxMelUyX3JhU1A2WGM2Q0k4cy1odkM5aC0xc2R6ZAGxlQjMzeVpkbHNaX3NlQ21tbzVxWXhYazBxa3U5WV9tTDV0eFU4ajhsYnpWVUVGaWMZD"
    
    print(f"🔎 検索対象URL: {target_url}")
    print(f"👤 ユーザーID: {user_id}")
    print(f"🔑 アクセストークン: {access_token[:20]}...\n")
    
    # 投稿IDを検索
    post_id = find_post_by_url(target_url, user_id, access_token)
    
    if post_id:
        print(f"\n🎉 .envファイルに以下を追加してください:")
        print(f"QUOTE_POST_ID_MARIKO={post_id}")
        
        # CSVでの使用例も表示
        print(f"\n📝 CSVでの使用方法:")
        print(f"quote_accountカラムに 'MARIKO' と記入")
        
        # 完全な設定例
        print(f"\n📋 完全な設定例:")
        print(f"1. .envファイル:")
        print(f"   QUOTE_POST_ID_MARIKO={post_id}")
        print(f"\n2. CSVファイル:")
        print(f"   ACCOUNT_ID,CONTENT_ID,main_text,image_usage,tree_post,tree_text,quote_account")
        print(f"   ACCOUNT_001,CONTENT_010,メインテキスト,YES,YES,引用コメント,MARIKO")
    else:
        print("\n💡 別の方法:")
        print("1. 投稿一覧から手動で確認")
        print("2. 新しい投稿を作成してそのIDを使用")
        print("\n📋 取得した投稿一覧を確認して、目的の投稿を探してください")

if __name__ == "__main__":
    main()