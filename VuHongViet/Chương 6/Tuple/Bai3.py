_tuple = ('ab', 'b', 'e', 'c', 'e', 'ab')
_new_list = []
for x in _tuple:
    if x not in _new_list:
        _new_list.append(x)
_new_tuple = tuple(_new_list)
print(f"cac phan tu khac nhau: {_new_tuple}")