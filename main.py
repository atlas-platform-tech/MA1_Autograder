# main.py

from writers.generate_course_folders import generate_course_folders
from writers.create_grading_sheet import create_grading_sheets_from_folder

from orchestrator import (
    phase1_grade_all_students,
    phase2_export_all_charts,
    phase3_insert_all_charts,
    phase4_cleanup_temp
)

# ✅ NEW: build instructor master workbook
from writers.build_instructor_master_workbook import build_instructor_master_workbook


def main():
    print("\n🟣 MA1 Auto-Grader V2 — Full Pipeline\n")

    course_label = input("Enter the course label (e.g., MAT-144-500): ").strip()

    folder_safe, graded_path, submissions_path = generate_course_folders(course_label)

    # Create grading sheets + copy submissions
    create_grading_sheets_from_folder(folder_safe)

    # PHASE 1 — Grade formulas
    phase1_grade_all_students(submissions_path, graded_path)

    # PHASE 2 — Export charts
    phase2_export_all_charts(submissions_path)

    # PHASE 3 — Insert charts into grading sheets
    phase3_insert_all_charts(graded_path)

    # PHASE 4 — Delete temp_charts folder
    phase4_cleanup_temp("temp_charts")

    # ✅ NEW PHASE 5 — Build Instructor Master Workbook
    try:
        master_path = build_instructor_master_workbook(graded_path)
        print(f"\n📘 Instructor Master workbook created: {master_path}")
    except Exception as e:
        print(f"\n⚠️ Could not build Instructor Master workbook: {e}")

    print("\n✅ All grading complete!")
    print(f"📁 Final grading sheets are located in: {graded_path}\n")


if __name__ == "__main__":
    main()
