import pytest
from backend.app.ai.form_question_answerer import form_question_answerer
from backend.app.notifications.email_scanner import email_scanner
from backend.app.discovery.scrapers.spiders.hirist_spider import HiristSpider

def test_form_question_answerer_deterministic():
    # Notice period
    ans_np = form_question_answerer.answer_question("What is your notice period?")
    assert "15" in ans_np or "Immediate" in ans_np

    # CTC
    ans_ctc = form_question_answerer.answer_question("What is your expected salary?")
    assert "LPA" in ans_ctc or "1000000" in ans_ctc

    # Citizenship / Authorization
    ans_auth = form_question_answerer.answer_question("Are you legally authorized to work in India?")
    assert ans_auth == "Yes"

    # Visa sponsorship
    ans_visa = form_question_answerer.answer_question("Will you require visa sponsorship?")
    assert ans_visa == "No"

    # Relocation
    ans_reloc = form_question_answerer.answer_question("Are you willing to relocate to Bangalore?")
    assert ans_reloc == "Yes"

    # Specific skill experience
    ans_py = form_question_answerer.answer_question("How many years of experience do you have with Python?")
    assert "2" in ans_py or "Python" in ans_py

def test_email_scanner_classification():
    # Interview
    res_interview = email_scanner._classify_email(
        "Invitation to Interview: Software Engineer at Acme Corp",
        "We would love to schedule a call with you to meet the team on Google Meet."
    )
    assert res_interview == "interview_scheduled"

    # Assessment
    res_test = email_scanner._classify_email(
        "Technical Assessment Link - Acme Corp",
        "Please complete the online coding test on HackerRank within 48 hours."
    )
    assert res_test == "assessment_received"

    # Under Review
    res_review = email_scanner._classify_email(
        "Thank you for applying to Kinetik AI",
        "We have received your application and our recruitment team is reviewing your application."
    )
    assert res_review == "under_review"

    # Rejection
    res_rejection = email_scanner._classify_email(
        "Update on your application",
        "Unfortunately, after careful consideration, we have decided to pursue other candidates."
    )
    assert res_rejection == "rejected"

    # Offer
    res_offer = email_scanner._classify_email(
        "Job Offer: Software Engineer at Kinetik AI",
        "We are pleased to offer you the position of Software Engineer! Please review the offer letter."
    )
    assert res_offer == "offer"

def test_hirist_spider_init():
    spider = HiristSpider(queries="python,ai", locations="Noida,Bangalore", experience="1", max_items="10")
    assert spider.name == "hirist"
    assert len(spider.start_urls) > 0
    assert any("hirist.tech" in u for u in spider.start_urls)
