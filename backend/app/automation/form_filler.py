import os
import re
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.app.config import settings
from backend.app.automation.browser_manager import browser_manager
from backend.app.ai.form_question_answerer import form_question_answerer

logger = logging.getLogger(__name__)

class FormFiller:
    def __init__(self):
        self.screenshot_dir = Path(settings.SCREENSHOT_DIR)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    async def fill_and_submit(
        self,
        application_url: str,
        profile: Dict[str, Any],
        resume_pdf_path: str,
        auto_submit: bool = True,
        job_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Navigates to job application portal, fills fields using verified profile data,
        attaches tailored ATS resume PDF, answers custom questions with RAG grounding,
        and submits or flags for manual review if CAPTCHA appears.
        """
        if not application_url or not application_url.startswith("http"):
            return {
                "status": "failed",
                "reason": "Invalid or missing application URL",
                "evidence": None
            }

        context = await browser_manager.new_context()
        page = await context.new_page()
        page.set_default_timeout(30000)

        submission_id = uuid.uuid4().hex[:8].upper()
        screenshot_path = str(self.screenshot_dir / f"app_{submission_id}.png")

        try:
            logger.info(f"[Automation] Navigating to {application_url}...")
            await page.goto(application_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2500) # Wait for client scripts to render

            page_content = (await page.content()).lower()
            current_url = page.url.lower()

            # 1. Bot Protection / CAPTCHA Detection
            captcha_signatures = ["recaptcha", "hcaptcha", "cf-turnstile", "g-recaptcha", "challenge-running", "arkose"]
            if any(sig in page_content for sig in captcha_signatures):
                await page.screenshot(path=screenshot_path, full_page=True)
                logger.warning(f"[Automation] CAPTCHA detected on {application_url}. Flagging for human review.")
                return {
                    "status": "manual_required",
                    "reason": "CAPTCHA / Security verification challenge detected on employer portal.",
                    "screenshot_path": screenshot_path,
                    "submission_code": f"MANUAL-{submission_id}"
                }

            # 2. Login Wall Detection (e.g. requires creating an account first)
            login_indicators = ["log in to apply", "sign in with your account", "enter your password", "create an account to continue"]
            if any(ind in page_content for ind in login_indicators) and "first name" not in page_content and "first_name" not in page_content:
                await page.screenshot(path=screenshot_path, full_page=True)
                return {
                    "status": "manual_required",
                    "reason": "Employer portal requires user login/account registration before applying.",
                    "screenshot_path": screenshot_path,
                    "submission_code": f"LOGIN-{submission_id}"
                }

            # 3. Detect ATS Type and Delegate
            filled_fields: List[str] = []

            if "greenhouse.io" in current_url or await page.query_selector("#application_form, #grnhse_app"):
                logger.info("[Automation] Detected Greenhouse ATS portal.")
                await self._fill_greenhouse_form(page, profile, resume_pdf_path, job_context, filled_fields)
            elif "lever.co" in current_url or await page.query_selector("form#posting-form, .lever-form"):
                logger.info("[Automation] Detected Lever ATS portal.")
                await self._fill_lever_form(page, profile, resume_pdf_path, job_context, filled_fields)
            else:
                logger.info("[Automation] Using adaptive generic form handler.")
                await self._fill_generic_form(page, profile, resume_pdf_path, job_context, filled_fields)

            # 4. Tailored Resume File Upload (if not already handled)
            if resume_pdf_path and os.path.exists(resume_pdf_path) and "Tailored Resume PDF Attached" not in filled_fields:
                file_inputs = await page.query_selector_all("input[type='file']")
                if file_inputs:
                    try:
                        await file_inputs[0].set_input_files(resume_pdf_path)
                        filled_fields.append("Tailored Resume PDF Attached")
                        logger.info(f"[Automation] Attached tailored resume: {resume_pdf_path}")
                    except Exception as e:
                        logger.warning(f"[Automation] Resume upload notice: {e}")

            # 5. Capture pre-submission screenshot
            await page.screenshot(path=screenshot_path, full_page=True)

            # 6. Submission or Approval Handling
            if not auto_submit:
                return {
                    "status": "pending_approval",
                    "reason": "Application filled and ready for your 1-click review.",
                    "filled_fields": filled_fields,
                    "screenshot_path": screenshot_path,
                    "submission_code": f"REVIEW-{submission_id}"
                }

            # Look for submit button
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Submit Application')",
                "button:has-text('Submit application')",
                "button:has-text('Submit')",
                "button:has-text('Apply')",
                "a:has-text('Submit Application')"
            ]

            submit_btn = None
            for sel in submit_selectors:
                btn = await page.query_selector(sel)
                if btn and await btn.is_visible():
                    submit_btn = btn
                    break

            if submit_btn:
                logger.info("[Automation] Clicking submit button...")
                await submit_btn.click()
                await page.wait_for_timeout(4000)

                # Capture post-submission screenshot
                await page.screenshot(path=screenshot_path, full_page=True)

                return {
                    "status": "applied",
                    "reason": "Application submitted successfully through automated browser.",
                    "filled_fields": filled_fields,
                    "screenshot_path": screenshot_path,
                    "submission_code": f"APP-{submission_id}",
                    "submitted_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "pending_approval",
                    "reason": "Form pre-filled. Please review and click Submit on portal.",
                    "filled_fields": filled_fields,
                    "screenshot_path": screenshot_path,
                    "submission_code": f"READY-{submission_id}"
                }

        except Exception as e:
            logger.error(f"[Automation] Error during application automation: {e}")
            try:
                await page.screenshot(path=screenshot_path, full_page=True)
            except Exception:
                pass
            return {
                "status": "manual_required",
                "reason": f"Portal navigation exception: {str(e)[:150]}",
                "screenshot_path": screenshot_path if os.path.exists(screenshot_path) else None,
                "submission_code": f"ERR-{submission_id}"
            }
        finally:
            await context.close()

    async def _fill_greenhouse_form(
        self,
        page,
        profile: Dict[str, Any],
        resume_pdf_path: str,
        job_context: Optional[Dict[str, Any]],
        filled_fields: List[str]
    ):
        """Specialized Greenhouse form filler with custom question handling."""
        first_name = profile.get("first_name", "Ayush")
        last_name = profile.get("last_name", "Rao")
        email = profile.get("email", "ayushrao786420@gmail.com")
        phone = profile.get("phone", "+91-7667880422")
        linkedin = profile.get("linkedin_url", "https://linkedin.com/in/ayush-ar-rao")
        github = profile.get("github_url", "https://github.com/Ayush2412Rao")

        # Standard Greenhouse inputs
        await self._fill_selector(page, "#first_name", first_name, filled_fields, "First Name")
        await self._fill_selector(page, "#last_name", last_name, filled_fields, "Last Name")
        await self._fill_selector(page, "#email", email, filled_fields, "Email")
        await self._fill_selector(page, "#phone", phone, filled_fields, "Phone")

        # Resume upload
        if resume_pdf_path and os.path.exists(resume_pdf_path):
            file_input = await page.query_selector("input[type='file'][id*='resume'], input[type='file']")
            if file_input:
                try:
                    await file_input.set_input_files(resume_pdf_path)
                    filled_fields.append("Tailored Resume PDF Attached")
                except Exception as e:
                    logger.debug(f"Greenhouse resume attach: {e}")

        # LinkedIn & Website custom fields
        await self._fill_first_matching(page, [
            "input[autocomplete*='custom-question-linkedin']",
            "input[name*='question_'][aria-label*='LinkedIn']",
            "input[placeholder*='LinkedIn']"
        ], linkedin, filled_fields, "LinkedIn")

        await self._fill_first_matching(page, [
            "input[autocomplete*='custom-question-website']",
            "input[name*='question_'][aria-label*='Website']",
            "input[placeholder*='Website']",
            "input[placeholder*='GitHub']"
        ], github, filled_fields, "Website/GitHub")

        # Dynamic questions in Greenhouse: typically inside .field elements
        fields = await page.query_selector_all(".field")
        for field in fields:
            try:
                label_el = await field.query_selector("label")
                if not label_el:
                    continue
                label_text = (await label_el.inner_text()).strip()
                if not label_text:
                    continue

                # Check for textarea
                textarea = await field.query_selector("textarea")
                if textarea and await textarea.is_visible():
                    val = await textarea.input_value()
                    if not val:
                        ans = form_question_answerer.answer_question(label_text, job_context)
                        if ans:
                            await textarea.fill(ans)
                            filled_fields.append(f"Custom Question: {label_text[:30]}")
                    continue

                # Check for text input
                text_input = await field.query_selector("input[type='text']")
                if text_input and await text_input.is_visible():
                    val = await text_input.input_value()
                    if not val:
                        ans = form_question_answerer.answer_question(label_text, job_context)
                        if ans:
                            await text_input.fill(ans)
                            filled_fields.append(f"Custom Input: {label_text[:30]}")
                    continue

                # Check for select dropdown
                select_el = await field.query_selector("select")
                if select_el and await select_el.is_visible():
                    await self._handle_dropdown(select_el, label_text, filled_fields)
            except Exception as ex:
                logger.debug(f"Greenhouse field handling notice: {ex}")

    async def _fill_lever_form(
        self,
        page,
        profile: Dict[str, Any],
        resume_pdf_path: str,
        job_context: Optional[Dict[str, Any]],
        filled_fields: List[str]
    ):
        """Specialized Lever form filler."""
        full_name = profile.get("full_name", f"{profile.get('first_name', 'Ayush')} {profile.get('last_name', 'Rao')}")
        email = profile.get("email", "ayushrao786420@gmail.com")
        phone = profile.get("phone", "+91-7667880422")
        employer = profile.get("current_employer", "MAQ Software")
        linkedin = profile.get("linkedin_url", "https://linkedin.com/in/ayush-ar-rao")
        github = profile.get("github_url", "https://github.com/Ayush2412Rao")

        await self._fill_selector(page, "input[name='name']", full_name, filled_fields, "Full Name")
        await self._fill_selector(page, "input[name='email']", email, filled_fields, "Email")
        await self._fill_selector(page, "input[name='phone']", phone, filled_fields, "Phone")
        await self._fill_selector(page, "input[name='org']", employer, filled_fields, "Current Company")
        await self._fill_selector(page, "input[name='urls[LinkedIn]']", linkedin, filled_fields, "LinkedIn")
        await self._fill_selector(page, "input[name='urls[GitHub]']", github, filled_fields, "GitHub")

        # Resume upload
        if resume_pdf_path and os.path.exists(resume_pdf_path):
            file_input = await page.query_selector("input[type='file'][id='resume-upload-input'], input[type='file']")
            if file_input:
                try:
                    await file_input.set_input_files(resume_pdf_path)
                    filled_fields.append("Tailored Resume PDF Attached")
                except Exception as e:
                    logger.debug(f"Lever resume attach: {e}")

        # Lever Custom Questions (.application-question)
        questions = await page.query_selector_all(".application-question")
        for q in questions:
            try:
                label_el = await q.query_selector(".application-label, label")
                if not label_el:
                    continue
                label_text = (await label_el.inner_text()).strip()
                if not label_text:
                    continue

                # Textarea
                textarea = await q.query_selector("textarea")
                if textarea and await textarea.is_visible():
                    val = await textarea.input_value()
                    if not val:
                        ans = form_question_answerer.answer_question(label_text, job_context)
                        if ans:
                            await textarea.fill(ans)
                            filled_fields.append(f"Lever Question: {label_text[:30]}")
                    continue

                # Text input
                inp = await q.query_selector("input[type='text']")
                if inp and await inp.is_visible():
                    val = await inp.input_value()
                    if not val:
                        ans = form_question_answerer.answer_question(label_text, job_context)
                        if ans:
                            await inp.fill(ans)
                            filled_fields.append(f"Lever Input: {label_text[:30]}")
                    continue

                # Radio options (e.g. Yes/No questions)
                radios = await q.query_selector_all("input[type='radio']")
                if radios:
                    ans = form_question_answerer.answer_question(label_text, job_context).lower()
                    for r in radios:
                        label = await q.query_selector(f"label[for='{await r.get_attribute('id')}']")
                        radio_text = (await label.inner_text()).lower() if label else ""
                        if (ans == "yes" and "yes" in radio_text) or (ans == "no" and "no" in radio_text):
                            await r.check()
                            filled_fields.append(f"Radio Checked: {label_text[:25]}")
                            break
            except Exception as ex:
                logger.debug(f"Lever custom question error: {ex}")

    async def _fill_generic_form(
        self,
        page,
        profile: Dict[str, Any],
        resume_pdf_path: str,
        job_context: Optional[Dict[str, Any]],
        filled_fields: List[str]
    ):
        """Adaptive generic form filler covering standard and custom application questions."""
        first_name = profile.get("first_name", "Ayush")
        last_name = profile.get("last_name", "Rao")
        full_name = profile.get("full_name", f"{first_name} {last_name}")
        email = profile.get("email", "ayushrao786420@gmail.com")
        phone = profile.get("phone", "+91-7667880422")
        current_ctc = str(profile.get("current_ctc", "6 LPA"))
        expected_ctc = str(profile.get("expected_ctc", "8 - 12 LPA"))
        notice_period = str(profile.get("notice_period", "Immediate / 15 days or less"))
        linkedin = profile.get("linkedin_url", "https://linkedin.com/in/ayush-ar-rao")
        github = profile.get("github_url", "https://github.com/Ayush2412Rao")
        current_employer = profile.get("current_employer", "MAQ Software")

        await self._fill_first_matching(page, [
            "input[name*='first_name']", "input[id*='first_name']", "input[name*='firstName']", "input[id*='firstName']", "input[placeholder*='First Name']"
        ], first_name, filled_fields, "First Name")

        await self._fill_first_matching(page, [
            "input[name*='last_name']", "input[id*='last_name']", "input[name*='lastName']", "input[id*='lastName']", "input[placeholder*='Last Name']"
        ], last_name, filled_fields, "Last Name")

        await self._fill_first_matching(page, [
            "input[name*='full_name']", "input[id*='full_name']", "input[name='name']", "input[id='name']", "input[placeholder*='Full Name']"
        ], full_name, filled_fields, "Full Name")

        await self._fill_first_matching(page, [
            "input[type='email']", "input[name*='email']", "input[id*='email']", "input[placeholder*='Email']"
        ], email, filled_fields, "Email")

        await self._fill_first_matching(page, [
            "input[type='tel']", "input[name*='phone']", "input[id*='phone']", "input[name*='mobile']", "input[placeholder*='Phone']"
        ], phone, filled_fields, "Phone")

        await self._fill_first_matching(page, [
            "input[name*='current_ctc']", "input[id*='current_ctc']", "input[name*='current_salary']", "input[placeholder*='Current CTC']"
        ], current_ctc, filled_fields, "Current CTC")

        await self._fill_first_matching(page, [
            "input[name*='expected_ctc']", "input[id*='expected_ctc']", "input[name*='expected_salary']", "input[placeholder*='Expected CTC']"
        ], expected_ctc, filled_fields, "Expected CTC")

        await self._fill_first_matching(page, [
            "input[name*='notice']", "input[id*='notice']", "input[placeholder*='Notice Period']"
        ], notice_period, filled_fields, "Notice Period")

        await self._fill_first_matching(page, [
            "input[name*='linkedin']", "input[id*='linkedin']", "input[placeholder*='LinkedIn']"
        ], linkedin, filled_fields, "LinkedIn")

        await self._fill_first_matching(page, [
            "input[name*='github']", "input[id*='github']", "input[placeholder*='GitHub']"
        ], github, filled_fields, "GitHub")

        await self._fill_first_matching(page, [
            "input[name*='company']", "input[id*='company']", "input[name*='organization']", "input[placeholder*='Current Company']"
        ], current_employer, filled_fields, "Current Company")

        # Custom textareas and inputs in generic forms
        textareas = await page.query_selector_all("textarea")
        for ta in textareas:
            try:
                if await ta.is_visible():
                    current_val = await ta.input_value()
                    if not current_val:
                        # Extract label or placeholder
                        prompt = await ta.get_attribute("placeholder") or await ta.get_attribute("aria-label") or ""
                        if not prompt:
                            id_val = await ta.get_attribute("id")
                            if id_val:
                                lbl = await page.query_selector(f"label[for='{id_val}']")
                                if lbl:
                                    prompt = await lbl.inner_text()
                        if prompt:
                            ans = form_question_answerer.answer_question(prompt, job_context)
                            if ans:
                                await ta.fill(ans)
                                filled_fields.append(f"Textarea: {prompt[:25]}")
            except Exception as ex:
                logger.debug(f"Generic textarea error: {ex}")

    async def _handle_dropdown(self, select_el, label_text: str, filled_fields: List[str]):
        """Intelligently selects the best matching option in an ATS dropdown."""
        try:
            q_lower = label_text.lower()
            options = await select_el.query_selector_all("option")
            option_texts = [(await opt.inner_text()).strip() for opt in options]

            target_val = None
            if "authorized" in q_lower or "right to work" in q_lower:
                target_val = next((t for t in option_texts if "yes" in t.lower()), None)
            elif "sponsorship" in q_lower or "visa" in q_lower:
                target_val = next((t for t in option_texts if "no" in t.lower()), None)
            elif "gender" in q_lower:
                target_val = next((t for t in option_texts if "male" in t.lower() and "female" not in t.lower()), None)
            elif "veteran" in q_lower:
                target_val = next((t for t in option_texts if "not a" in t.lower() or "no" in t.lower()), None)
            elif "disability" in q_lower:
                target_val = next((t for t in option_texts if "no" in t.lower() or "do not have" in t.lower()), None)

            if target_val:
                await select_el.select_option(label=target_val)
                filled_fields.append(f"Select: {label_text[:25]}")
        except Exception as e:
            logger.debug(f"Dropdown handle notice: {e}")

    async def _fill_selector(self, page, selector: str, value: str, filled_list: List[str], label: str):
        if not value:
            return
        try:
            el = await page.query_selector(selector)
            if el and await el.is_visible():
                current_val = await el.input_value()
                if not current_val:
                    await el.fill(str(value))
                    filled_list.append(label)
        except Exception:
            pass

    async def _fill_first_matching(self, page, selectors: List[str], value: str, filled_list: List[str], label: str):
        if not value:
            return
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    current_val = await el.input_value()
                    if not current_val:
                        await el.fill(str(value))
                        filled_list.append(label)
                    return
            except Exception:
                continue

form_filler = FormFiller()

