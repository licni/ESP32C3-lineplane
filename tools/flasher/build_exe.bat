@echo off
chcp 65001 >nul
rem 在 Windows 本機打包 LineplaneConfig.exe(線控飛機設定器)(GitHub Actions 也用同樣的指令,見 .github/workflows/flasher.yml).
rem 需要 Python 3.10 以上(python.org 安裝版內建 tkinter;3.14 也可以). 雙擊即可,產出在 dist\LineplaneConfig.exe.
cd /d "%~dp0"
python -m pip install -r requirements.txt || exit /b 1
python -m unittest -v test_fw_image test_board_link || exit /b 1
python -m PyInstaller --noconfirm --clean --onefile --windowed --name LineplaneConfig --collect-data esptool lineplane_config.py || exit /b 1
echo.
echo 完成:%~dp0dist\LineplaneConfig.exe
