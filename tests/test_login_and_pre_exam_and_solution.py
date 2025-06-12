import random

def test_example(page):
    page.goto("http://localhost:5173")
    assert "TakeIT" in page.title()

    email = "e2etest4@test.com"
    password = "Test123!"

    page.click("text=/login/i")

    #이메일 입력
    page.fill("input#email", email)

    #비밀번호 입력
    page.fill("input#password", password)

    # 로그인 버튼 클릭
    page.click("text=CONTINUE")

    try:
        page.wait_for_url("**/roadmap", timeout=5000)
        assert "/roadmap" in page.url
    except:
        page.screenshot(path="login_error.png")
        raise AssertionError("로그인 후 /roadmap으로 이동하지 않음")


    # 첫 번째 과목 노드 이미지 클릭
    try:
        # 모든 노드 아이콘을 가져옴
        nodes = page.query_selector_all("img")

        # 라벨과 위치 정보가 없으므로 icon 크기로 필터링 (w-7 h-7 → width 28px 기준)
        for img in nodes:
            bounding = img.bounding_box()
            if bounding and bounding['width'] in (28, 29):  # pixel 크기 기준 필터링
                img.click()
                print("✅ 첫 번째 과목 노드 클릭 성공")
                break
        else:
            page.screenshot(path="subject_click_fail.png")
            raise AssertionError("❌ 첫 번째 과목 노드 이미지를 찾지 못했습니다.")

    except Exception as e:
        page.screenshot(path="subject_click_error.png")
        raise AssertionError("❌ 첫 번째 과목 클릭 중 오류 발생") from e

    page.click("text=사전평가 보러가기")

    # 이동 확인
    page.wait_for_url("**/pretest**", timeout=5000)
    assert "pretest" in page.url

    # 평가 시작
    page.click("img[alt='startBtn']")
    page.wait_for_selector("div.shadow", timeout=5000)

    max_questions = 10
    answered = 0

    for i in range(max_questions):
        try:
            # 버튼 로딩 대기
            page.wait_for_selector("button", timeout=5000)

            # 선택지 필터링
            buttons = page.query_selector_all("button")
            choices = []
            for btn in buttons:
                text = btn.inner_text().strip()
                if (
                        btn.is_enabled()
                        and text
                        and "다음 문제로" not in text
                        and "이전 문제로" not in text
                        and "제출" not in text
                        and "로드맵 생성" not in text
                        and text not in ["LogIn", "SignUp", "MyPage", "Logout", "ROADMAP", "INTERVIEW", "CONTACT"]
                ):
                    choices.append((btn, text))

            if not choices:
                raise AssertionError(f"{i + 1}번째 질문에서 유효한 선택지를 찾을 수 없습니다.")

            # 랜덤 선택
            selected, selected_text = random.choice(choices)
            print(f"✅ [Q{i + 1}] 선택된 버튼: '{selected_text}'")
            selected.click(force=True)
            answered += 1

            # 다음/제출 버튼 등장 대기 및 클릭
            page.wait_for_timeout(500)  # 상태 반영 여유
            if page.is_visible("text=제출") or page.is_visible("text=로드맵 생성"):
                if page.is_visible("text=제출"):
                    page.click("text=제출")
                elif page.is_visible("text=로드맵 생성"):
                    page.click("text=로드맵 생성")
                break
            else:
                page.wait_for_selector("text=다음 문제로", timeout=3000)
                page.click("text=다음 문제로")

        except Exception as e:
            page.screenshot(path=f"diagnosis_error_step_{i + 1}.png")
            raise e

    # "오답노트 보러 가기" 모달 버튼 클릭
    try:
        page.wait_for_selector("text=오답노트 보러 가기", timeout=5000)
        page.click("text=오답노트 보러 가기")
        print("✅ 오답노트 보러 가기 클릭 완료")

        # 오답노트 페이지 로드 확인
        # page.wait_for_url("**/solution?subjectId=", timeout=5000)
        # assert "solution" in page.url
    except Exception as e:
        page.screenshot(path="solution_button_click_fail.png")
        raise AssertionError("❌ 오답노트 보러 가기 클릭 실패") from e

    # 페이지를 천천히 스크롤
    try:
        for _ in range(5):  # 여러 번 나눠서 스크롤
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(1000)  # 1초씩 대기
        print("✅ 스크롤 완료")
    except Exception as e:
        page.screenshot(path="solution_scroll_fail.png")
        raise AssertionError("❌ 오답노트 페이지 스크롤 실패") from e


