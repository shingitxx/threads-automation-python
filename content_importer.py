# content_importer.py
import os
import json
import shutil
from pathlib import Path

def create_content_structure(account_id, content_data_list, source_images_dir=None):
    """
    アカウント用のコンテンツ構造を一括作成
    
    Args:
        account_id (str): アカウントID (例: "ACCOUNT_021")
        content_data_list (list): コンテンツデータのリスト
            [
                {
                    "content_id": "001",  # コンテンツID番号
                    "text": "投稿テキスト内容",
                    "images": ["image1.jpg", "image2.jpg"]  # ソース画像ファイル名リスト
                },
                ...
            ]
        source_images_dir (str): ソース画像が格納されているディレクトリ
    """
    # アカウントのベースディレクトリを作成
    base_dir = Path(f"accounts/{account_id}/contents")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"{account_id}のコンテンツ構造を作成します...")
    
    for content_data in content_data_list:
        content_id = content_data["content_id"]
        text = content_data["text"]
        images = content_data.get("images", [])
        
        # コンテンツディレクトリ
        content_dir = base_dir / f"{account_id}_CONTENT_{content_id.zfill(3)}"
        content_dir.mkdir(exist_ok=True)
        print(f"  - {content_dir.name}フォルダを作成")
        
        # テキストデータをmetadata.jsonに保存
        metadata = {
            "text": text,
            "original_content_id": content_id,
            "created_at": "2025-06-23"  # 現在日付を使用
        }
        
        with open(content_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"    - metadata.jsonを作成")
        
        # 画像ファイルのコピー
        if source_images_dir and images:
            for i, image_file in enumerate(images):
                source_path = Path(source_images_dir) / image_file
                if i == 0:
                    # メイン画像
                    dest_path = content_dir / "image_main.jpg"
                else:
                    # 追加画像
                    dest_path = content_dir / f"image_{i}.jpg"
                
                if source_path.exists():
                    shutil.copy(source_path, dest_path)
                    print(f"    - 画像コピー: {image_file} → {dest_path.name}")
                else:
                    print(f"    ⚠ 警告: ソース画像が見つかりません: {source_path}")
    
    print(f"{account_id}のコンテンツ構造作成が完了しました！")

# 使用例
if __name__ == "__main__":
    # コマンドライン引数を追加するなどの改良も可能
    account_id = "ACCOUNT_021"
    
    # コンテンツデータの例
    content_data_list = [
        {
            "content_id": "001",
            "text": "みんなどこに出すのが好き？\nお腹口の中\nおっπ\nあそこの中\nコメントで教えてね🫶🫶",
            "images": ["source_image1.jpg", "source_image3.jpg"]
        },
        {
            "content_id": "002",
            "text": "中って…\n緩い方がいい？きつい方がいい？\nそれともあんまり分からないかな？",
            "images": ["source_image2.jpg", "source_image3.jpg"]
        },
        {
            "content_id": "003",
            "text": "友達が47歳の男性と付き合い始めたらしい🫣\n24歳差だって！！\n凄い👏✨\n私もひと回り上の彼氏欲しいなぁ🥺\n40歳超えてる人ってなんか余裕があってそれだけでかっこよく見えるよね✨",
            "images": ["source_image1.jpg", "source_image3.jpg"]
        },
        {
            "content_id": "004",
            "text": "今月は30人卒業させる‼️🍌💦",
            "images": ["source_image2.jpg", "source_image3.jpg"]
        },
        {
            "content_id": "005",
            "text": "私がしてほしい事\nせいじょーいでべ●ち●ーして\nぎゅーって抱きつきながら\nだいしゅきホールドでしがみついてる状態で\n激しく逝●せてほしい♡\n絶対気持ちいいし脳溶ける🫠♡\nみんなしたくない？",
            "images": ["source_image1.jpg", "source_image3.jpg"]
        },
        {
            "content_id": "006",
            "text": "めちゃくちゃにされるセ●●スなんてご褒美でしかないよね。\nThreadsで会ってくれた人ありがと♥",
            "images": ["source_image2.jpg", "source_image3.jpg"]
        },
        {
            "content_id": "007",
            "text": "『どこの店にいるの？』\nってよく聞かれるけど、\nメ●エスとかキ●バにいません🤣\nに会えるから気軽に誘ってほしいのに！🍋💕",
            "images": ["source_image1.jpg", "source_image3.jpg"]
        },
        {
            "content_id": "008",
            "text": "Threads出会えすぎて笑うしかない\n最高すぎる",
            "images": ["source_image2.jpg", "source_image3.jpg"]
        }
        # 必要に応じて追加
    ]
    
    # ソース画像のディレクトリ
    source_images_dir = "source_images"
    
    # 実行
    create_content_structure(account_id, content_data_list, source_images_dir)