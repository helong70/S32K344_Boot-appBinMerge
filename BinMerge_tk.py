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
            # 固定header写入0x80000
            merge_size = max(len(boot_data), 0x80000 + len(app_header), offset + len(app_data))
            merged = bytearray([0xFF] * merge_size)
            merged[:len(boot_data)] = boot_data
            merged[0x80000:0x80000+len(app_header)] = app_header
            merged[offset:offset+len(app_data)] = app_data
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
