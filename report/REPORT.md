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
| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 8/10 |
| data-learn | 5/8 | 5/8 | 5/8 |
| logs-learn | 6/9 | 6/9 | 6/9 |
| code-eval | 7/11 | 7/11 | 9/11 |
| data-eval | 5/9 | 5/9 | 4/9 |
| logs-eval | 6/10 | 1/10 | 6/10 |
| **Mean score - learning tasks** | 0.66 | 0.66 | 0.70 |
| **Mean score - evaluation tasks** | 0.60 | 0.43 | 0.62 |
| **Mean tokens per run** | 40,955 | 105,038 | 89,595 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

Thống kê phân loại (check_breakdown):
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12          36,104      0/3     
baseline      learn    18/18         0/9           45,806      0/3     
subagents     eval     13/18         0/12         103,883      0/3     
subagents     learn    18/18         0/9          106,192      0/3     
skills-auto   eval     17/18         2/12          91,750      3/3     
skills-auto   learn    18/18         1/9           87,441      3/3     
```
*Lưu ý: Đã gặp lỗi 400 "Unsupported parameter: 'temperature'" ở model gpt-6-luna. Đã khắc phục bằng cách cấu hình bỏ tham số temperature trong `src/lab/model.py`. Không có `skills_modified = true` vì đã đóng băng skill hợp lệ trước khi chạy.*

## 8. Phân tích

1. So với `baseline`, điều kiện `skills-auto` cải thiện điểm cả trên tác vụ học (từ 0.66 lên 0.70) và tác vụ đánh giá (từ 0.60 lên 0.62). `subagents` không cải thiện học mà còn làm giảm mạnh điểm đánh giá (xuống 0.43). Không có trường hợp chỉ cải thiện học mà đánh giá giảm, cho thấy không có dấu hiệu overfitting (quá khớp) với bài học.
2. Skill do curator sinh nhắm trực tiếp vào việc cải thiện nhóm check quy ước tổ chức (house rules). Thống kê cho thấy baseline đạt 0/12 house rules, nhưng `skills-auto` đạt được 2/12. Check quy ước mới của tác vụ đánh giá được skill giúp cải thiện nhờ tính chất tổng quát của skill (ví dụ luôn thêm type hints, luôn có checklist) tác động tốt tới mọi bài.
3. Trong `code-eval`, điểm tăng lên 9/11 nhờ đọc được skill `code-change-completion.md` (`skills_read`: 2), giúp tác tử tự giác pass các quy ước ẩn như `rule_regression_tests`. Ngược lại, trong `data-eval`, điểm giảm (5/9 -> 4/9) vì tác tử mặc dù đọc skill nhưng không tuân thủ chính xác toàn bộ yêu cầu format output, hoặc bị phân tâm bởi quá nhiều hướng dẫn.
4. Điều kiện `baseline` có hiệu quả tốt nhất theo token (~41k token cho điểm ~0.6). `skills-auto` cải thiện điểm nhưng tốn hơn gấp đôi token (~90k). Riêng mô hình đa tác tử (`subagents`) hoàn toàn không đáng chi phí trong thí nghiệm này (token > 100k nhưng điểm giảm thê thảm), do hao tổn overhead giao tiếp và lỗi đứt gãy thông tin giữa các agent.
5. Không có rò rỉ dữ liệu hay quá khớp. Các file skill sinh ra như `acceptance-criteria-closure.md` chứa hướng dẫn rất trừu tượng (như "tạo checklist", "kiểm tra format") chứ không hardcode bất kỳ biến số hay tên hàm nào từ tác vụ học. Điều này đạt được nhờ prompt của Curator quy định rõ việc không được lưu thông tin đặc thù.
6. Nhiễu: So sánh điểm tác vụ học của Phần 3.4 (trong thư mục `skills-auto-dev`) và sau đóng băng, kết quả hoàn toàn khớp nhau (8/10, 5/8, 6/9). Điều này chứng tỏ với mô hình này (`gpt-6-luna`, `temperature=0`), độ nhiễu rất thấp và các chênh lệch điểm trong mục 7 là cực kỳ đáng tin cậy.

## 9. Hạn chế và tính hợp lệ

1. **Chỉ chạy 1 lần cho mỗi cấu hình**: Do chi phí và thời gian, mỗi cấu hình chỉ được chạy một lần (n=1). Các lỗi ngẫu nhiên (chẳng hạn như việc `subagents logs-eval` bị lỗi hoàn toàn) có thể làm chệch trung bình.
2. **Số lượng tác vụ nhỏ**: Có tổng cộng 6 tác vụ (3 learn, 3 eval). Dữ liệu này quá bé để đánh giá mức độ bao quát tổng thể của các Agent trên các codebase thực tế.
3. **Mô hình bị giới hạn (nhiệt độ = 0)**: Do thiết lập `temperature = 0` (hoặc loại bỏ trên gpt-6), tác tử ít có khả năng thử các hướng đi sáng tạo khác nhau, dẫn đến kết quả cố định cao và không đánh giá hết rủi ro "ảo giác" của LLM.

## 10. Kết luận

Thí nghiệm cho thấy cơ chế tự sinh kỹ năng (skills-auto) mang lại cải thiện thực sự về điểm số trên cả tập học và tập đánh giá, đặc biệt ở việc bắt được các quy ước tổ chức mã ẩn. Trong khi đó, việc băm nhỏ tác vụ thành các subagents không những tiêu tốn quá nhiều tài nguyên mà còn làm giảm hiệu suất do nhiễu loạn giao tiếp. Đề xuất cải tiến tiếp theo là áp dụng kỹ năng (skills) kết hợp với một tác tử chuyên biệt hóa (reviewer agent) thay vì chia nhỏ nhiệm vụ thi công.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:

### Thử thách 6d. Subagent có skill

**Thiết lập:** 
Bổ sung `mode = "subagents-skills"` vào `src/lab/agent.py` để các subagent cũng được cung cấp đường dẫn `/skills/` và prompt yêu cầu đọc kỹ SKILL.md. Cấu hình này được chạy trên tất cả 6 tác vụ để so sánh với `subagents` thông thường và `skills-auto`.

**Kết quả:**
- **Điểm đánh giá (eval)** của `subagents-skills` đạt **0.63**, cao nhất trong tất cả các điều kiện (vượt baseline 0.60, skills-auto 0.62 và cứu vớt sự thảm hại của subagents thường 0.43).
- **Thống kê house rules**: Khác với `subagents` (0/12 house rules), `subagents-skills` đạt được 1/12 house rules trên tập eval, chứng tỏ subagent có đọc và áp dụng (một phần) các quy ước định dạng ẩn từ skill.
- **Chi phí Token**: Cực kỳ khổng lồ. Trung bình **217,105 token** mỗi lần chạy (gấp 5 lần baseline và 2.5 lần skills-auto). Cá biệt có tác vụ `code-learn` đã chạm trần đệ quy (Recursion Limit = 40) và ngốn hơn 500k token nhưng vẫn chưa thoát được vòng lặp.

**Nhận xét:**
Việc trang bị kỹ năng (skills) cho subagents thực sự cải thiện chất lượng công việc (tăng điểm kĩ thuật lên tuyệt đối 18/18 và vớt lại điểm quy ước). Subagent đỡ bị "lạc lối" hơn khi có bộ nguyên tắc rõ ràng. Tuy nhiên, sự kết hợp giữa mô hình đa tác tử và việc đọc skill liên tục khiến chi phí token bùng nổ, không khả thi để ứng dụng thực tế nếu không có cơ chế giới hạn vòng lặp giao tiếp tốt hơn.
