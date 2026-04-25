import sys
import platform
import subprocess
import winreg
import logging
import os

logger = logging.getLogger("com_bitness")
logging.basicConfig(level=logging.INFO)

def get_python_bitness(python_exe):
    try:
        out = subprocess.check_output([python_exe, '-c', 'import platform; print(platform.architecture()[0])'], universal_newlines=True)
        return out.strip()
    except Exception as e:
        return f"Fehler: {e}"

def get_office_bitness(app="Word"):
    # Office-Bitness aus Registry auslesen
    # Für Word: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Office\<Version>\Word\InstallRoot
    # Für Excel: ...Excel...
    # 32-Bit-Office auf 64-Bit-Windows steht unter Wow6432Node
    import winreg
    bitness = None
    for root, arch in [(winreg.HKEY_LOCAL_MACHINE, "64-bit"), (winreg.HKEY_LOCAL_MACHINE, "32-bit")]:
        for base in [r"SOFTWARE\Microsoft\Office", r"SOFTWARE\Wow6432Node\Microsoft\Office"]:
            try:
                with winreg.OpenKey(root, base) as office:
                    i = 0
                    while True:
                        try:
                            version = winreg.EnumKey(office, i)
                            path = f"{base}\\{version}\\{app}\\InstallRoot"
                            try:
                                with winreg.OpenKey(root, path) as key:
                                    exe, _ = winreg.QueryValueEx(key, "Path")
                                    if exe:
                                        # Prüfe, ob im x86- oder x64-Pfad
                                        if "Program Files (x86)" in exe:
                                            bitness = "32-bit"
                                        elif "Program Files" in exe:
                                            bitness = "64-bit"
                                        else:
                                            bitness = arch
                                        return bitness, exe
                            except FileNotFoundError:
                                pass
                            i += 1
                        except OSError:
                            break
            except FileNotFoundError:
                continue
    return None, None

def find_python_interpreters():
    # Sucht nach installierten Python-Interpretern (32/64 Bit)
    candidates = []
    # py-Launcher
    try:
        out = subprocess.check_output(['py', '-0p'], universal_newlines=True)
        for line in out.splitlines():
            path = line.strip().split()[-1]
            if os.path.exists(path):
                candidates.append(path)
    except Exception:
        pass
    # PATH
    for name in ["python.exe", "python3.exe"]:
        for dir in os.environ["PATH"].split(os.pathsep):
            exe = os.path.join(dir, name)
            if os.path.exists(exe) and exe not in candidates:
                candidates.append(exe)
    return candidates

def minimal_com_test(python_exe, app="Word"):
    try:
        out = subprocess.check_output([
            python_exe, "-c",
            f"import win32com.client; obj=win32com.client.Dispatch('{app}.Application'); obj.Quit(); print('OK')"
        ], universal_newlines=True, stderr=subprocess.STDOUT)
        logger.info(f"[{python_exe}] {app} COM-Automation erfolgreich!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[{python_exe}] {app} COM-Test fehlgeschlagen: {e.output.strip()}")
        return False
    except Exception as e:
        logger.error(f"[{python_exe}] {app} COM-Test Exception: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Office/Python Bitness-Checker ===")
    # Office-Bitness prüfen
    for app in ["Word", "Excel"]:
        bit, path = get_office_bitness(app)
        if bit:
            logger.info(f"{app}: {bit} ({path})")
        else:
            logger.warning(f"{app}: Bitness/Pfad nicht gefunden!")
    # Python-Interpreter suchen
    pythons = find_python_interpreters()
    if not pythons:
        logger.error("Keine Python-Interpreter gefunden!")
    for py in pythons:
        bit = get_python_bitness(py)
        logger.info(f"Python: {py} ({bit})")
        for app in ["Word", "Excel"]:
            minimal_com_test(py, app)