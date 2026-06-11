import os
import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import google.generativeai as genai

# Configure Gemini
API_KEY = getattr(settings, "GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=API_KEY)

# Choose the exact model name for Gemini 2.5 Flash Lite
MODEL_NAME = "gemini-2.5-flash-lite"


def chat_page(request):
    """Render main chatbot page."""
    return render(request, "chatbot/index.html")


@csrf_exempt  # for simplicity; in production, use proper CSRF handling
def chat_api(request):
    """Handle AJAX POST requests from the frontend and return Gemini response."""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_message = data.get("message", "").strip()
    if not user_message:
        return JsonResponse({"error": "Message is required"}, status=400)

    if not API_KEY:
        return JsonResponse({"error": "Gemini API key not configured"}, status=500)

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        result = model.generate_content(user_message)
        bot_reply = result.text.strip() if result and getattr(result, "text", None) else "No response."
    except Exception as e:
        # Log e in real apps
        return JsonResponse({"error": f"Gemini error: {str(e)}"}, status=500)

    return JsonResponse({"reply": bot_reply})
