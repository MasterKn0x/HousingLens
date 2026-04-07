import zipfile
import xml.etree.ElementTree as ET
import glob
import os

def extract(path):
    try:
        with zipfile.ZipFile(path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            return "".join([n.text for n in tree.findall('.//w:t', ns) if n.text])
    except Exception as e:
        return str(e)

docs = [f for f in os.listdir('..') if f.endswith('.docx')]
with open("proposal_docs.txt", "w", encoding="utf-8") as out:
    for doc in docs:
        path = os.path.join('..', doc)
        text = extract(path)
        out.write(f"=== {doc} ===\n")
        out.write(text + "\n")
        out.write("-" * 50 + "\n")
