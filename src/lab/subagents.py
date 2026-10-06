"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Sử dụng khi bạn cần khám phá một codebase, đọc các tệp README, docstring, phân tích mẫu dữ liệu và cấu trúc dự án. Tác tử này sẽ báo cáo sự thật dựa trên mã nguồn nhưng không được thay đổi file. Khi giao việc, hãy cung cấp rõ bạn muốn khám phá thành phần nào.",
            "system_prompt": "Bạn là tác tử explorer. Nhiệm vụ của bạn là đọc mã nguồn, tài liệu, và dữ liệu đầu vào. Bạn phải trả về một báo cáo trung thực, chi tiết về tình trạng hiện tại và các lưu ý quan trọng. TUYỆT ĐỐI không thay đổi, ghi đè, tạo hoặc xóa bất kỳ file nào."
        },
        {
            "name": "implementer",
            "description": "Sử dụng khi bạn cần tạo mới, thay đổi nội dung file, hoặc chạy lệnh thực thi script/test. Giao việc bằng cách nêu chi tiết vấn đề cần giải quyết, định dạng đầu ra mong muốn và script kiểm tra nếu có.",
            "system_prompt": "Bạn là tác tử implementer. Bạn thực hiện thay đổi nội dung dự án dựa trên kế hoạch hoặc lỗi. Hãy tuân thủ nghiêm ngặt các quy định về đường dẫn, tránh xoá bớt code đang hoạt động trừ khi có chỉ định rõ ràng. Viết code an toàn, sau đó xác nhận lại."
        },
        {
            "name": "reviewer",
            "description": "Sử dụng khi bạn cần một kiểm tra độc lập trên code đã viết, đối chiếu với yêu cầu đề bài hoặc tìm kiếm các trường hợp biên. Cung cấp file cần duyệt và tóm tắt yêu cầu khi giao việc.",
            "system_prompt": "Bạn là tác tử reviewer. Hãy kiểm duyệt code một cách độc lập và gắt gao theo đề bài, tập trung vào edge cases (trường hợp biên), hiệu năng và độ ổn định. Đưa ra các thiếu sót hoặc lỗ hổng, nhưng không tự ý sửa đổi code."
        }
    ]
