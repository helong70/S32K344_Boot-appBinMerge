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
		# CRC16算法（使用 C 代码的 CRC 表）
		g_dnpCrcTable = [
			0x0000, 0x365e, 0x6cbc, 0x5ae2, 0xd978, 0xef26, 0xb5c4, 0x839a,
			0xff89, 0xc9d7, 0x9335, 0xa56b, 0x26f1, 0x10af, 0x4a4d, 0x7c13,
			0xb26b, 0x8435, 0xded7, 0xe889, 0x6b13, 0x5d4d, 0x07af, 0x31f1,
			0x4de2, 0x7bbc, 0x215e, 0x1700, 0x949a, 0xa2c4, 0xf826, 0xce78,
			0x29af, 0x1ff1, 0x4513, 0x734d, 0xf0d7, 0xc689, 0x9c6b, 0xaa35,
			0xd626, 0xe078, 0xba9a, 0x8cc4, 0x0f5e, 0x3900, 0x63e2, 0x55bc,
			0x9bc4, 0xad9a, 0xf778, 0xc126, 0x42bc, 0x74e2, 0x2e00, 0x185e,
			0x644d, 0x5213, 0x08f1, 0x3eaf, 0xbd35, 0x8b6b, 0xd189, 0xe7d7,
			0x535e, 0x6500, 0x3fe2, 0x09bc, 0x8a26, 0xbc78, 0xe69a, 0xd0c4,
			0xacd7, 0x9a89, 0xc06b, 0xf635, 0x75af, 0x43f1, 0x1913, 0x2f4d,
			0xe135, 0xd76b, 0x8d89, 0xbbd7, 0x384d, 0x0e13, 0x54f1, 0x62af,
			0x1ebc, 0x28e2, 0x7200, 0x445e, 0xc7c4, 0xf19a, 0xab78, 0x9d26,
			0x7af1, 0x4caf, 0x164d, 0x2013, 0xa389, 0x95d7, 0xcf35, 0xf96b,
			0x8578, 0xb326, 0xe9c4, 0xdf9a, 0x5c00, 0x6a5e, 0x30bc, 0x06e2,
			0xc89a, 0xfec4, 0xa426, 0x9278, 0x11e2, 0x27bc, 0x7d5e, 0x4b00,
			0x3713, 0x014d, 0x5baf, 0x6df1, 0xee6b, 0xd835, 0x82d7, 0xb489,
			0xa6bc, 0x90e2, 0xca00, 0xfc5e, 0x7fc4, 0x499a, 0x1378, 0x2526,
			0x5935, 0x6f6b, 0x3589, 0x03d7, 0x804d, 0xb613, 0xecf1, 0xdaaf,
			0x14d7, 0x2289, 0x786b, 0x4e35, 0xcdaf, 0xfbf1, 0xa113, 0x974d,
			0xeb5e, 0xdd00, 0x87e2, 0xb1bc, 0x3226, 0x0478, 0x5e9a, 0x68c4,
			0x8f13, 0xb94d, 0xe3af, 0xd5f1, 0x566b, 0x6035, 0x3ad7, 0x0c89,
			0x709a, 0x46c4, 0x1c26, 0x2a78, 0xa9e2, 0x9fbc, 0xc55e, 0xf300,
			0x3d78, 0x0b26, 0x51c4, 0x679a, 0xe400, 0xd25e, 0x88bc, 0xbee2,
			0xc2f1, 0xf4af, 0xae4d, 0x9813, 0x1b89, 0x2dd7, 0x7735, 0x416b,
			0xf5e2, 0xc3bc, 0x995e, 0xaf00, 0x2c9a, 0x1ac4, 0x4026, 0x7678,
			0x0a6b, 0x3c35, 0x66d7, 0x5089, 0xd313, 0xe54d, 0xbfaf, 0x89f1,
			0x4789, 0x71d7, 0x2b35, 0x1d6b, 0x9ef1, 0xa8af, 0xf24d, 0xc413,
			0xb800, 0x8e5e, 0xd4bc, 0xe2e2, 0x6178, 0x5726, 0x0dc4, 0x3b9a,
			0xdc4d, 0xea13, 0xb0f1, 0x86af, 0x0535, 0x336b, 0x6989, 0x5fd7,
			0x23c4, 0x159a, 0x4f78, 0x7926, 0xfabc, 0xcce2, 0x9600, 0xa05e,
			0x6e26, 0x5878, 0x029a, 0x34c4, 0xb75e, 0x8100, 0xdbe2, 0xedbc,
			0x91af, 0xa7f1, 0xfd13, 0xcb4d, 0x48d7, 0x7e89, 0x246b, 0x1235
		]
		crc = 0x0000
		for byte in data:
			crc = (crc >> 8) ^ g_dnpCrcTable[(crc ^ byte) & 0x00FF]
		return (~crc) & 0xFFFF
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
		elif text == 'FC4150':
			# 预设 FC4150: App Offset 为 0x22000,Header Offset 为 0x20000
			try:
				self.offset_edit.setText('0x22000')
				self.header_offset_edit.setText('0x20000')
				self.header_offset_edit.setEnabled(True)
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
				# 根据所选板卡调整行为
				board = self.board_combo.currentText()
				if board == 'FU68X6':
					app_offset = 0x1500
					header_offset = 0
					app_header = self.make_app_header()
				elif board == 'FC4150':
					app_offset = 0x22000
					header_offset = 0x20000
					info_length = 0x2000
					# 验证 app_data 长度
					if len(app_data) <= info_length:
						QMessageBox.warning(self, '错误', f'App 文件大小 ({len(app_data)} 字节) 小于或等于 InfoLength (0x{info_length:X})。\nFC4150 要求 App 文件必须大于 {info_length} 字节。')
						return
					app_length = len(app_data)
					# CMAC 密钥（32字节用于 AES-256）
					cmac_key = bytes([
						0xAF, 0x06, 0x55, 0x7D, 0x96, 0xAB, 0xFC, 0xA9,
						0x2C, 0xBC, 0x1C, 0x87, 0x4B, 0xA3, 0x72, 0xE8,
						0x17, 0x42, 0x4B, 0x87, 0x44, 0xF9, 0xB9, 0x49,
						0x58, 0x5C, 0xBF, 0xA2, 0x17, 0xB2, 0x8D, 0x7F
					])
					# 计算 CMAC：从 0x0 开始到文件末尾的数据
					cmac_data = app_data
					cmac_signature = self.calc_cmac_aes128(cmac_data, cmac_key)
					# 先生成带 CMAC 签名的 header,CRC 字段设为 0
					app_header_temp = self.make_app_header(appCnt=1, crc=0, appStartAddr=0x22004, appLength=app_length, aFingerPrint=cmac_signature)
					# 计算 CRC (排除最后 4 字节: crc(2) + tail(2))
					crc_value = self.calc_crc16(app_header_temp[:-4])
					# 生成最终 header,包含计算出的 CRC
					app_header = self.make_app_header(appCnt=1, crc=crc_value, appStartAddr=0x22004, appLength=app_length, aFingerPrint=cmac_signature)
				else:
					app_header = self.make_app_header()
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

				# 写入 header（header_offset==0 则跳过）。对于 FC4150，延后到写入 app 之后以免被覆盖。
				if header_offset and board != 'FC4150':
					merged[header_offset:header_offset+len(app_header)] = app_header
				# 写入 app（非 FU68X6 情况直接写入完整 app_data）
				if board != 'FU68X6':
					merged[app_offset:app_offset+len(app_data)] = app_data
				# 对于 FC4150，写完 app 后再写 header，避免被 app 覆盖
				if board == 'FC4150' and header_offset:
					merged[header_offset:header_offset+len(app_header)] = app_header
				# FU68X6 特殊：在 0x1400 处写入 0xAA
				if board == 'FU68X6':
					merged[0x1400] = 0xAA
				# 如果是 FU68X6，且合并后长度超过 0x7FFF（索引范围 0..0x7FFF），则截断多余部分
				if board == 'FU68X6' and len(merged) > 0x8000:
					merged = merged[:0x8000]
				# 写出最终合并文件
				with open(save_path, 'wb') as f_out:
					f_out.write(merged)
				
				# FC4150 特殊处理：生成第二个 bin 文件(从 header_offset 开始)
				if board == 'FC4150' and header_offset:
					# 生成第二个文件名，在原文件名基础上加 _app 后缀
					import os
					base_name = os.path.splitext(save_path)[0]
					ext = os.path.splitext(save_path)[1]
					second_bin_path = f"{base_name}_app{ext}"
					
					# 从 header_offset 开始截取到文件末尾
					second_bin_data = merged[header_offset:]
					with open(second_bin_path, 'wb') as f_out2:
						f_out2.write(second_bin_data)
					
					QMessageBox.information(self, '成功', f'合并完成！\n完整文件: {save_path}\nApp文件: {second_bin_path}')
				else:
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
