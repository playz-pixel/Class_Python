import sys
import sqlite3
import re
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
# Import giao diện từ file bạn đã convert
from giaodien import Ui_MainWindow 

class MemberApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self)
        
        # 1. Tạo Database ngay khi mở ứng dụng
        self.init_database()
        
        # 2. Kết nối nút bấm Đăng ký (ObjectName: btnDangKy)
        self.uic.btnDangKy.clicked.connect(self.register_process)

    def init_database(self):
        """Tạo file database và bảng nếu chưa có"""
        conn = sqlite3.connect('quanly_thanhvien.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ho TEXT,
                ten TEXT,
                email TEXT,
                matkhau TEXT,
                ngaysinh TEXT,
                gioitinh TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def check_password_strength(self, password):
        """Kiểm tra: 8 ký tự, 1 hoa, 1 thường, 1 số, 1 đặc biệt"""
        if len(password) < 8: return False
        if not re.search("[a-z]", password): return False
        if not re.search("[A-Z]", password): return False
        if not re.search("[0-9]", password): return False
        if not re.search("[!@#$%^&*(),.?\":{}|<>]", password): return False
        return True

    def register_process(self):
        # Lấy dữ liệu từ các ô nhập liệu theo đúng ObjectName trong ảnh
        ho = self.uic.txtHo.text().strip()
        ten = self.uic.txtTen.text().strip()
        email = self.uic.txtEmail.text().strip()
        matkhau = self.uic.txtPassword.text().strip()
        
        # Lấy ngày sinh từ các ComboBox
        ngay = self.uic.comboBox.currentText()
        thang = self.uic.comboBox_2.currentText()
        nam = self.uic.comboBox_3.currentText()
        ngay_sinh = f"{ngay}/{thang}/{nam}"

        # Lấy giới tính từ RadioButton
        gioi_tinh = ""
        if self.uic.radioNam.isChecked():
            gioi_tinh = "Nam"
        elif self.uic.radioNu.isChecked():
            gioi_tinh = "Nữ"

        # Kiểm tra Checkbox đồng ý điều khoản
        dong_y = self.uic.chkDongY.isChecked()


        if not (ho and ten and email and matkhau and gioi_tinh):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ tất cả các trường!")
            return

        if not dong_y:
            QMessageBox.warning(self, "Lỗi", "Bạn phải đồng ý với điều khoản sử dụng!")
            return

        if not self.check_password_strength(matkhau):
            QMessageBox.warning(self, "Lỗi mật khẩu", 
                                "Mật khẩu phải có ít nhất 8 ký tự, gồm chữ hoa, chữ thường, số và ký tự đặc biệt!")
            return


        try:
            conn = sqlite3.connect('quanly_thanhvien.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO members (ho, ten, email, matkhau, ngaysinh, gioitinh) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ho, ten, email, matkhau, ngay_sinh, gioi_tinh))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Thành công", f"Chúc mừng {ten}, bạn đã đăng ký thành công!")
            self.clear_fields()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể lưu dữ liệu: {e}")

    def clear_fields(self):
        """Xóa trắng form sau khi đăng ký thành công"""
        self.uic.txtHo.clear()
        self.uic.txtTen.clear()
        self.uic.txtEmail.clear()
        self.uic.txtPassword.clear()
        self.uic.chkDongY.setChecked(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemberApp()
    window.show()
    sys.exit(app.exec())