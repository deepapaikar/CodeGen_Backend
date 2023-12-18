import textract
from collections import Counter
import re

# Read the uploaded file
file_path = "path/to/uploaded/file"
try:
    text = textract.process(file_path).decode("utf-8")
except Exception as e:
    print("Error reading the file:", str(e))
    exit()

# Clean the text
cleaned_text = re.sub(r"[^\w\s]", "", text)

# Tokenize the text
tokens = cleaned_text.split()

# Count the words
word_counts = Counter(tokens)

# Generate a summary
summary = " ".join(word for word, count in word_counts.most_common(10))

# Return the summary
summary