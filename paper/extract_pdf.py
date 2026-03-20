from pypdf import PdfReader

reader = PdfReader("/Users/zac/Documents/Documents-it/GitHub/Cartography_v2/paper/human_ai_roles.pptx.pdf")
text = ""
for i, page in enumerate(reader.pages):
    text += f"--- Slide {i+1} ---\n"
    text += page.extract_text() + "\n"
print(text)
