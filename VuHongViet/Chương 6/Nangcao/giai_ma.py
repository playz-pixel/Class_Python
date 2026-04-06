import json

def chuong_trinh_giai_ma():
    try:
        with open('bo_ma.json', 'r', encoding='utf-8') as f:
            cipher_dict = json.load(f)
        reverse_dict = {v: k for k, v in cipher_dict.items()}
        with open('ket_qua_ma_hoa.txt', 'r', encoding='utf-8') as f:
            text_da_ma_hoa = f.read()
        text_giai_ma = ""
        for char in text_da_ma_hoa:
            text_giai_ma += reverse_dict.get(char, char)
        print("--- Giải mã thành công! ---")
        print(f"Nội dung gốc khôi phục được: {text_giai_ma}")

    except FileNotFoundError:
        print("Lỗi: Thiếu tệp 'bo_ma.json' hoặc 'ket_qua_ma_hoa.txt'!")

chuong_trinh_giai_ma()