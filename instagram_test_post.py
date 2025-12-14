"""
Instagram テスト投稿スクリプト
実行すると自動的にテスト画像を投稿します
"""

from insta_auto import InstagramAPI

def main():
    print("=" * 50)
    print("Instagram テスト投稿")
    print("=" * 50)
    
    # APIクライアント初期化
    api = InstagramAPI()
    
    # アカウント情報を表示
    print("\n[INFO] アカウント情報を取得中...")
    account_info = api.get_account_info()
    print(f"  ユーザー名: @{account_info.get('username')}")
    print(f"  フォロワー数: {account_info.get('followers_count', 'N/A')}")
    
    # テスト画像を投稿
    print("\n[INFO] テスト画像を投稿します...")
    
    # Wikipediaの無料画像（蟻の画像）
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/320px-Camponotus_flavomarginatus_ant.jpg"
    test_caption = "Instagram Graph APIからの自動投稿テスト!\n\n#自動投稿 #Python #API #テスト"
    
    post_id = api.post_image(test_image_url, test_caption)
    
    if post_id:
        print("\n" + "=" * 50)
        print("[SUCCESS] テスト投稿が完了しました!")
        print(f"Post ID: {post_id}")
        print("=" * 50)
        print("\nInstagramアプリで投稿を確認してください!")
    else:
        print("\n[ERROR] 投稿に失敗しました")


if __name__ == "__main__":
    main()

