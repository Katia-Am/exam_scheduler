import subprocess
import sys

scripts = [
    "generate_data.py",      # 1. Base data (Students, Profs...)
    "generate_examens.py",   # 2. Assign exams (with equity)
    "generate_raw_schedule.py" # 3. Create initial conflict schedule
]

print("🚀 Starting Full Data Regeneration (Big Dataset)...")

for script in scripts:
    print(f"▶️ Running {script}...")
    try:
        subprocess.run([sys.executable, script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {script}. Stopping.")
        sys.exit(1)

print("✅ Full Regeneration Complete!")
