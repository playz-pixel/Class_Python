import json

def chuong_trinh_ma_hoa():
    try:
        with open('bo_ma.json', 'r', encoding='utf-8') as f:
            cipher_dict = json.load(f)
        text_goc = input("Nhập văn bản bạn muốn mã hóa: ").lower()
        text_ma_hoa = ""
        for char in text_goc:
            text_ma_hoa += cipher_dict.get(char, char)
        with open('ket_qua_ma_hoa.txt', 'w', encoding='utf-8') as f:
            f.write(text_ma_hoa)
        
        print("--- Mã hóa thành công! Nội dung đã lưu vào 'ket_qua_ma_hoa.txt' ---")
        print(f"Nội dung mã hóa: {text_ma_hoa}")

    except FileNotFoundError:
        print("Lỗi: Không tìm thấy tệp 'bo_ma.json'!")

chuong_trinh_ma_hoa()