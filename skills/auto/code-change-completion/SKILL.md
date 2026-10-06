---
name: code-change-completion
description: Dùng khi sửa lỗi hoặc mở rộng một gói mã nguồn cần kiểm thử, chú thích kiểu và ghi nhận thay đổi.
---
- Liệt kê mọi hàm công khai bị ảnh hưởng và bổ sung chú thích kiểu cho tham số lẫn giá trị trả về.
- Viết kiểm thử hồi quy riêng cho từng lỗi đã sửa; bảo đảm kiểm thử xác nhận hành vi, không chỉ chạy qua.
- Ghi từng sửa đổi vào mục thay đổi chưa phát hành theo quy ước của dự án.
- Chạy bộ kiểm thử liên quan và kiểm tra toàn bộ kết quả, kể cả kiểm thử mới.
- Xem lại diff để phát hiện thay đổi thiếu, tệp chưa được thêm hoặc yêu cầu nghiệm thu còn bỏ sót.