"""Fill the database with sample data:  python scripts/seed_demo_data.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tracker.database import init_db  # noqa: E402
from tracker.demo import seed_demo_data  # noqa: E402

if __name__ == "__main__":
    init_db()
    seed_demo_data()
    print("Demo data added.")
