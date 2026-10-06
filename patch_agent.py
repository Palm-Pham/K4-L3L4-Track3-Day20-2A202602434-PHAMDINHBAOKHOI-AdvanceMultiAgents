with open("src/lab/agent.py", "r") as f:
    code = f.read()
code = code.replace(
    'if mode not in {"single", "subagents"}:',
    'if mode not in {"single", "subagents", "subagents-skills"}:'
)
code = code.replace(
    'if mode == "subagents":',
    'if mode in ("subagents", "subagents-skills"):'
)
code = code.replace(
    'for sub in get_subagents()',
    'for sub in get_subagents()\n        ]\n        if mode == "subagents-skills":\n            for sub in kwargs["subagents"]:\n                sub["skills"] = ["/skills/"]\n                sub["system_prompt"] += " " + SKILLS_NOTE\n        # dummy'
)
with open("src/lab/agent.py", "w") as f:
    f.write(code)
