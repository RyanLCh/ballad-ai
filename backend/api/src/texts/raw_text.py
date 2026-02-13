import string

LINE_LEN_CHAR = 120

try:
    with open('story.txt', 'r') as file:
        RAW_TEXT = file.read()
    print("Content of RAW_TEXT:")
    print(RAW_TEXT)
    print(f"\nType of RAW_TEXT: {type(RAW_TEXT)}")

except FileNotFoundError:
    print("Error: 'story.txt' not found. Please make sure the file exists in the same directory as your script.")
    RAW_TEXT = ""
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    RAW_TEXT = ""

# --- Word-based greedy line wrap ---
lines = []
current_line = ""
line_index = 0

for word in RAW_TEXT.split():
    # If adding this word would go over the limit, start new line
    if len(current_line) + len(word) + 1 > LINE_LEN_CHAR:
        lines.append({"line": line_index, "text": current_line.strip()})
        current_line = ""
        line_index += 1

    current_line += word + " "

# Add any final remaining line
if current_line.strip():
    lines.append({"line": line_index, "text": current_line.strip()})

# --- Format for display or saving ---
FORMATTED_LINE = "\n".join([f"[Line {l['line']}] {l['text']}" for l in lines])
print(FORMATTED_LINE)