# writers/insert_saved_images_into_grading_sheets.py

import os
import pythoncom
import win32com.client as win32
from pathlib import Path

from utilities.paths import ensure_dir


def insert_images_into_grading_sheets(temp_chart_dir: str = None, graded_output_dir: str = None):
    """
    Inserts each PNG chart into the corresponding student's grading sheet.
    Only scans THIS graded_output_dir (per-course).
    Anchors images at cell J4.
    """

    if not graded_output_dir:
        raise ValueError("graded_output_dir is required (should be the course folder).")

    pythoncom.CoInitialize()

    try:
        # ✅ Default to workspace temp_charts
        temp_chart_dir = ensure_dir("temp_charts") if not temp_chart_dir else os.path.abspath(temp_chart_dir)
        graded_output_dir = os.path.abspath(graded_output_dir)

        if not os.path.isdir(temp_chart_dir):
            print(f"⚠️ temp_chart_dir not found: {temp_chart_dir}")
            return

        excel = None

        try:
            excel = win32.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False

            pngs = [f for f in os.listdir(temp_chart_dir) if f.lower().endswith(".png")]
            if not pngs:
                print("⚠️ No PNG charts found to insert.")
                return

            for image_file in pngs:
                student_name = Path(image_file).stem
                grading_file = os.path.join(graded_output_dir, f"{student_name}_MA1_Grade.xlsx")

                if not os.path.exists(grading_file):
                    print(f"⚠️ No grading sheet for {student_name}")
                    continue

                image_path = os.path.join(temp_chart_dir, image_file)

                wb = None
                try:
                    wb = excel.Workbooks.Open(grading_file)
                    ws = wb.Sheets("Grading Sheet")

                    anchor = ws.Range("J4")
                    ws.Shapes.AddPicture(
                        Filename=os.path.abspath(image_path),
                        LinkToFile=False,
                        SaveWithDocument=True,
                        Left=anchor.Left,
                        Top=anchor.Top,
                        Width=-1,
                        Height=-1
                    )

                    wb.Save()
                    wb.Close()
                    wb = None
                    print(f"🖼️ Inserted chart for {student_name}")

                except Exception as e:
                    print(f"❌ Failed to insert chart for {student_name}: {e}")
                    try:
                        if wb is not None:
                            wb.Close(SaveChanges=False)
                    except Exception:
                        pass

        finally:
            try:
                if excel is not None:
                    excel.Quit()
            except Exception:
                pass

    finally:
        pythoncom.CoUninitialize()
