from playwright.sync_api import sync_playwright

def test_example_com():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 브라우저 실제로 뜨게 함
        page = browser.new_page()
        page.goto("https://example.com")
        assert "Example Domain" in page.title()
        page.screenshot(path="example.png")  # 결과 스크린샷 찍기
        browser.close()
