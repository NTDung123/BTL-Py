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
    'password': 'Sonbui@2005',
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
        search: Optional[str] = None
):
    current_user = get_current_user(request)
    products_list = []
    categories = []
    brands = []

    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)

            query = """
                    SELECT sp.*, dm.ten as ten_danhmuc, th.ten as ten_thuonghieu
                    FROM sanpham sp
                             LEFT JOIN danhmuc dm ON sp.maDM = dm.maDM
                             LEFT JOIN thuonghieu th ON sp.maTH = th.maTH
                    WHERE 1 = 1 \
                    """
            params = []

            if category:
                query += " AND dm.ten = %s"
                params.append(category)

            if brand:
                query += " AND th.ten = %s"
                params.append(brand)

            if search:
                query += " AND sp.ten LIKE %s"
                params.append(f"%{search}%")

            query += " ORDER BY sp.maSP DESC"

            cursor.execute(query, params)
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

    return templates.TemplateResponse("products.html", {
        "request": request,
        "current_user": current_user,
        "products": products_list,
        "categories": categories,
        "brands": brands,
        "selected_category": category,
        "selected_brand": brand,
        "search_query": search
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

        if user and user['matKhau'] == password:
            response = RedirectResponse(url="/", status_code=302)
            response.set_cookie(key="user_id", value=str(user['maND']))
            response.set_cookie(key="username", value=username)
            response.set_cookie(key="role", value=user['vaiTro'])
            return response
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Tên đăng nhập hoặc mật khẩu không đúng"
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

    return templates.TemplateResponse("order_success.html", {
        "request": request,
        "current_user": current_user,
        "order": order_info
    })

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