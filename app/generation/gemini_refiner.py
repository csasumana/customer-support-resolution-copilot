from google import genai
from app.core.config import settings


class GeminiResponseRefiner:
    def __init__(self):
        self.enabled = bool(settings.GEMINI_API_KEY)

        if self.enabled:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            self.client = None

    def refine_response(
        self,
        customer_message: str,
        classification: str,
        resolution: str,
        base_response: str,
    ) -> tuple[str, str]:
        """
        Returns:
            refined_response, reason
        """

        if not self.enabled:
            return base_response, "Gemini disabled or API key missing; using deterministic response"

        prompt = f"""
You are a customer support communication assistant.

Rewrite the following customer support response to sound:
- empathetic
- professional
- concise
- operationally safe
- aligned with the given resolution

Do NOT change the resolution outcome.
Do NOT promise anything extra.
Do NOT invent compensation, timelines, or actions not already implied.
Do NOT add new refund timelines or policy claims.

Customer message:
{customer_message}

Classification:
{classification}

Resolution:
{resolution}

Base response:
{base_response}

Return only the final customer-facing response text.
""".strip()

        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
            )

            refined_text = (response.text or "").strip()

            if not refined_text:
                return base_response, "Gemini returned empty response; using deterministic response"

            return refined_text, "Gemini refined customer-facing response"

        except Exception as e:
            return base_response, f"Gemini refinement failed: {str(e)}"