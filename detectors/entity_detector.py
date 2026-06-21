import re
from collections import Counter
from bs4 import BeautifulSoup
import google.generativeai as genai
from ai_scraper.utils.env_loader import get_env_var
from ai_scraper.logging_config import logger

logger.info(f'GEMINI_API_KEY: {get_env_var("GEMINI_API_KEY")}')

counter = Counter()
genai.configure(
    api_key=get_env_var("GEMINI_API_KEY")
)
model = genai.GenerativeModel("gemini-3.5-flash")
# model = genai.GenerativeModel("gemini-2.5-flash")

def call_gemini(chunks) -> int:

    html_chunks = "\n\n".join(
        f"Candidate {i+1}:\n {chunks[i]}" if chunks[i] is not None else ""
        for i in range(len(chunks))
    )
    prompt  = f"""
You are an entity detector.

Below are candidate HTML structures.

Your task:
- Choose exactly ONE candidate that most likely represents a SINGLE record/entity.
- Ignore candidates that contain multiple records/entities or wrap all chunks together.
- Return ONLY the candidate index number (e.g., "2") and nothing else.

Candidates:
{html_chunks}
"""

    try:
        response = model.generate_content(prompt)
        try:
            index_num = int(response.text.strip())-1
        except:
            index_num = int(re.findall(r'\{(\d+)\}', response.text.strip())[0])-1

        logger.debug(f'index_num: {index_num}')

        return index_num

    except Exception as e:
        logger.error(f"[extractor] error: {e}")
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
            # avg_children = (
            #         value["total_children"]
            #         / value["count"]
            # )
            #
            # avg_text_length = (
            #         value["total_text_length"]
            #         / value["count"]
            # )

            score = (
                    value["count"]
                    *value["total_children"]
                    *value["total_text_length"]
                    # * avg_children
                    # * avg_text_length
            )

            new_dict.append({'tag': key[0], 'class': key[1], 'score': score})

        new_dict.sort(key=lambda x: x['score'], reverse=True)
        chunks = [data.find(item['tag'], attrs={'class': item['class'][0] if len(item['class'])>0 else ''}) for item in new_dict][:10]
        if use_mock:
            num = 1
        else:
            num = call_gemini(chunks)
        new_data = data.find_all(new_dict[num]['tag'], attrs={'class': new_dict[num]['class'][0]})
        return new_data

    except Exception as e:
        logger.error(f"[detect_html] error: {e}")


### debugging
# with open('../output.html', 'r') as f:
#     print(f'html length: {len(f.read())}')
#     all_blocks = detect_html(f.read(), False)
#     from ai_scraper.extractors.data_extractor import extract_data
#     data = extract_data(all_blocks,  [
#     "date",
#     "text",
#     "ratings"
#   ])
#     print(data)