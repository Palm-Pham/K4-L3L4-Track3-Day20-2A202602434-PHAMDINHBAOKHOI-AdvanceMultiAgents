"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import re
from pathlib import Path

from .tasks import eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    import json
    from lab.tasks import ROOT
    from lab.model import make_model

    if out_dir is None:
        out_dir = ROOT / "skills" / "auto"
    else:
        out_dir = Path(out_dir)

    runs = []
    source_dir = Path(results_dir) / source_condition
    if source_dir.exists():
        for task_dir in source_dir.iterdir():
            if not task_dir.is_dir():
                continue
            run_json_path = task_dir / "run.json"
            if not run_json_path.exists():
                continue

            try:
                with open(run_json_path, "r", encoding="utf-8") as f:
                    r = json.load(f)
            except Exception:
                continue

            if r.get("role") != "learn":
                continue

            failed = [(c["name"], c.get("detail", "")) for c in r.get("checks", []) if not c.get("passed", False)]
            if not failed:
                continue

            trace_path = task_dir / "trace.md"
            trace_content = ""
            if trace_path.exists():
                trace_content = trace_path.read_text(encoding="utf-8")
                if len(trace_content) > 6000:
                    trace_content = "..." + trace_content[-6000:]

            runs.append({
                "task": r.get("task"),
                "failed": failed,
                "trace": trace_content
            })

    if not runs:
        print("Cảnh báo: không có check thất bại ở tác vụ học")
        return []

    prompt_runs = ""
    for run in runs:
        prompt_runs += f"\n--- Task: {run['task']} ---\n"
        prompt_runs += "Failed checks:\n"
        for name, detail in run['failed']:
            prompt_runs += f"- {name}: {detail}\n"
        prompt_runs += f"Trace:\n{run['trace']}\n"

    prompt = f"""Bạn viết SKILL cho một tác tử lập trình và phân tích dữ liệu.
Dưới đây là các check thất bại (tên và nhận xét của bot đánh giá) và vết của các lần chạy.
Hãy tìm các lỗi QUY TRÌNH chung (không phải đáp án cụ thể) và viết tối đa {max_skills} skill ngắn
giúp tránh các lỗi đó trên tác vụ MỚI cùng loại.

Quy tắc:
- Skill phải tổng quát: không nêu id tác vụ, không nêu tên tệp riêng của một tác vụ, không nêu đáp án hay con số.
- Mỗi skill có frontmatter YAML gồm `name` (chữ thường, gạch ngang) và `description` (một câu: DÙNG KHI NÀO),
  sau đó tối đa 40 dòng chỉ dẫn mệnh lệnh (danh sách kiểm tra - checklist - hoạt động tốt).
- Định dạng đầu ra, đúng từng ký tự:
=== SKILL: <name> ===
---
name: <name>
description: <khi nào dùng>
---
<nội dung>
=== END ===

{prompt_runs}
"""

    if model is None:
        model = make_model()

    reply = model.invoke(prompt).content

    written = []
    for name, text in parse_skill_blocks(reply):
        if len(written) >= max_skills:
            break
        if validate_skill(text, expected_name=name):
            continue

        skill_dir = out_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(text, encoding="utf-8")
        written.append(skill_file)

    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
