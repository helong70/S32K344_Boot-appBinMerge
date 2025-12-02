import os
from cryptography.hazmat.primitives import cmac
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.backends import default_backend

boot_path = r'd:\flagchip-workspace\bootloader\Debug_FLASH\bootloader.bin'
app_path = r'd:\flagchip-workspace\demo\Debug_FLASH\demo.bin'
save_path = r'd:\CodeWorkSpace\CT_BinMerge\merged_fc4150_test.bin'

def calc_cmac_aes128(data, key):
    # 使用 AES-128 CMAC 计算签名
    c = cmac.CMAC(algorithms.AES(key), backend=default_backend())
    c.update(data)
    return c.finalize()  # 返回 16 字节的 CMAC

def make_app_header(appCnt=1, crc=None, appStartAddr=0x12004, appLength=None, aFingerPrint=None):
    isFlashProgramSuccessfull = 1
    isFlashErasedSuccessfull = 1
    isFlashStructValid = 1
    if aFingerPrint is None:
        aFingerPrint = bytes([0xFF]*17)
    else:
        # 确保 aFingerPrint 长度为 17 字节
        if len(aFingerPrint) == 16:
            aFingerPrint = aFingerPrint + bytes([0xFF])
        elif len(aFingerPrint) < 17:
            aFingerPrint = aFingerPrint + bytes([0xFF] * (17 - len(aFingerPrint)))
        else:
            aFingerPrint = aFingerPrint[:17]
    finger_padding = bytes([0xFF]*3)
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
    # 对于 FC4150，在 appStartAddr 和 crc 之间插入 appLength (uint32)
    if appLength is not None:
        header += appLength.to_bytes(4, 'little')
    # CRC：如果传入 None 则自动计算
    if crc is None:
        crc = calc_crc16(header)
    header += crc.to_bytes(2, 'little')
    header += bytes([0x00, 0x00])
    return bytes(header)


def calc_crc16(data):
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


def parse_header(hdr_bytes):
    if len(hdr_bytes) < 36:
        return None
    isProg = hdr_bytes[0]
    isErase = hdr_bytes[1]
    isValid = hdr_bytes[2]
    appCnt = hdr_bytes[3]
    aFinger = hdr_bytes[4:21]
    finger_padding = hdr_bytes[21:24]
    appStartAddrLen = int.from_bytes(hdr_bytes[24:28], 'little')
    appStartAddr = int.from_bytes(hdr_bytes[28:32], 'little')
    # Check if appLength is present (header is longer)
    if len(hdr_bytes) >= 40:
        appLength = int.from_bytes(hdr_bytes[32:36], 'little')
        crc = int.from_bytes(hdr_bytes[36:38], 'little')
        tail = hdr_bytes[38:40]
    else:
        appLength = None
        crc = int.from_bytes(hdr_bytes[32:34], 'little')
        tail = hdr_bytes[34:36]
    return {
        'isProg': isProg,
        'isErase': isErase,
        'isValid': isValid,
        'appCnt': appCnt,
        'appStartAddrLen': appStartAddrLen,
        'appStartAddr': appStartAddr,
        'appLength': appLength,
        'crc': crc,
        'tail': tail,
    }


def main():
    if not os.path.exists(boot_path):
        print(f'Boot file not found: {boot_path}')
        return
    if not os.path.exists(app_path):
        print(f'App file not found: {app_path}')
        return
    with open(boot_path, 'rb') as f:
        boot_data = f.read()
    with open(app_path, 'rb') as f:
        app_data = f.read()

    # FC4150 behavior
    app_offset = 0x22000
    header_write_offset = 0x20000  # header physically written here per current logic
    info_length = 0x2000  # InfoLength 默认值
    
    # 验证 app_data 长度
    if len(app_data) <= info_length:
        print(f'Error: App file size ({len(app_data)} bytes, 0x{len(app_data):X}) is smaller than or equal to InfoLength (0x{info_length:X})')
        print(f'App file must be larger than {info_length} bytes for FC4150')
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
    cmac_signature = calc_cmac_aes128(cmac_data, cmac_key)
    
    # 先生成带 CMAC 签名的 header,CRC 字段设为 0
    app_header_temp = make_app_header(appCnt=1, crc=0, appStartAddr=0x22004, appLength=app_length, aFingerPrint=cmac_signature)
    # 计算 CRC (排除最后 4 字节: crc(2) + tail(2))
    crc_value = calc_crc16(app_header_temp[:-4])
    # 生成最终 header,包含计算出的 CRC
    app_header = make_app_header(appCnt=1, crc=crc_value, appStartAddr=0x22004, appLength=app_length, aFingerPrint=cmac_signature)

    required_len = len(boot_data)
    if header_write_offset and header_write_offset + len(app_header) > required_len:
        required_len = header_write_offset + len(app_header)
    if app_offset + len(app_data) > required_len:
        required_len = app_offset + len(app_data)

    merged = bytearray([0xFF] * required_len)
    merged[:len(boot_data)] = boot_data

    # write app first, then header (avoid header being overwritten by app)
    merged[app_offset:app_offset+len(app_data)] = app_data
    if header_write_offset:
        merged[header_write_offset:header_write_offset+len(app_header)] = app_header

    with open(save_path, 'wb') as f:
        f.write(merged)
    
    # FC4150: 生成第二个 bin 文件(从 header_write_offset 开始)
    if header_write_offset:
        base_name = os.path.splitext(save_path)[0]
        ext = os.path.splitext(save_path)[1]
        second_bin_path = f"{base_name}_app{ext}"
        
        # 从 header_write_offset 开始截取到文件末尾
        second_bin_data = merged[header_write_offset:]
        with open(second_bin_path, 'wb') as f2:
            f2.write(second_bin_data)
        
        print(f"\nSecond bin file (from 0x{header_write_offset:X}) saved to: {second_bin_path} (size: {len(second_bin_data)})")



    print(f'Merged file saved to: {save_path} (size: {len(merged)})')
    print(f'App data size: {len(app_data)}, App offset: 0x{app_offset:X}')
    print(f'Calculated appLength: {app_length} (0x{app_length:X})')
    print(f'CMAC signature (16 bytes): {cmac_signature.hex().upper()}')

    # Inspect header area at 0x20000
    hdr_at_20000 = merged[0x20000:0x20000+40]
    parsed = parse_header(hdr_at_20000)
    print('\nHeader parsed at 0x20000:')
    for key, val in parsed.items():
        if key == 'tail':
            print(f'  {key}: {val.hex()}')
        elif isinstance(val, int):
            print(f'  {key}: {val} (0x{val:X})')
        else:
            print(f'  {key}: {val}')

    # Search for header pattern in merged
    idx = merged.find(app_header)
    if idx != -1:
        print(f'\nExact header bytes found at offset: 0x{idx:X}')
    else:
        print('\nExact header bytes not found as contiguous sequence in merged file (may be overwritten by app data).')

if __name__ == '__main__':
    main()
