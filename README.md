# BTL-Py — Clothing Shop (FastAPI + MySQL)

Ứng dụng web bán quần áo đơn giản xây dựng bằng FastAPI, Jinja2 Templates và MySQL. Dự án bao gồm trang người dùng (xem sản phẩm, giỏ hàng, đặt hàng) và trang quản trị (quản lý tài khoản, sản phẩm, đơn hàng, doanh thu).

Repo này được fork từ [sonhaiptit/BTL-Py](https://github.com/sonhaiptit/BTL-Py).

- Ngôn ngữ/stack chính: HTML, Python, JavaScript, CSS
- Thư viện chính: FastAPI, Uvicorn, Jinja2, mysql-connector-python, python-multipart

## Tính năng chính

Người dùng:
- Xem trang chủ và danh sách sản phẩm, lọc theo danh mục/nhãn hiệu, tìm kiếm, phân trang
- Xem chi tiết sản phẩm
- Đăng ký, đăng nhập, đăng xuất
- Quản lý hồ sơ cá nhân (xem/sửa), xóa tài khoản
- Giỏ hàng: thêm/xóa/cập nhật số lượng, quy trình checkout
- Lịch sử đơn hàng, hủy đơn khi còn trạng thái chờ xác nhận

Quản trị:
- Đăng nhập quản trị
- Bảng điều khiển
- Quản lý tài khoản: xem, khóa/mở khóa, xóa tài khoản (trừ ADMIN)
- Quản lý sản phẩm: xem, thêm, cập nhật
- Quản lý đơn hàng: xem, xóa (và hoàn kho khi xóa đơn “chờ xác nhận”)
- Thống kê doanh thu theo thương hiệu và danh mục

## Cấu trúc thư mục

```text
.
├─ main.py                # Ứng dụng FastAPI, định nghĩa routes (user + admin)
├─ run.py                 # Chạy Uvicorn, tự động chọn port trống 8000–8010
├─ requirements.txt       # Phụ thuộc Python
├─ clothing_shop.sql      # Script tạo schema & dữ liệu mẫu MySQL
├─ templates/             # Giao diện Jinja2 (base, index, products, cart, checkout, ...; admin/*)
├─ static/
│  ├─ css/
│  ├─ js/
│  └─ img/
├─ test_main.http         # Mẫu gọi thử endpoints (dùng HTTP Client)
└─ .gitignore
```

Các điểm vào chính:
- Ứng dụng: `main.py` (có thể chạy trực tiếp hoặc qua `run.py`)
- Server runner: `run.py` (khuyến nghị dùng để tự chọn port sẵn sàng)

## Yêu cầu hệ thống

- Python 3.9+ (khuyến nghị 3.10+)
- MySQL Server 8.x
- Trình duyệt web hiện đại

## Cài đặt và chạy

1) Clone repo
```bash
git clone https://github.com/NTDung123/BTL-Py.git
cd BTL-Py
```

2) Tạo môi trường ảo và cài phụ thuộc
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

3) Khởi tạo cơ sở dữ liệu MySQL
- Tạo database `clothing_shop` và import file `clothing_shop.sql`.

Ví dụ bằng dòng lệnh:
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS clothing_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p clothing_shop < clothing_shop.sql
```

4) Cấu hình kết nối DB
- Mặc định, cấu hình trong `main.py`:
  - host: `localhost`
  - user: `root`
  - password: `Ntdung123!`  ← Hãy đổi thành mật khẩu MySQL của bạn
  - database: `clothing_shop`
  - charset: `utf8mb4`

Bạn nên cập nhật `DB_CONFIG` trong `main.py` cho phù hợp môi trường của mình. Lưu ý: Mật khẩu đang được hard-code chỉ phục vụ demo — không phù hợp production.

5) Chạy ứng dụng
```bash
# Cách 1 (khuyến nghị): tự chọn port trống 8000–8010
python run.py

# Cách 2: chạy trực tiếp app
python main.py
```

- Mở trình duyệt: http://localhost:8000 (nếu port 8000 bận, `run.py` sẽ chọn 8001, 8002, …)
- Một số route chính sẽ được in ra console khi khởi động.

## Đăng nhập thử

- Quản trị: username `admin`, password `admin` (được mã hóa cứng trong mã nguồn để tiện demo)
- Người dùng: tự đăng ký tại `/register`

Lưu ý: Ứng dụng demo dùng mật khẩu dạng plain text và cookie đơn giản — KHÔNG dùng cho môi trường production.

## Kiểm thử nhanh endpoints

File [`test_main.http`](./test_main.http) có thể dùng với các HTTP Client (ví dụ: plugin "HTTP Client" trong VS Code/IntelliJ).

Ví dụ:
```http
GET http://127.0.0.1:8000/
Accept: application/json
```



Xem [requirements.txt](./requirements.txt):
- fastapi==0.104.1
- uvicorn==0.24.0
- mysql-connector-python==8.2.0
- jinja2==3.1.2
- python-multipart==0.0.6

## Giấy phép