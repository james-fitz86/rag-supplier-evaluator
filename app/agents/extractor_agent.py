from app.schemas.extraction import ExtractedQuotation

SYSTEM_PROMPT = """You extract structured fields from supplier quotations.

Return ONLY valid JSON with EXACTLY these keys (no others):
supplier_name, item_description, unit_price, currency, min_quantity, delivery_days, payment_terms, internal_note, risk_assessment

Rules:
- Use null for unknown optional fields.
- currency must be a short code like EUR/USD/GBP (default to EUR if not stated).
- min_quantity must be an integer (default 1 if not stated).
- delivery_days must be an integer number of days (0 if not stated).
- unit_price must be a number (float).
No prose, no markdown, JSON only.
"""

def build_user_prompt(text: str) -> str:
    return f"""Extract the quotation fields from this text:

--- QUOTATION TEXT ---
{text}
--- END ---
"""

def extract_quotation(llm_client, text: str) -> ExtractedQuotation:
    result = llm_client.chat_json(
        system=SYSTEM_PROMPT,
        user=build_user_prompt(text),
    )

    # Normalize common alias keys -> schema keys
    if "supplier" in result and "supplier_name" not in result:
        result["supplier_name"] = result.pop("supplier")

    if "delivery_time" in result and "delivery_days" not in result:
        result["delivery_days"] = result.pop("delivery_time")

    if "delivery" in result and "delivery_days" not in result:
        result["delivery_days"] = result.pop("delivery")

    return ExtractedQuotation.model_validate(result)
