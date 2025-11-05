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

## Các route tiêu biểu

Người dùng:
- GET `/` — Trang chủ, sản phẩm nổi bật
- GET `/products` — Danh sách sản phẩm, hỗ trợ `category`, `brand`, `search`, `page`, `page_size`
- GET `/product/{product_id}` — Chi tiết sản phẩm
- GET `/login` — Trang đăng nhập
- POST `/login` — Xử lý đăng nhập
- GET `/register` — Trang đăng ký
- POST `/register` — Xử lý đăng ký
- GET `/logout` — Đăng xuất
- GET `/profile` — Hồ sơ người dùng
- GET `/edit_profile` — Form sửa hồ sơ
- POST `/edit_profile` — Lưu sửa hồ sơ
- POST `/account/delete` — Xóa tài khoản người dùng
- GET `/cart` — Giỏ hàng
- POST `/cart/add/{product_id}` — Thêm vào giỏ (form: `quantity`, `size`, `color`)
- POST `/cart/update/{cart_item_id}` — Cập nhật số lượng (form: `action` = `increase|decrease`)
- POST `/cart/remove/{cart_item_id}` — Xóa khỏi giỏ
- GET `/checkout` — Trang thanh toán
- POST `/checkout` — Xử lý thanh toán, tạo đơn
- GET `/order_success/{order_id}` — Trang cảm ơn + mã QR VietQR (không áp dụng cho COD)
- GET `/orders` — Danh sách đơn hàng
- POST `/orders/delete/{order_id}` — Hủy đơn chờ xác nhận

Quản trị:
- GET `/admin` — Bảng điều khiển
- GET `/admin/accounts` — Quản lý tài khoản người dùng
  - POST `/admin/users/lock` — Khóa tài khoản (theo phút)
  - POST `/admin/users/unlock` — Mở khóa
  - POST `/admin/users/delete` — Xóa tài khoản (không cho phép xóa ADMIN)
- GET `/admin/orders` — Quản lý đơn hàng
  - POST `/admin/orders/delete` — Xóa đơn chờ xác nhận (và hoàn kho)
- GET `/admin/products` — Quản lý sản phẩm (phân trang)
  - POST `/admin/products/add` — Thêm
  - POST `/admin/products/update/{product_id}` — Cập nhật
- GET `/admin/revenue` — Thống kê doanh thu theo thương hiệu/danh mục

## Kiểm thử nhanh endpoints

File [`test_main.http`](./test_main.http) có thể dùng với các HTTP Client (ví dụ: plugin "HTTP Client" trong VS Code/IntelliJ).

Ví dụ:
```http
GET http://127.0.0.1:8000/
Accept: application/json
```

## Lưu ý bảo mật và giới hạn

- Mật khẩu người dùng đang lưu plaintext; không có hashing/salting
- Chưa có xác thực/bảo vệ phiên nâng cao, chưa có CSRF protection
- Chưa dùng ORM/migrations; thao tác SQL thuần
- Thông số kết nối DB hard-code trong mã (chỉ nên dùng cho học tập/demo)

Nếu triển khai thực tế, bạn nên:
- Dùng biến môi trường hoặc file `.env` để quản lý thông số DB
- Hash mật khẩu (ví dụ: `passlib[bcrypt]`)
- Thêm xác thực/ủy quyền bài bản (session/JWT), CSRF, HTTPS
- Dùng ORM (SQLAlchemy) và migration (Alembic)

## Sự cố thường gặp

- “Database connection failed”:
  - Kiểm tra MySQL đang chạy và đúng thông số trong `DB_CONFIG`
  - Đảm bảo DB `clothing_shop` đã được tạo và import dữ liệu
  - Cấu hình user/password MySQL đúng, cấp quyền truy cập
- Lỗi font/Unicode:
  - Đảm bảo database và kết nối dùng `utf8mb4`

## Phụ thuộc

Xem [requirements.txt](./requirements.txt):
- fastapi==0.104.1
- uvicorn==0.24.0
- mysql-connector-python==8.2.0
- jinja2==3.1.2
- python-multipart==0.0.6

## Giấy phép

Chưa chỉ định giấy phép. Nếu bạn dùng lại mã nguồn, vui lòng ghi nhận nguồn và tuân thủ điều khoản của dự án gốc (nếu có).

---
Chúc bạn học tốt và triển khai thành công!