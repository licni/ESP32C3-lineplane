@echo off
chcp 65001 >nul
rem 在 Windows 本機打包 LineplaneFlasher.exe(GitHub Actions 也用同樣的指令,見 .github/workflows/flasher.yml).
rem 需要 Python 3.10 以上(python.org 安裝版內建 tkinter). 產出在 dist\LineplaneFlasher.exe.
cd /d "%~dp0"
python -m pip install -r requirements.txt || exit /b 1
python -m unittest -v test_fw_image || exit /b 1
python -m PyInstaller --noconfirm --clean --onefile --windowed --name LineplaneFlasher --collect-data esptool lineplane_flasher.py || exit /b 1
echo.
echo 完成:%~dp0dist\LineplaneFlasher.exe
