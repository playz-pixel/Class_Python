import sqlite3
import os

# --- 1. KẾT NỐI DATABASE ---
def connect_db():
    # Lấy đường dẫn của thư mục chứa file main.py hiện tại
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Kết hợp với tên file database
    db_path = os.path.join(current_dir, 'nhansu.db')
    
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Lỗi kết nối: {e}")
        return None

# --- 2. CÁC HÀM CHỨC NĂNG ---

def them_nhan_su():
    conn = connect_db()
    cursor = conn.cursor()
    print("\n--- Thêm mới nhân sự ---")
    cccd = input("Nhập số CCCD: ")
    ten = input("Nhập họ và tên: ")
    ns = input("Nhập ngày sinh (dd/mm/yyyy): ")
    gt = input("Nhập giới tính: ")
    dc = input("Nhập địa chỉ: ")
    
    try:
        cursor.execute("INSERT INTO nhan_su VALUES (?, ?, ?, ?, ?)", (cccd, ten, ns, gt, dc))
        conn.commit()
        print("Thêm thành công!")
    except sqlite3.IntegrityError:
        print("Lỗi: Số CCCD này đã tồn tại.")
    conn.close()

def hien_thi_danh_sach():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nhan_su")
    rows = cursor.fetchall()
    
    print("\n--- Danh sách nhân sự ---")
    print(f"{'CCCD':<15} | {'Họ tên':<20} | {'Ngày sinh':<12} | {'GT':<5} | {'Địa chỉ'}")
    print("-" * 70)
    for row in rows:
        print(f"{row[0]:<15} | {row[1]:<20} | {row[2]:<12} | {row[3]:<5} | {row[4]}")
    conn.close()

def sua_nhan_su():
    conn = connect_db()
    cursor = conn.cursor()
    cccd = input("\nNhập số CCCD của người cần sửa: ")
    
    # Kiểm tra tồn tại
    cursor.execute("SELECT * FROM nhan_su WHERE cccd=?", (cccd,))
    if not cursor.fetchone():
        print("Không tìm thấy nhân sự!")
        return

    ten = input("Họ tên mới: ")
    ns = input("Ngày sinh mới: ")
    gt = input("Giới tính mới: ")
    dc = input("Địa chỉ mới: ")
    
    cursor.execute("UPDATE nhan_su SET ho_ten=?, ngay_sinh=?, gioi_tinh=?, dia_chi=? WHERE cccd=?", 
                   (ten, ns, gt, dc, cccd))
    conn.commit()
    print("Cập nhật thành công!")
    conn.close()

def xoa_nhan_su():
    conn = connect_db()
    cursor = conn.cursor()
    cccd = input("\nNhập số CCCD cần xóa: ")
    cursor.execute("DELETE FROM nhan_su WHERE cccd=?", (cccd,))
    conn.commit()
    if cursor.rowcount > 0:
        print("Đã xóa nhân sự.")
    else:
        print("Không tìm thấy CCCD này.")
    conn.close()

def tim_kiem():
    conn = connect_db()
    cursor = conn.cursor()
    print("\n1. Tìm theo CCCD\n2. Tìm theo Tên\n3. Tìm theo Địa chỉ")
    chon = input("Chọn kiểu tìm kiếm: ")
    keyword = input("Nhập từ khóa cần tìm: ")
    
    sql = ""
    if chon == '1': sql = "SELECT * FROM nhan_su WHERE cccd LIKE ?"
    elif chon == '2': sql = "SELECT * FROM nhan_su WHERE ho_ten LIKE ?"
    elif chon == '3': sql = "SELECT * FROM nhan_su WHERE dia_chi LIKE ?"
    
    cursor.execute(sql, ('%' + keyword + '%',))
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

# --- 3. MENU ĐIỀU KHIỂN ---

def menu():
    while True:
        print("\n===== QUẢN LÝ NHÂN SỰ =====")
        print("1. Thêm mới")
        print("2. Sửa thông tin")
        print("3. Xóa nhân sự")
        print("4. Xem danh sách")
        print("5. Tìm kiếm")
        print("0. Thoát")
        
        choice = input("Mời chọn (0-5): ")
        if choice == '1': them_nhan_su()
        elif choice == '2': sua_nhan_su()
        elif choice == '3': xoa_nhan_su()
        elif choice == '4': hien_thi_danh_sach()
        elif choice == '5': tim_kiem()
        elif choice == '0': break
        else: print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    menu()