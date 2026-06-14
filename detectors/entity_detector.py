from collections import Counter
from bs4 import BeautifulSoup
import google.generativeai as genai
import os

counter = Counter()
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)
# model = genai.GenerativeModel("gemini-3.5-flash")
model = genai.GenerativeModel("gemini-2.5-flash")

def call_gemini(chunks) -> int:

    html_chunks = "\n\n".join(
        f"Candidate {i+1}:\n {chunks[i]}" if chunks[i] is not None else ""
        for i in range(len(chunks))
    )
    prompt  = f"""You are an entity detector.

Below are candidate HTML structures.


Choose the ONE candidate that most likely
represents a single record/entity.

Return ONLY index number.

Candidates:

{html_chunks}

"""
    try:
        response = model.generate_content(prompt)
        index_num = int(response.text.strip())-1

        return index_num

    except Exception as e:
        print(f"[extractor] error: {e}")
        return None


def detect_html(html, use_mock):
    try:
        data = BeautifulSoup(html, 'html.parser')
        stats = {}
        for tag in data.find_all():
            key = (
                tag.name,
                tuple(sorted(tag.get("class", [])))
            )

            if key not in stats:
                stats[key] = {
                    "count": 0,
                    "total_children": 0,
                    "total_text_length": 0
                }

            stats[key]["count"] += 1

            stats[key]["total_children"] += len(
                tag.find_all(recursive=False)
            )

            stats[key]["total_text_length"] += len(
                tag.get_text(strip=True)
            )

        new_dict = []
        for key, value in stats.items():
            avg_children = (
                    value["total_children"]
                    / value["count"]
            )

            avg_text_length = (
                    value["total_text_length"]
                    / value["count"]
            )

            score = (
                    value["count"]
                    * avg_children
                    * avg_text_length
            )

            new_dict.append({'tag': key[0], 'class': key[1], 'score': score})
        print('******************\n')
        new_dict.sort(key=lambda x: x['score'], reverse=True)
        print(new_dict)
        chunks = [data.find(item['tag'], attrs={'class': item['class'][0] if len(item['class'])>0 else ''}) for item in new_dict[:5]]
        if use_mock:
            num = 1
        else:
            num = call_gemini(chunks)
        new_data = data.find_all(new_dict[num]['tag'], attrs={'class': new_dict[num]['class'][0]})
        return new_data

    except Exception as e:
        print(f"[detect_html] error: {e}")