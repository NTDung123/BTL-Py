import json
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mysql.connector
from mysql.connector import Error
import os
import uvicorn
from typing import Optional
import socket
import urllib.parse
from datetime import datetime, timedelta

app = FastAPI(title="Clothing Shop", debug=True)

# Tạo thư mục
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("templates/admin", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Ntdung123!',
    'database': 'clothing_shop',
    'charset': 'utf8mb4'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None


def get_current_user(request: Request):
    user_id = request.cookies.get("user_id")
    username = request.cookies.get("username")
    role = request.cookies.get("role")

    if user_id and username and role:
        return {"user_id": user_id, "username": username, "role": role}
    return None


def is_admin(user: Optional[dict]) -> bool:
    return bool(user and str(user.get("role", "")).upper() == "ADMIN")


# ===== ROUTES =====

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    current_user = get_current_user(request)

    featured_products = []
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                           SELECT sp.*, dm.ten as ten_danhmuc, th.ten as ten_thuonghieu
                           FROM sanpham sp
                                    LEFT JOIN danhmuc dm ON sp.maDM = dm.maDM
                                    LEFT JOIN thuonghieu th ON sp.maTH = th.maTH
                           ORDER BY sp.maSP DESC LIMIT 8
                           """)
            featured_products = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error fetching products: {e}")
        finally:
            if db.is_connected():
                db.close()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
        "featured_products": featured_products
    })


@app.get("/products", response_class=HTMLResponse)
async def products(
    request: Request,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 12
):
    current_user = get_current_user(request)
    products_list = []
    categories = []
    brands = []

    # Sanitize pagination
    allowed_sizes = {12, 20, 28}
    if page_size not in allowed_sizes:
        page_size = 12
    if page < 1:
        page = 1
    offset = (page - 1) * page_size

    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)

            base_from = (
                " FROM sanpham sp "
                " LEFT JOIN danhmuc dm ON sp.maDM = dm.maDM "
                " LEFT JOIN thuonghieu th ON sp.maTH = th.maTH "
                " WHERE 1 = 1 "
            )
            where_clauses = ""
            params: list = []

            if category:
                where_clauses += " AND dm.ten = %s"
                params.append(category)

            if brand:
                where_clauses += " AND th.ten = %s"
                params.append(brand)

            if search:
                where_clauses += " AND sp.ten LIKE %s"
                params.append(f"%{search}%")

            # Count total
            count_sql = "SELECT COUNT(*) AS total " + base_from + where_clauses
            cursor.execute(count_sql, params)
            total_row = cursor.fetchone() or {"total": 0}
            total_count = int(total_row.get("total", 0))

            # Paged query
            query = (
                " SELECT sp.*, dm.ten as ten_danhmuc, th.ten as ten_thuonghieu "
                + base_from + where_clauses + " ORDER BY sp.maSP DESC LIMIT %s OFFSET %s"
            )
            cursor.execute(query, params + [page_size, offset])
            products_list = cursor.fetchall()

            cursor.execute("SELECT ten FROM danhmuc")
            categories = [row['ten'] for row in cursor.fetchall()]

            cursor.execute("SELECT ten FROM thuonghieu")
            brands = [row['ten'] for row in cursor.fetchall()]

            cursor.close()

        except Error as e:
            print(f"Error: {e}")
        finally:
            if db.is_connected():
                db.close()

    # Compute pagination meta
    total_pages = (total_count + page_size - 1) // page_size if db else 1

    return templates.TemplateResponse("products.html", {
        "request": request,
        "current_user": current_user,
        "products": products_list,
        "categories": categories,
        "brands": brands,
        "selected_category": category,
        "selected_brand": brand,
        "search_query": search,
        "page": page,
        "page_size": page_size,
        "total": total_count,
        "total_pages": total_pages
    })


@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int):
    current_user = get_current_user(request)
    product = None

    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                           SELECT sp.*, dm.ten as ten_danhmuc, th.ten as ten_thuonghieu
                           FROM sanpham sp
                                    LEFT JOIN danhmuc dm ON sp.maDM = dm.maDM
                                    LEFT JOIN thuonghieu th ON sp.maTH = th.maTH
                           WHERE sp.maSP = %s
                           """, (product_id,))
            product = cursor.fetchone()
            cursor.close()
        except Error as e:
            print(f"Error: {e}")
        finally:
            if db.is_connected():
                db.close()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "current_user": current_user,
        "product": product
    })


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
):

    # Hardcoded admin access
    if username == "admin" and password == "admin":
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="user_id", value="-1")
        response.set_cookie(key="username", value=username)
        response.set_cookie(key="role", value="ADMIN")
        return response

    db = get_db_connection()
    if not db:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Database connection failed"
        })

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM nguoidung WHERE tenDangNhap = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        # Check user lock status if table exists
        locked = False
        if user:
            try:
                cursor2 = db.cursor(dictionary=True)
                cursor2.execute(
                    "CREATE TABLE IF NOT EXISTS user_locks (maND INT PRIMARY KEY, locked_until DATETIME NULL)"
                )
                cursor2.execute("SELECT locked_until FROM user_locks WHERE maND = %s", (user['maND'],))
                lock_row = cursor2.fetchone()
                if lock_row and lock_row.get('locked_until'):
                    # MySQL returns datetime already
                    if lock_row['locked_until'] and datetime.now() < lock_row['locked_until']:
                        locked = True
                cursor2.close()
            except Exception:
                pass

        if user and user['matKhau'] == password and not locked:
            response = RedirectResponse(url="/", status_code=302)
            response.set_cookie(key="user_id", value=str(user['maND']))
            response.set_cookie(key="username", value=username)
            response.set_cookie(key="role", value=user['vaiTro'])
            return response
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Tên đăng nhập hoặc mật khẩu không đúng" if not locked else "Tài khoản đang bị khóa, vui lòng thử lại sau"
            })
    except Error as e:
        print(f"Error: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Đăng nhập thất bại"
        })
    finally:
        if db.is_connected():
            db.close()
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    current_user = get_current_user(request)
    # If already admin, go to dashboard
    if is_admin(current_user):
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse("admin/login.html", {"request": request})


@app.post("/admin/login")
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    # Hardcoded admin shortcut
    if username == "admin" and password == "admin":
        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie(key="user_id", value="-1")
        response.set_cookie(key="username", value=username)
        response.set_cookie(key="role", value="ADMIN")
        return response

    # Try DB admin
    db = get_db_connection()
    if not db:
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "error": "Database connection failed"
        })
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM nguoidung WHERE tenDangNhap = %s AND vaiTro = 'ADMIN'", (username,))
        user = cursor.fetchone()

        # Check lock table
        locked = False
        if user:
            try:
                cursor2 = db.cursor(dictionary=True)
                cursor2.execute(
                    "CREATE TABLE IF NOT EXISTS user_locks (maND INT PRIMARY KEY, locked_until DATETIME NULL)"
                )
                cursor2.execute("SELECT locked_until FROM user_locks WHERE maND = %s", (user['maND'],))
                lock_row = cursor2.fetchone()
                if lock_row and lock_row.get('locked_until') and datetime.now() < lock_row['locked_until']:
                    locked = True
                cursor2.close()
            except Exception:
                pass

        if user and user['matKhau'] == password and not locked:
            response = RedirectResponse(url="/admin", status_code=302)
            response.set_cookie(key="user_id", value=str(user['maND']))
            response.set_cookie(key="username", value=username)
            response.set_cookie(key="role", value="ADMIN")
            return response
        else:
            return templates.TemplateResponse("admin/login.html", {
                "request": request,
                "error": "Sai thông tin đăng nhập hoặc tài khoản đang bị khóa"
            })
    except Error as e:
        print(f"Error: {e}")
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "error": "Đăng nhập thất bại"
        })
    finally:
        if db.is_connected():
            db.close()


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        fullname: str = Form(...),
        phone: str = Form(...)
):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Mật khẩu xác nhận không khớp"
        })

    db = get_db_connection()
    if not db:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Database connection failed"
        })

    try:
        cursor = db.cursor()

        cursor.execute("SELECT maND FROM nguoidung WHERE tenDangNhap = %s", (username,))
        if cursor.fetchone():
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Tên đăng nhập đã tồn tại"
            })

        cursor.execute("""
                       INSERT INTO nguoidung (tenDangNhap, matKhau, ten, soDienThoai, vaiTro)
                       VALUES (%s, %s, %s, %s, 'USER')
                       """, (username, password, fullname, phone))

        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO khachhang (maND) VALUES (%s)", (user_id,))

        db.commit()

        response = RedirectResponse(url="/login", status_code=302)
        return response

    except Error as e:
        db.rollback()
        print(f"Error: {e}")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Đăng ký thất bại"
        })
    finally:
        if db.is_connected():
            db.close()


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user_id")
    response.delete_cookie("username")
    response.delete_cookie("role")
    return response

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    # 1. Kiểm tra xem người dùng đã đăng nhập chưa
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    user_details = None
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)

            # 2. Lấy thông tin chi tiết của người dùng từ database
            cursor.execute(
                "SELECT tenDangNhap, ten, soDienThoai, vaiTro FROM nguoidung WHERE maND = %s",
                (current_user['user_id'],)
            )
            user_details = cursor.fetchone()
            cursor.close()
        except Error as e:
            print(f"Error fetching user profile: {e}")
        finally:
            if db.is_connected():
                db.close()

    if not user_details:
        # Nếu không tìm thấy thông tin (dù đã đăng nhập) thì báo lỗi
        raise HTTPException(status_code=404, detail="User not found")

    # 3. Trả về file profile.html và gửi dữ liệu user_details qua
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "current_user": current_user,
        "user_details": user_details
    })

# Hiển thị trang/form để chỉnh sửa thông tin
@app.get("/edit_profile", response_class=HTMLResponse)
async def edit_profile_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    user_details = None
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            # Lấy thông tin hiện tại để điền vào form
            cursor.execute(
                "SELECT ten, soDienThoai FROM nguoidung WHERE maND = %s",
                (current_user['user_id'],)
            )
            user_details = cursor.fetchone()
            cursor.close()
        except Error as e:
            print(f"Lỗi khi lấy thông tin user để sửa: {e}")
        finally:
            if db.is_connected():
                db.close()

    if not user_details:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    return templates.TemplateResponse("edit_profile.html", {
        "request": request,
        "current_user": current_user,
        "user_details": user_details
    })


# Xử lý dữ liệu khi người dùng nhấn "Lưu thay đổi"
@app.post("/edit_profile")
async def handle_edit_profile(
    request: Request,
    fullname: str = Form(...), # Lấy "Họ và tên" từ form
    phone: str = Form(...)     # Lấy "Số điện thoại" từ form
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Lỗi kết nối database")

    try:
        cursor = db.cursor()
        # Câu lệnh UPDATE để cập nhật database
        cursor.execute(
            "UPDATE nguoidung SET ten = %s, soDienThoai = %s WHERE maND = %s",
            (fullname, phone, current_user['user_id'])
        )
        db.commit() # Lưu thay đổi
        cursor.close()
    except Error as e:
        print(f"Lỗi khi cập nhật profile: {e}")
        db.rollback() # Hoàn tác nếu có lỗi
    finally:
        if db.is_connected():
            db.close()

    # Sau khi cập nhật xong, chuyển hướng người dùng về trang profile
    return RedirectResponse(url="/profile", status_code=302)


@app.post("/account/delete")
async def delete_account(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Lỗi kết nối database")

    try:
        cursor = db.cursor(dictionary=True)

        user_id = int(current_user["user_id"]) if current_user.get("user_id") is not None else None

        # Tìm khách hàng theo user
        customer_id = None
        cursor.execute("SELECT maKH FROM khachhang WHERE maND = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            customer_id = row["maKH"]

        if customer_id is not None:
            # Xóa chi tiết giỏ hàng -> giỏ hàng
            cursor.execute("SELECT maGH FROM giohang WHERE maKH = %s", (customer_id,))
            carts = cursor.fetchall()
            for c in carts:
                cursor.execute("DELETE FROM chitietgiohang WHERE maGH = %s", (c["maGH"],))
            cursor.execute("DELETE FROM giohang WHERE maKH = %s", (customer_id,))

            # Xóa chi tiết đơn hàng -> đơn hàng
            cursor.execute("SELECT maDH FROM donhang WHERE maKH = %s", (customer_id,))
            orders = cursor.fetchall()
            for o in orders:
                cursor.execute("DELETE FROM chitietdonhang WHERE maDH = %s", (o["maDH"],))
            cursor.execute("DELETE FROM donhang WHERE maKH = %s", (customer_id,))

            # Xóa bản ghi khách hàng
            cursor.execute("DELETE FROM khachhang WHERE maKH = %s", (customer_id,))

        # Cuối cùng xóa người dùng
        cursor.execute("DELETE FROM nguoidung WHERE maND = %s", (user_id,))

        db.commit()
        cursor.close()

        # Xóa cookie và chuyển hướng về trang chủ
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie("user_id")
        response.delete_cookie("username")
        response.delete_cookie("role")
        return response

    except Error as e:
        print(f"Error deleting account: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Không thể xóa tài khoản, vui lòng thử lại sau")
    finally:
        if db.is_connected():
            db.close()

@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login")

    cart_items = []
    total = 0

    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)

            cursor.execute("""
                           SELECT gh.maGH
                           FROM giohang gh
                                    JOIN khachhang kh ON gh.maKH = kh.maKH
                                    JOIN nguoidung nd ON kh.maND = nd.maND
                           WHERE nd.maND = %s
                             AND gh.trangThai = 'Đang mua'
                           """, (current_user['user_id'],))
            cart = cursor.fetchone()

            if cart:
                cursor.execute("""
                               SELECT ctgh.*, sp.ten, sp.gia, sp.hinhAnh, sp.soLuong as stock
                               FROM chitietgiohang ctgh
                                        JOIN sanpham sp ON ctgh.maSP = sp.maSP
                               WHERE ctgh.maGH = %s
                               """, (cart['maGH'],))
                cart_items = cursor.fetchall()

                for item in cart_items:
                    item['subtotal'] = item['soLuong'] * item['gia']
                    total += item['subtotal']

            cursor.close()

        except Error as e:
            print(f"Error fetching cart: {e}")
        finally:
            if db.is_connected():
                db.close()

    return templates.TemplateResponse("cart.html", {
        "request": request,
        "current_user": current_user,
        "cart_items": cart_items,
        "total": total
    })


@app.post("/cart/add/{product_id}")
async def add_to_cart(
        request: Request,
        product_id: int,
        quantity: int = Form(1)
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login")

    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor()

            cursor.execute("SELECT maKH FROM khachhang WHERE maND = %s", (current_user['user_id'],))
            customer = cursor.fetchone()
            if not customer:
                cursor.close()
                raise HTTPException(status_code=404, detail="Customer not found")

            customer_id = customer[0]

            cursor.execute("SELECT maGH FROM giohang WHERE maKH = %s AND trangThai = 'Đang mua'", (customer_id,))
            cart = cursor.fetchone()

            if not cart:
                cursor.execute("INSERT INTO giohang (maKH) VALUES (%s)", (customer_id,))
                cart_id = cursor.lastrowid
            else:
                cart_id = cart[0]

            cursor.execute("SELECT maCTGH, soLuong FROM chitietgiohang WHERE maGH = %s AND maSP = %s",
                           (cart_id, product_id))
            existing_item = cursor.fetchone()

            if existing_item:
                new_quantity = existing_item[1] + quantity
                cursor.execute("UPDATE chitietgiohang SET soLuong = %s WHERE maCTGH = %s",
                               (new_quantity, existing_item[0]))
            else:
                cursor.execute("INSERT INTO chitietgiohang (maGH, maSP, soLuong) VALUES (%s, %s, %s)",
                               (cart_id, product_id, quantity))

            db.commit()
            cursor.close()

        except Error as e:
            print(f"Error adding to cart: {e}")
        finally:
            if db.is_connected():
                db.close()

    return RedirectResponse(url="/cart", status_code=302)


@app.post("/cart/update/{cart_item_id}")
async def update_cart_item(
    request: Request,
    cart_item_id: int,
    action: str = Form(...) # Sẽ nhận giá trị "increase" hoặc "decrease"
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = db.cursor(dictionary=True)

        # Lấy số lượng hiện tại của item và số lượng tồn kho (stock)
        cursor.execute("""
            SELECT ctgh.soLuong, sp.soLuong as stock
            FROM chitietgiohang ctgh
            JOIN sanpham sp ON ctgh.maSP = sp.maSP
            WHERE ctgh.maCTGH = %s
        """, (cart_item_id,))
        item = cursor.fetchone()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        new_quantity = item['soLuong']

        # Logic tăng/giảm
        if action == "increase" and item['soLuong'] < item['stock']:
            new_quantity += 1
        elif action == "decrease" and item['soLuong'] > 1:
            new_quantity -= 1

        # Cập nhật số lượng mới vào database
        cursor.execute(
            "UPDATE chitietgiohang SET soLuong = %s WHERE maCTGH = %s",
            (new_quantity, cart_item_id)
        )

        db.commit()
        cursor.close()

    except Error as e:
        print(f"Error updating cart: {e}")
        db.rollback()
    finally:
        if db.is_connected():
            db.close()

    # Tải lại trang giỏ hàng
    return RedirectResponse(url="/cart", status_code=302)


@app.post("/cart/remove/{cart_item_id}")
async def remove_from_cart(
    request: Request,
    cart_item_id: int
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = db.cursor()

        # Xóa thẳng item khỏi chi tiết giỏ hàng
        cursor.execute("DELETE FROM chitietgiohang WHERE maCTGH = %s", (cart_item_id,))

        db.commit()
        cursor.close()

    except Error as e:
        print(f"Error removing from cart: {e}")
        db.rollback()
    finally:
        if db.is_connected():
            db.close()

    # Tải lại trang giỏ hàng
    return RedirectResponse(url="/cart", status_code=302)


@app.get("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    cart_items = []
    total = 0

    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)

            # Lấy giỏ hàng hiện tại
            cursor.execute("""
                           SELECT gh.maGH
                           FROM giohang gh
                                    JOIN khachhang kh ON gh.maKH = kh.maKH
                                    JOIN nguoidung nd ON kh.maND = nd.maND
                           WHERE nd.maND = %s
                             AND gh.trangThai = 'Đang mua'
                           """, (current_user['user_id'],))
            cart = cursor.fetchone()

            if cart:
                cursor.execute("""
                               SELECT ctgh.*, sp.ten, sp.gia, sp.hinhAnh, sp.soLuong as stock
                               FROM chitietgiohang ctgh
                                        JOIN sanpham sp ON ctgh.maSP = sp.maSP
                               WHERE ctgh.maGH = %s
                               """, (cart['maGH'],))
                cart_items = cursor.fetchall()

                for item in cart_items:
                    item['subtotal'] = item['soLuong'] * item['gia']
                    total += item['subtotal']

            cursor.close()

        except Error as e:
            print(f"Error fetching cart for checkout: {e}")
        finally:
            if db.is_connected():
                db.close()

    if not cart_items:
        return RedirectResponse(url="/cart", status_code=302)

    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "current_user": current_user,
        "cart_items": cart_items,
        "total": total
    })


@app.post("/checkout")
async def process_checkout(
        request: Request,
        fullname: str = Form(...),
        phone: str = Form(...),
        address: str = Form(...),
        payment_method: str = Form(...)
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = db.cursor(dictionary=True)

        # Lấy thông tin khách hàng và giỏ hàng
        cursor.execute("""
                       SELECT kh.maKH, gh.maGH
                       FROM khachhang kh
                                JOIN giohang gh ON kh.maKH = gh.maKH
                       WHERE kh.maND = %s
                         AND gh.trangThai = 'Đang mua'
                       """, (current_user['user_id'],))
        customer_cart = cursor.fetchone()

        if not customer_cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        # Lấy các sản phẩm trong giỏ hàng
        cursor.execute("""
                       SELECT ctgh.maSP, ctgh.soLuong, sp.gia, sp.ten, sp.soLuong as stock
                       FROM chitietgiohang ctgh
                                JOIN sanpham sp ON ctgh.maSP = sp.maSP
                       WHERE ctgh.maGH = %s
                       """, (customer_cart['maGH'],))
        cart_items = cursor.fetchall()

        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # Tính tổng tiền
        total_amount = sum(item['soLuong'] * item['gia'] for item in cart_items)

        # Kiểm tra tồn kho
        for item in cart_items:
            if item['soLuong'] > item['stock']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sản phẩm {item['ten']} không đủ số lượng tồn kho"
                )

        # Tạo đơn hàng
        cursor.execute("""
                       INSERT INTO donhang (maKH, hoTen, soDienThoai, diaChi, tongTien, phuongThucThanhToan, trangThai)
                       VALUES (%s, %s, %s, %s, %s, %s, 'CHO_XAC_NHAN')
                       """, (customer_cart['maKH'], fullname, phone, address, total_amount, payment_method))

        order_id = cursor.lastrowid

        # Thêm chi tiết đơn hàng
        for item in cart_items:
            subtotal = item['soLuong'] * item['gia']
            cursor.execute("""
                           INSERT INTO chitietdonhang (maDH, maSP, soLuong, donGia, thanhTien)
                           VALUES (%s, %s, %s, %s, %s)
                           """, (order_id, item['maSP'], item['soLuong'], item['gia'], subtotal))

            # Cập nhật số lượng tồn kho
            cursor.execute("""
                           UPDATE sanpham
                           SET soLuong = soLuong - %s,
                               daBan   = daBan + %s
                           WHERE maSP = %s
                           """, (item['soLuong'], item['soLuong'], item['maSP']))

        # Xóa giỏ hàng (đánh dấu là đã hoàn thành)
        cursor.execute("UPDATE giohang SET trangThai = 'Đã hoàn thành' WHERE maGH = %s", (customer_cart['maGH'],))

        # Tạo giỏ hàng mới cho khách hàng
        cursor.execute("INSERT INTO giohang (maKH) VALUES (%s)", (customer_cart['maKH'],))

        db.commit()
        cursor.close()

        # Chuyển hướng đến trang cảm ơn
        return RedirectResponse(url=f"/order_success/{order_id}", status_code=302)

    except Error as e:
        db.rollback()
        print(f"Error during checkout: {e}")
        raise HTTPException(status_code=500, detail="Checkout failed")
    finally:
        if db.is_connected():
            db.close()


@app.get("/order_success/{order_id}", response_class=HTMLResponse)
async def order_success(request: Request, order_id: int):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    order_info = None
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                           SELECT dh.*, kh.maKH
                           FROM donhang dh
                                    JOIN khachhang kh ON dh.maKH = kh.maKH
                                    JOIN nguoidung nd ON kh.maND = nd.maND
                           WHERE dh.maDH = %s
                             AND nd.maND = %s
                           """, (order_id, current_user['user_id']))
            order_info = cursor.fetchone()
            cursor.close()
        except Error as e:
            print(f"Error fetching order: {e}")
        finally:
            if db.is_connected():
                db.close()

    if not order_info:
        raise HTTPException(status_code=404, detail="Order not found")

    # Build VietQR image URL with proper URL encoding (skip if COD)
    qr_url = None
    try:
        method = str(order_info.get("phuongThucThanhToan", "")).strip().upper()
        if method != "COD":
            base_url = "https://img.vietqr.io/image/techcombank-0828251105-compact2.jpg"
            params = {
                "amount": int(order_info["tongTien"]) if order_info.get("tongTien") is not None else 0,
                # Example: thanh_toan_don_hang_#123
                "addInfo": f"thanh_toan_don_hang_#{order_id}",
                "accountName": "Clothing Shop",
            }
            qr_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    except Exception:
        qr_url = None

    return templates.TemplateResponse("order_success.html", {
        "request": request,
        "current_user": current_user,
        "order": order_info,
        "qr_url": qr_url
    })


@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    orders = []
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT dh.maDH, dh.tongTien, dh.trangThai, dh.phuongThucThanhToan, dh.ngayTao
                FROM donhang dh
                JOIN khachhang kh ON dh.maKH = kh.maKH
                JOIN nguoidung nd ON kh.maND = nd.maND
                WHERE nd.maND = %s
                ORDER BY dh.maDH DESC
                """,
                (current_user["user_id"],)
            )
            orders = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error fetching orders: {e}")
        finally:
            if db.is_connected():
                db.close()

    return templates.TemplateResponse("orders.html", {
        "request": request,
        "current_user": current_user,
        "orders": orders
    })


@app.post("/orders/delete/{order_id}")
async def delete_order(request: Request, order_id: int):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cursor = db.cursor(dictionary=True)
        # Verify ownership and status
        cursor.execute(
            """
            SELECT dh.*
            FROM donhang dh
            JOIN khachhang kh ON dh.maKH = kh.maKH
            JOIN nguoidung nd ON kh.maND = nd.maND
            WHERE dh.maDH = %s AND nd.maND = %s
            """,
            (order_id, current_user["user_id"]) 
        )
        order = cursor.fetchone()
        if not order:
            cursor.close()
            return RedirectResponse(url="/orders", status_code=302)

        # Only allow delete if waiting for confirmation
        if str(order.get("trangThai", "")).upper() != "CHO_XAC_NHAN":
            cursor.close()
            return RedirectResponse(url="/orders", status_code=302)

        # Restore stock for each item
        cursor.execute("SELECT maSP, soLuong FROM chitietdonhang WHERE maDH = %s", (order_id,))
        items = cursor.fetchall()
        for it in items:
            cursor.execute(
                "UPDATE sanpham SET soLuong = soLuong + %s, daBan = GREATEST(daBan - %s, 0) WHERE maSP = %s",
                (it["soLuong"], it["soLuong"], it["maSP"]) 
            )

        # Delete order details then order
        cursor.execute("DELETE FROM chitietdonhang WHERE maDH = %s", (order_id,))
        cursor.execute("DELETE FROM donhang WHERE maDH = %s", (order_id,))

        db.commit()
        cursor.close()
    except Error as e:
        db.rollback()
        print(f"Error deleting order: {e}")
    finally:
        if db.is_connected():
            db.close()

    return RedirectResponse(url="/orders", status_code=302)

def find_available_port(start_port=8000, max_port=8010):
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return start_port

if __name__ == "__main__":
    port = find_available_port()
    print(f"   Starting Clothing Shop on http://localhost:{port}")
    print(f"   Available routes:")
    print(f"   http://localhost:{port} - Trang chủ")
    print(f"   http://localhost:{port}/products - Sản phẩm")
    print(f"   http://localhost:{port}/login - Đăng nhập")
    print(f"   http://localhost:{port}/register - Đăng ký")
    uvicorn.run(app, host="127.0.0.1", port=port, reload=True)


# =================== ADMIN ROUTES ===================

def ensure_user_locks_table():
    db = get_db_connection()
    if not db:
        return
    try:
        cursor = db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS user_locks (maND INT PRIMARY KEY, locked_until DATETIME NULL)"
        )
        db.commit()
        cursor.close()
    except Exception:
        pass
    finally:
        if db.is_connected():
            db.close()


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    current_user = get_current_user(request)
    if not is_admin(current_user):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "current_user": current_user,
    })


@app.get("/admin/accounts", response_class=HTMLResponse)
async def admin_accounts(request: Request):
    current_user = get_current_user(request)
    if not is_admin(current_user):
        return RedirectResponse(url="/login", status_code=302)

    ensure_user_locks_table()

    users = []
    locks = {}
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT maND, tenDangNhap, ten, soDienThoai, vaiTro FROM nguoidung ORDER BY maND DESC")
            users = cursor.fetchall()

            cursor.execute("SELECT maND, locked_until FROM user_locks")
            for row in cursor.fetchall():
                locks[row['maND']] = row['locked_until']

            cursor.close()
        except Error as e:
            print(f"Error fetching users: {e}")
        finally:
            if db.is_connected():
                db.close()

    return templates.TemplateResponse("admin/accounts.html", {
        "request": request,
        "current_user": current_user,
        "users": users,
        "locks": locks
    })


@app.post("/admin/users/lock")
async def admin_lock_user(request: Request, user_id: int = Form(...), duration_minutes: int = Form(60)):
    current_user = get_current_user(request)
    if not is_admin(current_user):
        return RedirectResponse(url="/login", status_code=302)

    ensure_user_locks_table()
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cursor = db.cursor()
        locked_until = datetime.now() + timedelta(minutes=duration_minutes)
        cursor.execute(
            "REPLACE INTO user_locks (maND, locked_until) VALUES (%s, %s)",
            (user_id, locked_until)
        )
        db.commit()
        cursor.close()
    finally:
        if db.is_connected():
            db.close()
    return RedirectResponse(url="/admin/accounts", status_code=302)


@app.post("/admin/users/unlock")
async def admin_unlock_user(request: Request, user_id: int = Form(...)):
    current_user = get_current_user(request)
    if not is_admin(current_user):
        return RedirectResponse(url="/login", status_code=302)

    ensure_user_locks_table()
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM user_locks WHERE maND = %s", (user_id,))
        db.commit()
        cursor.close()
    finally:
        if db.is_connected():
            db.close()
    return RedirectResponse(url="/admin/accounts", status_code=302)


@app.post("/admin/users/delete")
async def admin_delete_user(request: Request, user_id: int = Form(...)):
    current_user = get_current_user(request)
    if not is_admin(current_user):
        return RedirectResponse(url="/login", status_code=302)

    # Reuse deletion logic similar to /account/delete
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cursor = db.cursor(dictionary=True)

        # Prevent deleting admin accounts by mistake (by role)
        cursor.execute("SELECT vaiTro FROM nguoidung WHERE maND = %s", (user_id,))
        r = cursor.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail="User not found")
        if str(r.get('vaiTro', '')).upper() == 'ADMIN':
            raise HTTPException(status_code=400, detail="Không thể xóa tài khoản ADMIN")

        # Remove locks
        try:
            cursor2 = db.cursor()
            cursor2.execute("DELETE FROM user_locks WHERE maND = %s", (user_id,))
            cursor2.close()
        except Exception:
            pass

        # Cascade delete similar to user self-delete
        cursor.execute("SELECT maKH FROM khachhang WHERE maND = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            customer_id = row['maKH']
            cursor.execute("SELECT maGH FROM giohang WHERE maKH = %s", (customer_id,))
            carts = cursor.fetchall()
            for c in carts:
                cursor.execute("DELETE FROM chitietgiohang WHERE maGH = %s", (c['maGH'],))
            cursor.execute("DELETE FROM giohang WHERE maKH = %s", (customer_id,))

            cursor.execute("SELECT maDH FROM donhang WHERE maKH = %s", (customer_id,))
            orders = cursor.fetchall()
            for o in orders:
                cursor.execute("DELETE FROM chitietdonhang WHERE maDH = %s", (o['maDH'],))
            cursor.execute("DELETE FROM donhang WHERE maKH = %s", (customer_id,))

            cursor.execute("DELETE FROM khachhang WHERE maKH = %s", (customer_id,))

        cursor.execute("DELETE FROM nguoidung WHERE maND = %s", (user_id,))
        db.commit()
        cursor.close()
    except Error as e:
        db.rollback()
        print(f"Error admin deleting user: {e}")
        raise HTTPException(status_code=500, detail="Không thể xóa tài khoản")
    finally:
        if db.is_connected():
            db.close()
    return RedirectResponse(url="/admin/accounts", status_code=302)


@app.get("/admin/orders", response_class=HTMLResponse)
async def admin_orders(request: Request):
    current_user = get_current_user(request)
    if not is_admin(current_user):
        return RedirectResponse(url="/login", status_code=302)

    orders = []
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT dh.*, nd.tenDangNhap, nd.ten AS tenNguoiDung
                FROM donhang dh
                JOIN khachhang kh ON dh.maKH = kh.maKH
                JOIN nguoidung nd ON kh.maND = nd.maND
                ORDER BY dh.maDH DESC
                """
            )
            orders = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error fetching orders for admin: {e}")
        finally:
            if db.is_connected():
                db.close()

    return templates.TemplateResponse("admin/orders.html", {
        "request": request,
        "current_user": current_user,
        "orders": orders
    })


@app.post("/admin/orders/delete")
async def admin_delete_order(request: Request, order_id: int = Form(...)):
    current_user = get_current_user(request)
    if not is_admin(current_user):
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT trangThai FROM donhang WHERE maDH = %s", (order_id,))
        order = cursor.fetchone()
        if not order:
            cursor.close()
            return RedirectResponse(url="/admin/orders", status_code=302)

        # Only delete and restock if awaiting confirmation
        if str(order.get("trangThai", "")).upper() != "CHO_XAC_NHAN":
            cursor.close()
            return RedirectResponse(url="/admin/orders", status_code=302)

        cursor.execute("SELECT maSP, soLuong FROM chitietdonhang WHERE maDH = %s", (order_id,))
        items = cursor.fetchall()
        for it in items:
            cursor.execute(
                "UPDATE sanpham SET soLuong = soLuong + %s, daBan = GREATEST(daBan - %s, 0) WHERE maSP = %s",
                (it["soLuong"], it["soLuong"], it["maSP"]) 
            )

        cursor.execute("DELETE FROM chitietdonhang WHERE maDH = %s", (order_id,))
        cursor.execute("DELETE FROM donhang WHERE maDH = %s", (order_id,))
        db.commit()
        cursor.close()
    except Error as e:
        db.rollback()
        print(f"Error admin deleting order: {e}")
    finally:
        if db.is_connected():
            db.close()

    return RedirectResponse(url="/admin/orders", status_code=302)


@app.get("/admin/revenue", response_class=HTMLResponse)
async def admin_revenue(request: Request):
    current_user = get_current_user(request)
    if not is_admin(current_user):
        return RedirectResponse(url="/login", status_code=302)

    by_brand = []
    by_category = []
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            # Revenue by brand
            cursor.execute(
                """
                SELECT th.ten AS thuongHieu, SUM(ct.thanhTien) AS doanhThu
                FROM chitietdonhang ct
                JOIN sanpham sp ON ct.maSP = sp.maSP
                LEFT JOIN thuonghieu th ON sp.maTH = th.maTH
                GROUP BY th.ten
                ORDER BY doanhThu DESC
                """
            )
            by_brand = cursor.fetchall()

            # Revenue by category
            cursor.execute(
                """
                SELECT dm.ten AS danhMuc, SUM(ct.thanhTien) AS doanhThu
                FROM chitietdonhang ct
                JOIN sanpham sp ON ct.maSP = sp.maSP
                LEFT JOIN danhmuc dm ON sp.maDM = dm.maDM
                GROUP BY dm.ten
                ORDER BY doanhThu DESC
                """
            )
            by_category = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error computing revenue: {e}")
        finally:
            if db.is_connected():
                db.close()

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "current_user": current_user,
        "by_brand": by_brand,
        "by_category": by_category
    })


@app.get("/admin/products", response_class=HTMLResponse)
async def admin_products(request: Request, page: int = 1, page_size: int = 12):
    current_user = get_current_user(request)
    if not is_admin(current_user):
        return RedirectResponse(url="/login", status_code=302)

    products = []
    categories = []
    brands = []
    total_count = 0
    allowed_sizes = {12, 20, 28}
    if page_size not in allowed_sizes:
        page_size = 12
    if page < 1:
        page = 1
    offset = (page - 1) * page_size
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) AS total FROM sanpham")
            total_row = cursor.fetchone() or {"total": 0}
            total_count = int(total_row.get("total", 0))

            cursor.execute(
                "SELECT sp.*, dm.ten AS ten_danhmuc, th.ten AS ten_thuonghieu FROM sanpham sp "
                "LEFT JOIN danhmuc dm ON sp.maDM = dm.maDM "
                "LEFT JOIN thuonghieu th ON sp.maTH = th.maTH ORDER BY sp.maSP DESC LIMIT %s OFFSET %s",
                (page_size, offset)
            )
            products = cursor.fetchall()

            cursor.execute("SELECT maDM, ten FROM danhmuc ORDER BY ten")
            categories = cursor.fetchall()

            cursor.execute("SELECT maTH, ten FROM thuonghieu ORDER BY ten")
            brands = cursor.fetchall()

            cursor.close()
        except Error as e:
            print(f"Error fetching products for admin: {e}")
        finally:
            if db.is_connected():
                db.close()

    total_pages = (total_count + page_size - 1) // page_size if db else 1

    return templates.TemplateResponse("admin/products.html", {
        "request": request,
        "current_user": current_user,
        "products": products,
        "categories": categories,
        "brands": brands,
        "page": page,
        "page_size": page_size,
        "total": total_count,
        "total_pages": total_pages
    })


@app.post("/admin/products/add")
async def admin_add_product(
    request: Request,
    ten: str = Form(...),
    gia: int = Form(...),
    soLuong: int = Form(0),
    maDM: int = Form(...),
    maTH: int = Form(...),
    hinhAnh: str = Form("")
):
    current_user = get_current_user(request)
    if not is_admin(current_user):
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO sanpham (ten, gia, soLuong, maDM, maTH, hinhAnh) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (ten, gia, soLuong, maDM, maTH, hinhAnh)
        )
        db.commit()
        cursor.close()
    except Error as e:
        db.rollback()
        print(f"Error adding product: {e}")
    finally:
        if db.is_connected():
            db.close()
    return RedirectResponse(url="/admin/products", status_code=302)


@app.post("/admin/products/update/{product_id}")
async def admin_update_product(
    request: Request,
    product_id: int,
    ten: str = Form(...),
    gia: int = Form(...),
    soLuong: int = Form(...),
    maDM: int = Form(...),
    maTH: int = Form(...),
    hinhAnh: str = Form("")
):
    current_user = get_current_user(request)
    if not is_admin(current_user):
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE sanpham SET ten=%s, gia=%s, soLuong=%s, maDM=%s, maTH=%s, hinhAnh=%s WHERE maSP=%s
            """,
            (ten, gia, soLuong, maDM, maTH, hinhAnh, product_id)
        )
        db.commit()
        cursor.close()
    except Error as e:
        db.rollback()
        print(f"Error updating product: {e}")
    finally:
        if db.is_connected():
            db.close()
    return RedirectResponse(url="/admin/products", status_code=302)
