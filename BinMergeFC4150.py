import os
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QComboBox
)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import cmac
from cryptography.hazmat.primitives.ciphers import algorithms


def resolve_resource_path(filename):
    """Return the best-effort path to an external resource like key.txt."""
    if not filename:
        return None
    candidates = []
    if getattr(sys, 'frozen', False):
        # PyInstaller bundles resources under _MEIPASS; exec dir allows overrides.
        candidates.append(os.path.join(getattr(sys, '_MEIPASS', ''), filename))
        candidates.append(os.path.join(os.path.dirname(sys.executable), filename))
    else:
        candidates.append(os.path.join(os.path.dirname(__file__), filename))
        candidates.append(os.path.join(os.getcwd(), filename))
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


class BinMergeFC4150App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FC4150 Bin 文件合并工具')
        self.setFixedSize(600, 480)
        self.boot_path = ''
        self.app_path = ''
        self.init_ui()
        self.setAcceptDrops(True)
        self.load_default_key()

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
        self.offset_edit = QLineEdit('0x22000')
        self.offset_edit.setPlaceholderText('默认 0x22000')
        offset_layout.addWidget(offset_label)
        offset_layout.addWidget(self.offset_edit)

        header_offset_layout = QHBoxLayout()
        header_offset_label = QLabel('App Header Offset (十六进制/字节):')
        self.header_offset_edit = QLineEdit('0x20000')
        self.header_offset_edit.setPlaceholderText('默认 0x20000')
        header_offset_layout.addWidget(header_offset_label)
        header_offset_layout.addWidget(self.header_offset_edit)

        key_length_layout = QHBoxLayout()
        key_length_label = QLabel('Key 长度 (bit):')
        self.key_length_combo = QComboBox()
        self.key_length_combo.addItems(['128', '256'])
        self.key_length_combo.setCurrentText('256')
        key_length_layout.addWidget(key_length_label)
        key_length_layout.addWidget(self.key_length_combo)

        key_input_layout = QHBoxLayout()
        key_label = QLabel('Key (Hex):')
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText('请输入十六进制密钥字符串，无空格，例如 AF06...')
        key_input_layout.addWidget(key_label)
        key_input_layout.addWidget(self.key_edit)

        merge_btn = QPushButton('合并并保存')
        merge_btn.clicked.connect(self.merge_bin)

        layout.addWidget(self.boot_label)
        layout.addWidget(boot_btn)
        layout.addWidget(self.app_label)
        layout.addWidget(app_btn)
        layout.addLayout(offset_layout)
        layout.addLayout(header_offset_layout)
        layout.addLayout(key_length_layout)
        layout.addLayout(key_input_layout)
        layout.addWidget(merge_btn)

        self.setLayout(layout)

    def load_default_key(self):
        key_path = resolve_resource_path('key.txt')
        if not key_path:
            return
        try:
            with open(key_path, 'r', encoding='utf-8') as f:
                key_text = ''.join(line.strip() for line in f)
        except Exception:
            return
        cleaned = key_text.replace('0x', '').replace('0X', '')
        cleaned = cleaned.replace(',', '')
        cleaned = ''.join(cleaned.split())
        if not cleaned:
            return
        self.key_edit.setText(cleaned)
        try:
            key_bytes = bytes.fromhex(cleaned)
        except ValueError:
            return
        if len(key_bytes) == 16:
            self.key_length_combo.setCurrentText('128')
        elif len(key_bytes) == 32:
            self.key_length_combo.setCurrentText('256')

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

    def parse_offset(self, line_edit, default_value):
        text = line_edit.text().strip()
        if not text:
            return default_value
        try:
            return int(text, 0)
        except ValueError:
            raise ValueError(f'偏移量格式错误: {text}')

    def parse_key(self):
        key_text = self.key_edit.text().strip()
        if not key_text:
            raise ValueError('Key 不能为空')
        cleaned = key_text.replace('0x', '').replace('0X', '')
        cleaned = cleaned.replace(',', '')
        cleaned = ''.join(cleaned.split())
        if len(cleaned) % 2 != 0:
            raise ValueError('Key 长度必须是偶数字节的十六进制字符串')
        try:
            key_bytes = bytes.fromhex(cleaned)
        except ValueError:
            raise ValueError('Key 含有非十六进制字符')
        selected_len = int(self.key_length_combo.currentText())
        expected_bytes = 16 if selected_len == 128 else 32
        if len(key_bytes) != expected_bytes:
            raise ValueError(f'Key 字节长度应为 {expected_bytes}，当前为 {len(key_bytes)}')
        return key_bytes

    def merge_bin(self):
        if not self.boot_path or not self.app_path:
            QMessageBox.warning(self, '提示', '请先选择 Boot 和 App 文件')
            return
        try:
            app_offset = self.parse_offset(self.offset_edit, 0x22000)
            header_offset = self.parse_offset(self.header_offset_edit, 0x20000)
        except ValueError as exc:
            QMessageBox.warning(self, '错误', str(exc))
            return
        try:
            key_bytes = self.parse_key()
        except ValueError as exc:
            QMessageBox.warning(self, '错误', str(exc))
            return
        info_length = 0x2000
        try:
            with open(self.boot_path, 'rb') as f_boot, open(self.app_path, 'rb') as f_app:
                boot_data = f_boot.read()
                app_data = f_app.read()
        except Exception as exc:
            QMessageBox.critical(self, '错误', f'读取文件失败: {exc}')
            return
        if len(app_data) <= info_length:
            QMessageBox.warning(
                self,
                '错误',
                f'App 文件大小 ({len(app_data)} 字节) 必须大于 InfoLength 0x{info_length:X}'
            )
            return
        app_length = len(app_data)
        try:
            cmac_signature = self.calc_cmac(app_data, key_bytes)
        except Exception as exc:
            QMessageBox.critical(self, '错误', f'计算 CMAC 失败: {exc}')
            return
        app_header_temp = self.make_app_header(
            appCnt=1,
            crc=0,
            appStartAddr=app_offset + 4,
            appLength=app_length,
            aFingerPrint=cmac_signature
        )
        crc_value = self.calc_crc16(app_header_temp[:-4])
        app_header = self.make_app_header(
            appCnt=1,
            crc=crc_value,
            appStartAddr=app_offset + 4,
            appLength=app_length,
            aFingerPrint=cmac_signature
        )
        required_len = max(len(boot_data), header_offset + len(app_header), app_offset + len(app_data))
        merged = bytearray([0xFF] * required_len)
        merged[:len(boot_data)] = boot_data
        merged[app_offset:app_offset + len(app_data)] = app_data
        merged[header_offset:header_offset + len(app_header)] = app_header
        save_path, _ = QFileDialog.getSaveFileName(self, '保存合并后的 bin 文件', '', 'Bin Files (*.bin)')
        if not save_path:
            return
        try:
            with open(save_path, 'wb') as f_out:
                f_out.write(merged)
        except Exception as exc:
            QMessageBox.critical(self, '错误', f'写入合并文件失败: {exc}')
            return
        try:
            base_name, ext = os.path.splitext(save_path)
            second_bin_path = f'{base_name}_app{ext}'
            second_bin_data = merged[header_offset:]
            with open(second_bin_path, 'wb') as f_out2:
                f_out2.write(second_bin_data)
        except Exception as exc:
            QMessageBox.critical(self, '错误', f'写入 App 子文件失败: {exc}')
            return
        QMessageBox.information(self, '成功', f'合并完成！\n完整文件: {save_path}\nApp 文件: {second_bin_path}')

    def make_app_header(self, appCnt=1, crc=None, appStartAddr=0x22004, appLength=None, aFingerPrint=None):
        isFlashProgramSuccessfull = 1
        isFlashErasedSuccessfull = 1
        isFlashStructValid = 1
        if aFingerPrint is None:
            aFingerPrint = bytes([0xFF] * 17)
        else:
            if len(aFingerPrint) == 16:
                aFingerPrint = aFingerPrint + bytes([0xFF])
            elif len(aFingerPrint) < 17:
                aFingerPrint = aFingerPrint + bytes([0xFF] * (17 - len(aFingerPrint)))
            else:
                aFingerPrint = aFingerPrint[:17]
        finger_padding = bytes([0xFF] * 3)
        appStartAddrLen = 4
        header = bytearray()
        header.append(isFlashProgramSuccessfull)
        header.append(isFlashErasedSuccessfull)
        header.append(isFlashStructValid)
        header.append(appCnt)
        header += aFingerPrint
        header += finger_padding
        header += appStartAddrLen.to_bytes(4, 'little')
        header += appStartAddr.to_bytes(4, 'little')
        if appLength is not None:
            header += appLength.to_bytes(4, 'little')
        if crc is None:
            crc = self.calc_crc16(header)
        header += crc.to_bytes(2, 'little')
        header += bytes([0x00, 0x00])
        return bytes(header)

    def calc_crc16(self, data):
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

    def calc_cmac(self, data, key_bytes):
        cmac_ctx = cmac.CMAC(algorithms.AES(key_bytes), backend=default_backend())
        cmac_ctx.update(data)
        return cmac_ctx.finalize()

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
            if not self.boot_path:
                self.boot_path = file
                self.boot_label.setText(f'Boot 文件: {file}')
            elif not self.app_path:
                self.app_path = file
                self.app_label.setText(f'App 文件: {file}')
            else:
                self.app_path = file
                self.app_label.setText(f'App 文件: {file}')


def main():
    app = QApplication(sys.argv)
    window = BinMergeFC4150App()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
