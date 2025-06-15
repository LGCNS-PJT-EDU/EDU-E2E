import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as playwright:
        yield playwright

@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=False, slow_mo=500)
    yield browser
    browser.close()

@pytest.fixture
def page(browser, request):
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir="videos/",  # 저장 폴더 경로
        record_video_size={"width": 1280, "height": 720}  # 선택: 해상도
    )
    page = context.new_page()
    yield page

    context.close()
