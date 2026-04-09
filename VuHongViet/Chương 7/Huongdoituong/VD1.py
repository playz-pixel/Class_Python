class Nhanvien:
    dem = 0
    def __init__(self, name, salary):
        self._name = name
        self._salary = salary
        Nhanvien.dem += 1
    def hien_thi_so_luong(self):
        print("Tổng số nhân viên được tạo: %d" % Nhanvien.dem)
    def hien_thi_nhan_vien(self):
        print("Tên:",self._name,", Lương: ", self._salary) 
    def cap_nhat(self, name=None, salary=None):
        self._name=name
        self._salary=salary
nhan_vien_dev = Nhanvien ('Nguyen Van A', 1000)
nhan_vien_test = Nhanvien ('Nguyen Van B', 1200)
nhan_vien_dev.hien_thi_nhan_vien()
nhan_vien_test.hien_thi_nhan_vien()
print(nhan_vien_dev.dem)
print(nhan_vien_dev._name)
print(nhan_vien_test._name)