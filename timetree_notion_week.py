# timetree_notion_week.py
import os
import json
import requests
import asyncio
import aiohttp # 追加: 非同期通信用
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time

# --- 1. 設定値読み込み ---
load_dotenv()

# TimeTreeのログイン情報
TIMETREE_EMAIL = os.getenv("TIMETREE_EMAIL")
TIMETREE_PASSWORD = os.getenv("TIMETREE_PASSWORD")
CALENDAR_URL = os.getenv("TIMETREE_CALENDAR_URL")

# NotionのAPI情報
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Notionのプロパティ名マッピング
NOTION_PROPS = {
    "title": "参加者",         # タイトル
    "date" : "教室日時",       # 日付
    "memo" : "メモ",           # テキスト または リッチテキスト
    "timetree_id": "TimeTreeID", # 【重要】TimeTreeのイベントIDを保存するテキスト列
    "url1" : "URL1",           # 画像URL
    "url2" : "URL2"            # 画像URL
}

# --- 2. ヘルパー関数 (同期: 読み取り用) ---
def call_notion_api_sync(endpoint, method="POST", data=None, max_retries=3):
    """
    Notion APIを呼び出す同期関数（既存データの読み取り用）
    Requestsライブラリを使用
    """
    url = f"https://api.notion.com/v1{endpoint}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    for attempt in range(max_retries):
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "GET":
                response = requests.get(url, headers=headers)
            
            response.raise_for_status() 
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"  [Error] Sync API call failed (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise e

def get_existing_notion_pages(date_start, date_end):
    """
    Notionから指定期間のページを取得し、照合用のマップを作成する。
    """
    print(f"Checking existing Notion pages from {date_start} to {date_end}...")
    pages_map_by_id = {}    # IDでの照合用
    pages_map_by_key = {}   # 日時+タイトルでの照合用
    
    has_more = True
    next_cursor = None

    payload = {
        "filter": {
            "and": [
                {"property": NOTION_PROPS["date"], "date": {"on_or_after": date_start}},
                {"property": NOTION_PROPS["date"], "date": {"on_or_before": date_end}}
            ]
        },
        "page_size": 100
    }

    while has_more:
        if next_cursor:
            payload["start_cursor"] = next_cursor
        
        try:
            # 読み取りは同期処理のままでOK
            data = call_notion_api_sync(f"/databases/{NOTION_DATABASE_ID}/query", "POST", payload)
        except Exception as e:
            print(f"Fatal Error fetching Notion pages: {e}")
            return {}, {}

        for page in data.get("results", []):
            page_id = page["id"]
            props = page["properties"]
            
            # --- A. TimeTreeID の取得 ---
            tt_id_prop = props.get(NOTION_PROPS["timetree_id"], {})
            tt_id_list = tt_id_prop.get("rich_text", [])
            tt_id = tt_id_list[0]["plain_text"] if tt_id_list else None

            if tt_id:
                pages_map_by_id[tt_id] = page_id
            
            # --- B. タイトルと日時の取得 (フォールバック用) ---
            title_list = props.get(NOTION_PROPS["title"], {}).get("title", [])
            title = title_list[0]["plain_text"] if title_list else ""
            
            date_info = props.get(NOTION_PROPS["date"], {}).get("date", {})
            start_date_full = date_info.get("start", "")
            
            if "T" in start_date_full and len(start_date_full) >= 16:
                date_key = start_date_full[:16]
            else:
                date_key = start_date_full
            
            fallback_key = f"{date_key}_{title}"
            pages_map_by_key[fallback_key] = page_id

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")
        
    print(f"Found {len(pages_map_by_id) + len(pages_map_by_key)} existing pages in Notion buffer.")
    return pages_map_by_id, pages_map_by_key


# --- 3. 非同期APIヘルパー関数 (書き込み高速化用) ---

AUTO_IMAGE_CAPTION = "TimeTree Auto Image"


try:
    # 公開リポジトリには含めないスクレイピング関数を外部から読み込む
    from private_scraper import scrape_one_week_events
except ImportError:
    def scrape_one_week_events(*_args, **_kwargs):
        raise RuntimeError(
            "scrape_one_week_events は private_scraper.py に移動しました。"
            "ローカルでは private_scraper.py を配置し、CI では secrets から復元してください。"
        )


async def call_notion_api_async(session, endpoint, method="POST", data=None, params=None, max_retries=5):
    """
    非同期でNotion APIを呼び出す (aiohttp使用)
    レート制限(429)のハンドリングを含む
    """
    url = f"https://api.notion.com/v1{endpoint}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    for attempt in range(max_retries):
        try:
            async with session.request(method, url, headers=headers, json=data, params=params) as response:
                if response.status == 429:
                    # レート制限: Notionから返ってくるRetry-Afterヘッダを見るか、デフォルト2秒待つ
                    retry_after = int(response.headers.get("Retry-After", 2))
                    print(f"    [Rate Limit] Sleeping for {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            print(f"    [Async Error] Attempt {attempt+1}: {e}")
            await asyncio.sleep(1 * (attempt + 1))
        except Exception as e:
            raise e
            
    raise Exception("Max retries exceeded in async call")


async def append_image_blocks(session, page_id, image_urls):
    """
    指定したNotionページ本文に外部画像ブロックを追加する
    """
    await cleanup_auto_image_blocks(session, page_id)

    blocks = []
    for url in image_urls:
        if not url:
            continue
        blocks.append({
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {"url": url},
                "caption": [
                    {
                        "type": "text",
                        "text": {"content": AUTO_IMAGE_CAPTION}
                    }
                ]
            }
        })

    if not blocks:
        return

    try:
        await call_notion_api_async(
            session,
            f"/blocks/{page_id}/children",
            "PATCH",
            {"children": blocks}
        )
    except Exception as e:
        print(f"    [Warn] Failed to append image blocks: {e}")


async def cleanup_auto_image_blocks(session, page_id):
    """
    過去に自動追加した画像ブロック（キャプション一致）を削除する
    """
    next_cursor = None
    try:
        while True:
            params = {"page_size": 100}
            if next_cursor:
                params["start_cursor"] = next_cursor

            data = await call_notion_api_async(
                session,
                f"/blocks/{page_id}/children",
                "GET",
                params=params
            )

            for block in data.get("results", []):
                if block.get("type") != "image":
                    continue
                caption = block["image"].get("caption", [])
                if any(item.get("plain_text") == AUTO_IMAGE_CAPTION for item in caption):
                    block_id = block.get("id")
                    if block_id:
                        await call_notion_api_async(
                            session,
                            f"/blocks/{block_id}",
                            "DELETE"
                        )

            if not data.get("has_more"):
                break
            next_cursor = data.get("next_cursor")
    except Exception as e:
        print(f"    [Warn] Failed to cleanup image blocks: {e}")

async def sync_single_event_async(session, semaphore, event, existing_page_id):
    """
    1件のイベントを非同期で同期する
    semaphoreで同時実行数を制御する
    """
    async with semaphore:
        # 時間整形
        formatted_time = event['time'].zfill(5) 
        iso_date = f"{event['date']}T{formatted_time}:00+09:00"
        
        properties = {
            NOTION_PROPS["title"]: {
                "title": [{"text": {"content": event["title"]}}]
            },
            NOTION_PROPS["date"]: {
                "date": {"start": iso_date}
            },
            NOTION_PROPS["memo"]: {
                "rich_text": [{"text": {"content": event["memo"] or ""}}]
            },
            NOTION_PROPS["timetree_id"]: {
                "rich_text": [{"text": {"content": event["id"] or ""}}]
            }
        }

        # URL1の設定
        if event.get("url1"):
            properties[NOTION_PROPS["url1"]] = {
                "files": [
                    {
                        "name": "image.jpg",
                        "type": "external",
                        "external": {"url": event["url1"]}
                    }
                ]
            }
        
        # URL2の設定
        if event.get("url2"):
            properties[NOTION_PROPS["url2"]] = {
                "files": [
                    {
                        "name": "image.jpg",
                        "type": "external",
                        "external": {"url": event["url2"]}
                    }
                ]
            }

        try:
            page_id = existing_page_id
            if existing_page_id:
                # 更新 (PATCH)
                await call_notion_api_async(
                    session, 
                    f"/pages/{existing_page_id}", 
                    "PATCH", 
                    {"properties": properties}
                )
                print(f"  [Updated] {event['title']}")
            else:
                # 新規作成 (POST)
                payload = {
                    "parent": {"database_id": NOTION_DATABASE_ID},
                    "properties": properties
                }
                created_page = await call_notion_api_async(
                    session, 
                    "/pages", 
                    "POST", 
                    payload
                )
                page_id = created_page.get("id")
                print(f"  [Created] {event['title']}")

            if page_id and (event.get("url1") or event.get("url2")):
                await append_image_blocks(
                    session,
                    page_id,
                    [event.get("url1"), event.get("url2")]
                )
            
            # 成功したらNoneを返す
            return None

        except Exception as e:
            return {
                "title": event['title'],
                "date": f"{event['date']} {event['time']}",
                "error": str(e)
            }

async def process_sync_batch(all_events, map_by_id, map_by_key):
    """
    全イベントの同期タスクを作成し、並列実行する
    """
    # Notion APIの安全な同時リクエスト数（3～4推奨）
    semaphore = asyncio.Semaphore(3)
    
    tasks = []
    async with aiohttp.ClientSession() as session:
        for event in all_events:
            event_id = event.get('id')
            event_title = event.get('title')
            
            # 既存ページIDの特定
            existing_page_id = None
            if event_id and event_id in map_by_id:
                existing_page_id = map_by_id[event_id]
            else:
                iso_date_simple = f"{event['date']}T{event['time']}"
                fallback_key = f"{iso_date_simple}_{event_title}"
                if fallback_key in map_by_key:
                    existing_page_id = map_by_key[fallback_key]

            # タスクを作成してリストに追加
            task = sync_single_event_async(session, semaphore, event, existing_page_id)
            tasks.append(task)
        
        # 全タスクを一気に実行
        results = await asyncio.gather(*tasks)
    
    # エラー（None以外）だけを抽出して返す
    return [res for res in results if res is not None]


# --- 4. スクレイピング関数 ---
# private_scraper.py 内で定義し、公開リポジトリでは import のみ行う


# --- 5. メイン処理 ---

def main():
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        print("Error: Environment variables for Notion are not set.")
        return

    all_events = []
    
    print("--- Starting TimeTree Scraper ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--force-device-scale-factor=1.1"]
        )
        context = browser.new_context(
            timezone_id="Asia/Tokyo",
            locale="ja-JP"
        )
        page = context.new_page()

        print("Navigating to TimeTree...")
        page.goto(CALENDAR_URL, wait_until="networkidle")
        
        if "signin" in page.url:
            print("Logging in...")
            page.fill('input[type="email"]', TIMETREE_EMAIL)
            page.fill('input[type="password"]', TIMETREE_PASSWORD)
            page.click('button[type="submit"]')
        
        try:
            page.wait_for_selector('[data-test-id="weekly-calendar-root"]', timeout=40000)
            page.wait_for_load_state('networkidle')
        except:
            print("Timeout waiting for calendar to load.")
            browser.close()
            return

        print("\n--- Scraping Week ---")
        page.locator('button[value="next"]').click()
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(500)
        events,month_year = scrape_one_week_events(page)
        if events:
            all_events.extend(events)
            print(f"[{month_year}] Found {len(events)} events")

        for i in range(20):
            page.locator('button[value="previous"]').click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(500)
            events,month_year = scrape_one_week_events(page)
            if events is not None:
                all_events.extend(events)
                print(f"[{month_year}] Found {len(events)} events")
            else:
                print(f"break 2025-07")
                break

        context.close()
        browser.close()

    # --- 6. Notionへの同期処理（非同期で高速実行） ---
    print(f"\n--- Starting Async Sync to Notion (Total: {len(all_events)}) ---")
    if not all_events:
        print("No events to sync.")
        return

    # 既存データの取得（読み取りは100件ずつなので同期処理のまま）
    dates = [e['date'] for e in all_events]
    min_date = min(dates)
    max_date = max(dates)
    map_by_id, map_by_key = get_existing_notion_pages(min_date, max_date)
    
    # ★非同期で一気に書き込み実行
    failed_events = asyncio.run(process_sync_batch(all_events, map_by_id, map_by_key))

    print("\nAll sync operations completed.")

    # --- 7. 失敗ログの出力 ---
    if failed_events:
        print("\n" + "="*40)
        print(f" WARNING: {len(failed_events)} Events Failed to Sync ")
        print("="*40)
        for f in failed_events:
            print(f"- Title: {f['title']}")
            print(f"  Date : {f['date']}")
            print(f"  Error: {f['error']}")
            print("-" * 20)
    else:
        print("\nSuccess: No errors occurred.")

if __name__ == "__main__":
    main()