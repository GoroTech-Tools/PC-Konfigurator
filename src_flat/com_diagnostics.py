import sys
import platform
import subprocess
import winreg
import logging

logger = logging.getLogger("com_diag")
logging.basicConfig(level=logging.INFO)

def check_python_office_bitness():
    py_arch = platform.architecture()[0]
    logger.info(f"Python-Bitness: {py_arch}")
    logger.info("Bitte prüfe die Office-Bitness in Word: Datei > Konto > Info zu Word.")

def check_office_com_registry(app="Word"):
    progid = f"{app}.Application"
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, progid + "\\CLSID") as key:
            clsid, _ = winreg.QueryValueEx(key, "")
            logger.info(f"{progid} CLSID: {clsid}")
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"CLSID\\{clsid}\\LocalServer32") as key:
            exe, _ = winreg.QueryValueEx(key, "")
            logger.info(f"{progid} LocalServer32: {exe}")
    except Exception as e:
        logger.error(f"Registry-Check für {progid} fehlgeschlagen: {e}")
        logger.error("Office ist installiert, aber COM-Server ist NICHT korrekt registriert!")
        logger.error("Führe winword.exe /regserver bzw. excel.exe /regserver aus.")

def run_regserver(app="Word"):
    exe = "winword.exe" if app.lower() == "word" else "excel.exe"
    try:
        subprocess.run([exe, "/regserver"], check=True)
        logger.info(f"{exe} /regserver erfolgreich ausgeführt.")
    except Exception as e:
        logger.error(f"{exe} /regserver fehlgeschlagen: {e}")

def minimal_com_test(app="Word"):
    import win32com.client
    try:
        obj = win32com.client.Dispatch(f"{app}.Application")
        obj.Visible = True
        logger.info(f"{app} COM-Automation erfolgreich!")
        obj.Quit()
        return True
    except Exception as e:
        logger.error(f"COM-Test für {app} fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Office COM-Diagnose ===")
    check_python_office_bitness()
    check_office_com_registry("Word")
    check_office_com_registry("Excel")
    logger.info("Führe Minimaltest für Word durch...")
    if not minimal_com_test("Word"):
        logger.info("Führe winword.exe /regserver aus und prüfe Bitness/Installation!")
    logger.info("Führe Minimaltest für Excel durch...")
    if not minimal_com_test("Excel"):
        logger.info("Führe excel.exe /regserver aus und prüfe Bitness/Installation!")
