def test_01_sign_up_and_login_successfully(page):
    page.goto("http://localhost:5173")
    assert "TakeIT" in page.title()

    email = "e2etest01@test.com"
    password = "Test123!"

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
    except Exception:
        page.screenshot(path="login_error.png")
        raise AssertionError("로그인 후 dashboard로 이동하지 않음")

    page.screenshot(path="sign_up_and_login_successfully.png")
