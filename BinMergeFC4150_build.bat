@echo off
REM 激活虚拟环境
call .venv\Scripts\activate

REM 用虚拟环境的 python 打包 FC4150 专用工具
.venv\Scripts\python.exe -m PyInstaller --onefile --windowed BinMergeFC4150.py

REM 关闭虚拟环境
deactivate

pause
