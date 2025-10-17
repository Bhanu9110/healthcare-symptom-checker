from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import random
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Symptom -> diseases mapping
SYMPTOM_MAP = {
    # Head
    "headache": ["Migraine", "Tension Headache", "Stress", "Dehydration", "Flu", "COVID-19"],
    "dizziness": ["Vertigo", "Low Blood Pressure", "Anemia", "Dehydration", "Hypoglycemia"],
    "blurred vision": ["Eye strain", "Diabetes", "Migraine", "Glaucoma"],

    # Eyes
    "red eyes": ["Conjunctivitis", "Allergy", "Infection", "Dry eyes"],
    "itchy eyes": ["Allergy", "Dry eyes", "Conjunctivitis"],
    "watering eyes": ["Allergy", "Cold", "Foreign body in eye"],

    # Ears
    "ear pain": ["Ear infection", "Earwax blockage", "Temporomandibular joint disorder"],
    "hearing loss": ["Ear infection", "Age-related hearing loss", "Wax buildup", "Noise-induced hearing loss"],
    "ringing in ears": ["Tinnitus", "Hearing loss", "Stress"],

    # Nose
    "runny nose": ["Common Cold", "Allergy", "Sinus Infection"],
    "nasal congestion": ["Allergy", "Sinusitis", "Flu"],
    "nosebleed": ["Dry air", "Injury", "High Blood Pressure"],

    # Throat
    "sore throat": ["Tonsillitis", "Viral Infection", "Common Cold", "Allergy"],
    "difficulty swallowing": ["Tonsillitis", "Strep throat", "Throat infection", "Acid reflux"],
    "hoarseness": ["Laryngitis", "Overuse of voice", "Throat infection"],

    # Chest
    "chest pain": ["Heart Attack", "Angina", "Acid reflux", "Muscle strain", "Pneumonia"],
    "shortness of breath": ["Asthma", "COVID-19", "Heart failure", "Pneumonia", "Anxiety"],
    "palpitations": ["Anxiety", "Arrhythmia", "Hyperthyroidism"],

    # Abdomen
    "stomach pain": ["Gastritis", "Food poisoning", "Indigestion", "Appendicitis", "Ulcer"],
    "nausea": ["Food poisoning", "Pregnancy", "Gastritis", "Vertigo"],
    "diarrhea": ["Food poisoning", "Infection", "IBS", "Food intolerance"],
    "constipation": ["Dietary issues", "Hypothyroidism", "IBS"],

    # Limbs & muscles
    "muscle pain": ["Flu", "COVID-19", "Dengue", "Fibromyalgia", "Overexertion"],
    "joint pain": ["Arthritis", "Dengue", "Lupus", "Gout"],
    "back pain": ["Muscle strain", "Herniated disc", "Arthritis", "Poor posture"],
    "body ache": ["Flu", "COVID-19", "Common Cold", "Dengue"],
    "numbness or tingling": ["Nerve compression", "Diabetes", "Vitamin B12 deficiency"],

    # Skin
    "rash": ["Allergy", "Chickenpox", "Measles", "Eczema", "Insect bite", "Psoriasis"],
    "itching": ["Allergy", "Eczema", "Fungal infection", "Dry skin"],
    "red spots": ["Allergy", "Chickenpox", "Heat rash", "Infection"],

    # General symptoms
    "fatigue": ["Anemia", "Hypothyroidism", "Flu", "COVID-19", "Chronic fatigue syndrome"],
    "fever": ["Flu", "COVID-19", "Common Cold", "Dengue", "Infection", "Malaria"],
    "chills": ["Flu", "COVID-19", "Malaria", "Infection"],
    "weight loss": ["Hyperthyroidism", "Diabetes", "Cancer", "Stress"],
    "weight gain": ["Hypothyroidism", "Overeating", "Fluid retention"],

    # Others
    "swelling": ["Injury", "Allergy", "Kidney disease", "Heart failure"],
    "bleeding gums": ["Vitamin deficiency", "Gingivitis", "Infection"],
    "frequent urination": ["Diabetes", "Urinary tract infection", "Prostate issues"],
    "painful urination": ["Urinary tract infection", "Kidney stones", "STI"],

    # Mental & neurological
    "anxiety": ["Stress", "Panic disorder", "Depression"],
    "depression": ["Major depressive disorder", "Stress", "Vitamin D deficiency"],
    "insomnia": ["Stress", "Depression", "Caffeine", "Sleep apnea"],
    # General

    "fever": ["Flu", "COVID-19", "Malaria", "Dengue", "Infection"],
    "chills": ["Flu", "COVID-19", "Malaria", "Bacterial infection"],
    "fatigue": ["Anemia", "Hypothyroidism", "Flu", "COVID-19", "Depression", "Chronic fatigue syndrome"],
    "weight loss": ["Hyperthyroidism", "Diabetes", "Cancer", "Stress"],
    "weight gain": ["Hypothyroidism", "Overeating", "Fluid retention"],

    # Head & Brain
    "headache": ["Migraine", "Tension headache", "Stress", "Hypertension", "Brain tumor"],
    "dizziness": ["Vertigo", "Low BP", "Dehydration", "Inner ear issues"],
    "seizures": ["Epilepsy", "Brain tumor", "Infection", "Stroke"],
    "memory loss": ["Alzheimer's", "Vitamin B12 deficiency", "Stress", "Dementia"],

    # Eyes
    "blurred vision": ["Diabetes", "Cataract", "Glaucoma", "Migraine"],
    "red eyes": ["Conjunctivitis", "Allergy", "Infection", "Dry eyes"],
    "watering eyes": ["Allergy", "Cold", "Foreign body in eye"],

    # Ears
    "ear pain": ["Ear infection", "Earwax blockage", "TMJ disorder"],
    "ringing in ears": ["Tinnitus", "Hearing loss", "Stress"],
    "hearing loss": ["Ear infection", "Age-related", "Noise-induced"],

    # Nose & Throat
    "runny nose": ["Common Cold", "Allergy", "Sinus infection"],
    "nasal congestion": ["Allergy", "Sinusitis", "Flu"],
    "sore throat": ["Tonsillitis", "Viral infection", "Common Cold", "Allergy"],
    "hoarseness": ["Laryngitis", "Throat infection", "Overuse of voice"],

    # Cardiovascular
    "chest pain": ["Heart attack", "Angina", "Acid reflux", "Muscle strain", "Pneumonia"],
    "palpitations": ["Arrhythmia", "Anxiety", "Hyperthyroidism"],
    "swelling": ["Heart failure", "Kidney disease", "Allergy"],

    # Respiratory
    "cough": ["Common Cold", "Bronchitis", "COVID-19", "Allergy", "Pneumonia"],
    "shortness of breath": ["Asthma", "COVID-19", "Heart failure", "Pneumonia", "Anxiety"],

    # Gastrointestinal
    "stomach pain": ["Gastritis", "Food poisoning", "Indigestion", "Appendicitis", "Ulcer"],
    "nausea": ["Food poisoning", "Pregnancy", "Gastritis", "Vertigo"],
    "vomiting": ["Food poisoning", "Gastritis", "Migraine", "Infection"],
    "diarrhea": ["Food poisoning", "Infection", "IBS", "Food intolerance"],
    "constipation": ["Dietary issues", "Hypothyroidism", "IBS"],
    "heartburn": ["GERD", "Acid reflux"],

    # Musculoskeletal
    "joint pain": ["Arthritis", "Lupus", "Gout", "Dengue", "Injury"],
    "back pain": ["Muscle strain", "Herniated disc", "Arthritis", "Poor posture"],
    "muscle pain": ["Flu", "COVID-19", "Dengue", "Fibromyalgia", "Overexertion"],
    "body ache": ["Flu", "COVID-19", "Dengue", "Common Cold"],

    # Skin
    "rash": ["Allergy", "Chickenpox", "Measles", "Eczema", "Psoriasis"],
    "itching": ["Allergy", "Eczema", "Fungal infection", "Dry skin"],
    "red spots": ["Allergy", "Chickenpox", "Heat rash", "Infection"],

    # Genitourinary
    "painful urination": ["Urinary tract infection", "Kidney stones", "STI"],
    "frequent urination": ["Diabetes", "Urinary tract infection", "Prostate issues"],
    "blood in urine": ["Kidney stones", "UTI", "Bladder cancer"],

    # Neurological / Mental health
    "anxiety": ["Stress", "Panic disorder", "Depression"],
    "depression": ["Major depressive disorder", "Stress", "Vitamin D deficiency"],
    "insomnia": ["Stress", "Depression", "Caffeine", "Sleep apnea"],
    "numbness or tingling": ["Nerve compression", "Diabetes", "Vitamin B12 deficiency"],

    # Infectious / Systemic
    "infection": ["Bacterial infection", "Viral infection", "Fungal infection", "Parasitic infection"],
}





# Reverse mapping: disease -> symptoms
DISEASE_MAP = {}
for symptom, diseases in SYMPTOM_MAP.items():
    for disease in diseases:
        DISEASE_MAP.setdefault(disease.lower(), []).append(symptom.lower())

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/check", response_class=HTMLResponse)
async def check_symptom(request: Request, symptom: str = Form(...)):
    # Normalize and split input by comma, 'and' (word), semicolon or newline
    user_input = symptom.lower()
    user_symptoms = re.split(r",|\band\b|;|\n", user_input)
    user_symptoms = [s.strip() for s in user_symptoms if s.strip()]

    possible_conditions = set()
    matched_symptoms = set()

    # Check user tokens against every known symptom (word-boundary aware)
    for user_symptom in user_symptoms:
        for known_symptom, diseases in SYMPTOM_MAP.items():
            # match exact word or phrase inside the user input (avoid partial-word matches)
            if re.search(r"\b" + re.escape(known_symptom) + r"\b", user_symptom) \
               or re.search(r"\b" + re.escape(user_symptom) + r"\b", known_symptom) \
               or known_symptom in user_symptom \
               or user_symptom in known_symptom:
                matched_symptoms.add(known_symptom)
                for d in diseases:
                    possible_conditions.add(d)

    # Fallback: if nothing matched, try previous disease-centric heuristic
    if not possible_conditions:
        for disease, disease_symptoms in DISEASE_MAP.items():
            for user_symptom in user_symptoms:
                if any(user_symptom in ds_symptom for ds_symptom in disease_symptoms) or user_symptom in disease:
                    possible_conditions.add(disease.title())

    if not possible_conditions:
        possible_conditions = {"Unable to determine. Please consult a doctor."}

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
            "conditions": sorted(list(possible_conditions)),
            "next_steps": random.sample(next_steps, 2),
            "disclaimer": disclaimer,
            "matched_symptoms": sorted(list(matched_symptoms))
        }
    )
