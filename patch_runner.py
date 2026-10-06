with open("src/lab/runner.py", "r") as f:
    code = f.read()
code = code.replace(
    '"skills-auto": {"mode": "single", "skills_dir": "skills/auto"},',
    '"skills-auto": {"mode": "single", "skills_dir": "skills/auto"},\n    "subagents-skills": {"mode": "subagents-skills", "skills_dir": "skills/auto"},'
)
with open("src/lab/runner.py", "w") as f:
    f.write(code)
