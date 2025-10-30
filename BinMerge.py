import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QComboBox
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
		# 启用拖拽
		self.setAcceptDrops(True)

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

		# Board selector
		board_layout = QHBoxLayout()
		board_label = QLabel('Board:')
		self.board_combo = QComboBox()
		self.board_combo.addItems(['S32K344', 'FU68X6'])
		self.board_combo.currentTextChanged.connect(self.on_board_change)
		board_layout.addWidget(board_label)
		board_layout.addWidget(self.board_combo)
		# 默认选择 S32K344
		self.board_combo.setCurrentText('S32K344')

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
		layout.addLayout(board_layout)
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

	def on_board_change(self, text):
		# 当选择不同板卡时调整 offset/header 行为
		if text == 'FU68X6':
			# 预设 App Offset 为 0x1500，禁用 header offset
			try:
				self.offset_edit.setText('0x1500')
			except Exception:
				pass
			try:
				self.header_offset_edit.setText('0x0')
				self.header_offset_edit.setEnabled(False)
			except Exception:
				pass
		else:
			# 恢复默认行为
			try:
				self.header_offset_edit.setEnabled(True)
				# 恢复默认 header offset 和 app offset
				self.header_offset_edit.setText('0x80000')
				self.offset_edit.setText('0x80200')
			except Exception:
				pass

	def merge_bin(self):
		if not self.boot_path or not self.app_path:
			QMessageBox.warning(self, '提示', '请先选择 Boot 和 App 文件')
			return
		try:
			save_path, _ = QFileDialog.getSaveFileName(self, '保存合并后的 bin 文件', '', 'Bin Files (*.bin)')
			if not save_path:
				return
			with open(self.boot_path, 'rb') as f_boot, open(self.app_path, 'rb') as f_app:
				boot_data = f_boot.read()
				app_data = f_app.read()
				app_header = self.make_app_header()
				# 根据所选板卡调整行为
				board = self.board_combo.currentText()
				if board == 'FU68X6':
					app_offset = 0x1500
					header_offset = 0
				else:
					# 读取 header offset 输入框
					header_offset_str = self.header_offset_edit.text().strip()
					try:
						header_offset = int(header_offset_str, 0)
					except Exception:
						header_offset = 0x80000
					# app offset 按用户输入
					try:
						offset = int(self.offset_edit.text().strip(), 0)
					except Exception:
						QMessageBox.warning(self, '错误', 'Offset格式错误')
						return
					app_offset = offset

				# 计算需要的合并长度
				required_len = len(boot_data)
				if header_offset and header_offset + len(app_header) > required_len:
					required_len = header_offset + len(app_header)
				if app_offset + len(app_data) > required_len:
					required_len = app_offset + len(app_data)
				# FU68X6 需要在 0x1400 写入一个字节
				if board == 'FU68X6' and 0x1400 + 1 > required_len:
					required_len = 0x1400 + 1

				merged = bytearray([0xFF] * required_len)
				# 写入 boot
				merged[:len(boot_data)] = boot_data
				# 对于 FU68X6，要保证 0x0..0x14FF 区间为 0，且 app 从 0x1500 开始
				# 写入 header（header_offset==0 则跳过）
				if board == 'FU68X6':
					# 若 boot 未占满到 app_offset，通过 0x00 填充 boot_end..app_offset
					if len(boot_data) < app_offset:
						start_zero = len(boot_data)
						end_zero = app_offset
						merged[start_zero:end_zero] = b'\x00' * (end_zero - start_zero)
					# 若 boot 为空，也将 0x0..app_offset 设置为 0
					if len(boot_data) == 0:
						merged[0:app_offset] = b'\x00' * app_offset
					# 对于 FU68X6，app.bin 中有用数据可能从其内部偏移 0x1500 开始
					app_src_offset = 0x1500
					if len(app_data) <= app_src_offset:
						# app 文件不包含 0x1500 偏移的数据，提示并跳过写入
						QMessageBox.warning(self, '警告', 'App 文件长度小于 0x1500，未包含从 0x1500 开始的有效数据')
						write_app_bytes = 0
					else:
						write_app_bytes = len(app_data) - app_src_offset
					# 写入 app 时，把 app.bin 的 0x1500 对应的数据放到合并文件的 0x1500
					if write_app_bytes:
						merged[app_offset:app_offset+write_app_bytes] = app_data[app_src_offset:app_src_offset+write_app_bytes]

				# 写入 header（header_offset==0 则跳过）
				if header_offset:
					merged[header_offset:header_offset+len(app_header)] = app_header
				# 写入 app（非 FU68X6 情况直接写入完整 app_data）
				if board != 'FU68X6':
					merged[app_offset:app_offset+len(app_data)] = app_data
				# FU68X6 特殊：在 0x1400 处写入 0xAA
				if board == 'FU68X6':
					merged[0x1400] = 0xAA
				# 如果是 FU68X6，且合并后长度超过 0x7FFF（索引范围 0..0x7FFF），则截断多余部分
				if board == 'FU68X6' and len(merged) > 0x8000:
					merged = merged[:0x8000]
				# 写出最终合并文件
				with open(save_path, 'wb') as f_out:
					f_out.write(merged)
			QMessageBox.information(self, '成功', f'合并完成，保存为：{save_path}')
		except Exception as e:
			QMessageBox.critical(self, '错误', f'合并失败：{e}')

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			urls = event.mimeData().urls()
			if any(url.toLocalFile().lower().endswith('.bin') for url in urls):
				event.acceptProposedAction()
			else:
				event.ignore()
		else:
			event.ignore()

	def dropEvent(self, event):
		files = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile().lower().endswith('.bin')]
		for file in files:
			# 优先填充未选择的，若都已选则覆盖 app
			if not self.boot_path:
				self.boot_path = file
				self.boot_label.setText(f'Boot 文件: {file}')
			elif not self.app_path:
				self.app_path = file
				self.app_label.setText(f'App 文件: {file}')
			else:
				# 都已选，默认覆盖 app
				self.app_path = file
				self.app_label.setText(f'App 文件: {file}')

if __name__ == '__main__':
	import sys
	from PyQt5.QtWidgets import QApplication
	app = QApplication(sys.argv)
	window = BinMergeApp()
	window.show()
	sys.exit(app.exec_())
	sys.exit(app.exec_())
