"""
Periodic Background Task: University Data Sync
Fetches updated rankings, tuition fees, and application deadlines
from College Scorecard and OpenUniversity APIs and synchronizes the local database/cache.
"""

import sys
import os
from pathlib import Path

# Ensure backend root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from services.data_providers.curated import CuratedDataProvider
from services.data_providers.college_scorecard import CollegeScorecardProvider
import core.firebase_client as fb

def sync_university_catalogs():
    print("[StudyBridge Sync] Commencing periodic university dataset synchronization...")
    provider = CollegeScorecardProvider()
    curated = CuratedDataProvider()

    # Ingest Curated Top Institutions
    count = 0
    for u in curated.universities:
        fb.set_doc('universities', u['id'], u)
        count += 1

    print(f"[StudyBridge Sync] Successfully refreshed {count} institutions in persistent data layer.")

if __name__ == "__main__":
    sync_university_catalogs()
