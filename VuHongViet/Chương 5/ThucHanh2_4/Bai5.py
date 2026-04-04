file_name = 'demo_file2.txt'
content = 'Dem so luong tu xuat hien abc abc abc 12 12 it it eaut'

with open(file_name, 'w', encoding='utf-8') as f:
    f.write(content)

word_count = {}

try:
    with open(file_name, 'r', encoding='utf-8') as f:
        words = f.read().split()
        
        for word in words:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1

    print("Kết quả trả về:")
    print(word_count)

except FileNotFoundError:
    print("Lỗi: Không tìm thấy file 'demo_file2.txt'")