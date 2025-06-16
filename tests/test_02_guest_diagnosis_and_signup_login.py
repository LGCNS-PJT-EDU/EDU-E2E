import random


def test_02_guest_diagnosis_and_signup_login(page):
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
    page.wait_for_url("**/roadmap", timeout=50000)
    page.wait_for_timeout(2000)

    try:
        page.wait_for_selector("text=오늘도 학습을 시작해볼까요", timeout=5000)
    except:
        # "로드맵이 없습니다" 모달이 떠 있으면 명확히 실패 처리
        if page.is_visible("text=로드맵이 없습니다"):
            raise AssertionError("❌ 로드맵 생성 후에도 로드맵 조회 실패 (로그인 상태 확인 필요)")
        page.screenshot(path="roadmap_render_fail.png")
        raise AssertionError("❌ 로드맵 페이지에서 정상 렌더링이 되지 않았습니다.")

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

    page.click("text=로그인 하러가기")
    # 회원가입으로 이동
    page.click("text=/signup/i")
    page.wait_for_url("**/signup")
    assert "/signup" in page.url

    # 개인정보 동의 모달 확인 및 동의 처리
    page.wait_for_selector("text=개인정보", timeout=3000)
    page.click("text=모두 동의")  # 모달 내 동의 버튼 (정확한 텍스트 필요 시 조정)
    page.click("text=동의하고 계속")

    # 닉네임 입력
    page.fill("input[placeholder='닉네임']", "E2E test")

    # 사용 가능한 이메일 입력
    page.fill("input[placeholder='이메일']", email)
    page.click("text=중복확인")
    page.wait_for_selector("text=사용 가능한 이메일입니다.")

    # 비밀번호 입력
    page.fill("input[placeholder='비밀번호']", password)
    page.fill("input[placeholder='비밀번호 확인']", password)

    # ✅ 회원가입 버튼: 정확히 하나 선택
    btn = page.get_by_role("button", name="회원가입")
    btn.wait_for(state="visible")
    assert btn.is_enabled()
    btn.click()

    # 회원가입 완료 후 로그인 페이지 이동 확인
    page.wait_for_url("**/login", timeout=5000)
    assert "/login" in page.url

    # 로그인
    page.fill("input#email", email)
    page.fill("input#password", password)
    page.click("text=CONTINUE")

    try:
        page.wait_for_url("**/roadmap", timeout=5000)
        assert "/roadmap" in page.url
    except:
        page.screenshot(path="guest_roadmap_login_error.png")
        raise AssertionError("로그인 후 roadmap으로 이동하지 않음")

    try:
        page.wait_for_selector("text=오늘도 학습을 시작해볼까요", timeout=5000)
    except:
        # "로드맵이 없습니다" 모달이 떠 있으면 명확히 실패 처리
        if page.is_visible("text=로드맵이 없습니다"):
            raise AssertionError("❌ 로드맵 생성 후에도 로드맵 조회 실패 (로그인 상태 확인 필요)")
        page.screenshot(path="roadmap_render_fail.png")
        raise AssertionError("❌ 로드맵 페이지에서 정상 렌더링이 되지 않았습니다.")

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

    page.wait_for_timeout(3000)
    page.screenshot(path="test2_success.png")
