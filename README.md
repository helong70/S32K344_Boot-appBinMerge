# BinMerge 工具

## 项目简介
本工具用于合并 boot 和 app bin 文件，支持自定义 offset，自动插入 app header。支持 PyQt5 和 Tkinter 两种界面版本，已提供一键打包和环境初始化脚本。

## 功能
- 选择 boot/app bin 文件
- 输入 offset（支持十进制/十六进制）
- 自动插入 app header，地址固定为0x80000（CRC 固定为 0x3caf，后两字节为 0x00）
- 合并并保存新 bin 文件
- 支持 PyQt5 和 Tkinter 两种界面

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

## 相关 Demo 工程

如需 app 和 boot bin 文件的参考工程，可访问 NXP 官方 Unified bootloader Demo：

[ bootloader Demo (NXP 社区)](https://community.nxp.com/t5/S32K-Knowledge-Base/Unified-bootloader-Demo/ta-p/1423099)

该页面包含 bootloader 及应用程序的完整工程和说明。
