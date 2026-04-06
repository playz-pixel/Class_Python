_list = ['python', 'java', 'c++', 'python', 'ruby']
try:
    n = int(input("nhap so nguyen N = "))
    ket_qua = [work for work in _list if len(work) > n]
    print(f"cac chuoi co do dai lon hon {n}: {ket_qua}")
except ValueError:
    print("vui long nhap mot so nguyen hop le.")