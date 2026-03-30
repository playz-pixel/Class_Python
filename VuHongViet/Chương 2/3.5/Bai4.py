n = int(input("Nhập vào một số nguyên dương: "))

if n <= 0:
    print("Vui lòng nhập một số nguyên dương lớn hơn 0.")
else:
    chia_het_cho_2 = (n % 2 == 0)
    chia_het_cho_3 = (n % 3 == 0)

    if chia_het_cho_2 and chia_het_cho_3:
        print(f"{n} chia hết cho cả 2 và 3.")
    elif chia_het_cho_2:
        print(f"{n} chia hết cho 2.")
    elif chia_het_cho_3:
        print(f"{n} chia hết cho 3.")
    else:
        print(f"{n} không chia hết cho 2 cũng không chia hết cho 3.")