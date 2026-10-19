import os
import re
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from backend.app.config import settings
from backend.app.automation.browser_manager import browser_manager

class FormFiller:
    def __init__(self):
        self.screenshot_dir = Path(settings.SCREENSHOT_DIR)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    async def fill_and_submit(
        self,
        application_url: str,
        profile: Dict[str, Any],
        resume_pdf_path: str,
        auto_submit: bool = True
    ) -> Dict[str, Any]:
        """Navigates to job application portal, fills fields using verified profile data,
        attaches tailored ATS resume PDF, and submits or flags for manual review if CAPTCHA appears.
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
            print(f"[Automation] Navigating to {application_url}...")
            await page.goto(application_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2500) # Wait for client scripts to render

            page_content = (await page.content()).lower()

            # 1. Bot Protection / CAPTCHA Detection
            captcha_signatures = ["recaptcha", "hcaptcha", "cf-turnstile", "g-recaptcha", "challenge-running", "arkose"]
            if any(sig in page_content for sig in captcha_signatures):
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"[Automation] CAPTCHA detected on {application_url}. Flagging for human review.")
                return {
                    "status": "manual_required",
                    "reason": "CAPTCHA / Security verification challenge detected on employer portal.",
                    "screenshot_path": screenshot_path,
                    "submission_code": f"MANUAL-{submission_id}"
                }

            # 2. Login Wall Detection (e.g. requires creating an account first)
            login_indicators = ["log in to apply", "sign in with your account", "enter your password"]
            if any(ind in page_content for ind in login_indicators) and "first name" not in page_content:
                await page.screenshot(path=screenshot_path, full_page=True)
                return {
                    "status": "manual_required",
                    "reason": "Employer portal requires user login/account registration before applying.",
                    "screenshot_path": screenshot_path,
                    "submission_code": f"LOGIN-{submission_id}"
                }

            # 3. Form Field Detection & Auto-Filling
            filled_fields = []

            # First Name / Last Name / Full Name
            first_name = profile.get("first_name", "Ayush")
            last_name = profile.get("last_name", "Rao")
            full_name = profile.get("full_name", f"{first_name} {last_name}")

            await self._fill_first_matching(page, [
                "input[name*='first_name']", "input[id*='first_name']", "input[name*='firstName']", "input[id*='firstName']", "input[placeholder*='First Name']"
            ], first_name, filled_fields, "First Name")

            await self._fill_first_matching(page, [
                "input[name*='last_name']", "input[id*='last_name']", "input[name*='lastName']", "input[id*='lastName']", "input[placeholder*='Last Name']"
            ], last_name, filled_fields, "Last Name")

            await self._fill_first_matching(page, [
                "input[name*='full_name']", "input[id*='full_name']", "input[name*='name']", "input[id*='name']", "input[placeholder*='Full Name']"
            ], full_name, filled_fields, "Full Name")

            # Email
            email = profile.get("email", "ayushrao786420@gmail.com")
            await self._fill_first_matching(page, [
                "input[type='email']", "input[name*='email']", "input[id*='email']", "input[placeholder*='Email']"
            ], email, filled_fields, "Email")

            # Phone
            phone = profile.get("phone", "+91-7667880422")
            await self._fill_first_matching(page, [
                "input[type='tel']", "input[name*='phone']", "input[id*='phone']", "input[name*='mobile']", "input[placeholder*='Phone']"
            ], phone, filled_fields, "Phone")

            # Current CTC & Expected CTC
            current_ctc = str(profile.get("current_ctc", "6 LPA"))
            expected_ctc = str(profile.get("expected_ctc", "7 - 12 LPA"))
            await self._fill_first_matching(page, [
                "input[name*='current_ctc']", "input[id*='current_ctc']", "input[name*='current_salary']", "input[placeholder*='Current CTC']"
            ], current_ctc, filled_fields, "Current CTC")

            await self._fill_first_matching(page, [
                "input[name*='expected_ctc']", "input[id*='expected_ctc']", "input[name*='expected_salary']", "input[placeholder*='Expected CTC']"
            ], expected_ctc, filled_fields, "Expected CTC")

            # Notice Period
            notice_period = str(profile.get("notice_period", "Immediate / 15 days or less"))
            await self._fill_first_matching(page, [
                "input[name*='notice']", "input[id*='notice']", "input[placeholder*='Notice Period']", "select[name*='notice']"
            ], notice_period, filled_fields, "Notice Period")

            # URLs (LinkedIn / GitHub / Portfolio)
            linkedin = profile.get("linkedin_url", "https://linkedin.com/in/ayush-ar-rao")
            await self._fill_first_matching(page, [
                "input[name*='linkedin']", "input[id*='linkedin']", "input[placeholder*='LinkedIn']"
            ], linkedin, filled_fields, "LinkedIn")

            github = profile.get("github_url", "https://github.com/Ayush2412Rao")
            await self._fill_first_matching(page, [
                "input[name*='github']", "input[id*='github']", "input[placeholder*='GitHub']"
            ], github, filled_fields, "GitHub")

            # Current Company & Job Title
            current_employer = profile.get("current_employer", "MAQ Software")
            await self._fill_first_matching(page, [
                "input[name*='company']", "input[id*='company']", "input[name*='organization']", "input[placeholder*='Current Company']"
            ], current_employer, filled_fields, "Current Company")

            # 4. Tailored Resume File Upload
            if resume_pdf_path and os.path.exists(resume_pdf_path):
                file_inputs = await page.query_selector_all("input[type='file']")
                if file_inputs:
                    try:
                        await file_inputs[0].set_input_files(resume_pdf_path)
                        filled_fields.append("Tailored Resume PDF Attached")
                        print(f"[Automation] Attached tailored resume: {resume_pdf_path}")
                    except Exception as e:
                        print(f"[Automation] Resume upload notice: {e}")

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
                print(f"[Automation] Clicking submit button...")
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
            print(f"[Automation] Error during application automation: {e}")
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

    async def _fill_first_matching(self, page, selectors, value, filled_list, label):
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
