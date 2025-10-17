from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Simple rule-based mapping for demo
SYMPTOM_MAP = {
    "fever": ["Flu", "COVID-19", "Common Cold"],
    "cough": ["Bronchitis", "Allergy", "COVID-19"],
    "headache": ["Migraine", "Stress", "Dehydration"],
    "stomach pain": ["Gastritis", "Food poisoning", "Indigestion"],
    "sore throat": ["Tonsillitis", "Viral Infection", "Allergy"]
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/check", response_class=HTMLResponse)
async def check_symptom(request: Request, symptom: str = Form(...)):
    symptom_lower = symptom.lower()
    possible_conditions = []

    for key, value in SYMPTOM_MAP.items():
        if key in symptom_lower:
            possible_conditions.extend(value)

    if not possible_conditions:
        possible_conditions = ["Unable to determine. Please consult a doctor."]

    next_steps = [
        "Stay hydrated and rest well.",
        "Monitor your temperature.",
        "Consult a healthcare provider if symptoms persist.",
        "Avoid self-medication."
    ]

    disclaimer = "⚠️ This tool is for educational purposes only. Please consult a licensed medical professional for real diagnosis."

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "symptom": symptom,
            "conditions": list(set(possible_conditions)),
            "next_steps": random.sample(next_steps, 2),
            "disclaimer": disclaimer
        }
    )
