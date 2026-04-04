n = int(input("nhap so nguyen N = "))
for i in range(1, n):
    tich = 2 * n
    print(f"{tich} = 2 * {i}", end=", " if i < n- 1 else "")
    print()