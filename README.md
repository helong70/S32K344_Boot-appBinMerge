# BinMerge 工具

## 项目简介
本工具用于合并 boot 和 app bin 文件，支持自定义 offset，自动插入 app header，并针对 FC4150 板卡提供了独立的 UI 与签名流程。当前提供通用 PyQt5/Tkinter 版本与 FC4150 专用 PyQt5 版本，同时附带一键打包和环境初始化脚本。

## 功能
- 通用 GUI（`BinMerge.py` / `BinMerge_tk.py`）
  - 选择 boot/app bin 文件
  - 输入 offset（支持十进制/十六进制）
  - 自动插入 app header（默认 offset 0x80000，CRC 默认 0x3caf）
  - 合并并保存新 bin 文件
  - 支持拖拽加载文件，优先填充空位，若已填则覆盖 App
- FC4150 专用 GUI（`BinMergeFC4150.py`）
  - 固定默认 offset：header 0x20000、app 0x22000，可手动调整
  - 支持 128/256 bit 密钥下拉选择，自动验证十六进制密钥长度
  - 自动读取 `key.txt`（支持源码与 PyInstaller 单文件模式）
  - 根据密钥计算 CMAC 签名并写入 header
  - 生成完整合并文件与 `_app` 结尾的 App 子文件

## 环境搭建
1. 安装 Python 3.8 及以上版本
2. 双击 `init_venv.bat`，自动创建虚拟环境并安装依赖

## 打包为 exe
- 通用 PyQt5 版本：运行 `BinMerge_build.bat`
- Tkinter 版本：运行 `BinMerge_tk_build.bat`
- FC4150 专用版本：运行 `BinMergeFC4150_build.bat`
- 生成的 exe 文件位于 `dist/` 目录

### 关于 key.txt
- FC4150 版本默认在同目录读取 `key.txt`，PyInstaller 打包后也会尝试从 `_MEIPASS`、exe 所在目录及当前工作目录检索
- 如需将密钥随 exe 分发，可在打包命令中追加 `--add-data key.txt;.`，或在部署时将 `key.txt` 放在 exe 相同目录

## 文件说明
- `BinMerge.py`：通用 PyQt5 版本
- `BinMerge_tk.py`：通用 Tkinter 版本
- `BinMergeFC4150.py`：FC4150 专用 PyQt5 版本
- `init_venv.bat`：一键创建虚拟环境并安装依赖
- `BinMerge_build.bat`：通用 PyQt5 打包脚本
- `BinMerge_tk_build.bat`：Tkinter 打包脚本
- `BinMergeFC4150_build.bat`：FC4150 专用打包脚本
- `key.txt`：FC4150 默认密钥（十六进制字符串）
- `requirements.txt`：依赖列表
- `.gitignore`：排除虚拟环境与打包产物

## 常见问题
- exe 文件体积较大：可用 UPX 压缩或精简依赖
- 打包失败：请检查虚拟环境和 requirements.txt 是否完整
- Tkinter 版本更轻量，推荐用于简单需求

---

# BinMerge Tool (English)

## Project Overview
This tool merges boot and app bin files, supports custom offsets, auto-inserts app headers, and now ships with a dedicated FC4150 UI that handles CMAC signing. We provide generic PyQt5/Tkinter GUIs plus an FC4150-only PyQt5 GUI, together with one-click packaging and environment setup scripts.

## Features
- Generic GUI (`BinMerge.py` / `BinMerge_tk.py`)
	- Select boot/app bin files
	- Input offset (decimal or hex)
	- Auto-insert app header (default offset 0x80000, CRC default 0x3caf)
	- Merge and save the combined bin
	- Drag-and-drop support, filling empty slots first and overwriting the app otherwise
- FC4150 GUI (`BinMergeFC4150.py`)
	- Default offsets: header 0x20000, app 0x22000 (editable)
	- Key length combo (128/256 bit) with strict hex-length validation
	- Auto-loads `key.txt` in both source and PyInstaller single-file modes
	- Generates CMAC signature and writes the header
	- Outputs both the full merged file and the `_app` suffix sub-file

## Environment Setup
1. Install Python 3.8 or above
2. Double-click `init_venv.bat` to create a virtual environment and install dependencies automatically

## Packaging as exe
- Generic PyQt5 version: run `BinMerge_build.bat`
- Tkinter version: run `BinMerge_tk_build.bat`
- FC4150 version: run `BinMergeFC4150_build.bat`
- Output executables are placed under `dist/`

### About key.txt
- The FC4150 build searches for `key.txt` next to the executable, within `_MEIPASS`, and in the current working directory
- To bundle the key with PyInstaller, append `--add-data key.txt;.` or ship `key.txt` alongside the exe

## File Description
- `BinMerge.py`: Generic PyQt5 program
- `BinMerge_tk.py`: Generic Tkinter program
- `BinMergeFC4150.py`: FC4150-specific PyQt5 program
- `init_venv.bat`: One-click venv and dependency install
- `BinMerge_build.bat`: Generic PyQt5 packaging script
- `BinMerge_tk_build.bat`: Tkinter packaging script
- `BinMergeFC4150_build.bat`: FC4150 packaging script
- `key.txt`: Default FC4150 hex key
- `requirements.txt`: Dependency list
- `.gitignore`: Excludes venv and build folders from git

## Related Demo Project
For reference boot/app bin files, see the official NXP Unified bootloader Demo:
[Unified bootloader Demo (NXP Community)](https://community.nxp.com/t5/S32K-Knowledge-Base/Unified-bootloader-Demo/ta-p/1423099)

## FAQ
- Large exe size: Use UPX or minimize dependencies
- Packaging failed: Check venv and requirements.txt
- Tkinter version is lighter, recommended for simple needs
