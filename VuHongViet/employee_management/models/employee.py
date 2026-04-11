from abc import ABC, abstractmethod
from exceptions.employee_exceptions import InvalidAgeError, InvalidSalaryError

class Employee(ABC):
    def __init__(self, emp_id, name, age, email, base_salary):
        if not (18 <= age <= 65): raise InvalidAgeError("Tuổi phải từ 18-65")
        if base_salary <= 0: raise InvalidSalaryError("Lương phải > 0")
        if "@" not in email: raise ValueError("Email sai định dạng")
        
        self.id = emp_id
        self.name = name
        self.age = age
        self.email = email
        self.base_salary = base_salary
        self.projects = []
        self.performance_score = 0

    @abstractmethod
    def calculate_salary(self):
        pass