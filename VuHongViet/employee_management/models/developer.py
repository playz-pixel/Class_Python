from .employee import Employee

class Developer(Employee):
    def __init__(self, emp_id, name, age, email, base_salary, language):
        super().__init__(emp_id, name, age, email, base_salary)
        self.language = language

    def calculate_salary(self):
        return self.base_salary + 2000