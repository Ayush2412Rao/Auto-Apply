import sys
import os
import json
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Base project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCRAPERS_DIR = Path(__file__).resolve().parent / "scrapers"

def run_spider(
    spider_name: str,
    queries: Optional[List[str]] = None,
    locations: Optional[List[str]] = None,
    experience: int = 1,
    max_items: int = 30,
    timeout_seconds: int = 60
) -> List[Dict[str, Any]]:
    """Runs a Scrapy spider in an isolated subprocess to prevent Twisted/Asyncio reactor collisions."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
        tmp_output_path = tmp_file.name

    try:
        # Build spider args
        q_str = ",".join(queries) if queries else "Software Engineer,AI Engineer,Python,Data Engineer"
        loc_str = ",".join(locations) if locations else "Noida,Gurgaon,Delhi,Bangalore,Remote"

        cmd = [
            sys.executable,
            "-m", "scrapy", "crawl", spider_name,
            "-a", f"queries={q_str}",
            "-a", f"locations={loc_str}",
            "-a", f"experience={experience}",
            "-a", f"max_items={max_items}",
            "-O", tmp_output_path,
            "-s", "LOG_LEVEL=WARNING",
            "-s", "DOWNLOAD_TIMEOUT=15",
        ]

        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        env["SCRAPY_SETTINGS_MODULE"] = "backend.app.discovery.scrapers.settings"

        logger.info(f"Running Scrapy spider '{spider_name}' (max_items={max_items})...")
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )

        if result.returncode != 0:
            logger.warning(
                f"Scrapy spider '{spider_name}' exited with code {result.returncode}. Stderr: {result.stderr[:300]}"
            )

        # Read output JSON
        if os.path.exists(tmp_output_path) and os.path.getsize(tmp_output_path) > 0:
            try:
                with open(tmp_output_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        logger.info(f"Spider '{spider_name}' successfully scraped {len(data)} items.")
                        return data
            except Exception as read_err:
                logger.error(f"Error reading Scrapy output from {tmp_output_path}: {read_err}")

        return []
    except subprocess.TimeoutExpired:
        logger.warning(f"Scrapy spider '{spider_name}' timed out after {timeout_seconds} seconds.")
        return []
    except Exception as exc:
        logger.error(f"Failed to execute Scrapy spider '{spider_name}': {exc}")
        return []
    finally:
        if os.path.exists(tmp_output_path):
            try:
                os.remove(tmp_output_path)
            except Exception:
                pass
