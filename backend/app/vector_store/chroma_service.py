import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.app.config import settings

class ChromaVectorService:
    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Collections
        self.profile_collection = self.client.get_or_create_collection(
            name="profile_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        self.job_collection = self.client.get_or_create_collection(
            name="job_knowledge",
            metadata={"hnsw:space": "cosine"}
        )

    def ingest_master_profile(self, user_id: int, profile_data: Dict[str, Any]):
        """Ingests structured profile items into ChromaDB with metadata isolation."""
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []

        # 1. Professional Summary
        summary = profile_data.get("summary", "")
        if summary:
            doc_id = f"user_{user_id}_summary"
            documents.append(f"Professional Summary: {summary}")
            metadatas.append({"user_id": user_id, "type": "summary", "category": "general"})
            ids.append(doc_id)

        # 2. Experience Bullets
        for exp_idx, exp in enumerate(profile_data.get("experience", [])):
            company = exp.get("company", "")
            role = exp.get("role", "")
            dates = f"{exp.get('start_date', '')} - {exp.get('end_date', '')}"
            for b_idx, bullet in enumerate(exp.get("bullets", [])):
                doc_id = f"user_{user_id}_exp_{exp_idx}_{b_idx}"
                doc_text = f"Experience at {company} as {role} ({dates}): {bullet}"
                documents.append(doc_text)
                metadatas.append({
                    "user_id": user_id,
                    "type": "experience",
                    "company": company,
                    "role": role
                })
                ids.append(doc_id)

        # 3. Projects
        for p_idx, proj in enumerate(profile_data.get("projects", [])):
            title = proj.get("title", "")
            techs = ", ".join(proj.get("technologies", []))
            for b_idx, bullet in enumerate(proj.get("bullets", [])):
                doc_id = f"user_{user_id}_proj_{p_idx}_{b_idx}"
                doc_text = f"Project {title} [Tech: {techs}]: {bullet}"
                documents.append(doc_text)
                metadatas.append({
                    "user_id": user_id,
                    "type": "project",
                    "title": title
                })
                ids.append(doc_id)

        # 4. Skills by Category
        skills = profile_data.get("skills", {})
        if isinstance(skills, dict):
            for category, skill_list in skills.items():
                doc_id = f"user_{user_id}_skills_{category.lower().replace(' ', '_').replace('&', 'and')}"
                doc_text = f"Skill Category '{category}': {', '.join(skill_list)}"
                documents.append(doc_text)
                metadatas.append({
                    "user_id": user_id,
                    "type": "skills",
                    "category": category
                })
                ids.append(doc_id)

        # 5. Education & Certifications
        for e_idx, edu in enumerate(profile_data.get("education", [])):
            doc_id = f"user_{user_id}_edu_{e_idx}"
            doc_text = f"Education: {edu.get('degree')} at {edu.get('institution')} (CGPA: {edu.get('cgpa')}, {edu.get('dates')})"
            documents.append(doc_text)
            metadatas.append({"user_id": user_id, "type": "education"})
            ids.append(doc_id)

        for c_idx, cert in enumerate(profile_data.get("certifications", [])):
            doc_id = f"user_{user_id}_cert_{c_idx}"
            doc_text = f"Certification: {cert}"
            documents.append(doc_text)
            metadatas.append({"user_id": user_id, "type": "certification"})
            ids.append(doc_id)

        if documents:
            self.profile_collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"ChromaDB: Ingested {len(documents)} profile items for user {user_id}")

    def query_profile_context(self, query: str, user_id: int, n_results: int = 6) -> List[Dict[str, Any]]:
        """Retrieves user profile facts most relevant to the job query."""
        results = self.profile_collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"user_id": user_id}
        )
        
        items = []
        if results and results.get("documents"):
            for doc, meta, doc_id in zip(results["documents"][0], results["metadatas"][0], results["ids"][0]):
                items.append({
                    "id": doc_id,
                    "content": doc,
                    "metadata": meta
                })
        return items

chroma_service = ChromaVectorService()

if __name__ == "__main__":
    import json
    profile_file = BASE_DIR / "data" / "master_profile.json"
    if profile_file.exists():
        with open(profile_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        chroma_service.ingest_master_profile(user_id=1, profile_data=data)
        
        test_query = "Looking for an AI Engineer with LangGraph and Snowflake experience"
        matches = chroma_service.query_profile_context(test_query, user_id=1, n_results=3)
        print("\nTest Retrieval Results:")
        for m in matches:
            print(f"[{m['metadata']['type']}] {m['content']}")
