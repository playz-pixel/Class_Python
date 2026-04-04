file_name = 'demo_file1.txt'
content = 'Thuc \nhanh \nvoi \nfile\n IO\n'

with open(file_name, 'w', encoding='utf-8') as f:
    f.write(content)

print("--- Câu a (In trên một dòng): ---")
with open(file_name, 'r', encoding='utf-8') as f:
    content_a = f.read()
    
    one_line = content_a.replace('\n', ' ')
    print(one_line)

print("\n" + "-"*30)
print("--- Câu b (In theo từng dòng): ---")
with open(file_name, 'r', encoding='utf-8') as f:
    for line in f:
        print(line.strip())