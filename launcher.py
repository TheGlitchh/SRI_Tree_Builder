import os
import zipfile
import subprocess
import sys

APP_NAME = "TreeDesigner"
BASE_DIR = os.path.join(os.getenv("LOCALAPPDATA"), APP_NAME)
PYTHON_DIR = os.path.join(BASE_DIR, "winpython")
PYTHON_EXE = os.path.join(PYTHON_DIR, "python.exe")
PYTHON_ZIP = os.path.join(os.path.dirname(__file__), "python.zip")  # Your WinPython zip
SCRIPT = os.path.join(os.path.dirname(__file__), "tree.py")

def extract_winpython():
    print(f"Extracting WinPython to: {PYTHON_DIR}")
    os.makedirs(PYTHON_DIR, exist_ok=True)
    with zipfile.ZipFile(PYTHON_ZIP, "r") as zip_ref:
        zip_ref.extractall(PYTHON_DIR)
    print("Done extracting WinPython.")

def run_script():
    print(f"Running {SCRIPT} with {PYTHON_EXE}")
    subprocess.run([PYTHON_EXE, SCRIPT])

def main():
    if not os.path.exists(PYTHON_EXE):
        if not os.path.exists(PYTHON_ZIP):
            print(f"ERROR: {PYTHON_ZIP} not found.")
            sys.exit(1)
        extract_winpython()
    
    run_script()

if __name__ == "__main__":
    main()
