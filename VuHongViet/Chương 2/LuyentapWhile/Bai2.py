n = int(input("Nhập số nguyên dương n: "))
giai_thua = 1
i = 1

while i <= n:
    giai_thua *= i
    i += 1

print(f"{n}! = {giai_thua}")