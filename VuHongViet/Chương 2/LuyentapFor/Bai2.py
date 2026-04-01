n = int(input("Nhập số nguyên n: "))

if n > 10:
    print("Số nhập vào phải bé hơn 10.")
else:
    print(f"Các số chẵn từ 1 đến {n} là:")
    for i in range(1, n + 1):
        if i % 2 == 0:
            print(i, end=" ")
    print()