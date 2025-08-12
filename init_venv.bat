@echo off
REM 创建虚拟环境
python -m venv .venv

REM 激活虚拟环境
call .venv\Scripts\activate

REM 升级 pip
python -m pip install --upgrade pip

REM 自动安装 requirements.txt 依赖
pip install -r requirements.txt

REM 关闭虚拟环境
deactivate

pause
