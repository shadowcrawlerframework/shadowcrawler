import os
import re

old = r"4\.1\.0"
new = "4.1.1"

pattern = re.compile(old)

for root, dirs, files in os.walk("."):
    for name in files:
        if name.endswith((".py", ".md")):
            path = os.path.join(root, name)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            new_content = pattern.sub(new, content)

            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print("✔ actualizado:", path)
