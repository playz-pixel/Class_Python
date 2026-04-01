def bai1():
    n = int(input("Bài 1 - Nhập số nguyên dương n: "))
    if n <= 0:
        print("n phải là số nguyên dương > 0.")
        return
    print("Kết quả bài 1:")
    for i in range(1, n):
        tich = 2 * i
        print(f"{tich} = 2 * {i}", end=", " if i < n - 1 else "")
    print("\n")


def bai2():
    n = int(input("Bài 2 - Nhập một số nguyên n: "))
    if n > 10:
        print("Số nhập vào phải bé hơn 10.")
    else:
        chan = [str(i) for i in range(1, n + 1) if i % 2 == 0]
        print("Các số chẵn trong khoảng từ 1 đến n:", ", ".join(chan) if chan else "(không có)")
    print("\n")


def bai3():
    print("Bài 3 - Các số trong khoảng 80-100 chia hết cho 2 và 3:")
    result = [str(i) for i in range(80, 101) if i % 6 == 0]
    print(", ".join(result) if result else "(không có)")
    print("\n")


def bai4():
    n = int(input("Bài 4 - Nhập số nguyên n < 20: "))
    if n >= 20:
        print("n phải nhỏ hơn 20.")
        return
    result = [str(i) for i in range(1, n + 1) if i % 5 == 0 or i % 7 == 0]
    print("Các số chia hết cho 5 hoặc 7:", ", ".join(result) if result else "(không có)")


if __name__ == '__main__':
    bai1()
    bai2()
    bai3()
    bai4()