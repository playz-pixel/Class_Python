from .employee import Employee

class Intern(Employee):
    def calculate_salary(self):
        return self.base_salary * 0.8