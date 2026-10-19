import sys
from pathlib import Path

# Add workspace root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
from backend.app.db.session import sync_engine, Base, SyncSessionLocal
from backend.app.models.user import User, UserProfile, JobPreference, QuestionnaireAnswer
from backend.app.models.job import DiscoveredJob, JobMatchEvaluation
from backend.app.models.application import ResumeDocument, ResumeVersion, JobApplication, AgentRun, AgentRunEvent, NotificationRecord

def initialize_database():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=sync_engine)
    print("Database tables created successfully.")

    session = SyncSessionLocal()
    try:
        user = session.query(User).filter(User.email == "ayushrao786420@gmail.com").first()
        if not user:
            print("Creating primary user: ayushrao786420@gmail.com")
            user = User(
                email="ayushrao786420@gmail.com",
                full_name="Ayush Rao",
                hashed_password="hashed_placeholder_for_local_auth",
                is_active=True
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        profile_path = BASE_DIR / "data" / "master_profile.json"
        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
            
            existing_profile = session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            if not existing_profile:
                print("Seeding verified master user profile...")
                profile = UserProfile(
                    user_id=user.id,
                    contact_info=profile_data.get("contact", {}),
                    professional_summary=profile_data.get("summary", ""),
                    skills=profile_data.get("skills", {}),
                    experience=profile_data.get("experience", []),
                    education=profile_data.get("education", []),
                    projects=profile_data.get("projects", []),
                    certifications=profile_data.get("certifications", []),
                    is_verified=True
                )
                session.add(profile)

        pref_path = BASE_DIR / "data" / "preferences.json"
        if pref_path.exists():
            with open(pref_path, "r", encoding="utf-8") as f:
                pref_data = json.load(f)

            existing_pref = session.query(JobPreference).filter(JobPreference.user_id == user.id).first()
            if not existing_pref:
                print("Seeding user job preferences...")
                pref = JobPreference(
                    user_id=user.id,
                    target_titles=pref_data.get("target_titles", []),
                    preferred_locations=pref_data.get("preferred_locations", []),
                    remote_preference=pref_data.get("remote_preference", "hybrid_or_remote"),
                    min_match_score=pref_data.get("min_match_score", 75),
                    max_applications_per_hour=pref_data.get("max_applications_per_hour", 5),
                    max_applications_per_day=pref_data.get("max_applications_per_day", 25),
                    automation_mode=pref_data.get("automation_mode", "automatic"),
                    work_authorization=pref_data.get("work_authorization", "Authorized to work in India (Citizen)"),
                    requires_sponsorship=pref_data.get("requires_sponsorship", False),
                    notice_period_days=pref_data.get("notice_period_days", 15)
                )
                session.add(pref)

        q_path = BASE_DIR / "data" / "questionnaire_answers.json"
        if q_path.exists():
            with open(q_path, "r", encoding="utf-8") as f:
                q_data = json.load(f)

            print("Seeding verified questionnaire answers...")
            for key, val in q_data.items():
                existing_q = session.query(QuestionnaireAnswer).filter(
                    QuestionnaireAnswer.user_id == user.id,
                    QuestionnaireAnswer.question_key == key
                ).first()
                if not existing_q:
                    q_ans = QuestionnaireAnswer(
                        user_id=user.id,
                        question_key=key,
                        question_text=key.replace("_", " ").capitalize(),
                        answer_value=json.dumps(val) if isinstance(val, (dict, list)) else str(val),
                        status="verified",
                        category="general"
                    )
                    session.add(q_ans)

        session.commit()
        print("Database initialized and seeded successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    initialize_database()
