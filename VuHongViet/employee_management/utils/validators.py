import re
from exceptions.employee_exceptions import InvalidAgeError, InvalidSalaryError

class Validator:
    @staticmethod
    def validate_integer(value, field_name):
        """Kiểm tra xem đầu vào có phải là số nguyên hợp lệ không (Menu 9)"""
        try:
            val = int(value)
            return val
        except ValueError:
            raise ValueError(f"{field_name} phải là một số nguyên!")

    @staticmethod
    def validate_email(email):
        """Kiểm tra định dạng email (Yêu cầu bảng Exception)"""
        if "@" not in email:
            raise ValueError("Email sai định dạng (thiếu ký tự @)")
        return email

    @staticmethod
    def validate_age(age):
        """Kiểm tra tuổi từ 18-65"""
        if not (18 <= age <= 65):
            raise InvalidAgeError(f"Tuổi {age} không hợp lệ (phải từ 18-65)")
        return age

    @staticmethod
    def validate_score(score):
        """Kiểm tra điểm hiệu suất 0-10"""
        if not (0 <= score <= 10):
            raise ValueError("Điểm hiệu suất phải nằm trong khoảng 0-10")
        return score