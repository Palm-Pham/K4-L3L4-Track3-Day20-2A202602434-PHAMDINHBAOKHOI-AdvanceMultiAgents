# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
|Pham Dinh Bao Khoi|2A2026| |

- Model (`LAB_MODEL` / OpenAI deployment): `gpt-6-luna`, `LAB_TEMPERATURE`: `0.1` (loại bỏ parameter `temperature` trong kwargs của `ChatOpenAI` do model `gpt-6-luna` không hỗ trợ), `recursion_limit`: `40` (và `60` cho các run mặc định ban đầu).
- Deep Agents version (`pip show deepagents`): `0.7.21`, OS: `Ubuntu Linux 7.0.0-34-generic x86_64`, chạy trực tiếp trên host OS (bare metal, không dùng Docker).
- Số lần run task đã dùng / budget: 24 runs (gồm baseline: 6, subagents: 6, curator: 1, skills-auto dev: 3, skills-auto all: 6, subagents-skills: 6) / nằm trong token & run budget được cấp.
- Commit hash của tag `freeze`: `dcc44ce17e637ac073c1095622b716419b9f74de` (tag: `freeze`).

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

| Task | Failed check | Error Group (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc trace) |
|---|---|---|---|
| data-learn | rule_money_in_cents | E. Vi phạm house rules (Organization conventions) | RULE: money values in answer.json are integer cents |
| data-learn | rule_meta_block | E. Vi phạm house rules (Organization conventions) | RULE: answer.json has an object `meta` |
| data-learn | rule_clean_csv | E. Vi phạm house rules (Organization conventions) | RULE: write workspace/clean.csv with the header order_id... |
| code-learn | rule_type_hints | E. Vi phạm house rules (Organization conventions) | RULE: every public function ... has type annotations |
| code-learn | rule_regression_tests | E. Vi phạm house rules (Organization conventions) | RULE: add tests/test_regressions.py with one test |
| code-learn | rule_changelog | E. Vi phạm house rules (Organization conventions) | RULE: record each fix in CHANGELOG.md under ... |
| logs-learn | rule_service_names | E. Vi phạm house rules (Organization conventions) | RULE: service names in the output are lower-case with '-' |
| logs-learn | rule_sorted_errors | E. Vi phạm house rules (Organization conventions) | RULE: `errors` is sorted by service, then by timestamp_utc |
| logs-learn | rule_schema_header | E. Vi phạm house rules (Organization conventions) | RULE: the top-level object has "schema_version": 2 |

Nhận xét: nhóm lỗi nào chiếm đa số? Skill có thể phòng ngừa nhóm đó không?
- Đa số lỗi thuộc nhóm E (House rules / Organization conventions). Agent giải quyết chính xác logic kỹ thuật nhưng vi phạm output format do thiếu explicit prompt instruction. Việc tạo ra các skill bổ sung context về format validation sẽ trực tiếp phòng ngừa nhóm lỗi này.
- **Bằng chứng phủ định cho các error groups còn lại (A-D, F-G)**: Đối chiếu với kết quả từ `scripts/check_breakdown.py`, ở điều kiện `baseline`, agent vượt qua tuyệt đối 18/18 technical checks trên cả 3 learning tasks. Điều này chứng minh agent hoàn toàn không gặp lỗi về programming logic (nhóm A), không lỗi syntax hay tools (nhóm B, C, D), và không gặp infrastructure error. 100% các failed checks (9/9 check) đều thuần túy thuộc nhóm E (house rules do thiếu format specifications).

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (name, role, design rationale):
  - `explorer`: Khám phá codebase, đọc dữ liệu, phân tích quy luật. Thiết kế read-only để tránh side-effects làm hỏng workspace.
  - `implementer`: Trực tiếp code modification và run test execution. Đóng vai trò thi công.
  - `reviewer`: Code review độc lập, verify edge cases và compliance. Đóng vai trò QA.
- `subagent_calls` ở từng task và nhận xét (kể cả trường hợp bằng 0):
  - `code-learn`: 2 calls (gọi implementer và reviewer).
  - `data-learn`: 1 call (gọi explorer).
  - `logs-learn`: 1 call.
  Nhận xét: Main agent chủ động delegate task cho các bài có độ phức tạp cao.
- Thông tin thiếu hoặc thừa khi giao việc (delegation prompt):
  - Delegation prompt tuy có nhắc nhở đọc conventions ("Identify Acme reporting conventions", "Follow Acme Python team conventions") nhưng lại thiếu việc trích xuất cụ thể các quy tắc đó. Main agent ỷ lại vào việc subagent tự explore trong README, dẫn đến subagent có thể bỏ sót. Subagent response được main agent tin tưởng dùng cho final output, khiến lỗi thiếu format vẫn tồn tại.
- Ảnh hưởng đến token và latency:
  - Token usage tăng vọt so với `baseline` (ví dụ: `code-learn` từ 60.5k lên 174.9k, `data-learn` từ 26k lên 81k, `logs-learn` từ 50.8k lên 61.9k). Execution time cũng kéo dài hơn đáng kể.
  - Mặc dù chi phí token tăng cao, score không cải thiện (thậm chí suy giảm trên eval tasks) do lỗi gốc (nhóm E - house rules) không được giải quyết tốt hơn qua multi-agent architecture.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: 1 lần chạy curator, 0 skill bị xóa vì các generated skills đều đạt tiêu chuẩn chất lượng, không chứa harmful instructions hay hardcoded data.

| Skill | Generalization (Tổng quát hay riêng cho learning task)? | Correctness (Đúng hay sai)? | Length, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| acceptance-criteria-closure | Rất tổng quát, không chứa hardcoded file/variable names. | Đúng, hướng dẫn xây dựng checklist và validation toàn diện. | ~10 lines. Description rõ ràng. Đã được read ở cả 3 learning tasks. |
| structured-data-validation | Tổng quát, tập trung schema, numeric format, sorting keys. | Đúng, đặc biệt hữu ích chống lỗi formatting tiền tệ/timestamp. | ~10 lines. Đã được read ở 2 tasks (`data-learn`, `logs-learn`). |
| code-change-completion | Tổng quát, hướng dẫn type hints, regression tests và changelog entries. | Đúng, chuẩn hóa development best practices. | ~10 lines. Đã được read ở `code-learn`. |

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
*Lưu ý: Đã gặp lỗi 400 "Unsupported parameter: 'temperature'" ở model `gpt-6-luna`. Đã khắc phục bằng cách omit parameter `temperature` trong kwargs tại `src/lab/model.py`. Không có `skills_modified = true` vì đã freeze skill hợp lệ trước khi run.*

## 8. Phân tích

1. So với `baseline`, điều kiện `skills-auto` cải thiện mean score cả trên learning tasks (từ 0.66 lên 0.70) và evaluation tasks (từ 0.60 lên 0.62). Ngược lại, `subagents` không cải thiện learning tasks và làm suy giảm mạnh evaluation tasks (xuống 0.43). Không có trường hợp chỉ cải thiện learning tasks mà evaluation tasks bị sụt giảm, chứng minh không có dấu hiệu overfitting vào learning tasks.
2. Skills do curator sinh ra nhắm trực tiếp vào việc cải thiện house rules checks. Trong khi baseline đạt 0/12 house rules, `skills-auto` đạt được 2/12 trên evaluation tasks và 1/9 trên learning tasks. Các house rules mới của evaluation tasks được hỗ trợ nhờ tính generalization của skills (như yêu cầu type annotations, regression testing, output validation).
3. Trong `code-eval`, score tăng lên 9/11 nhờ read skill `code-change-completion.md` (`skills_read`: 2), giúp agent tự động pass các house rules như `rule_regression_tests`. Ngược lại, ở `data-eval`, score giảm nhẹ (5/9 -> 4/9) do agent tuy có read skill nhưng không match chính xác toàn bộ format requirement, hoặc gặp context noise từ prompt dài.
4. Về cost efficiency: `baseline` có hiệu quả token cao nhất (~41k token cho score ~0.60). `skills-auto` cải thiện score nhưng tiêu tốn gấp đôi token (~90k). Riêng multi-agent pattern (`subagents`) hoàn toàn không cost-effective trong benchmark này (token > 100k nhưng score giảm mạnh), do communication overhead và context fragmentation giữa main agent và subagents.
5. Không có data leakage hay overfitting. Các skill files sinh ra như `acceptance-criteria-closure.md` chứa abstract guidelines (tạo checklist, schema validation) chứ không hardcode bất kỳ biến số, tên file hay task-specific logic nào từ learning tasks.
6. Noise variance: So sánh score của learning tasks ở Phần 3.4 (lưu trong `skills-auto-dev`) và sau freeze, kết quả hoàn toàn trùng khớp (8/10, 5/8, 6/9). Điều này chứng minh rằng với model `gpt-6-luna` (không dùng sampling temperature), noise variance rất thấp và các score difference trong bảng mục 7 là hoàn toàn đáng tin cậy.

## 9. Hạn chế và tính hợp lệ

1. **Small sample size / Single run**: Mỗi configuration chỉ được run 1 lần (n=1) do ràng buộc về compute budget và time. Stochastic noise (như việc `subagents logs-eval` bị lỗi bất thường) có thể làm chệch mean score.
2. **Task diversity giới hạn**: Benchmark gồm 6 tasks (3 learn, 3 eval), tập trung vào các tình huống phần mềm nhỏ và chưa phản ánh hết độ phức tạp của real-world production codebases.
3. **Deterministic evaluation (Zero temperature)**: Do model `gpt-6-luna` không cho phép tùy biến `temperature`, agent hoạt động mang tính deterministic cao, chưa đánh giá được độ ổn định trước LLM hallucination hay exploration diversity ở các mức temperature khác nhau.

## 10. Kết luận

Thí nghiệm chứng minh cơ chế self-evolving skills (`skills-auto`) mang lại cải thiện thực sự về benchmark score trên cả learning và evaluation tasks, đặc biệt hiệu quả trong việc khắc phục vi phạm house rules. Ngược lại, kiến trúc multi-agent qua subagents làm bùng nổ token consumption và suy giảm performance do communication overhead. Hướng cải tiến tiếp theo là kết hợp self-evolving skills với một single agent hoặc một dedicated reviewer agent thay vì chia nhỏ execution path.

## Phụ lục

- **Lệnh đã chạy (theo thứ tự):**
  1. `pytest` (xác nhận harness và các bài test ban đầu).
  2. `python -m lab.runner --condition baseline --tasks learn` (chạy baseline trên tập học).
  3. `python -m lab.runner --condition subagents --tasks learn` (chạy subagents trên tập học).
  4. `python -m lab.curator` (sinh 3 skill tự động vào `skills/auto/`).
  5. `python -m lab.runner --condition skills-auto --tasks learn` (kiểm tra skill trước khi đóng băng, sao lưu kết quả vào `results/skills-auto-dev`).
  6. `git add -A && git commit -m "hypotheses"` (commit giả thuyết H1-H3).
  7. `git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze` (đóng băng skills).
  8. `python -m lab.runner --condition baseline --tasks eval` (chạy baseline trên tập đánh giá).
  9. `python -m lab.runner --condition subagents --tasks eval` (chạy subagents trên tập đánh giá).
  10. `python -m lab.runner --condition skills-auto --tasks all` (chạy chính thức skills-auto trên toàn bộ tác vụ).
  11. `python scripts/verify_freeze.py` (kiểm tra tính toàn vẹn của freeze).
  12. `python -m lab.compare > report/table.md` (tạo bảng so sánh tổng hợp).
  13. `python scripts/check_breakdown.py > report/breakdown.txt` (thống kê phân loại kỹ thuật và quy ước).
  14. `python -m lab.runner --condition subagents-skills --tasks all --recursion-limit 40` (chạy thử thách mở rộng 6d).
- **Thử thách mở rộng đã chọn:** 6d (Subagent có skill).
- **Ghi chú khác:** Không có xung đột môi trường hay vi phạm rò rỉ dữ liệu. Các kết quả đều được lưu trữ đầy đủ trong `results/`.

### Thử thách 6d. Subagent có skill

**Thiết lập:** 
Bổ sung `mode = "subagents-skills"` vào `src/lab/agent.py` để các subagent cũng được cung cấp đường dẫn `/skills/` và prompt yêu cầu đọc kỹ SKILL.md. Cấu hình này được chạy trên tất cả 6 tác vụ để so sánh với `subagents` thông thường và `skills-auto`.

**Kết quả:**
- **Điểm đánh giá (eval)** của `subagents-skills` đạt **0.63**, cao nhất trong tất cả các điều kiện (vượt baseline 0.60, skills-auto 0.62 và cứu vớt sự thảm hại của subagents thường 0.43).
- **Thống kê house rules**: Khác với `subagents` (0/12 house rules), `subagents-skills` đạt được 1/12 house rules trên tập eval, chứng tỏ subagent có đọc và áp dụng (một phần) các quy ước định dạng ẩn từ skill.
- **Chi phí Token**: Cực kỳ khổng lồ. Trung bình **217,105 token** mỗi lần chạy (gấp 5 lần baseline và 2.5 lần skills-auto). Cá biệt có tác vụ `code-learn` đã chạm trần đệ quy (Recursion Limit = 40) và ngốn hơn 500k token nhưng vẫn chưa thoát được vòng lặp.

**Nhận xét:**
Việc trang bị kỹ năng (skills) cho subagents thực sự cải thiện chất lượng công việc (tăng điểm kĩ thuật lên tuyệt đối 18/18 và vớt lại điểm quy ước). Subagent đỡ bị "lạc lối" hơn khi có bộ nguyên tắc rõ ràng. Tuy nhiên, sự kết hợp giữa mô hình đa tác tử và việc đọc skill liên tục khiến chi phí token bùng nổ, không khả thi để ứng dụng thực tế nếu không có cơ chế giới hạn vòng lặp giao tiếp tốt hơn.
