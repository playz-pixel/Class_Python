class Hocvien:
    def __init__(self, _Ten, _Ngaysinh, _Email, _Sdt, _Điachi, _Lop):
        self._Ten = _Ten
        self._Ngaysinh = _Ngaysinh
        self._Email = _Email
        self._Sdt = _Sdt
        self._Điachi = _Điachi
        self._Lop = _Lop
    def show_info(self):
        info = (f"-------thông tin học viên-------\n"
                f"Tên: {self._Ten}\n"
                f"Ngày sinh: {self._Ngaysinh}\n"
                f"Email: {self._Email}\n"
                f"Số điện thoại: {self._Sdt}\n"
                f"Địa chỉ: {self._Điachi}\n"
                f"Lớp: {self._Lop}\n"
                f"--------------------------------\n")
        return info
    def change_info(self, _Điachi="Hà nội", _Lop="IT12.x"):
        self._Điachi = _Điachi
        self._Lop = _Lop
        print(f"Địa chỉ và lớp đã được cập nhật thành:{_Điachi} và lớp thành {_Lop}")
if __name__ == "__main__":
    hocvien1 = Hocvien("Nguyen Van A", "01/01/2000", "nguyenvana@email.com", "0123456789", "Hà Nội", "IT12.1")
    
    print("Dữ liệu ban đầu:")
    print(hocvien1.show_info())
    hocvien1.change_info()
    print("Dữ liệu sau khi cập nhật:")
    print(hocvien1.show_info())