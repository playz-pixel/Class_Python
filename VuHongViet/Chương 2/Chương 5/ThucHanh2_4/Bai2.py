file_name = 'output.txt'
content = "Chào mừng bạn đến với bài thực hành lập trình Python!"

with open(file_name, 'w', encoding='utf-8') as f:
    f.write(content)


with open(file_name, 'r', encoding='utf-8') as f:
    data = f.read()
    print("Nội dung trong file là:")
    print(data)