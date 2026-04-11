class EmployeeException(Exception):
    """Base exception cho hệ thống nhân viên - Mọi lỗi khác sẽ kế thừa từ đây"""
    pass

class EmployeeNotFoundError(EmployeeException):
    """Lỗi khi không tìm thấy ID nhân viên trong hệ thống"""
    def __init__(self, employee_id):
        self.employee_id = employee_id
        super().__init__(f"Không tìm thấy nhân viên có ID: {employee_id}")

class InvalidSalaryError(EmployeeException):
    """Lỗi khi nhập lương <= 0"""
    def __init__(self, message="Lương không hợp lệ! Lương phải là số dương lớn hơn 0."):
        super().__init__(message)

class InvalidAgeError(EmployeeException):
    """Lỗi khi nhập tuổi nằm ngoài khoảng 18-65"""
    def __init__(self, age):
        self.age = age
        super().__init__(f"Tuổi {age} không hợp lệ! Nhân viên phải từ 18 đến 65 tuổi.")

class ProjectAllocationError(EmployeeException):
    """Lỗi khi phân công quá 5 dự án cho 1 nhân viên"""
    def __init__(self, message="Lỗi: Nhân viên này đã tham gia tối đa 5 dự án, không thể thêm mới."):
        super().__init__(message)

class DuplicateEmployeeError(EmployeeException):
    """Lỗi khi thêm một ID đã tồn tại trong hệ thống"""
    def __init__(self, employee_id):
        self.employee_id = employee_id
        super().__init__(f"Lỗi: ID {employee_id} đã tồn tại trong hệ thống.")