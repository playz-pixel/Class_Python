class PayrollService:
    @staticmethod
    def calculate_total_payroll(employees_dict):
        """Tính tổng lương công ty (Menu 4b)"""
        return sum(emp.calculate_salary() for emp in employees_dict.values())

    @staticmethod
    def get_top_3_salaries(employees_dict):
        """Lấy top 3 nhân viên lương cao nhất (Menu 4c)"""
        emp_list = list(employees_dict.values())
        sorted_list = sorted(emp_list, key=lambda x: x.calculate_salary(), reverse=True)
        return sorted_list[:3]

    @staticmethod
    def get_salary_stats_by_type(employees_dict):
        """Thống kê số lượng nhân viên theo loại (Menu 8a)"""
        stats = {"Manager": 0, "Developer": 0, "Intern": 0}
        for emp in employees_dict.values():
            stats[type(emp).__name__] += 1
        return stats
    @staticmethod
    def get_top_10_busy_employees(employees_dict):
        """Lấy top 10 nhân viên tham gia nhiều dự án nhất (Menu 8c mở rộng)"""
        emp_list = list(employees_dict.values())
        sorted_list = sorted(emp_list, key=lambda x: len(x.projects), reverse=True)
        return sorted_list[:10]
    @staticmethod
    def get_top_10_least_busy_employees(employees_dict):
        """Lấy top 10 nhân viên tham gia ít dự án nhất"""
        emp_list = list(employees_dict.values())
        sorted_list = sorted(emp_list, key=lambda x: len(x.projects))
        return sorted_list[:10]