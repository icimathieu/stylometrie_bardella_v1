import json
import sys
from ebooklib import epub
from ebooklib import ITEM_DOCUMENT
from bs4 import BeautifulSoup


def epub_to_json(epub_path, output_path):
    book = epub.read_epub(epub_path)

    data = {
        "source": epub_path,
        "chapters": []
    }

    chapter_id = 0

    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "lxml")

            # Récupération du titre de chapitre si présent
            title_tag = soup.find(["h1", "h2", "h3"])
            title = title_tag.get_text(strip=True) if title_tag else f"chapter_{chapter_id}"

            paragraphs = []
            for p in soup.find_all("p"):
                text = p.get_text(" ", strip=True)
                if len(text.split()) >= 5:  # filtre très léger
                    paragraphs.append(text)

            if paragraphs:
                data["chapters"].append({
                    "id": chapter_id,
                    "title": title,
                    "paragraphs": paragraphs
                })
                chapter_id += 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python epub_to_json_stylometry.py livre.epub sortie.json")
        sys.exit(1)

    epub_to_json(sys.argv[1], sys.argv[2])