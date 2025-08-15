# BinMerge 工具

## 项目简介
本工具用于合并 boot 和 app bin 文件，支持自定义 offset，自动插入 app header。支持 PyQt5 和 Tkinter 两种界面版本，已提供一键打包和环境初始化脚本。

## 功能
- 选择 boot/app bin 文件
- 输入 offset（支持十进制/十六进制）
- 自动插入 app header，地址固定为0x80000（CRC 固定为 0x3caf，后两字节为 0x00）
- 合并并保存新 bin 文件
- 支持 PyQt5 和 Tkinter 两种界面
- 支持将 boot/app bin 文件直接拖拽到窗口自动加载，无需手动选择,优先填充未选择的，若都已选则覆盖 app。

## 环境搭建
1. 安装 Python 3.8 及以上版本
2. 双击 `init_venv.bat`，自动创建虚拟环境并安装依赖

## 打包为 exe
- PyQt5 版本：运行 `BinMerge_build.bat`
- Tkinter 版本：运行 `BinMerge_tk_build.bat`
- 生成的 exe 文件在 `dist/` 目录

## 文件说明
- `BinMerge.py`：PyQt5 版本主程序
- `BinMerge_tk.py`：Tkinter 版本主程序
- `init_venv.bat`：一键创建虚拟环境并安装依赖
- `BinMerge_build.bat`：PyQt5 版本打包脚本
- `BinMerge_tk_build.bat`：Tkinter 版本打包脚本
- `requirements.txt`：依赖列表
- `.gitignore`：禁止上传虚拟环境、打包文件夹

## 常见问题
- exe 文件体积较大：可用 UPX 压缩或精简依赖
- 打包失败：请检查虚拟环境和 requirements.txt 是否完整
- Tkinter 版本更轻量，推荐用于简单需求

---

# BinMerge Tool (English)

## Project Overview
This tool merges boot and app bin files, supports custom offset, and auto-inserts app header. Both PyQt5 and Tkinter GUI versions are provided, with one-click packaging and environment setup scripts.

## Features
- Select boot/app bin files
- Input offset (supports decimal/hex)
- Auto-insert app header (CRC fixed to 0x3caf, next two bytes 0x00)
- Merge and save new bin file
- PyQt5 and Tkinter GUI versions
- **New:** Drag and drop boot/app bin files directly into the window for auto-loading (fills empty slot first, then overwrites app if both selected)

## Environment Setup
1. Install Python 3.8 or above
2. Double-click `init_venv.bat` to create a virtual environment and install dependencies automatically

## Packaging as exe
- PyQt5 version: Run `BinMerge_build.bat`
- Tkinter version: Run `BinMerge_tk_build.bat`
- The generated exe file is in the `dist/` directory

## File Description
- `BinMerge.py`: PyQt5 main program
- `BinMerge_tk.py`: Tkinter main program
- `init_venv.bat`: One-click venv and dependency install
- `BinMerge_build.bat`: PyQt5 packaging script
- `BinMerge_tk_build.bat`: Tkinter packaging script
- `requirements.txt`: Dependency list
- `.gitignore`: Excludes venv and build folders from git

## Related Demo Project
For reference boot/app bin files, see the official NXP Unified bootloader Demo:
[Unified bootloader Demo (NXP Community)](https://community.nxp.com/t5/S32K-Knowledge-Base/Unified-bootloader-Demo/ta-p/1423099)

## FAQ
- Large exe size: Use UPX or minimize dependencies
- Packaging failed: Check venv and requirements.txt
- Tkinter version is lighter, recommended for simple needs
