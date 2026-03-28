import time

 
x = time.localtime()
year = x[0]
n = int(input("năm sinh: "))
age = year - n
print("tuổi của bạn là: ", age)