import google.generativeai as genai
from ai_scraper.logging_config import logger
from ai_scraper.utils.env_loader import get_env_var
import json
import re

print(f'GEMINI_API_KEY: {get_env_var("GEMINI_API_KEY")}')
genai.configure(
    api_key=get_env_var("GEMINI_API_KEY")
)
model = genai.GenerativeModel("gemini-3.5-flash")
# model = genai.GenerativeModel("gemini-2.5-flash")

def call_gemini(html, fields) -> list:
    fields_text = "\n".join(
        f"- {field}"
        for field in fields
    )
    html_chunks = ",\n".join(
        f"{block}"
        for block in html
    )
    prompt  = f"""You are a data extraction engine.

        Extract:
        
        {fields_text}
        
        Return ONLY a JSON array.
        
        HTML Blocks:
        
        {html_chunks}
        """
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r'```json\s*|```', '', raw).strip()

        if not raw or raw == "[]":
            return []

        parsed = json.loads(raw)
        return parsed

    except Exception as e:
        logger.error(f"[extractor] error: {e}")
        return []


def parse_fields(user_input):
    return [
        field.strip()
        for field in user_input.split(",")
        if field.strip()
    ]


def extract_data(all_blocks, fields):
    try:
        logger.info(f'fields: {fields}')
        logger.info(f'length of all_blocks: {len(all_blocks)}')
        final_data = call_gemini(all_blocks, fields)
        return final_data

    except Exception as e:
        logger.error(f'[extract_data] error: {e}')