import json
import textwrap

LINE_LEN_CHAR = 120
try:
    with open('story.txt', 'r') as file:
        RAW_TEXT = file.read()
    print("Content of RAW_TEXT:")
    print(RAW_TEXT)
    print(f"\nType of RAW_TEXT: {type(RAW_TEXT)}")

except FileNotFoundError:
    print("Error: 'story.txt' not found. Please make sure the file exists in the same directory as your script.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
lines = []
for raw_line in RAW_TEXT.splitlines():
    wrapped_lines = textwrap.wrap(raw_line, width=LINE_LEN_CHAR)
    if wrapped_lines:
        lines.extend([w for w in wrapped_lines])
    else:
        lines.append("")
lines = [{"line": i, "text": l} for i, l in enumerate(lines)]

FORMATTED_LINE = "\n".join([f"[Line {l['line']}] {l['text']}"for l in lines])
print(FORMATTED_LINE)


