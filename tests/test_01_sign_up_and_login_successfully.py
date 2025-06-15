def test_example(page):
    page.goto("http://localhost:5173")
    assert "TakeIT" in page.title()

    email = "e2etest01@test.com"
    password = "Test123!"

    #회원가입으로 이동
    page.click("text=/signup/i")
    page.wait_for_url("**/signup")
    assert "/signup" in page.url

    # 닉네임 입력
    page.fill("input[placeholder='닉네임']", "E2E test")

    # # 잘못된 이메일 입력
    # page.fill("input[placeholder='이메일']", "abcde")
    # page.click("text=중복확인")
    # page.wait_for_timeout(1000)
    #
    # # 중복 이메일 입력
    # page.fill("input[placeholder='이메일']", "abc@aaa.com")
    # page.click("text=중복확인")
    # page.wait_for_timeout(1000)

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
        raise AssertionError("로그인 후 dashboard로 이동하지 않음")

    page.screenshot(path="sign_up_and_login_successfully.png")