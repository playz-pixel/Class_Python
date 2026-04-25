import pandas as pd
import matplotlib.pyplot as plt
file_path = 'sales-data-sample.csv' 

try:
    df = pd.read_csv(file_path, encoding='utf-8')
    print("Đã tải dữ liệu thành công!")
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{file_path}'. Hãy kiểm tra lại tên file.")
    exit()
df['OrderDate'] = pd.to_datetime(df['OrderDate'])

df['Month'] = df['OrderDate'].dt.month
df['Year'] = df['OrderDate'].dt.year
df['Quarter'] = df['OrderDate'].dt.quarter
df['Month_Year'] = df['OrderDate'].dt.to_period('M').astype(str) 

plt.style.use('ggplot') 
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

monthly_sales = df.groupby('Month')['Sales'].sum()
axes[0, 0].plot(monthly_sales.index, monthly_sales.values, marker='s', color='blue')
axes[0, 0].set_title('Tổng Doanh Thu Theo Tháng (Tất cả các năm)')
axes[0, 0].set_xticks(range(1, 13))
axes[0, 0].set_xlabel('Tháng')

quarterly_sales = df.groupby('Quarter')['Sales'].sum()
axes[0, 1].bar(quarterly_sales.index.astype(str), quarterly_sales.values, color='orange')
axes[0, 1].set_title('Doanh Thu Theo Quý')
axes[0, 1].set_xlabel('Quý')

category_sales = df.groupby('Category')['Sales'].sum().sort_values()
category_sales.plot(kind='barh', ax=axes[1, 0], color='green')
axes[1, 0].set_title('Doanh Thu Theo Loại Mặt Hàng')
axes[1, 0].set_xlabel('Doanh Thu')

yearly_sales = df.groupby('Year')['Sales'].sum()
yearly_sales.plot(kind='pie', ax=axes[1, 1], autopct='%1.1f%%', startangle=90, cmap='Pastel1')
axes[1, 1].set_title('Tỷ Trọng Doanh Thu Theo Năm')
axes[1, 1].set_ylabel('') 

plt.tight_layout()

print("Đang hiển thị biểu đồ...")
plt.show()