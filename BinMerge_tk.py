import tkinter as tk
from tkinter import filedialog, messagebox
import struct
import os

class BinMergeApp:
    def __init__(self, root):
        self.root = root
        self.root.title('BinMerge Tool (Tkinter)')
        self.boot_path = ''
        self.app_path = ''

        # Boot file
        tk.Label(root, text='Boot文件:').grid(row=0, column=0, sticky='e')
        self.boot_entry = tk.Entry(root, width=40)
        self.boot_entry.grid(row=0, column=1)
        tk.Button(root, text='选择', command=self.select_boot).grid(row=0, column=2)

        # App file
        tk.Label(root, text='App文件:').grid(row=1, column=0, sticky='e')
        self.app_entry = tk.Entry(root, width=40)
        self.app_entry.grid(row=1, column=1)
        tk.Button(root, text='选择', command=self.select_app).grid(row=1, column=2)

        # Offset
        tk.Label(root, text='App Offset (十六进制/十进制):').grid(row=2, column=0, sticky='e')
        self.offset_entry = tk.Entry(root, width=20)
        self.offset_entry.grid(row=2, column=1, sticky='w')
        self.offset_entry.insert(0, '0x100000')

        # Board selector
        tk.Label(root, text='Board:').grid(row=2, column=2, sticky='e')
        self.board_var = tk.StringVar(value='S32K344')
        board_menu = tk.OptionMenu(root, self.board_var, 'S32K344', 'FU68X6', command=self.on_board_change)
        board_menu.grid(row=2, column=3, sticky='w')

        # App Header Offset (可被特定板卡忽略)
        tk.Label(root, text='App Header Offset:').grid(row=3, column=0, sticky='e')
        self.header_offset_entry = tk.Entry(root, width=20)
        self.header_offset_entry.grid(row=3, column=1, sticky='w')
        self.header_offset_entry.insert(0, '0x80000')

        # Merge button
        tk.Button(root, text='合并', command=self.merge_bin).grid(row=3, column=1, pady=10)

    def select_boot(self):
        path = filedialog.askopenfilename(title='选择Boot文件', filetypes=[('BIN文件', '*.bin'), ('所有文件', '*.*')])
        if path:
            self.boot_path = path
            self.boot_entry.delete(0, tk.END)
            self.boot_entry.insert(0, path)

    def select_app(self):
        path = filedialog.askopenfilename(title='选择App文件', filetypes=[('BIN文件', '*.bin'), ('所有文件', '*.*')])
        if path:
            self.app_path = path
            self.app_entry.delete(0, tk.END)
            self.app_entry.insert(0, path)

    def on_board_change(self, value):
        """根据板卡选择调整 UI 行为和值。"""
        if value == 'FU68X6':
            # 预设 App Offset 为 0x1500，禁用 header offset
            try:
                self.offset_entry.delete(0, tk.END)
                self.offset_entry.insert(0, '0x1500')
            except Exception:
                pass
            try:
                self.header_offset_entry.delete(0, tk.END)
                self.header_offset_entry.insert(0, '0x0')
                self.header_offset_entry.config(state='disabled')
            except Exception:
                pass
        else:
            # 恢复默认行为
            try:
                self.header_offset_entry.config(state='normal')
                self.header_offset_entry.delete(0, tk.END)
                self.header_offset_entry.insert(0, '0x80000')
                # 恢复默认 app offset
                self.offset_entry.delete(0, tk.END)
                self.offset_entry.insert(0, '0x100000')
            except Exception:
                pass

    def make_app_header(self):
        isFlashProgramSuccessfull = 1
        isFlashErasedSuccessfull = 1
        isFlashStructValid = 1
        appCnt = 0
        aFingerPrint = bytes([0xFF]*17)
        finger_padding = bytes([0xFF]*3)
        appStartAddrLen = 4
        appStartAddr = 4727841
        header = bytearray()
        header.append(isFlashProgramSuccessfull)
        header.append(isFlashErasedSuccessfull)
        header.append(isFlashStructValid)
        header.append(appCnt)
        header += aFingerPrint
        header += finger_padding
        header += appStartAddrLen.to_bytes(4, 'little')
        header += appStartAddr.to_bytes(4, 'little')
        crc = 0x3caf
        header += crc.to_bytes(2, 'little')
        header += bytes([0x00, 0x00])
        return bytes(header)

    def merge_bin(self):
        boot_path = self.boot_entry.get()
        app_path = self.app_entry.get()
        # 选择板卡
        board = self.board_var.get()
        offset_str = self.offset_entry.get()
        try:
            offset = int(offset_str, 0)
        except Exception:
            messagebox.showerror('错误', 'Offset格式错误')
            return
        if not os.path.isfile(boot_path) or not os.path.isfile(app_path):
            messagebox.showerror('错误', '请正确选择Boot和App文件')
            return
        try:
            with open(boot_path, 'rb') as f:
                boot_data = f.read()
            with open(app_path, 'rb') as f:
                app_data = f.read()
            app_header = self.make_app_header()
            # 根据所选板卡调整行为
            # 默认 header 写入 offset_from_header (0x80000)；若板卡为 FU68X6，则 header 不写入且 app offset 固定为 0x1500
            if board == 'FU68X6':
                app_offset = 0x1500
                header_offset = 0
            else:
                # 读取 header offset 输入框
                header_offset_str = self.header_offset_entry.get().strip()
                try:
                    header_offset = int(header_offset_str, 0)
                except Exception:
                    header_offset = 0x80000
                app_offset = offset

            # 计算合并长度，保证包含 boot, header(if any), app, 以及 FU68X6 特殊写入的地址 0x1400
            required_len = len(boot_data)
            if header_offset and header_offset + len(app_header) > required_len:
                required_len = header_offset + len(app_header)
            if app_offset + len(app_data) > required_len:
                required_len = app_offset + len(app_data)
            # FU68X6 要在 0x1400 写入 1 字节
            if board == 'FU68X6' and 0x1400 + 1 > required_len:
                required_len = 0x1400 + 1

            merged = bytearray([0xFF] * required_len)
            merged[:len(boot_data)] = boot_data

            # 写入 header（header_offset==0 则跳过）
            if header_offset:
                merged[header_offset:header_offset+len(app_header)] = app_header

            # 写入 app
            merged[app_offset:app_offset+len(app_data)] = app_data

            # FU68X6 特殊：在 0x1400 处写入 0xAA
            if board == 'FU68X6':
                merged[0x1400] = 0xAA
            out_path = filedialog.asksaveasfilename(title='保存合并文件', defaultextension='.bin', filetypes=[('BIN文件', '*.bin')])
            if out_path:
                with open(out_path, 'wb') as f:
                    f.write(merged)
                messagebox.showinfo('成功', f'合并完成！输出文件：{out_path}')
        except Exception as e:
            messagebox.showerror('错误', f'合并失败：{e}')

if __name__ == '__main__':
    root = tk.Tk()
    app = BinMergeApp(root)
    root.mainloop()
