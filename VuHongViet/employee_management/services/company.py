from models import Manager, Developer, Intern
from exceptions.employee_exceptions import (
    EmployeeNotFoundError, 
    DuplicateEmployeeError, 
    ProjectAllocationError
)

class Company:
    def __init__(self):
        self.employees = {}

    def add_employee(self, employee):
        if employee.id in self.employees:
            new_id = f"{employee.id}_new" 
            employee.id = new_id
        self.employees[employee.id] = employee

    def get_employee_by_id(self, emp_id):
        if emp_id not in self.employees:
            raise EmployeeNotFoundError(emp_id)
        return self.employees[emp_id]

    def remove_employee(self, emp_id):
        if emp_id not in self.employees:
            raise EmployeeNotFoundError(emp_id)
        del self.employees[emp_id]

    def find_by_name(self, name):
        return [emp for emp in self.employees.values() if name.lower() in emp.name.lower()]

    def assign_project(self, emp_id, project_name):
        emp = self.get_employee_by_id(emp_id)
        if len(emp.projects) >= 5:
            raise ProjectAllocationError(f"Nhân viên {emp.name} đã tham gia tối đa 5 dự án.")
        emp.projects.append(project_name)

    def get_all_employees(self, sort_by_performance=False):
        emp_list = list(self.employees.values())
        if sort_by_performance:
            return sorted(emp_list, key=lambda x: x.performance_score, reverse=True)
        return emp_list
    def get_employees_by_project(self, project_name):
        """Lọc danh sách nhân viên tham gia một dự án cụ thể"""
        result = []
        for emp in self.employees.values():
            if any(project_name.lower() == p.lower() for p in emp.projects):
                result.append(emp)
        return result
    def fire_employee(self, emp_id):
        """Chức năng sa thải/cho nghỉ việc nhân viên theo ID"""
        if emp_id not in self.employees:
            raise EmployeeNotFoundError(emp_id)
        name = self.employees[emp_id].name
        del self.employees[emp_id]
        return name
    def remove_employee_from_project(self, emp_id, project_name):
        """Xóa một dự án cụ thể khỏi danh sách dự án của nhân viên"""
        emp = self.get_employee_by_id(emp_id)
        
        if project_name in emp.projects:
            emp.projects.remove(project_name)
            return True
        else:
            raise ValueError(f"Nhân viên {emp.name} không tham gia dự án '{project_name}'.")