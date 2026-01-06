# writers/export_chart_to_image.py

import os
import shutil
import pythoncom
import win32com.client as win32
from pathlib import Path

from utilities.paths import ensure_dir


def _try_clear_win32com_gen_cache():
    """
    Fixes common pywin32 cache corruption issues like:
      - CLSIDToClassMap missing
      - MinorVersion missing

    This is safe to attempt; if it fails we just move on.
    """
    try:
        import win32com
        gen_path = os.path.join(os.path.dirname(win32com.__file__), "gen_py")
        if os.path.isdir(gen_path):
            shutil.rmtree(gen_path, ignore_errors=True)
    except Exception:
        pass


def export_chart_to_image(student_path: str, image_output_dir: str = None) -> str | None:
    """
    Export the XY scatter chart from the student's 'Income Analysis' tab.
    Returns the saved image path if exported, else None.
    """

    pythoncom.CoInitialize()

    try:
        student_path = os.path.abspath(student_path)

        # ✅ Default to workspace temp_charts
        if not image_output_dir:
            image_output_dir = ensure_dir("temp_charts")
        else:
            image_output_dir = os.path.abspath(image_output_dir)
            Path(image_output_dir).mkdir(parents=True, exist_ok=True)

        student_name = Path(student_path).stem.replace("_MA1", "")
        image_path = os.path.join(image_output_dir, f"{student_name}.png")

        excel = None
        wb = None

        try:
            # ✅ Avoid gencache/gen_py issues (and isolates this Excel instance)
            excel = win32.DispatchEx("Excel.Application")

            # Safe to ignore if COM refuses
            try:
                excel.Visible = False
            except Exception:
                pass

            try:
                excel.DisplayAlerts = False
            except Exception:
                pass

            wb = excel.Workbooks.Open(student_path)
            ws = wb.Sheets("Income Analysis")

            for obj in ws.ChartObjects():
                chart = obj.Chart
                if chart.ChartType == -4169:  # XY Scatter
                    chart.Export(image_path)
                    print(f"📤 Exported chart → {image_path}")
                    return image_path

            print(f"⚠️ No XY Scatter chart found for {student_path}")
            return None

        except Exception as e:
            # 🔧 If it's the classic gen_py corruption, try clearing and retry once
            msg = str(e)
            if ("CLSIDToClassMap" in msg) or ("MinorVersion" in msg):
                _try_clear_win32com_gen_cache()
                try:
                    # retry once
                    excel = win32.DispatchEx("Excel.Application")
                    excel.Visible = False
                    excel.DisplayAlerts = False
                    wb = excel.Workbooks.Open(student_path)
                    ws = wb.Sheets("Income Analysis")

                    for obj in ws.ChartObjects():
                        chart = obj.Chart
                        if chart.ChartType == -4169:
                            chart.Export(image_path)
                            print(f"📤 Exported chart → {image_path}")
                            return image_path

                    print(f"⚠️ No XY Scatter chart found for {student_path}")
                    return None
                except Exception as e2:
                    print(f"❌ Chart export failed for {student_path}: {e2}")
                    return None

            print(f"❌ Chart export failed for {student_path}: {e}")
            return None

        finally:
            try:
                if wb is not None:
                    wb.Close(SaveChanges=False)
            except Exception:
                pass

            try:
                if excel is not None:
                    excel.Quit()
            except Exception:
                pass

    finally:
        pythoncom.CoUninitialize()
