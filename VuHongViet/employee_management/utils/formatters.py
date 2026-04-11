class Formatter:
    @staticmethod
    def format_currency(amount):
        """Định dạng số tiền: 1000000 -> 1,000,000 VND"""
        return "{:,.0f} VND".format(amount)

    @staticmethod
    def print_header(title):
        print("\n" + "="*50)
        print(f"{title.upper():^50}")
        print("="*50)

    @staticmethod
    def display_employee_table(employees):
        """Hiển thị danh sách nhân viên theo dạng bảng đẹp mắt"""
        if not employees:
            print(">>> Danh sách trống <<<")
            return

        header = f"{'ID':<10} | {'Tên':<20} | {'Tuổi':<5} | {'Lương':<15} | {'Điểm':<5}"
        print("-" * len(header))
        print(header)
        print("-" * len(header))
        
        for emp in employees:
            salary = Formatter.format_currency(emp.calculate_salary())
            print(f"{emp.id:<10} | {emp.name:<20} | {emp.age:<5} | {salary:<15} | {emp.performance_score:<5}")
        print("-" * len(header))
    
    @staticmethod
    def display_employee_projects_table(employees):
        """Bảng hiển thị chuyên biệt cho thống kê dự án"""
        if not employees:
            print(">>> Danh sách trống <<<")
            return

        header = f"{'ID':<10} | {'Tên':<20} | {'Số dự án':<10} | {'Danh sách dự án'}"
        print("-" * 60)
        print(header)
        print("-" * 60)
        
        for emp in employees:
            projects_str = ", ".join(emp.projects) if emp.projects else "Chưa có"
            print(f"{emp.id:<10} | {emp.name:<20} | {len(emp.projects):<10} | {projects_str}")
        print("-" * 60)