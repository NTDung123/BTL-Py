CREATE DATABASE clothing_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE clothing_shop;

-- Bảng người dùng
CREATE TABLE NguoiDung (
    maND BIGINT AUTO_INCREMENT PRIMARY KEY,
    tenDangNhap VARCHAR(50) UNIQUE NOT NULL,
    matKhau VARCHAR(255) NOT NULL,
    ten VARCHAR(100),
    ngaySinh DATE,
    gioiTinh VARCHAR(10),
    diaChi VARCHAR(255),
    soDienThoai VARCHAR(20),
    ngayTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vaiTro VARCHAR(20) DEFAULT 'USER'
);

-- Bảng danh mục
CREATE TABLE DanhMuc (
    maDM BIGINT AUTO_INCREMENT PRIMARY KEY,
    ten VARCHAR(100),
    hinhAnh VARCHAR(255)
);

-- Bảng thương hiệu
CREATE TABLE ThuongHieu (
    maTH BIGINT AUTO_INCREMENT PRIMARY KEY,
    ten VARCHAR(100),
    logo VARCHAR(255)
);

-- Bảng quản trị viên
CREATE TABLE QuanTriVien (
    maQTV BIGINT AUTO_INCREMENT PRIMARY KEY,
    maND BIGINT,
    email VARCHAR(100),
    FOREIGN KEY (maND) REFERENCES NguoiDung(maND) ON DELETE CASCADE
);

-- Bảng nhân viên
CREATE TABLE NhanVien (
    maNV BIGINT AUTO_INCREMENT PRIMARY KEY,
    maND BIGINT,
    email VARCHAR(100),
    luong DECIMAL(15,2),
    FOREIGN KEY (maND) REFERENCES NguoiDung(maND) ON DELETE CASCADE
);

-- Bảng khách hàng
CREATE TABLE KhachHang (
    maKH BIGINT AUTO_INCREMENT PRIMARY KEY,
    maND BIGINT,
    diemTichLuy INT DEFAULT 0,
    FOREIGN KEY (maND) REFERENCES NguoiDung(maND) ON DELETE CASCADE
);

-- Bảng sản phẩm
CREATE TABLE SanPham (
    maSP BIGINT AUTO_INCREMENT PRIMARY KEY,
    maDM BIGINT,
    maTH BIGINT,
    ten VARCHAR(100),
    moTa TEXT,
    gia DECIMAL(15,2),
    soLuong INT,
    kichCo VARCHAR(50),
    mauSac VARCHAR(50),
    chatLieu VARCHAR(100),
    hinhAnh VARCHAR(255),
    daBan INT DEFAULT 0,
    FOREIGN KEY (maDM) REFERENCES DanhMuc(maDM) ON DELETE SET NULL,
    FOREIGN KEY (maTH) REFERENCES ThuongHieu(maTH) ON DELETE SET NULL
);

-- Bảng giỏ hàng
CREATE TABLE GioHang (
    maGH BIGINT AUTO_INCREMENT PRIMARY KEY,
    maKH BIGINT,
    trangThai VARCHAR(50) DEFAULT 'Đang mua',
    FOREIGN KEY (maKH) REFERENCES KhachHang(maKH) ON DELETE CASCADE
);

-- Bảng đơn hàng
CREATE TABLE DonHang (
    maDH BIGINT AUTO_INCREMENT PRIMARY KEY,
    maKH BIGINT,
    maNV BIGINT,
    hoTen VARCHAR(100),
    email VARCHAR(100),
    soDienThoai VARCHAR(20),
    diaChi VARCHAR(255),
    tongTien DECIMAL(15,2),
    phuongThucThanhToan VARCHAR(50),
    trangThai VARCHAR(50) DEFAULT 'CHO_XAC_NHAN',
    ngayTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (maKH) REFERENCES KhachHang(maKH) ON DELETE CASCADE,
    FOREIGN KEY (maNV) REFERENCES NhanVien(maNV) ON DELETE SET NULL
);

-- Bảng chi tiết đơn hàng
CREATE TABLE ChiTietDonHang (
    maCTDH BIGINT AUTO_INCREMENT PRIMARY KEY,
    maDH BIGINT,
    maSP BIGINT,
    soLuong INT,
    donGia DECIMAL(15,2),
    thanhTien DECIMAL(15,2),
    kichCo VARCHAR(50),
    mauSac VARCHAR(50),
    FOREIGN KEY (maDH) REFERENCES DonHang(maDH) ON DELETE CASCADE,
    FOREIGN KEY (maSP) REFERENCES SanPham(maSP) ON DELETE CASCADE
);

-- Bảng chi tiết giỏ hàng
CREATE TABLE ChiTietGioHang (
    maCTGH BIGINT AUTO_INCREMENT PRIMARY KEY,
    maGH BIGINT,
    maSP BIGINT,
    soLuong INT,
    kichCo VARCHAR(50),
    mauSac VARCHAR(50),
    FOREIGN KEY (maGH) REFERENCES GioHang(maGH) ON DELETE CASCADE,
    FOREIGN KEY (maSP) REFERENCES SanPham(maSP) ON DELETE CASCADE
);

-- =========================
-- DỮ LIỆU MẪU
-- =========================

INSERT INTO NguoiDung VALUES
(1,'admin','$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTV5UiC','Quản Trị Viên',NULL,NULL,NULL,NULL,'2025-10-14 00:14:54','ADMIN'),
(2,'user','$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTV5UiC','Người Dùng',NULL,NULL,NULL,NULL,'2025-10-14 00:14:54','USER');

INSERT INTO DanhMuc VALUES
(1,'Áo Thun','https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500'),
(2,'Quần Jeans','https://images.unsplash.com/photo-1542272604-787c3835535d?w=500'),
(3,'Áo Khoác','https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500'),
(4,'Đầm/Váy','https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500'),
(5,'Áo Sơ Mi','https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500'),
(6,'Quần Short','https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=500'),
(7,'Áo Len','https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=500');

INSERT INTO ThuongHieu VALUES
(1,'Nike','https://logos-world.net/wp-content/uploads/2020/04/Nike-Logo.png'),
(2,'Adidas','https://logos-world.net/wp-content/uploads/2020/04/Adidas-Logo.png'),
(3,'Zara','https://logos-world.net/wp-content/uploads/2020/04/Zara-Logo.png'),
(4,'Uniqlo','https://logos-world.net/wp-content/uploads/2020/12/Uniqlo-Logo.png'),
(5,'H&M','https://logos-world.net/wp-content/uploads/2020/04/HM-Logo.png'),
(6,'Gucci','https://logos-world.net/wp-content/uploads/2020/04/Gucci-Logo.png'),
(7,'Puma','https://logos-world.net/wp-content/uploads/2020/04/Puma-Logo.png');

INSERT INTO SanPham (maDM, maTH, ten, moTa, gia, soLuong, kichCo, mauSac, chatLieu, hinhAnh, daBan) VALUES
-- Áo Thun (6 sản phẩm)
(1,1,'Áo thun Nike Sportswear','Áo thun thể thao cotton thoáng mát',350000.00,50,'S,M,L,XL','Đen','Cotton 100%','https://static.nike.com/a/images/t_web_pdp_535_v2/f_auto/025fcce7-dec4-455d-b089-4a45c4aed01d/AS+M+NK+DF+TEE+RUN+ENERGY+SP25.png',120),
(1,2,'Áo thun Adidas Originals','Áo thun cổ tròn in logo Adidas',320000.00,40,'M,L,XL','Trắng','Cotton','https://assets.adidas.com/images/h_840,f_auto,q_auto,fl_lossy,c_fill,g_auto/4eb95e8f57de44f099accc38e8fa0e75_9366/Ao_DJau_Jacquard_adidas_Adicolor_Mau_xanh_da_troi_JW5879_21_model.jpg',95),
(1,7,'Áo thun Puma Classic','Áo thun basic Puma, chất liệu mềm mại',280000.00,35,'S,M,L','Xám','Cotton pha Spandex','https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_2000,h_2000/global/629636/02/mod01/fnd/VNM/fmt/png/%C3%81o-thun-nam-GRAPHICS-PUMA-Hotel-Relaxed',75),
(1,4,'Áo thun Uniqlo Airism','Áo thun công nghệ Airism',250000.00,60,'S,M,L,XL,XXL','Xanh navy','Cotton Airism','https://image.uniqlo.com/UQ/ST3/vn/imagesgoods/465185/item/vngoods_19_465185_3x4.jpg?width=369',150),
(1,5,'Áo thun H&M Basic','Áo thun basic giá rẻ',250000.00,100,'S,M,L,XL','Trắng','Cotton','https://image.hm.com/assets/hm/99/be/99be7acc36e38e86c91bfe40d30fe53215cd9843.jpg?imwidth=1260',200),
(1,6,'Áo thun Gucci Logo','Áo thun cao cấp in logo Gucci',1300000.00,10,'M,L','Đen','Cotton cao cấp','https://media.gucci.com/style/DarkGray_Center_0_0_2400x2400/1758013221/796395_XJHC9_3254_003_100_0000_Light-Printed-cotton-jersey-T-shirt.jpg',25),

-- Quần Jeans (5 sản phẩm)
(2,2,'Quần jeans Adidas Slim Fit','Quần jeans form slim fit co giãn',650000.00,30,'28,29,30,31,32','Xanh đậm','Denim co giãn','https://assets.adidas.com/images/h_840,f_auto,q_auto,fl_lossy,c_fill,g_auto/448001745b654961b96fdf127a19d0e7_9366/Quan_Denim_Om_Dang_Adilenium_Season_4_Teamgeist_LR_Mau_xanh_da_troi_KE9801_21_model.jpg',85),
(2,1,'Quần jeans Nike Destroyed','Quần jeans destroyed streetwear',720000.00,15,'29,30,31,32','Xanh nhạt','Denim','https://static.nike.com/a/images/t_web_pdp_535_v2/f_auto,u_126ab356-44d8-4a06-89b4-fcdcc8df0245,c_scale,fl_relative,w_1.0,h_1.0,fl_layer_apply/7ffed27f-7cdd-42f5-aa53-976b7efe1491/M+J+FLT+UTILITY+PANT.png',35),
(2,3,'Quần jeans Zara Skinny','Quần jeans form skinny, ôm chân',550000.00,25,'26,27,28,29','Đen','Denim skinny','https://static.zara.net/assets/public/85de/afe9/392a4e4ab113/080e6d1cc93d/00103250400-p/00103250400-p.jpg?ts=1756308141969&w=1024',60),
(2,5,'Quần jeans H&M Regular','Quần jeans form regular, thoải mái',450000.00,40,'30,31,32,33,34','Xanh trung','Denim regular','https://image.hm.com/assets/hm/7d/a5/7da57056ae5d35fa3b8302407bb1e686ae0af8cf.jpg?imwidth=1260',90),
(2,4,'Quần jeans Uniqlo Selvedge','Quần jeans selvedge cao cấp',850000.00,20,'30,31,32','Xanh indigo','Denim selvedge','https://image.uniqlo.com/UQ/ST3/vn/imagesgoods/470542/item/vngoods_08_470542_3x4.jpg?width=423',40),

-- Áo Khoác (4 sản phẩm)
(3,3,'Áo khoác Zara Basic','Áo khoác basic phong cách Hàn Quốc',850000.00,20,'S,M,L','Be','Kaki','https://static.zara.net/assets/public/f852/9407/317e48ca980c/c14ce0f81999/06318406811-a1/06318406811-a1.jpg?ts=1758270016198&w=1125',45),
(3,1,'Áo khoác Nike Windrunner','Áo khoác gió Nike, nhẹ gọn',1200000.00,15,'M,L,XL','Đen','Polyester','https://static.nike.com/a/images/t_web_pdp_535_v2/f_auto/b9bf7777-8d74-4c4e-8b43-55e834ad9e6a/AS+W+NSW+NK+WR+WVN+UV+FZ+JKT.png',30),
(3,2,'Áo khoác Adidas Essentials','Áo khoác mùa đông Adidas',950000.00,18,'S,M,L,XL','Xám','Nỉ','https://assets.adidas.com/images/h_2000,f_auto,q_auto,fl_lossy,c_fill,g_auto/6392033da0da429aac12e1812d2372e8_9366/Ao_Gio_3_Soc_Essentials_Mau_vang_IM7847_25_model.jpg',55),
(3,4,'Áo khoác Uniqlo Ultra Light','Áo khoác siêu nhẹ, gấp gọn được',650000.00,30,'S,M,L','Xanh pastel','Ultra light down','https://image.uniqlo.com/UQ/ST3/vn/imagesgoods/478270/item/vngoods_77_478270_3x4.jpg?width=423',70),

-- Đầm/Váy (4 sản phẩm)
(4,4,'Đầm body Uniqlo','Đầm body dáng ôm, phù hợp đi làm',550000.00,25,'S,M,L','Đỏ','Vải tổng hợp','https://image.uniqlo.com/UQ/ST3/vn/imagesgoods/477316/item/vngoods_09_477316_3x4.jpg?width=423',60),
(4,3,'Váy liền Zara','Váy liền thân dáng suông, thoải mái',750000.00,20,'S,M','Hoa','Vải voan','https://static.zara.net/assets/public/de67/d3b5/94ce488aa6ef/1448119253d1/05919201800-p/05919201800-p.jpg?ts=1752661919205&w=1024',45),
(4,6,'Đầm dạ hội Gucci','Đầm dạ hội cao cấp, sang trọng',850000.00,5,'S,M','Đen','Lụa','https://media.gucci.com/style/DarkGray_Center_0_0_490x490/1758134773/837157_Z8B2Y_1000_003_100_0000_Light-satin-dress-with-double-g-belt.jpg',8),
(4,5,'Váy công sở H&M','Váy công sở lịch sự, form A-line',450000.00,35,'S,M,L','Xanh dương','Vải Kate','https://image.hm.com/assets/hm/08/fc/08fccb668e385a4700cc17d85945df15e301a93b.jpg?imwidth=2160',80),

-- Áo Sơ Mi (3 sản phẩm)
(5,3,'Áo sơ mi trắng Zara','Áo sơ mi trắng basic, form regular',550000.00,30,'S,M,L,XL','Trắng','Cotton','https://static.zara.net/assets/public/de99/42ba/89bf4c679bb9/f973cd227dbe/04043253250-a3/04043253250-a3.jpg?ts=1760026339972&w=1379',65),
(5,5,'Áo sơ mi kẻ sọc H&M','Áo sơ mi kẻ sọc thanh lịch',480000.00,25,'M,L,XL','Xanh trắng','Cotton','https://image.hm.com/assets/hm/b3/6a/b36aab21dfc6f406007e252e840259cbc3646d04.jpg?imwidth=1260',50),
(5,4,'Áo sơ mi Uniqlo Premium','Áo sơ mi cao cấp, không nhăn',650000.00,20,'S,M,L','Xanh pastel','Cotton premium','https://image.uniqlo.com/UQ/ST3/vn/imagesgoods/462369/item/vngoods_65_462369_3x4.jpg?width=369',40),

-- Quần Short (3 sản phẩm)
(6,1,'Quần short Nike Sport','Quần short thể thao Nike, thoáng mát',350000.00,40,'M,L,XL','Đen','Polyester','https://static.nike.com/a/images/t_web_pdp_535_v2/f_auto/e5f44e14-f6c6-4f49-997a-ab041b2a4be0/AS+M+NK+DF+FORM+7IN+UL+SHORT.png',85),
(6,2,'Quần short Adidas Originals','Quần short casual Adidas',320000.00,35,'S,M,L','Xám','Cotton','https://assets.adidas.com/images/h_2000,f_auto,q_auto,fl_lossy,c_fill,g_auto/6739ddc25daa4df3875e8497ca3f01bd_9366/Own_The_Run_Shorts_Blue_JX2247_21_model.jpg',70),
(6,7,'Quần short Puma Basic','Quần short basic Puma, nhiều màu',280000.00,45,'S,M,L,XL','Navy','Cotton','https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_2000,h_2000/global/682598/03/mod03/fnd/PNA/fmt/png/PUMA-Essentials-Men\'s-10%22-Shorts',95),

-- Áo Len (3 sản phẩm)
(7,6,'Áo len Gucci','Áo len vải thun cotton Gucci',1500000.00,40,'M,L,XL','Đen','Vải thun cotton','https://media.gucci.com/style/DarkGray_Center_0_0_2400x2400/1757932225/838450_XJHJO_1043_003_100_0000_Light-Brushed-cotton-jersey-sweatshirt.jpg',40),
(7,5,'Áo nỉ H&M','Áo nỉ dáng thụng H&M Basics',399000.00,45,'XS,S,M,L','Xanh Navy','Cotton, Polyester','https://image.hm.com/assets/hm/d2/29/d229e5925fab8f6b9db1cdf4f386a269616e632b.jpg?imwidth=2160',60),
(7,3,'Áo len Zara','Áo len Polo cổ tay Zara',1280000.00,30,'S,M,L,XL','Navy Blue','Cotton, Polyester','https://static.zara.net/assets/public/7f3d/981f/a95a48fda38b/12e72a1415da/00526310401-a1/00526310401-a1.jpg?ts=1754995160359&w=1125',65);

SELECT * FROM sanpham