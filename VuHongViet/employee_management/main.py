import sys
from models import Manager, Developer, Intern
from services import Company, PayrollService
from utils import Validator, Formatter
from exceptions import (
    EmployeeException, 
    EmployeeNotFoundError, 
    ProjectAllocationError,
    DuplicateEmployeeError
)

def main():
    company = Company()
    payroll = PayrollService()
    
    # Dữ liệu mẫu (tùy chọn)
    # company.add_employee(Manager("M01", "Nguyen Van A", 40, "a@abc.com", 20000))

    while True:
        Formatter.print_header("Hệ thống quản lý nhân viên công ty ABC")
        print("1. Thêm nhân viên mới")
        print("2. Hiển thị danh sách nhân viên")
        print("3. Tìm kiếm nhân viên")
        print("4. Quản lý lương")
        print("5. Quản lý dự án")
        print("6. Đánh giá hiệu suất")
        print("7. Quản lý nhân sự (Xóa/Tăng lương/Thăng chức)")
        print("8. Thống kê báo cáo")
        print("9. Thoát")
        print("="*50)
        
        try:
            choice = input("Chọn chức năng (1-9): ")
            
            # --- 1. THÊM NHÂN VIÊN ---
            if choice == '1':
                print("\na. Thêm Manager | b. Thêm Developer | c. Thêm Intern")
                sub_choice = input("Chọn loại: ").lower()
                
                eid = input("Nhập ID: ")
                name = input("Nhập tên: ")
                age = Validator.validate_integer(input("Nhập tuổi: "), "Tuổi")
                email = Validator.validate_email(input("Nhập email: "))
                salary = float(input("Nhập lương cơ bản: "))
                
                if sub_choice == 'a':
                    emp = Manager(eid, name, age, email, salary)
                elif sub_choice == 'b':
                    lang = input("Ngôn ngữ lập trình: ")
                    emp = Developer(eid, name, age, email, salary, lang)
                elif sub_choice == 'c':
                    emp = Intern(eid, name, age, email, salary)
                else:
                    print("Lựa chọn không hợp lệ!")
                    continue
                
                company.add_employee(emp)
                print(">>> Thêm nhân viên thành công!")

            # --- 2. HIỂN THỊ DANH SÁCH ---
            elif choice == '2':
                print("\na. Tất cả | b. Theo loại | c. Theo hiệu suất")
                sub = input("Chọn: ")
                if sub == 'a':
                    Formatter.display_employee_table(company.get_all_employees())
                elif sub == 'c':
                    Formatter.display_employee_table(company.get_all_employees(sort_by_performance=True))

            # --- 3. TÌM KIẾM ---
            elif choice == '3':
                eid = input("Nhập ID cần tìm: ")
                emp = company.get_employee_by_id(eid)
                Formatter.display_employee_table([emp])

            # --- 4. QUẢN LÝ LƯƠNG ---
            elif choice == '4':
                print(f"Tổng lương công ty: {Formatter.format_currency(payroll.calculate_total_payroll(company.employees))}")
                print("Top 3 lương cao nhất:")
                Formatter.display_employee_table(payroll.get_top_3_salaries(company.employees))

            # --- 5. QUẢN LÝ DỰ ÁN ---
            elif choice == '5':
                print("\na. Phân công dự án | b. Xóa nhân viên khỏi dự án")
                print("c. Hiển thị dự án của 1 nhân viên | d. Liệt kê nhân viên theo dự án")
                sub = input("Chọn: ").lower()

                if sub == 'a':
                    eid = input("Nhập ID nhân viên: ")
                    p_name = input("Tên dự án mới: ")
                    company.assign_project(eid, p_name)
                    print(f">>> Đã phân công dự án '{p_name}'")
                elif sub == 'b':
                    eid = input("Nhập ID nhân viên: ")
                    p_name = input("Nhập tên dự án muốn xóa: ")
                    try:
                        company.remove_employee_from_project(eid, p_name)
                        print(f">>> Đã xóa dự án '{p_name}' khỏi nhân viên {eid} thành công.")
                    except ValueError as e:
                        print(f"[THÔNG BÁO] {e}")
                elif sub == 'c':
                    eid = input("Nhập ID nhân viên cần xem dự án: ")
                    emp = company.get_employee_by_id(eid) 
                    print(f"\nDanh sách dự án của {emp.name}:")
                    if not emp.projects:
                        print("- Chưa tham gia dự án nào.")
                    else:
                        for idx, p in enumerate(emp.projects, 1):
                            print(f"{idx}. {p}")
                    input("\nNhấn Enter để quay lại menu...")

                elif sub == 'd':
                    p_name = input("Nhập tên dự án cần tra cứu: ")
                    emps = company.get_employees_by_project(p_name)
                    
                    Formatter.print_header(f"THÀNH VIÊN THAM GIA DỰ ÁN: {p_name.upper()}")
                    Formatter.display_employee_projects_table(emps)

            # --- 6. ĐÁNH GIÁ HIỆU SUẤT ---
            elif choice == '6':
                eid = input("Nhập ID nhân viên: ")
                score = float(input("Nhập điểm (0-10): "))
                emp = company.get_employee_by_id(eid)
                emp.performance_score = Validator.validate_score(score)
                print(">>> Cập nhật điểm thành công!")
            # --- 7. QUẢN LÝ NHÂN SỰ ---
            elif choice == '7':
                print("\na. Xóa nhân viên (Nghỉ việc) | b. Tăng lương | c. Thăng chức")
                sub = input("Chọn chức năng: ").lower()
                
                if sub == 'a':
                    eid = input("Nhập ID nhân viên cần cho nghỉ việc: ")
                    confirm = input(f"Bạn có chắc chắn muốn cho nhân viên {eid} nghỉ việc? (y/n): ")                   
                    if confirm.lower() == 'y':
                        fired_name = company.fire_employee(eid)
                        print(f">>> Đã xóa nhân viên {fired_name} (ID: {eid}) khỏi hệ thống.")
                    else:
                        print(">>> Đã hủy thao tác.")

            # --- 8. THỐNG KÊ ---
            elif choice == '8':
                print("\na. Số lượng theo loại | b. Tổng lương")
                print("c. Top 10 nhiều dự án nhất | d. Top 10 ít dự án nhất")
                sub = input("Chọn: ").lower()
                
                if sub == 'a':
                    stats = payroll.get_salary_stats_by_type(company.employees)
                    print(f"Thống kê nhân sự: {stats}")
                elif sub == 'b':
                    total = payroll.calculate_total_payroll(company.employees)
                    print(f"Tổng lương toàn công ty: {Formatter.format_currency(total)}")
                elif sub == 'c':
                    # Gọi logic đã thêm ở Bước 1 và Bước 2
                    top_busy = payroll.get_top_10_busy_employees(company.employees)
                    Formatter.print_header("TOP 10 NHÂN VIÊN THAM GIA NHIỀU DỰ ÁN NHẤT")
                    Formatter.display_employee_projects_table(top_busy)
                elif sub == 'd':
                    top_least = payroll.get_top_10_least_busy_employees(company.employees)
                    Formatter.print_header("TOP 10 NHÂN VIÊN THAM GIA ÍT DỰ ÁN NHẤT")
                    Formatter.display_employee_projects_table(top_least)

            # --- 9. THOÁT ---
            elif choice == '9':
                print("Cảm ơn bạn đã sử dụng hệ thống. Tạm biệt!")
                sys.exit()

        except EmployeeNotFoundError as e:
            print(f"[LỖI] {e}")
        except EmployeeException as e:
            print(f"[CẢNH BÁO] {e}")
        except ValueError as e:
            print(f"[SAI ĐỊNH DẠNG] {e}")
        except IndexError as e:
            print(f"[DỮ LIỆU] {e}")
        except Exception as e:
            print(f"[LỖI HỆ THỐNG] Đã xảy ra lỗi không xác định: {e}")

if __name__ == "__main__":
    main()