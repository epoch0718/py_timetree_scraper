# TimeTree to Notion Sync Tool

TimeTree（Web版）のカレンダー予定をスクレイピングし、Notionのデータベースへ自動的に同期するPythonツールです。
Playwrightを使用してデータを取得し、Asyncio（非同期処理）を用いてNotion APIへ高速に書き込みを行います。

## 特徴

*   **自動スクレイピング**: TimeTreeにログインし、過去約20週間分（設定可能）と今週・来週の予定を取得します。
*   **高速同期**: Notionへの書き込みは非同期処理（Asyncio + aiohttp）で行うため、大量のデータも素早く反映されます。
*   **画像連携**: 予定に添付された画像（最大2枚）を取得し、Notionの「ファイルとメディア」プロパティに埋め込みます。
*   **重複防止**: TimeTreeのイベントIDを用いて、既存の予定は「更新」、新しい予定は「新規作成」として処理します。
*   **除外機能**: 特定のラベルカラー（例: ディープ・スカイブルー）の予定を除外するロジックが含まれています。

## 必要要件

*   Python 3.9 以上
*   Notion インテグレーション（APIキー）
*   TimeTree アカウント

## インストール手順

1.  **リポジトリのクローンまたはファイルの配置**
    このディレクトリに `timetree_notion_week.py` と `requirements.txt` を配置します。

2.  **ライブラリのインストール**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Playwrightブラウザのインストール**
    スクレイピングに必要なブラウザバイナリをインストールします。
    ```bash
    playwright install chromium
    ```

## 設定方法

### 1. 環境変数の設定 (`.env`)

プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の情報を記述してください。

```ini
# TimeTree設定
TIMETREE_EMAIL=your_email@example.com
TIMETREE_PASSWORD=your_password
TIMETREE_CALENDAR_URL=https://timetreeapp.com/calendars/xxxxxxxxxxxx

# Notion設定
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. Notionデータベースの準備

同期先のNotionデータベースには、以下のプロパティ（列）が必須です。  
**名前が一致していないとエラーになります。**

| プロパティ名 | 種類 (Type) | 説明 |
| :--- | :--- | :--- |
| **参加者** | タイトル (Title) | イベントのタイトルが入ります |
| **教室日時** | 日付 (Date) | イベントの日時が入ります |
| **メモ** | テキスト (Text) | メモ内容が入ります |
| **TimeTreeID** | テキスト (Text) | **必須**。同期用のIDを管理します |
| **URL1** | ファイルとメディア | 1枚目の画像URLが入ります |
| **URL2** | ファイルとメディア | 2枚目の画像URLが入ります |

## 実行方法

以下のコマンドでスクリプトを実行します。

```bash
python timetree_notion_week.py
```

### 動作の流れ
1.  Chromiumブラウザが起動し、TimeTreeにログインします。
2.  カレンダーを操作し、指定期間のイベントデータを収集します。
3.  Notionから既存のデータを取得し、差分を確認します。
4.  新規・更新が必要なデータをNotionに一括送信（非同期）します。

## コード内のカスタマイズ設定

`timetree_notion_week.py` 内の以下の箇所は、必要に応じて変更してください。

*   **スクレイピング期間**: デフォルトでは過去20週間分を遡ります（`range(20)` のループ部分）。
*   **終了条件**: 特定の年月（例: `2025-07`）に到達すると処理を中断するロジックが含まれています。
*   **除外ラベル**: `scrape_one_week_events` 関数内で特定の色（ディープ・スカイブルーなど）を除外しています。

## 注意事項

*   TimeTreeのWebサイト構造が変更された場合、スクレイピング（CSSセレクタ）が機能しなくなる可能性があります。
*   Notion APIのレート制限（Rate Limits）を考慮し、非同期処理の同時実行数はコード内で制限されています（`semaphore`設定）。
