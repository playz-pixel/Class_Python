n = int(input("Nhập số nguyên dương n: "))

if n < 2:
    print("Không phải số nguyên tố")
else:
    la_so_nguyen_to = True
    i = 2
    # Kiểm tra xem n có chia hết cho số nào từ 2 đến căn bậc hai của n không
    while i * i <= n:
        if n % i == 0:
            la_so_nguyen_to = False
            break
        i += 1
    
    if la_so_nguyen_to:
        print("Đây là số nguyên tố")
    else:
        print("Không phải số nguyên tố")