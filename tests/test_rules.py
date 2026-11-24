from screener.rules import screen, load_profile, fee_flags

P = load_profile()

def test_fee_is_risky():
    r = screen({"title": "Intern", "text": "Pay Rs 2000 as registration fee", "location": "Chennai"}, P)
    assert r.label == "Risky"

def test_good_fit():
    r = screen({"title": "QA Intern", "text": "Postman, JIRA and manual testing", "location": "Bengaluru"}, P)
    assert r.label == "Good fit"

def test_wrong_city_needs_check():
    r = screen({"title": "Data Intern", "text": "SQL and Excel", "location": "Jaipur"}, P)
    assert r.label == "Check carefully"

def test_remote_ok():
    r = screen({"title": "ML Intern", "text": "Python and pandas", "location": "Work from home"}, P)
    assert r.label == "Good fit"

def test_clean_text_has_no_fee_flag():
    assert fee_flags("Stipend 10000 per month, Python required") == []


def test_unpaid_with_big_salary_promise_and_mass_hiring_is_risky():
    text = ("Unpaid. Work from home. On successful conversion the candidate can expect a salary of "
            "₹ 880000 to 940000/year. Python and SQL. Opportunities posted: 387; Candidates hired: 5773.")
    r = screen({"title": "Data Intern", "text": text, "location": "Work from home"}, P)
    assert r.label == "Risky"

def test_very_low_stipend_is_not_good_fit():
    text = "Python and SQL. ₹ 5,000 - 8,000 /month. Work from home."
    r = screen({"title": "Data Intern", "text": text, "location": "Work from home"}, P)
    assert r.label == "Check carefully"

def test_comment_interested_plus_gmail_is_risky():
    text = 'Data analyst. Comment "INTERESTED" to get details. Email resume to hr123@gmail.com'
    r = screen({"title": "Analyst", "text": text, "location": "Remote"}, P)
    assert r.label == "Risky"
