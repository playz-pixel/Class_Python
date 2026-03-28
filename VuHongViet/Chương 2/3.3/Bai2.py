_a = int(input("nhập số nguyên dương a: "))
_b = int(input("nhập số nguyên dương b: "))
_c = int(input("nhập số nguyên dương c: "))
if(_a + _b > _c) and (_a + _c > _b) and (_b + _c > _a):
    print("đây là 3 cạnh của một tam giác")
else:
    print("đây không phải là 3 cạnh của một tam giác")
