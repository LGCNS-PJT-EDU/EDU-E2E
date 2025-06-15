import random

def test_example(page):
    page.goto("http://localhost:5173")
    assert "TakeIT" in page.title()

    email = "e2eTotalTest01@test.com"
    password = "Test123!"

    #회원가입으로 이동
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

    #진단 페이지로 이동
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
                raise AssertionError(f"{i+1}번째 질문에서 유효한 선택지를 찾을 수 없습니다.")

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
            page.screenshot(path=f"diagnosis_error_step_{i+1}.png")
            raise e

    # 결과 페이지 도달 확인
    page.reload()
    page.wait_for_url("**/roadmap", timeout=50000)
    #assert "/roadmap" in page.url
    #page.reload()
    # 로드맵 로딩이 완료될 때까지 대기
    try:
        page.wait_for_selector("text=오늘도 학습을 시작해볼까요", timeout=5000)
    except:
        # "로드맵이 없습니다" 모달이 떠 있으면 명확히 실패 처리
        if page.is_visible("text=로드맵이 없습니다"):
            raise AssertionError("❌ 로드맵 생성 후에도 로드맵 조회 실패 (로그인 상태 확인 필요)")
        page.screenshot(path="roadmap_render_fail.png")
        raise AssertionError("❌ 로드맵 페이지에서 정상 렌더링이 되지 않았습니다.")


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

    # 사전 평가 시작
    page.click("img[alt='startBtn']")
    page.wait_for_selector("div.shadow", timeout=5000)

    for i in range(10):
        try:
            # 버튼 로딩 대기
            page.wait_for_selector("button", timeout=3000)

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

            # 다음/제출 버튼 등장 대기 및 클릭
            page.wait_for_timeout(500)  # 상태 반영 여유
            submit_btn = page.query_selector("text=제출")
            create_btn = page.query_selector("text=로드맵 생성")

            if i >= 9:
                if submit_btn and submit_btn.is_enabled():
                    submit_btn.click()
                elif create_btn and create_btn.is_enabled():
                    create_btn.click()
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

    page.wait_for_timeout(1000)
    btns = page.query_selector_all("text=해설 보기")
    btns[0].click()
    page.wait_for_timeout(2000)

    # 페이지를 천천히 스크롤
    try:
        for _ in range(7):  # 여러 번 나눠서 스크롤
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(1000)  # 1초씩 대기
        print("✅ 스크롤 완료")
    except Exception as e:
        page.screenshot(path="solution_scroll_fail.png")
        raise AssertionError("❌ 오답노트 페이지 스크롤 실패") from e

    page.click("text=/roadmap/i")
    page.wait_for_url("**/roadmap", timeout=5000)
    assert "/roadmap" in page.url

    page.wait_for_timeout(10000)

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

    # 추천 컨텐츠 확인
    try:
        scroll_area = page.query_selector("div.overflow-y-auto")

        if scroll_area:
            # Playwright evaluate를 통해 스크롤을 여러 번 천천히 내림
            for i in range(3):
                scroll_area.evaluate("(el) => el.scrollBy(0, 200)")
                page.wait_for_timeout(1000)
            print("✅ 서브젝트 스크롤 완료")
        else:
            page.screenshot(path="modal_scroll_area_not_found.png")
            raise AssertionError("❌ 스크롤 가능한 서브젝트 영역을 찾을 수 없습니다.")
    except Exception as e:
        page.screenshot(path="modal_scroll_fail.png")
        raise AssertionError("❌ 서브젝트 스크롤 실패") from e

    page.click("text=평가 리포트 보러가기")

    # 평가 리포트 페이지를 천천히 스크롤
    page.wait_for_timeout(1000)
    try:
        for _ in range(2):  # 여러 번 나눠서 스크롤
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(1000)  # 1초씩 대기
        print("✅ 스크롤 완료")
    except Exception as e:
        page.screenshot(path="solution_scroll_fail.png")
        raise AssertionError("❌ 평가 리포트 페이지 스크롤 실패") from e

    page.click("text=/roadmap/i")
    page.wait_for_url("**/roadmap", timeout=5000)
    assert "/roadmap" in page.url

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

    page.click("text=사후평가 보러가기")

    # 이동 확인
    page.wait_for_url("**/posttest**", timeout=5000)
    assert "posttest" in page.url

    # 사후 평가 시작
    page.click("img[alt='startBtn']")
    page.wait_for_selector("div.shadow", timeout=5000)

    for i in range(15):
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

            # 다음/제출 버튼 등장 대기 및 클릭
            page.wait_for_timeout(500)  # 상태 반영 여유
            submit_btn = page.query_selector("text=제출")
            create_btn = page.query_selector("text=로드맵 생성")

            if i >= 14:
                if submit_btn and submit_btn.is_enabled():
                    submit_btn.click()
                elif create_btn and create_btn.is_enabled():
                    create_btn.click()
                break
            else:
                page.wait_for_selector("text=다음 문제로", timeout=3000)
                page.click("text=다음 문제로")

        except Exception as e:
            page.screenshot(path=f"post_test_error_step_{i + 1}.png")
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

    # 한 문제의 해설 보기
    page.wait_for_timeout(1000)
    btns = page.query_selector_all("text=해설 보기")
    btns[0].click()
    page.wait_for_timeout(2000)

    # 페이지를 천천히 스크롤
    try:
        for _ in range(10):  # 여러 번 나눠서 스크롤
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(1000)  # 1초씩 대기
        print("✅ 스크롤 완료")
    except Exception as e:
        page.screenshot(path="solution_scroll_fail.png")
        raise AssertionError("❌ 오답노트 페이지 스크롤 실패") from e

    page.click("text=/roadmap/i")
    page.wait_for_url("**/roadmap", timeout=5000)
    assert "/roadmap" in page.url

    page.wait_for_timeout(2000)

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

    page.wait_for_timeout(2000)

    page.click("text=평가 리포트 보러가기")
    page.wait_for_url("**/report**", timeout=5000)
    assert "/report" in page.url

    for i in range(2):
        page.locator("button").nth(6 + i).click()
        page.wait_for_timeout(1000)

    # page.locator("button").nth(6).click()
    # page.wait_for_timeout(1000)
    # page.locator("button").nth(3).click()
    # page.wait_for_timeout(1000)
    #
    # buttons = page.query_selector_all("button")
    # print("🔍 페이지 내 버튼 목록:")
    # for i, btn in enumerate(buttons, start=1):
    #     try:
    #         text = btn.inner_text().strip()
    #         print(f"{i:02d}. '{text}'")
    #     except Exception as e:
    #         print(f"{i:02d}. (텍스트 읽기 실패): {e}")

    # MyPage 버튼 클릭
    page.click("text=MyPage")
    page.wait_for_url("**/mypage", timeout=5000)

    page.wait_for_timeout(2000)

    page.click("text=평가 리포트")
    page.wait_for_timeout(2000)

    page.click("text=추천 콘텐츠")
    page.wait_for_timeout(2000)

    page.screenshot(path="total_test.png")

