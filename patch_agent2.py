with open("src/lab/agent.py", "r") as f:
    lines = f.readlines()
# fix the syntax error
new_lines = []
for line in lines:
    if line.strip() == "]":
        if new_lines[-1].strip() == "# dummy":
            new_lines.pop() # remove dummy
            continue # skip the extra ]
    new_lines.append(line)
with open("src/lab/agent.py", "w") as f:
    f.writelines(new_lines)
