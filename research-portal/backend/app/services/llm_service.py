from openai import OpenAI
from backend.app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def normalize_line_items(raw_items: list):
    prompt = f"""
    Normalize these financial line items into standard names:

    {raw_items}

    Return JSON mapping.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content
