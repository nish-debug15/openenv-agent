# 15 varied medical triage cases
cases = [
    # Case 1: Active heart attack
    {
        "symptoms": ["chest pain", "shortness of breath", "sweating"],
        "pain_level": 9,
        "age": 58,
        "true_severity": "Emergency",
        "hidden_info": ["History of coronary artery disease.", "Electrocardiogram shows ST elevation."]
    },
    # Case 2: Appendicitis (ambiguous early symptoms)
    {
        "symptoms": ["diffuse abdominal pain", "nausea", "loss of appetite"],
        "pain_level": 6,
        "age": 22,
        "true_severity": "Emergency",
        "hidden_info": ["Rebound tenderness in the right lower quadrant.", "Fever developed recently (38.5C)."]
    },
    # Case 3: Simple viral infection
    {
        "symptoms": ["runny nose", "sore throat", "mild cough"],
        "pain_level": 2,
        "age": 14,
        "true_severity": "Mild",
        "hidden_info": ["No history of asthma or respiratory issues.", "Vitals are stable."]
    },
    # Case 4: Kidney Stones
    {
        "symptoms": ["severe flank pain", "blood in urine"],
        "pain_level": 10,
        "age": 45,
        "true_severity": "Emergency",
        "hidden_info": ["Pain comes in waves.", "No fever."]
    },
    # Case 5: Minor laceration
    {
        "symptoms": ["small cut on finger", "bleeding stopped"],
        "pain_level": 2,
        "age": 30,
        "true_severity": "Mild",
        "hidden_info": ["Last tetanus shot was 2 years ago.", "Wound appears clean."]
    },
    # Case 6: Pediatric asthma exacerbation
    {
        "symptoms": ["wheezing", "coughing"],
        "pain_level": 4,
        "age": 6,
        "true_severity": "Emergency", # breathing issues in a child
        "hidden_info": ["Visible chest retractions.", "Oxygen saturation is 91%."]
    },
    # Case 7: Migraine
    {
        "symptoms": ["throbbing headache", "photophobia", "nausea"],
        "pain_level": 6,
        "age": 28,
        "true_severity": "Moderate", 
        "hidden_info": ["Patient has a history of chronic migraines identical to this.", "No neurological deficits."]
    },
    # Case 8: Elderly urinary tract infection with confusion
    {
        "symptoms": ["confusion", "fatigue", "mild fever"],
        "pain_level": 3,
        "age": 82,
        "true_severity": "Emergency", # confusion in elderly is a red flag for sepsis
        "hidden_info": ["Urine dipstick is positive for leukocytes.", "Blood pressure is dropping (90/60)."]
    },
    # Case 9: Sprained ankle
    {
        "symptoms": ["ankle swelling", "pain when walking"],
        "pain_level": 5,
        "age": 19,
        "true_severity": "Moderate",
        "hidden_info": ["Able to bear some weight.", "No obvious deformity."]
    },
    # Case 10: Ectopic pregnancy or ruptured cyst
    {
        "symptoms": ["sudden pelvic pain", "dizziness"],
        "pain_level": 8,
        "age": 26, 
        "true_severity": "Emergency",
        "hidden_info": ["Patient missed her last period.", "Heart rate is elevated (115 bpm)."]
    },
    # Case 11: Mild sunburn
    {
        "symptoms": ["red skin", "warm to touch"],
        "pain_level": 3,
        "age": 24,
        "true_severity": "Mild",
        "hidden_info": ["No blistering.", "Patient stayed hydrated."]
    },
    # Case 12: Diabetic Ketoacidosis
    {
        "symptoms": ["excessive thirst", "frequent urination", "fruity breath"],
        "pain_level": 2,
        "age": 16,
        "true_severity": "Emergency",
        "hidden_info": ["Patient is a known Type 1 Diabetic.", "Blood glucose is 450 mg/dL."]
    },
    # Case 13: Gastroenteritis
    {
        "symptoms": ["diarrhea", "stomach cramps", "low-grade fever"],
        "pain_level": 5,
        "age": 35,
        "true_severity": "Moderate",
        "hidden_info": ["Patient has been drinking fluids.", "No signs of severe dehydration or blood in stool."]
    },
    # Case 14: Panic Attack
    {
        "symptoms": ["palpitations", "tingling in fingers", "fear of dying"],
        "pain_level": 4,
        "age": 31,
        "true_severity": "Moderate", 
        "hidden_info": ["ECG is normal.", "Patient has a history of anxiety disorders."]
    },
    # Case 15: Elderly Stroke
    {
        "symptoms": ["slurred speech", "facial droop", "arm weakness"],
        "pain_level": 2, # Stroke often isn't very painful
        "age": 75,
        "true_severity": "Emergency",
        "hidden_info": ["Symptoms started 45 minutes ago.", "Requires immediate stroke protocol."]
    }
]

def task_1(): return cases[0]
def task_2(): return cases[1]
def task_3(): return cases[2]
def task_4(): return cases[3]
def task_5(): return cases[4]
def task_6(): return cases[5]
def task_7(): return cases[6]
def task_8(): return cases[7]
def task_9(): return cases[8]
def task_10(): return cases[9]
def task_11(): return cases[10]
def task_12(): return cases[11]
def task_13(): return cases[12]
def task_14(): return cases[13]
def task_15(): return cases[14]
