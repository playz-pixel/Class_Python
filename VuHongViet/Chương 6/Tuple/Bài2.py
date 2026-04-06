_tuple = ('ab', 'b', 'e', 'c', 'e', 'ab')
_new_list = [x for x in _tuple if _tuple.count(x) == 1]
_new_tuple = tuple(_new_list)
print(f"cac phan tu xuat hien 1 lan: {_new_tuple}")