import random

def test_example(page):
    page.goto("http://localhost:5173")
    assert "TakeIT" in page.title()

    email = "testGuestDiagnosis01@test.com"
    password = "Test123!"

    page.click("text=/roadmap/i")
    page.wait_for_url("**/roadmap", timeout=5000)
    assert "/roadmap" in page.url

    # 진단 페이지로 이동
    page.wait_for_selector("text=로드맵이 없습니다", timeout=3000)
    page.click("text=진단하러 가기")

    # 진단 페이지 도달 확인
    page.wait_for_url("**/diagnosis", timeout=5000)
    assert "/diagnosis" in page.url

    # 진단 시작
    page.click("img[alt='startBtn']")
    page.wait_for_selector("div.shadow", timeout=5000)

    max_questions = 10  # 진단 문항 예상 수
    answered = 0

    for i in range(max_questions):
        try:
            # 선택지가 로딩될 때까지 기다림
            page.wait_for_selector("button", timeout=5000)

            # 모든 버튼 중에서 텍스트가 비어있지 않은 버튼만 필터링
            buttons = page.query_selector_all("button")
            choices = []
            for btn in buttons:
                text = btn.inner_text().strip()
                if (
                        btn.is_enabled()
                        and text
                        and "다음 문제로" not in btn.inner_text()
                        and "이전 문제로" not in btn.inner_text()
                        and "제출" not in btn.inner_text()
                        and "로드맵 생성" not in btn.inner_text()
                        and text not in ["LogIn", "SignUp", "MyPage", "Logout", "ROADMAP", "INTERVIEW", "CONTACT"]
                ):
                    choices.append((btn, text))

            if not choices:
                raise AssertionError(f"{i + 1}번째 질문에서 유효한 선택지를 찾을 수 없습니다.")

            # 랜덤 선택
            selected, selected_text = random.choice(choices)
            print(f"✅ [Q{i + 1}] 선택된 버튼: '{selected_text}'")
            selected.click()
            answered += 1

            # 다음 또는 제출 버튼 클릭
            if page.is_visible("text=제출") or page.is_visible("text=로드맵 생성"):
                if page.is_visible("text=제출"):
                    page.click("text=제출")
                elif page.is_visible("text=로드맵 생성"):
                    page.click("text=로드맵 생성")
                break
            else:
                page.click("text=다음 문제로")

        except Exception as e:
            page.screenshot(path=f"diagnosis_error_step_{i + 1}.png")
            raise e

    # 결과 페이지 도달 확인
    page.reload()
    page.wait_for_url("**/roadmap", timeout=50000)
    # assert "/roadmap" in page.url
    # page.reload()
    # 로드맵 로딩이 완료될 때까지 대기
    try:
        page.wait_for_selector("text=오늘도 학습을 시작해볼까요", timeout=5000)
    except:
        # "로드맵이 없습니다" 모달이 떠 있으면 명확히 실패 처리
        if page.is_visible("text=로드맵이 없습니다"):
            raise AssertionError("❌ 로드맵 생성 후에도 로드맵 조회 실패 (로그인 상태 확인 필요)")
        page.screenshot(path="roadmap_render_fail.png")
        raise AssertionError("❌ 로드맵 페이지에서 정상 렌더링이 되지 않았습니다.")

    # 회원가입으로 이동
    page.click("text=/signup/i")
    page.wait_for_url("**/signup")
    assert "/signup" in page.url

    # 닉네임 입력
    page.fill("input[placeholder='닉네임']", "E2E test")

    # 사용 가능한 이메일 입력
    page.fill("input[placeholder='이메일']", email)
    page.click("text=중복확인")

    # 비밀번호 입력
    page.fill("input[placeholder='비밀번호']", password)
    page.fill("input[placeholder='비밀번호 확인']", password)

    # Join In 버튼 클릭
    page.click("text=Join In")

    # 회원가입 완료 후 로그인 페이지 이동 확인
    page.wait_for_url("**/login", timeout=5000)
    assert "/login" in page.url

    # 이메일 입력
    page.fill("input#email", email)

    # 비밀번호 입력
    page.fill("input#password", password)

    # 로그인 버튼 클릭
    page.click("text=CONTINUE")

    try:
        page.wait_for_url("**/roadmap", timeout=5000)
        assert "/roadmap" in page.url
    except:
        page.screenshot(path="login_error.png")
        raise AssertionError("로그인 후 /roadmap으로 이동하지 않음")