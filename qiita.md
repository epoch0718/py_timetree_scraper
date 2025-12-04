# 公開リポジトリ × 無料 GitHub Actions を最大活用して TimeTree → Notion 同期を自動化する方法

TimeTree の予定を Notion に同期する自動化を、**一切課金せず** GitHub Actions だけで永久運用できたら嬉しくないですか？  
この記事では、公開リポジトリのまま機密ロジックを守りつつ、10 分ごとに走るスクレイピング＆同期基盤を構築するための実践テクニックを紹介します。

---

## ゴール

- GitHub Actions（Public リポジトリ枠）を完全無料で回し続ける
- 公開したくないロジック／認証情報は **Secrets への埋め込みだけ** で守る
- TimeTree から取得した予定を Notion データベースへ同期し、画像も添付する

---

## リポジトリのURL
https://github.com/epoch0718/py_timetree_scraper.git
git cloneしても使えません。　（笑）

## 仕組みの全体像

1. **公開リポジトリ** にメインスクリプト (`timetree_notion_week.py`) とワークフロー (`.github/workflows/main.yml`) を置く  
2. **スクレイピングのコア部分 (`private_scraper.py`) と `.env`** はリポジトリから分離  
3. GitHub Actions の **Secrets** に `PRIVATE_SCRAPER` / `ENV_FILE` として全文を保存  
4. ワークフロー起動時に Secrets からファイルを書き戻し → スクリプトを実行  
5. TimeTree からイベントを取り込み、非同期で Notion API へ同期

> ポイント：公開リポジトリでも「重要ロジックは置いていない」ので、悪用される心配がありません。

---

## フォルダ構成（公開側）

```
py_timetree_scraper/
├─ .github/
│   └─ workflows/
│       └─ main.yml        # GitHub Actions 定義
├─ timetree_notion_week.py # メインスクリプト（スクレイピング関数は外部 import）
├─ requirements.txt
├─ README.md
└─ .gitignore              # private_scraper.py / .env を除外
```

### 秘密ファイルの扱い

- `private_scraper.py` … スクレイピングロジックを丸ごと格納（公開しない）
- `.env` … TimeTree/Notion の認証情報

どちらも `.gitignore` に追加し、レポジトリには存在しません。

---

## GitHub Actions ワークフロー（核心部分）

```yaml
# .github/workflows/main.yml の抜粋 (10分刻みで自動実行)
on:
  schedule:
    - cron: "*/10 * * * *"
  workflow_dispatch:

jobs:
  scrape-and-update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - run: pip install -r requirements.txt

      - name: Restore .env from secret
        run: |
          printf '%s' "$ENV_FILE" > .env
        env:
          ENV_FILE: ${{ secrets.ENV_FILE }}

      - name: Restore private scraper
        run: |
          printf '%s' "$PRIVATE_SCRAPER" > private_scraper.py
        env:
          PRIVATE_SCRAPER: ${{ secrets.PRIVATE_SCRAPER }}

      - run: python timetree_notion_week.py
```

### なぜこれで機密が守られる？

- 公開リポジトリ側には機密ロジックを一切置いていない  
- GitHub Actions が起動する瞬間だけ Secrets からファイルを復元し、処理終了後には runner が破棄される  
- 誰かがリポジトリをクローンしても、肝心の `private_scraper.py` が無いのでスクレイピングはできない

---

## Secrets 登録手順（ENV_FILE / PRIVATE_SCRAPER）

1. `.env`、`private_scraper.py` の内容をコピー  
2. GitHub のリポジトリ設定 → `Settings > Secrets and variables > Actions`  
3. `New repository secret` で以下を登録

| 名前 | 内容 |
| ---- | ---- |
| `ENV_FILE` | `.env` の全文（改行込み） |
| `PRIVATE_SCRAPER` | `private_scraper.py` の全文 |

貼り付けるだけで OK。Base64 変換などは不要です。

---

## ローカル開発との両立

1. `private_scraper.py` と `.env` をローカルのプロジェクト直下に配置  
2. `python timetree_notion_week.py` を実行するだけで動作  
3. 万が一ファイルを消してしまっても、**非公開バックアップリポジトリ**（例: `py_timetree_scraper_private_scraper`）へ push しておけば、すぐ復元可能

> バックアップリポジトリは Private にして、アクセス権限を最小化するのがコツ。

---

## この構成のメリット

- **永遠に無料**  
  公開リポジトリは GitHub Actions の無料枠が潤沢。cron で 10 分ごとに回しても課金の心配なし。

- **スクレイピングロジックを秘匿**  
  `private_scraper.py` が無いと TimeTree の DOM セレクタや除外ルールはわからない＝悪用されない。

- **Secrets 一括管理**  
  `.env` も含めて Secrets に突っ込んでおけるので、環境差分がなく再現性も高い。

- **Playwright + 非同期 Notion API**  
  画像添付や TimeTreeID ベースの差分更新など、実用的な同期ロジックをそのまま流用できる。

---

## まとめ

公開リポジトリでも「見せたい部分だけを公開し、核となるロジックは別ファイル＋Secrets」に分離すれば、GitHub Actions を完全無料でフル稼働させつつ、安全に運用できます。  
スクレイピングパートを非公開化しているので、リポジトリ自体は「コード全体を見たい人には無意味」＝悪用されない状態をキープできます。

あなたの自動化ワークフローでも、同じ方法で「無料かつ安全」な仕組みを構築してみてください！


