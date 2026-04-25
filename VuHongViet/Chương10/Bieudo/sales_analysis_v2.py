import pandas as pd
import matplotlib.pyplot as plt

# 1. Đọc dữ liệu từ file CSV
# Đảm bảo file CSV đặt cùng thư mục với file code này
file_path = 'sales-data-sample.csv' 

try:
    # Đọc file với bảng mã utf-8 hoặc latin1 tùy file của bạn
    df = pd.read_csv(file_path, encoding='utf-8')
    print("Đã tải dữ liệu thành công!")
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{file_path}'. Hãy kiểm tra lại tên file.")
    exit()

# 2. Tiền xử lý dữ liệu
# Chuyển OrderDate sang định dạng datetime (xử lý cả múi giờ Z)
df['OrderDate'] = pd.to_datetime(df['OrderDate'])

# Trích xuất thông tin thời gian
df['Month'] = df['OrderDate'].dt.month
df['Year'] = df['OrderDate'].dt.year
df['Quarter'] = df['OrderDate'].dt.quarter
df['Month_Year'] = df['OrderDate'].dt.to_period('M').astype(str) # Dùng để vẽ theo tiến trình tháng-năm

# 3. Vẽ biểu đồ
plt.style.use('ggplot') # Sử dụng style cho biểu đồ đẹp hơn
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# --- Biểu đồ A: Doanh thu theo Tháng (Tổng hợp tất cả các năm) ---
monthly_sales = df.groupby('Month')['Sales'].sum()
axes[0, 0].plot(monthly_sales.index, monthly_sales.values, marker='s', color='blue')
axes[0, 0].set_title('Tổng Doanh Thu Theo Tháng (Tất cả các năm)')
axes[0, 0].set_xticks(range(1, 13))
axes[0, 0].set_xlabel('Tháng')

# --- Biểu đồ B: Doanh thu theo Quý ---
quarterly_sales = df.groupby('Quarter')['Sales'].sum()
axes[0, 1].bar(quarterly_sales.index.astype(str), quarterly_sales.values, color='orange')
axes[0, 1].set_title('Doanh Thu Theo Quý')
axes[0, 1].set_xlabel('Quý')

# --- Biểu đồ C: Doanh thu theo Loại mặt hàng (Category) ---
category_sales = df.groupby('Category')['Sales'].sum().sort_values()
category_sales.plot(kind='barh', ax=axes[1, 0], color='green')
axes[1, 0].set_title('Doanh Thu Theo Loại Mặt Hàng')
axes[1, 0].set_xlabel('Doanh Thu')

# --- Biểu đồ D: Doanh thu theo Năm ---
yearly_sales = df.groupby('Year')['Sales'].sum()
yearly_sales.plot(kind='pie', ax=axes[1, 1], autopct='%1.1f%%', startangle=90, cmap='Pastel1')
axes[1, 1].set_title('Tỷ Trọng Doanh Thu Theo Năm')
axes[1, 1].set_ylabel('') # Ẩn chữ 'Sales' ở trục Y

# Tối ưu hóa khoảng cách giữa các biểu đồ
plt.tight_layout()

# 4. Hiển thị biểu đồ
print("Đang hiển thị biểu đồ...")
plt.show()