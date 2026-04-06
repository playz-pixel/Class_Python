_list = ['abc' , 'xyz' , 'abcd' , '1233' , 'ii' , '1222' , '5a' ]
n_min = 4
count = 0
for i in _list:
    if len(i) >= n_min and i[0] == i[-1]:
        count += 1
print(f"Số lượng chuỗi thỏa mãn điều kiện: {count}")