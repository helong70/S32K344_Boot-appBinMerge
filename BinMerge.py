import sys
from PyQt5.QtWidgets import (
	QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit
)
import sys
from PyQt5.QtWidgets import (
	QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit
)

class BinMergeApp(QWidget):
	def make_app_header(self):
		# 头部结构体字段
		isFlashProgramSuccessfull = 1
		isFlashErasedSuccessfull = 1
		isFlashStructValid = 1
		appCnt = 0
		aFingerPrint = bytes([0xFF]*17)
		finger_padding = bytes([0xFF]*3)
		appStartAddrLen = 4
		appStartAddr = 4727841
		# 拼接除crc外的前32字节
		header = bytearray()
		header.append(isFlashProgramSuccessfull)
		header.append(isFlashErasedSuccessfull)
		header.append(isFlashStructValid)
		header.append(appCnt)
		header += aFingerPrint
		header += finger_padding
		header += appStartAddrLen.to_bytes(4, 'little')
		header += appStartAddr.to_bytes(4, 'little')
		# CRC直接写死为0x3caf，后补两个0x00
		crc = 0x3caf
		header += crc.to_bytes(2, 'little')
		header += bytes([0x00, 0x00])
		return bytes(header)

	def calc_crc16(self, data):
		# 标准CRC16算法（多用于嵌入式，与你C代码一致）
		crc = 0xFFFF
		for b in data:
			crc ^= b
			for _ in range(8):
				if crc & 1:
					crc = (crc >> 1) ^ 0xA001
				else:
					crc >>= 1
		return crc & 0xFFFF
	def __init__(self):
		super().__init__()
		self.setWindowTitle('Bin 文件合并工具')
		self.setFixedSize(600, 400)
		self.boot_path = ''
		self.app_path = ''
		self.offset = 0
		self.init_ui()

	def init_ui(self):
		layout = QVBoxLayout()

		self.boot_label = QLabel('Boot 文件: 未选择')
		self.app_label = QLabel('App 文件: 未选择')

		boot_btn = QPushButton('选择 Boot 文件')
		boot_btn.clicked.connect(self.select_boot)
		app_btn = QPushButton('选择 App 文件')
		app_btn.clicked.connect(self.select_app)

		offset_layout = QHBoxLayout()
		offset_label = QLabel('App Offset (十六进制/字节):')
		self.offset_edit = QLineEdit('0x80200')
		self.offset_edit.setPlaceholderText('如: 0x1000 或 4096')
		offset_layout.addWidget(offset_label)
		offset_layout.addWidget(self.offset_edit)

		# 新增 App Header Offset 输入框
		header_offset_layout = QHBoxLayout()
		header_offset_label = QLabel('App Header Offset (十六进制/字节):')
		self.header_offset_edit = QLineEdit('0x80000')
		self.header_offset_edit.setPlaceholderText('如: 0x80000 或 524288')
		header_offset_layout.addWidget(header_offset_label)
		header_offset_layout.addWidget(self.header_offset_edit)

		merge_btn = QPushButton('合并并保存')
		merge_btn.clicked.connect(self.merge_bin)

		layout.addWidget(self.boot_label)
		layout.addWidget(boot_btn)
		layout.addWidget(self.app_label)
		layout.addWidget(app_btn)
		layout.addLayout(offset_layout)
		layout.addLayout(header_offset_layout)
		layout.addWidget(merge_btn)

		self.setLayout(layout)

	def select_boot(self):
		path, _ = QFileDialog.getOpenFileName(self, '选择 Boot bin 文件', '', 'Bin Files (*.bin)')
		if path:
			self.boot_path = path
			self.boot_label.setText(f'Boot 文件: {path}')

	def select_app(self):
		path, _ = QFileDialog.getOpenFileName(self, '选择 App bin 文件', '', 'Bin Files (*.bin)')
		if path:
			self.app_path = path
			self.app_label.setText(f'App 文件: {path}')

	def merge_bin(self):
		if not self.boot_path or not self.app_path:
			QMessageBox.warning(self, '提示', '请先选择 Boot 和 App 文件')
			return
		try:
			save_path, _ = QFileDialog.getSaveFileName(self, '保存合并后的 bin 文件', '', 'Bin Files (*.bin)')
			if not save_path:
				return
			with open(self.boot_path, 'rb') as f_boot, open(self.app_path, 'rb') as f_app, open(save_path, 'wb') as f_out:
				boot_data = f_boot.read()
				app_data = f_app.read()
				f_out.write(boot_data)
				# 读取 header offset 输入框
				header_offset_str = self.header_offset_edit.text().strip()
				if header_offset_str.lower().startswith('0x'):
					app_header_offset = int(header_offset_str, 16)
				else:
					app_header_offset = int(header_offset_str)
				if len(boot_data) < app_header_offset:
					f_out.write(b'\xFF' * (app_header_offset - len(boot_data)))
				elif len(boot_data) > app_header_offset:
					QMessageBox.warning(self, '警告', f'boot文件长度超过0x{app_header_offset:X}，app_header将紧跟boot写入')
				app_header = self.make_app_header()
				f_out.write(app_header)
				# app内容写入位置与输入框offset一致
				offset_str = self.offset_edit.text().strip()
				if offset_str.lower().startswith('0x'):
					app_offset = int(offset_str, 16)
				else:
					app_offset = int(offset_str)
				cur_pos = f_out.tell()
				if cur_pos < app_offset:
					f_out.write(b'\xFF' * (app_offset - cur_pos))
				elif cur_pos > app_offset:
					QMessageBox.warning(self, '警告', f'app内容将紧跟app_header写入，未能对齐到0x{app_offset:X}')
				f_out.write(app_data)
			QMessageBox.information(self, '成功', f'合并完成，保存为：{save_path}')
		except Exception as e:
			QMessageBox.critical(self, '错误', f'合并失败：{e}')

if __name__ == '__main__':
	import sys
	from PyQt5.QtWidgets import QApplication
	app = QApplication(sys.argv)
	window = BinMergeApp()
	window.show()
	sys.exit(app.exec_())
	sys.exit(app.exec_())
