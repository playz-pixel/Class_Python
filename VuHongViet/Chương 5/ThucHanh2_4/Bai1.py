file_name = 'data.txt'

try:
    n = int(input("Nhập số dòng n cần đọc: "))
    
    with open(file_name, 'r', encoding='utf-8') as f:
        for i in range(n):
            line = f.readline()
            if not line:
                break  
            print(line.strip())
            
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{file_name}'")
except ValueError:
    print("Vui lòng nhập một số nguyên hợp lệ.")