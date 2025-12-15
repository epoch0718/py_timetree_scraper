# Instagram & LINE 自動投稿・通知システム 設定ガイド

このドキュメントは、Instagram Graph APIとLINE Messaging APIを使った自動化システムの設定手順をまとめたものです。

---

## 目次

1. [Instagram Graph API 設定](#1-instagram-graph-api-設定)
2. [LINE 自動メッセージ送信](#2-line-自動メッセージ送信)
3. [お客様向けLINEリマインドシステム](#3-お客様向けlineリマインドシステム)

---

# 1. Instagram Graph API 設定

## 1.1 前提条件

Instagram Graph APIを使用するには以下が必要です：

| 必須項目 | 説明 |
|---------|------|
| Instagramプロアカウント | ビジネスまたはクリエイターアカウント |
| Facebookページ | Instagramと連携するページ |
| Facebookアカウント | 開発者登録用 |
| 公開URL（任意） | 画像投稿には画像の公開URLが必要 |

---

## 1.2 Instagramプロアカウントの作成

### 手順：

1. **Instagramアプリを開く**
2. **プロフィール画面に移動** → 右上の「≡」（メニュー）をタップ
3. **「設定とプライバシー」** をタップ
4. **「アカウントの種類とツール」** をタップ
5. **「プロアカウントに切り替える」** をタップ
6. **カテゴリを選択**（例：デジタルクリエイター、ブロガーなど）
7. **アカウントタイプを選択**
   - **ビジネス**：企業・ブランド向け
   - **クリエイター**：個人・インフルエンサー向け
8. **連絡先情報を入力**（任意）
9. **「完了」** をタップ

---

## 1.3 Facebookページの作成と連携

### 1.3.1 Facebookページの作成

1. **Facebook** (https://www.facebook.com/) にログイン
2. 右上の **「+」** → **「ページ」** をクリック
3. 以下を入力：
   - **ページ名**：任意の名前
   - **カテゴリ**：適切なものを選択
   - **自己紹介**：任意
4. **「Facebookページを作成」** をクリック

**または直接アクセス**：
```
https://www.facebook.com/pages/create
```

### 1.3.2 InstagramとFacebookページの連携

**方法A：Instagramアプリから**

1. Instagramアプリで **プロフィール** → **「プロフェッショナルダッシュボード」**
2. **「アカウント設定」** → **「リンク済みアカウント」**
3. **「Facebook」** を選択
4. 連携したい **Facebookページを選択**
5. **「完了」** をタップ

**方法B：Facebookから**

1. Facebookページの **「設定」** を開く
2. **「リンク済みアカウント」** または **「Instagram」** をクリック
3. **「アカウントをリンク」** をクリック
4. Instagramの **ログイン情報を入力**
5. **「確認」** をクリック

---

## 1.4 Meta for Developersでのアプリ作成

### 1.4.1 開発者アカウントの登録

1. **Meta for Developers** (https://developers.facebook.com/) にアクセス
2. 右上の **「ログイン」** をクリック
3. Facebookアカウントでログイン
4. 初回の場合は **「開発者として登録」** をクリック
5. **利用規約に同意** して登録完了

### 1.4.2 アプリの作成

1. **「マイアプリ」** をクリック
2. **「アプリを作成」** ボタンをクリック
3. **ユースケースを選択**：
   - **「その他」** を選択 → **「次へ」**
4. **アプリタイプを選択**：
   - **「ビジネス」** を選択 → **「次へ」**
5. **アプリ情報を入力**：
   - **アプリ名**：任意（例：`MyInstagramApp`）
   - **連絡先メールアドレス**：有効なメールアドレス
   - **ビジネスアカウント**：（あれば選択、なければスキップ）
6. **「アプリを作成」** をクリック
7. パスワードを入力して **認証**

---

## 1.5 Facebookログインでの設定

### 1.5.1 製品を追加

1. アプリのダッシュボードで左メニューの **「製品を追加」** または **「製品」** セクションを探す
2. **「Facebookログイン」** を見つけて **「設定」** をクリック
3. **「ウェブ」** を選択（Pythonなどでバックエンドから使う場合）
4. サイトURLを入力（開発中は `https://localhost/` でOK）

### 1.5.2 Facebookログインの設定

左メニュー → **「Facebookログイン」** → **「設定」**

| 設定項目 | 推奨値 |
|---------|-------|
| クライアントOAuthログイン | **オン** |
| ウェブOAuthログイン | **オン** |
| HTTPSを強制 | **オン** |

**「変更を保存」** をクリック

---

## 1.6 必要な権限の追加

### 1.6.1 アプリレビュー画面へ

1. 左メニュー → **「アプリレビュー」** → **「アクセス許可と機能」**

### 1.6.2 権限を追加（開発モード用）

以下の権限を探して **「追加」** をクリック：

| 権限名 | 用途 |
|-------|------|
| `pages_show_list` | 管理しているページ一覧を取得 |
| `pages_read_engagement` | ページのエンゲージメント情報 |
| `instagram_basic` | Instagram基本情報の取得 |
| `instagram_content_publish` | **投稿する（最重要）** |
| `business_management` | ビジネスアセット管理 |

---

## 1.7 Graph API エクスプローラーでアクセストークン取得

### 1.7.1 エクスプローラーを開く

**Graph API エクスプローラー**にアクセス：
```
https://developers.facebook.com/tools/explorer/
```

または、左メニュー → **「ツール」** → **「グラフAPIエクスプローラ」**

### 1.7.2 アプリの選択

右上のドロップダウンで：
- **Metaアプリ**: 作成したアプリを選択
- **ユーザーまたはページ**: ユーザートークン

### 1.7.3 権限の追加

**「アクセス許可を追加」** ボタンをクリックして、以下にチェック：

```
✅ pages_show_list
✅ pages_read_engagement
✅ business_management
✅ instagram_basic
✅ instagram_content_publish
```

### 1.7.4 トークンの生成

1. **「Generate Access Token」** （アクセストークンを取得）をクリック
2. Facebookのログイン画面が表示される
3. **「〇〇としてログイン」** をクリック
4. 許可する項目を確認して **「OK」** をクリック
5. **連携するFacebookページ**を選択
6. **連携するInstagramアカウント**を選択
7. **「完了」** をクリック

---

## 1.8 InstagramビジネスアカウントIDの取得

### APIリクエスト

Graph API エクスプローラーで、以下を入力して **「送信」**：

```
me/accounts?fields=id,name,access_token,instagram_business_account
```

### レスポンス例

```json
{
  "data": [
    {
      "id": "947573568438321",
      "name": "Ai大好きおじさん",
      "access_token": "EAAV...(ページアクセストークン)...",
      "instagram_business_account": {
        "id": "17841403181337231"
      }
    }
  ]
}
```

### メモすべき情報

| 項目 | レスポンスのキー | 用途 |
|-----|----------------|------|
| ページID | `"id": "947573568438321"` | API呼び出しに使用 |
| ページアクセストークン | `"access_token": "EAAV..."` | **無期限で有効！投稿に使う** |
| InstagramビジネスアカウントID | `"instagram_business_account.id": "17841403181337231"` | **投稿先のID** |

---

## 1.9 取得した認証情報（実際の値）

```
ページ名:         Ai大好きおじさん
ページID:         947573568438321
InstagramアカウントID: 17841403181337231

ページアクセストークン:
EAAVVE3fjarQBQI59yX9gHIhb4GztIoxxNchIWnJaZA9omTRgWTZCnYbvX1vvAmLZAXZAa9u80KrQXrMUCjHSx1eJN2ZAePU8BNKzdqPE68YKxbma6yPv4DeMo2g4SK3DIf0lBo2taIwQHupz3yhtkTgboHGiWGIq3glyarByrXz4wpTfMCPESNdrii6fN7CbkY9vUaTN4ylvOqN1cz0oWjFTADdg3ZCfZAw6QbskNvJ3ZCi0d6DaVVGEFTeBly4ZD
```

**注意**: このトークンは安全な場所に保存し、公開しないでください！

---

## 1.10 Pythonコード（Instagram自動投稿）

### instagram_config.py

```python
"""
Instagram API 設定ファイル
※このファイルは .gitignore に追加してください！
"""

# ページアクセストークン（Graph API エクスプローラーで取得）
INSTAGRAM_ACCESS_TOKEN = "EAAVVE3fjarQBQI59yX9g..."

# InstagramビジネスアカウントID
INSTAGRAM_ACCOUNT_ID = "17841403181337231"

# APIバージョン
API_VERSION = "v24.0"
```

### insta_auto.py（メインスクリプト）

```python
"""
Instagram 自動投稿スクリプト
Instagram Graph API を使用して画像・動画を自動投稿します。
"""

import time
import requests
from typing import Optional

from instagram_config import (
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_ACCOUNT_ID,
    API_VERSION
)

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
                "アクセストークンとアカウントIDが必要です。"
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
    
    def post_image(self, image_url: str, caption: str = "") -> Optional[str]:
        """
        画像を投稿
        
        Args:
            image_url: 画像のURL（公開されているURL必須）
            caption: 投稿のキャプション
        
        Returns:
            投稿ID または None
        """
        print(f"[INFO] 画像を投稿中: {image_url[:50]}...")
        
        # Step 1: コンテナ作成
        result = self._make_request(
            "POST",
            f"{self.account_id}/media",
            {"image_url": image_url, "caption": caption}
        )
        
        if "id" not in result:
            print(f"[ERROR] メディアコンテナ作成エラー: {result}")
            return None
        
        container_id = result["id"]
        print(f"[OK] メディアコンテナ作成成功: {container_id}")
        
        # 少し待機
        time.sleep(5)
        
        # Step 2: 公開
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
    
    def post_carousel(self, media_urls: list, caption: str = "") -> Optional[str]:
        """カルーセル投稿（複数画像）"""
        if len(media_urls) < 2 or len(media_urls) > 10:
            print("[ERROR] カルーセルは2〜10枚の画像が必要です")
            return None
        
        # 各画像のコンテナを作成
        children_ids = []
        for url in media_urls:
            result = self._make_request(
                "POST",
                f"{self.account_id}/media",
                {"image_url": url, "is_carousel_item": "true"}
            )
            if "id" in result:
                children_ids.append(result["id"])
        
        # カルーセルコンテナを作成
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
            return None
        
        time.sleep(5)
        
        # 公開
        result = self._make_request(
            "POST",
            f"{self.account_id}/media_publish",
            {"creation_id": result["id"]}
        )
        
        return result.get("id")
    
    def post_reel(self, video_url: str, caption: str = "") -> Optional[str]:
        """リール動画を投稿"""
        # コンテナ作成
        result = self._make_request(
            "POST",
            f"{self.account_id}/media",
            {
                "video_url": video_url,
                "caption": caption,
                "media_type": "REELS"
            }
        )
        
        if "id" not in result:
            return None
        
        container_id = result["id"]
        
        # 動画処理完了を待機
        while True:
            status = self._make_request(
                "GET",
                container_id,
                {"fields": "status_code"}
            )
            if status.get("status_code") == "FINISHED":
                break
            elif status.get("status_code") == "ERROR":
                return None
            time.sleep(10)
        
        # 公開
        result = self._make_request(
            "POST",
            f"{self.account_id}/media_publish",
            {"creation_id": container_id}
        )
        
        return result.get("id")


# 使用例
if __name__ == "__main__":
    api = InstagramAPI()
    
    # アカウント情報を表示
    info = api.get_account_info()
    print(f"ユーザー名: @{info.get('username')}")
    
    # 画像を投稿
    # api.post_image(
    #     image_url="https://example.com/image.jpg",
    #     caption="自動投稿テスト #Python #API"
    # )
```

---

## 1.11 テスト投稿結果

テスト投稿を実行し、成功しました：

```
==================================================
Instagram テスト投稿
==================================================

[INFO] アカウント情報を取得中...
  ユーザー名: @taro.ninyonyo
  フォロワー数: 2307

[INFO] テスト画像を投稿します...
[INFO] 画像を投稿中: https://upload.wikimedia.org/wikipedia/commons/thu...
[OK] メディアコンテナ作成成功: 18432953659106045
[SUCCESS] 投稿成功! Post ID: 18116307988504962

==================================================
[SUCCESS] テスト投稿が完了しました!
Post ID: 18116307988504962
==================================================
```

---

## 1.12 重要な注意点

### API制限
- **1時間あたり200リクエスト** が上限（目安）
- 投稿は **1日25件まで** の制限あり

### 画像要件
| 項目 | 要件 |
|-----|------|
| 形式 | JPEG |
| 最大サイズ | 8MB |
| アスペクト比 | 4:5 〜 1.91:1 |
| 最小解像度 | 320px |
| 最大解像度 | 1440px |

### 動画要件（リール）
| 項目 | 要件 |
|-----|------|
| 形式 | MP4, MOV |
| 最大サイズ | 1GB |
| 長さ | 3秒〜15分 |
| アスペクト比 | 9:16（推奨） |

### 画像URLについて
- 画像は**インターネット上で公開されているURL**が必要
- ローカルファイルは直接アップロードできません
- AWS S3、Cloudflare R2、Firebase Storageなどを利用してください

---

# 2. LINE 自動メッセージ送信

## 2.1 自分宛てに通知を送る方法（LINE Notify）

### 2.1.1 LINE Notifyとは

**自分宛ての通知を送信**するのに最適です。無料で簡単に使えます。

| 項目 | 内容 |
|-----|------|
| 料金 | **無料** |
| 難易度 | **簡単**（トークン取得のみ） |
| 用途 | 自分 or グループへの通知 |
| 制限 | 1時間に1000回まで |

### 2.1.2 設定手順

#### Step 1: LINE Notifyにアクセス
```
https://notify-bot.line.me/ja/
```

#### Step 2: トークンを発行
1. **ログイン**（LINEアカウントで）
2. 右上の **「マイページ」** をクリック
3. **「トークンを発行する」** をクリック
4. **トークン名**を入力（例：`自動通知`）
5. **通知先**を選択：
   - 「**1:1でLINE Notifyから通知を受け取る**」 ← 自分宛て
   - または特定のグループ
6. **「発行する」** をクリック
7. 表示されたトークンを**コピーして保存**（一度しか表示されません！）

### 2.1.3 Pythonコード

```python
import requests

LINE_NOTIFY_TOKEN = "あなたのトークン"

def send_line_message(message: str):
    """LINEに通知を送信"""
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": message}
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        print("[OK] LINE通知を送信しました")
    else:
        print(f"[ERROR] 送信失敗: {response.text}")
    
    return response.status_code == 200

# 使用例
send_line_message("\n今日のタスクが完了しました！")
```

### 2.1.4 画像も送れます

```python
def send_line_with_image(message: str, image_path: str):
    """画像付きでLINE通知を送信"""
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": message}
    
    with open(image_path, "rb") as f:
        files = {"imageFile": f}
        response = requests.post(url, headers=headers, data=data, files=files)
    
    return response.status_code == 200
```

---

# 3. お客様向けLINEリマインドシステム

## 3.1 概要

お客様に個別にLINEでリマインドを送信するシステムです。

### 連絡手段の比較

| 方法 | 必要な情報 | 費用 | 到達率 | 難易度 |
|-----|-----------|------|-------|-------|
| **LINE公式アカウント** | 友達追加が必要 | 無料枠あり | 高い | 中 |
| **メール** | メールアドレス | 無料〜 | 中 | 低 |
| **SMS** | 電話番号 | 有料(約10円/通) | 非常に高い | 低 |

---

## 3.2 LINE公式アカウント + Messaging API

### 3.2.1 特徴
- **無料枠**：月200通まで無料
- **有料プラン**：月5,000円〜で5,000通以上
- お客様の**開封率が高い**（メールより読まれやすい）

### 3.2.2 設定手順

#### Step 1: LINE公式アカウントを作成
```
https://www.linebiz.com/jp/entry/
```
1. LINEビジネスIDでログイン
2. 公式アカウントを作成

#### Step 2: Messaging APIを有効化
1. **LINE Official Account Manager** にログイン
2. **設定** → **Messaging API** → **有効化**
3. **LINE Developers** でチャネルアクセストークンを取得

#### Step 3: 応答設定

| 項目 | 設定 |
|-----|------|
| 応答モード | **Bot** |
| あいさつメッセージ | オン/オフ（お好みで） |
| 応答メッセージ | **オフ** |
| Webhook | **オン** |

#### Step 4: お客様に友達追加してもらう
- QRコードを送る
- URLを送る（`https://line.me/R/ti/p/@xxxx`）

### 3.2.3 料金プラン

| プラン | 月額 | 無料メッセージ数 |
|-------|------|-----------------|
| コミュニケーション | 無料 | 200通 |
| ライト | 5,000円 | 5,000通 |
| スタンダード | 15,000円 | 30,000通 |

---

## 3.3 自動リマインドシステムの流れ

```
┌─────────────────────────────────────────────────────────────┐
│                    自動リマインドシステム                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ① お客様がLINE公式アカウントに友達追加・メッセージ送信        │
│                      ↓                                      │
│  ② WebhookでLINE User IDを取得                              │
│                      ↓                                      │
│  ③ Notionのお客様DBに登録（お客様名 + LINE User ID）          │
│                      ↓                                      │
│  ④ 毎日スクリプトを実行（例：夕方18時）                       │
│      │                                                      │
│      ├─→ TimeTreeから明日の予定を取得                        │
│      │                                                      │
│      ├─→ 予定に含まれるお客様をNotionで検索                   │
│      │                                                      │
│      └─→ LINE User IDがあるお客様にリマインド送信             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3.4 Notionの顧客DBの構成例

| プロパティ名 | タイプ | 説明 |
|------------|-------|------|
| 名前 | タイトル | お客様の名前 |
| LINE User ID | テキスト | `U1234567890...` |
| メールアドレス | メール | 連絡先 |
| 電話番号 | 電話 | 連絡先 |
| メモ | テキスト | 備考 |

---

## 3.5 Pythonコード（LINE Messaging API）

```python
import requests
from typing import Optional

class LINEMessaging:
    """LINE Messaging APIクライアント"""
    
    def __init__(self, channel_access_token: str):
        self.token = channel_access_token
        self.base_url = "https://api.line.me/v2/bot"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def send_message(self, user_id: str, message: str) -> bool:
        """特定のユーザーにメッセージを送信"""
        url = f"{self.base_url}/message/push"
        data = {
            "to": user_id,
            "messages": [{"type": "text", "text": message}]
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            print(f"[OK] メッセージ送信成功: {user_id[:10]}...")
            return True
        else:
            print(f"[ERROR] 送信失敗: {response.text}")
            return False
    
    def send_to_multiple(self, user_ids: list, message: str) -> bool:
        """複数のユーザーに同じメッセージを送信（最大500人）"""
        url = f"{self.base_url}/message/multicast"
        data = {
            "to": user_ids,
            "messages": [{"type": "text", "text": message}]
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.status_code == 200
    
    def send_with_buttons(self, user_id: str, title: str, text: str, buttons: list) -> bool:
        """ボタン付きメッセージを送信"""
        url = f"{self.base_url}/message/push"
        data = {
            "to": user_id,
            "messages": [{
                "type": "template",
                "altText": title,
                "template": {
                    "type": "buttons",
                    "title": title,
                    "text": text,
                    "actions": buttons
                }
            }]
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.status_code == 200
```

---

## 3.6 お客様へリマインド + 自分にも通知

```python
class LineReminder:
    def __init__(self, messaging_token: str, notify_token: str):
        """
        messaging_token: LINE公式アカウントのチャネルアクセストークン
        notify_token: LINE Notifyのトークン（自分用）
        """
        self.messaging_token = messaging_token
        self.notify_token = notify_token
    
    def send_to_customer(self, user_id: str, message: str) -> bool:
        """お客様にLINE送信（Messaging API）"""
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Authorization": f"Bearer {self.messaging_token}",
            "Content-Type": "application/json"
        }
        data = {
            "to": user_id,
            "messages": [{"type": "text", "text": message}]
        }
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200
    
    def send_to_self(self, message: str) -> bool:
        """自分にLINE通知（LINE Notify）"""
        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {self.notify_token}"}
        data = {"message": message}
        response = requests.post(url, headers=headers, data=data)
        return response.status_code == 200
    
    def send_reminder(self, customer_name: str, customer_line_id: str, 
                      event_datetime: str, event_title: str):
        """お客様にリマインド送信 + 自分にも通知"""
        
        # お客様へのメッセージ
        customer_message = f"""明日のご予約のリマインドです。

日時: {event_datetime}
内容: {event_title}

よろしくお願いいたします。"""
        
        # お客様に送信
        success = self.send_to_customer(customer_line_id, customer_message)
        
        # 自分にも通知
        if success:
            self_message = f"""
【リマインド送信完了】
お客様: {customer_name}
日時: {event_datetime}
内容: {event_title}
ステータス: 送信成功"""
        else:
            self_message = f"""
【リマインド送信失敗】
お客様: {customer_name}
日時: {event_datetime}
※確認してください"""
        
        self.send_to_self(self_message)
        
        return success
```

---

## 3.7 TimeTree + Notion + LINE 連携の処理フロー

```python
from datetime import datetime, timedelta

def send_tomorrow_reminders():
    """明日の教室のお客様にリマインドを送信"""
    
    # 1. TimeTreeから明日の予定を取得
    tomorrow = datetime.now() + timedelta(days=1)
    events = timetree.get_events_for_date(tomorrow)
    
    # 2. 教室の予定を抽出
    lesson_events = [e for e in events if "教室" in e["title"]]
    
    # 3. 各予定のお客様にリマインド送信
    for event in lesson_events:
        customer_name = event["title"]
        
        # Notionからお客様情報を検索
        customer = notion.search_customer(customer_name)
        
        if customer and customer.get("line_user_id"):
            # LINEでリマインド送信
            reminder.send_reminder(
                customer_name=customer_name,
                customer_line_id=customer["line_user_id"],
                event_datetime=event['start_time'],
                event_title=event['title']
            )
            print(f"[OK] {customer_name} にリマインド送信")
        else:
            print(f"[SKIP] {customer_name} - LINE未登録")


# 毎日夕方に実行
if __name__ == "__main__":
    send_tomorrow_reminders()
```

---

## 3.8 自動実行の設定（Windows タスクスケジューラー）

毎日18時に自動実行する設定：

1. **タスクスケジューラ**を開く
2. **「タスクの作成」**
3. **トリガー**: 毎日 18:00
4. **操作**: `python C:\Users\sinzy\py_timetree_scraper\line_reminder.py`

---

# 参考リンク

## Instagram関連
- [Meta for Developers](https://developers.facebook.com/)
- [Instagram Graph API 公式ドキュメント](https://developers.facebook.com/docs/instagram-api/)
- [Graph API エクスプローラー](https://developers.facebook.com/tools/explorer/)
- [Content Publishing API](https://developers.facebook.com/docs/instagram-api/guides/content-publishing/)

## LINE関連
- [LINE Notify](https://notify-bot.line.me/ja/)
- [LINE for Business](https://www.linebiz.com/jp/)
- [LINE Developers](https://developers.line.biz/)
- [LINE Messaging API ドキュメント](https://developers.line.biz/ja/docs/messaging-api/)

---

# 作成日

2024年12月15日

