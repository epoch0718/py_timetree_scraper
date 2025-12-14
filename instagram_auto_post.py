"""
Instagram 自動投稿スクリプト
Instagram Graph API を使用して画像・動画を自動投稿します。

使用方法:
1. instagram_config.py に以下を設定:
   INSTAGRAM_ACCESS_TOKEN = "your_access_token"
   INSTAGRAM_ACCOUNT_ID = "your_instagram_business_account_id"

2. スクリプトを実行:
   python insta_auto.py
"""

import time
import requests
from typing import Optional

# 設定ファイルから読み込み
try:
    from instagram_config import (
        INSTAGRAM_ACCESS_TOKEN,
        INSTAGRAM_ACCOUNT_ID,
        API_VERSION
    )
except ImportError:
    print("[ERROR] instagram_config.py が見つかりません。")
    print("   instagram_config.py を作成して、アクセストークンとアカウントIDを設定してください。")
    INSTAGRAM_ACCESS_TOKEN = None
    INSTAGRAM_ACCOUNT_ID = None
    API_VERSION = "v24.0"

# 設定
CONFIG = {
    "access_token": INSTAGRAM_ACCESS_TOKEN,
    "instagram_account_id": INSTAGRAM_ACCOUNT_ID,
    "api_version": API_VERSION
}


class InstagramAPI:
    """Instagram Graph API クライアント"""
    
    def __init__(self, access_token: str = None, account_id: str = None):
        self.access_token = access_token or CONFIG["access_token"]
        self.account_id = account_id or CONFIG["instagram_account_id"]
        self.api_version = CONFIG["api_version"]
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        if not self.access_token or not self.account_id:
            raise ValueError(
                "アクセストークンとアカウントIDが必要です。\n"
                "instagram_config.py に INSTAGRAM_ACCESS_TOKEN と INSTAGRAM_ACCOUNT_ID を設定してください。"
            )
    
    def _make_request(self, method: str, endpoint: str, params: dict = None) -> dict:
        """APIリクエストを実行"""
        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        params["access_token"] = self.access_token
        
        if method.upper() == "GET":
            response = requests.get(url, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, params=params)
        else:
            raise ValueError(f"サポートされていないHTTPメソッド: {method}")
        
        return response.json()
    
    def get_account_info(self) -> dict:
        """Instagramアカウント情報を取得"""
        return self._make_request(
            "GET",
            self.account_id,
            {"fields": "id,username,name,profile_picture_url,followers_count,media_count"}
        )
    
    def create_media_container(
        self,
        image_url: str = None,
        video_url: str = None,
        caption: str = "",
        media_type: str = None,
        is_carousel_item: bool = False
    ) -> Optional[str]:
        """
        メディアコンテナを作成
        
        Args:
            image_url: 画像のURL（公開されているURL必須）
            video_url: 動画のURL（リール用）
            caption: 投稿のキャプション
            media_type: メディアタイプ（REELS, CAROUSEL など）
            is_carousel_item: カルーセルのアイテムかどうか
        
        Returns:
            コンテナID または None
        """
        params = {"caption": caption}
        
        if video_url:
            params["video_url"] = video_url
            params["media_type"] = media_type or "REELS"
        elif image_url:
            params["image_url"] = image_url
            if media_type:
                params["media_type"] = media_type
        else:
            raise ValueError("image_url または video_url が必要です")
        
        if is_carousel_item:
            params["is_carousel_item"] = "true"
            # カルーセルアイテムにはキャプションは付けられない
            params.pop("caption", None)
        
        result = self._make_request("POST", f"{self.account_id}/media", params)
        
        if "id" in result:
            print(f"[OK] メディアコンテナ作成成功: {result['id']}")
            return result["id"]
        else:
            print(f"[ERROR] メディアコンテナ作成エラー: {result}")
            return None
    
    def check_media_status(self, container_id: str) -> dict:
        """メディアコンテナのステータスを確認（動画処理用）"""
        return self._make_request(
            "GET",
            container_id,
            {"fields": "status_code,status"}
        )
    
    def wait_for_media_ready(self, container_id: str, timeout: int = 300, interval: int = 10) -> bool:
        """
        メディアの処理完了を待機
        
        Args:
            container_id: コンテナID
            timeout: タイムアウト秒数
            interval: チェック間隔秒数
        
        Returns:
            処理完了したかどうか
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.check_media_status(container_id)
            status_code = status.get("status_code", "")
            
            print(f"[WAIT] ステータス: {status_code}")
            
            if status_code == "FINISHED":
                print("[OK] メディア処理完了")
                return True
            elif status_code == "ERROR":
                print(f"[ERROR] メディア処理エラー: {status}")
                return False
            elif status_code == "IN_PROGRESS":
                time.sleep(interval)
            else:
                # 画像の場合はステータスコードがない場合もある
                return True
        
        print("[ERROR] タイムアウト")
        return False
    
    def publish_media(self, container_id: str) -> Optional[str]:
        """
        メディアを公開
        
        Args:
            container_id: 公開するメディアコンテナのID
        
        Returns:
            投稿ID または None
        """
        result = self._make_request(
            "POST",
            f"{self.account_id}/media_publish",
            {"creation_id": container_id}
        )
        
        if "id" in result:
            print(f"[SUCCESS] 投稿成功! Post ID: {result['id']}")
            return result["id"]
        else:
            print(f"[ERROR] 投稿エラー: {result}")
            return None
    
    def post_image(self, image_url: str, caption: str = "") -> Optional[str]:
        """
        画像を投稿（シンプルな方法）
        
        Args:
            image_url: 画像のURL（公開されているURL必須）
            caption: 投稿のキャプション
        
        Returns:
            投稿ID または None
        """
        print(f"[INFO] 画像を投稿中: {image_url[:50]}...")
        
        # Step 1: コンテナ作成
        container_id = self.create_media_container(image_url=image_url, caption=caption)
        if not container_id:
            return None
        
        # 少し待機
        time.sleep(5)
        
        # Step 2: 公開
        return self.publish_media(container_id)
    
    def post_reel(self, video_url: str, caption: str = "", share_to_feed: bool = True) -> Optional[str]:
        """
        リール動画を投稿
        
        Args:
            video_url: 動画のURL（公開されているURL必須）
            caption: 投稿のキャプション
            share_to_feed: フィードにも共有するか
        
        Returns:
            投稿ID または None
        """
        print(f"[INFO] リールを投稿中: {video_url[:50]}...")
        
        # Step 1: コンテナ作成
        params = {
            "video_url": video_url,
            "caption": caption,
            "media_type": "REELS"
        }
        if share_to_feed:
            params["share_to_feed"] = "true"
        
        container_id = self.create_media_container(**params)
        if not container_id:
            return None
        
        # Step 2: 動画処理完了を待機
        if not self.wait_for_media_ready(container_id):
            return None
        
        # Step 3: 公開
        return self.publish_media(container_id)
    
    def post_carousel(self, media_urls: list, caption: str = "") -> Optional[str]:
        """
        カルーセル投稿（複数画像）
        
        Args:
            media_urls: 画像URLのリスト（2〜10枚）
            caption: 投稿のキャプション
        
        Returns:
            投稿ID または None
        """
        if len(media_urls) < 2 or len(media_urls) > 10:
            print("[ERROR] カルーセルは2〜10枚の画像が必要です")
            return None
        
        print(f"[INFO] カルーセル投稿中: {len(media_urls)}枚の画像")
        
        # Step 1: 各画像のコンテナを作成
        children_ids = []
        for i, url in enumerate(media_urls):
            print(f"  画像 {i+1}/{len(media_urls)}: {url[:50]}...")
            container_id = self.create_media_container(
                image_url=url,
                is_carousel_item=True
            )
            if container_id:
                children_ids.append(container_id)
            else:
                print(f"[ERROR] 画像 {i+1} のコンテナ作成に失敗")
                return None
        
        # Step 2: カルーセルコンテナを作成
        result = self._make_request(
            "POST",
            f"{self.account_id}/media",
            {
                "media_type": "CAROUSEL",
                "caption": caption,
                "children": ",".join(children_ids)
            }
        )
        
        if "id" not in result:
            print(f"[ERROR] カルーセルコンテナ作成エラー: {result}")
            return None
        
        carousel_container_id = result["id"]
        print(f"[OK] カルーセルコンテナ作成成功: {carousel_container_id}")
        
        # 少し待機
        time.sleep(5)
        
        # Step 3: 公開
        return self.publish_media(carousel_container_id)
    
    def get_recent_media(self, limit: int = 10) -> list:
        """最近の投稿を取得"""
        result = self._make_request(
            "GET",
            f"{self.account_id}/media",
            {"fields": "id,caption,media_type,timestamp,permalink", "limit": limit}
        )
        return result.get("data", [])


def main():
    """メイン関数 - テスト投稿"""
    
    print("=" * 50)
    print("Instagram 自動投稿スクリプト")
    print("=" * 50)
    
    # APIクライアントを初期化
    try:
        api = InstagramAPI()
    except ValueError as e:
        print(f"[ERROR] 初期化エラー: {e}")
        return
    
    # アカウント情報を確認
    print("\n[INFO] アカウント情報を取得中...")
    account_info = api.get_account_info()
    if "username" in account_info:
        print(f"  ユーザー名: @{account_info.get('username')}")
        print(f"  フォロワー数: {account_info.get('followers_count', 'N/A')}")
        print(f"  投稿数: {account_info.get('media_count', 'N/A')}")
    else:
        print(f"  アカウント情報取得エラー: {account_info}")
        return
    
    # メニュー表示
    print("\n" + "=" * 50)
    print("操作を選択してください")
    print("=" * 50)
    print("1. テスト画像を投稿")
    print("2. カスタム画像URLで投稿")
    print("3. 最近の投稿を表示")
    print("0. 終了")
    
    choice = input("\n選択 (0-3): ").strip()
    
    if choice == "1":
        # テスト画像投稿
        test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/320px-Camponotus_flavomarginatus_ant.jpg"
        test_caption = "Instagram APIからの自動投稿テスト!\n\n#自動投稿 #Python #API"
        
        print(f"\n[INFO] テスト画像を投稿します...")
        post_id = api.post_image(test_image_url, test_caption)
        if post_id:
            print(f"\n[SUCCESS] テスト投稿完了! Post ID: {post_id}")
    
    elif choice == "2":
        # カスタム画像URL投稿
        image_url = input("画像URL（公開URL）: ").strip()
        caption = input("キャプション: ").strip()
        
        if not image_url:
            print("[ERROR] 画像URLが必要です")
            return
        
        print(f"\n[INFO] 画像を投稿します...")
        post_id = api.post_image(image_url, caption)
        if post_id:
            print(f"\n[SUCCESS] 投稿完了! Post ID: {post_id}")
    
    elif choice == "3":
        # 最近の投稿表示
        print("\n[INFO] 最近の投稿を取得中...")
        media_list = api.get_recent_media(limit=5)
        
        if media_list:
            for i, media in enumerate(media_list, 1):
                print(f"\n--- 投稿 {i} ---")
                print(f"  ID: {media.get('id')}")
                print(f"  タイプ: {media.get('media_type')}")
                print(f"  日時: {media.get('timestamp')}")
                caption = media.get('caption', '')
                if caption:
                    print(f"  キャプション: {caption[:50]}...")
                print(f"  URL: {media.get('permalink')}")
        else:
            print("  投稿がありません")
    
    elif choice == "0":
        print("終了します")
    
    else:
        print("[ERROR] 無効な選択です")


def test_post():
    """テスト投稿を直接実行（スクリプトから呼び出し用）"""
    api = InstagramAPI()
    
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/320px-Camponotus_flavomarginatus_ant.jpg"
    test_caption = "Instagram APIからの自動投稿テスト!\n\n#自動投稿 #Python #API"
    
    return api.post_image(test_image_url, test_caption)


if __name__ == "__main__":
    main()
