file_name = 'setInfo.txt'
print("--- Nhập thông tin cá nhân ---")
ten = input("Tên: ")
tuoi = input("Tuổi: ")
email = input("Email: ")
skype = input("Skype: ")
dia_chi = input("Địa chỉ: ")
noi_lam_viec = input("Nơi làm việc: ")

with open(file_name, 'w', encoding='utf-8') as f:
    f.write(f"Tên: {ten}\n")
    f.write(f"Tuổi: {tuoi}\n")
    f.write(f"Email: {email}\n")
    f.write(f"Skype: {skype}\n")
    f.write(f"Địa chỉ: {dia_chi}\n")
    f.write(f"Nơi làm việc: {noi_lam_viec}\n")

print("\nĐã lưu thông tin vào file thành công!")
print("-" * 30)

print("--- Đọc dữ liệu từ file 'setInfo.txt' ---")
try:
    with open(file_name, 'r', encoding='utf-8') as f:
        noi_dung = f.read()
        print(noi_dung)
except FileNotFoundError:
    print("Lỗi: Không tìm thấy file dữ liệu.")