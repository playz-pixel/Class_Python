import math
a = float(input("Nhập hệ số a: "))
b = float(input("Nhập hệ số b: "))
c = float(input("Nhập hệ số c: "))

if a == 0:
    if b == 0:
        if c == 0:
            print("Phương trình có vô số nghiệm.")
        else:
            print("Phương trình vô nghiệm.")
    else:
        x = -c / b
        print(f"Phương trình bậc 1 có nghiệm x = {x}")
else:
    delta = b**2 - 4*a*c
    print(f"Delta = {delta}")

    if delta < 0:
        print("Phương trình vô nghiệm.")
    elif delta == 0:
        x = -b / (2 * a)
        print(f"Phương trình có nghiệm kép: x1 = x2 = {x}")
    else:
        x1 = (-b + math.sqrt(delta)) / (2 * a)
        x2 = (-b - math.sqrt(delta)) / (2 * a)
        print(f"Phương trình có 2 nghiệm phân biệt:")
        print(f"x1 = {x1}")
        print(f"x2 = {x2}")