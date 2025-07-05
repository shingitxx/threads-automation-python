# run_instagram_creator.py を以下のように修正
import sys
import os

# パスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from instagram_automation.instagram_creator_with_kukulu import InstagramCreatorWithKukulu

def main():
    print("=== Instagram自動アカウント作成（kuku.lu版） ===")
    
    creator = InstagramCreatorWithKukulu(use_proxy=False)
    
    if creator.create_account():
        print("\n✅ アカウント作成完了！")
    else:
        print("\n❌ アカウント作成失敗")

if __name__ == "__main__":
    main()