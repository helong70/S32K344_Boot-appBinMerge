@echo off
REM 激活虚拟环境
call .venv\Scripts\activate

REM 用虚拟环境的 python 打包，直接在窗口打印日志
.venv\Scripts\python.exe -m PyInstaller --onefile --windowed BinMerge.py

REM 关闭虚拟环境
deactivate

pause
