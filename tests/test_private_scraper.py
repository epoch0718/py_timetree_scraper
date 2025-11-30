import pytest

private_scraper = pytest.importorskip(
    "private_scraper", reason="private_scraper.py が存在しないためテストをスキップします。"
)


def test_parse_weekly_time_extracts_time():
    parser = private_scraper.parse_weekly_time
    assert parser("2025-01-01", "7:00 〜 8:00") == "7:00"
    assert parser("2025-01-01", "09:30 開始") == "09:30"
    assert parser("2025-01-01", None) is None
    assert parser("2025-01-01", "") is None

