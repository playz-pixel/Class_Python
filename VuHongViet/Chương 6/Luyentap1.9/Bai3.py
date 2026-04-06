_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
even_list = []
odd_list = []
for x in _list:
    if x % 2 == 0:
        even_list.append(x)
    else:
        odd_list.append(x)
print(f"List số chẵn: {even_list}")
print(f"List số lẻ: {odd_list}")