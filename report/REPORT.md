# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
|Pham Dinh Bao Khoi|2A2026| |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`:
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker:
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): `subagents` dự đoán không mang lại cải thiện đột phá về điểm số so với baseline trên tác vụ đánh giá, thậm chí điểm có thể dao động nhẹ. Lý do: Ở phần 2.3, dù subagents tiêu tốn token gấp 2-3 lần, nó không giải quyết được các lỗi nhóm E (vi phạm quy ước định dạng) do thông tin quy ước không được truyền xuống rõ ràng trong prompt giao việc.
- H2 (skills-auto so với baseline): `skills-auto` dự đoán sẽ đạt điểm cao nhất. Lý do: Các skill sinh ra từ curator đóng vai trò như lời nhắc nhở checklist, đánh trúng các lỗi bỏ sót định dạng ở baseline (Ví dụ: ở Phần 3.4, `code-learn` đã tăng điểm từ 3/6 lên 8/10, `logs-learn` từ 2/5 lên 6/9). Các skill này khá tổng quát nên dự kiến tác dụng tốt ở tác vụ mới.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trên tác vụ đánh giá có thể sẽ thấp hơn tác vụ học ở điều kiện `skills-auto`. Lý do: Theo tài liệu nghiên cứu SkillEvolBench, skill tự sinh dễ bị quá khớp (overfit) vào lỗi của tập học, và khi gặp tác vụ đánh giá có cấu trúc mới, skill có thể chưa bao quát hết trường hợp.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Công cụ cho phép chạy lệnh là `execute`.
2. Mô tả của công cụ `task` nói subagent `general-purpose` dùng để nghiên cứu các câu hỏi phức tạp, tìm kiếm tệp và nội dung, và thực thi các tác vụ nhiều bước; nó có quyền truy cập vào tất cả các công cụ giống như tác tử chính. Subagent đó chỉ nhìn thấy ngữ cảnh duy nhất là prompt mà tác tử chính truyền vào cho nó (mỗi lần gọi là độc lập/stateless), không nhìn thấy toàn bộ lịch sử ngữ cảnh của tác tử chính.
3. - Trích từ mô tả `task`: "The agent's report is not shown to the user; relay a summary yourself."
- Trích từ mô tả `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| data-learn | rule_money_in_cents | E. Vi phạm quy ước tổ chức | RULE: money values in answer.json are integer cents |
| data-learn | rule_meta_block | E. Vi phạm quy ước tổ chức | RULE: answer.json has an object `meta` |
| data-learn | rule_clean_csv | E. Vi phạm quy ước tổ chức | RULE: write workspace/clean.csv with the header order_id... |
| code-learn | rule_type_hints | E. Vi phạm quy ước tổ chức | RULE: every public function ... has type annotations |
| code-learn | rule_regression_tests | E. Vi phạm quy ước tổ chức | RULE: add tests/test_regressions.py with one test |
| code-learn | rule_changelog | E. Vi phạm quy ước tổ chức | RULE: record each fix in CHANGELOG.md under ... |
| logs-learn | rule_service_names | E. Vi phạm quy ước tổ chức | RULE: service names in the output are lower-case with '-' |
| logs-learn | rule_sorted_errors | E. Vi phạm quy ước tổ chức | RULE: `errors` is sorted by service, then by timestamp_utc |
| logs-learn | rule_schema_header | E. Vi phạm quy ước tổ chức | RULE: the top-level object has "schema_version": 2 |

Nhận xét: nhóm lỗi nào chiếm đa số? Skill có thể phòng ngừa nhóm đó không?
Đa số lỗi thuộc nhóm E (Vi phạm quy ước tổ chức). Các tác tử giải quyết được logic nhưng không làm theo đúng định dạng đầu ra vì thiếu hướng dẫn đặc thù. Việc tạo ra các skill đọc quy ước định dạng sẽ phòng ngừa trực tiếp nhóm lỗi này.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  - `explorer`: Khám phá codebase, đọc dữ liệu, phân tích quy luật. Thiết kế để đọc mà không sửa, tránh hỏng dữ liệu.
  - `implementer`: Trực tiếp sửa code và chạy test. Thiết kế để làm người thợ thi công.
  - `reviewer`: Kiểm tra lại code độc lập, đánh giá edge cases. Thiết kế để đóng vai trò QA.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  - `code-learn`: 2 (gọi implementer và reviewer).
  - `data-learn`: 1 (gọi explorer).
  - `logs-learn`: 1.
  Nhận xét: Tác tử chính tích cực giao việc cho các bài phức tạp.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc):
  - Lời giao việc tuy có nhắc nhở đọc quy ước ("Identify Acme reporting conventions", "Follow Acme Python team conventions") nhưng lại thiếu truyền đạt chính xác quy ước đó là gì. Tác tử chính "lười" và ủy thác cho subagent tự đi tìm quy ước trong README, dẫn đến subagent có thể bỏ sót. Báo cáo của subagent được tác tử chính tin tưởng dùng để ra kết quả cuối, nhưng đôi khi vẫn bị thiếu format do subagent không nhắc lại quy ước.
- Ảnh hưởng đến token và thời gian:
  - Lượng token tăng vọt so với `baseline` (VD: `code-learn` từ 60.5k lên 174.9k, `data-learn` từ 26k lên 81k, `logs-learn` từ 50.8k lên 61.9k). Thời gian chạy cũng dài hơn rất nhiều.
  - Dù tốn nhiều chi phí token, điểm số không tăng lên đáng kể (hoặc thậm chí giảm) do lỗi gốc (nhóm E - vi phạm quy ước format ẩn) không được giải quyết tốt hơn thông qua cơ chế đa tác tử.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: 1 lần chạy, 0 skill bị xóa vì các skill sinh ra đều đạt chất lượng tốt, không chứa hướng dẫn gây hại hay hardcode.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| acceptance-criteria-closure | Rất tổng quát, không chứa tên file/biến. | Đúng, khuyên lập checklist và kiểm tra toàn diện. | ~10 dòng. Description rộng. Đã được đọc ở 3 tác vụ học. |
| structured-data-validation | Tổng quát, tập trung lược đồ, định dạng số, khóa sắp xếp. | Đúng, đặc biệt hữu ích chống lỗi định dạng tiền tệ/thời gian. | ~10 dòng. Đã được đọc ở 2 tác vụ (`data-learn`, `logs-learn`). |
| code-change-completion | Tổng quát, nhắc bổ sung type hints, test hồi quy và changelog không hardcode. | Đúng, phản ánh best practices lập trình. | ~10 dòng. Đã được đọc ở `code-learn`. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
