"""
Sample FHIR Data Loader

Generates synthetic patient data with clinical information and loads it into
InterSystems IRIS for Health FHIR server.
"""

import requests
import json
from datetime import datetime, timedelta
import random
import base64

# FHIR Server Configuration
FHIR_BASE_URL = "http://localhost:52773/fhir/r4"
USERNAME = "SuperUser"
PASSWORD = "SYS"

# Create Basic Auth header
credentials = f"{USERNAME}:{PASSWORD}"
encoded = base64.b64encode(credentials.encode()).decode()
HEADERS = {
    "Authorization": f"Basic {encoded}",
    "Content-Type": "application/fhir+json",
    "Accept": "application/fhir+json"
}

# Sample data
FIRST_NAMES = ["John", "Mary", "Robert", "Patricia", "Michael", "Linda", "William", "Barbara", "David", "Elizabeth"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

HIGH_RISK_CONDITIONS = [
    {"code": "I50.9", "display": "Heart Failure, unspecified"},
    {"code": "J44.9", "display": "Chronic Obstructive Pulmonary Disease"},
    {"code": "E11.9", "display": "Type 2 Diabetes Mellitus"},
    {"code": "I25.10", "display": "Atherosclerotic Heart Disease"},
    {"code": "N18.9", "display": "Chronic Kidney Disease, unspecified"}
]

HIGH_RISK_ALLERGIES = [
    {
        "substance_code": "372687004",
        "substance_display": "Penicillin",
        "criticality": "high",
        "reaction_display": "Anaphylaxis"
    },
    {
        "substance_code": "372665008",
        "substance_display": "NSAIDs (Non-steroidal anti-inflammatory drugs)",
        "criticality": "high",
        "reaction_display": "Acute Kidney Injury"
    },
    {
        "substance_code": "387584000",
        "substance_display": "Iodinated contrast media",
        "criticality": "high",
        "reaction_display": "Anaphylactoid Reaction"
    }
]

MODERATE_RISK_ALLERGIES = [
    {
        "substance_code": "372726002",
        "substance_display": "Sulfonamides",
        "criticality": "low",
        "reaction_display": "Skin rash"
    },
    {
        "substance_code": "29175007",
        "substance_display": "Codeine",
        "criticality": "low",
        "reaction_display": "Nausea and vomiting"
    }
]

MEDICATIONS = [
    {"code": "197361", "display": "Metformin 500 MG Oral Tablet"},
    {"code": "314076", "display": "Lisinopril 10 MG Oral Tablet"},
    {"code": "197316", "display": "Atorvastatin 20 MG Oral Tablet"},
    {"code": "309362", "display": "Furosemide 40 MG Oral Tablet"},
    {"code": "197511", "display": "Aspirin 81 MG Oral Tablet"}
]


def create_patient(first_name, last_name, birth_date, gender):
    """Create a Patient resource"""
    patient = {
        "resourceType": "Patient",
        "name": [
            {
                "use": "official",
                "family": last_name,
                "given": [first_name]
            }
        ],
        "gender": gender,
        "birthDate": birth_date
    }
    return patient


def create_encounter(patient_id, date, encounter_type="inpatient"):
    """Create an Encounter resource"""
    encounter = {
        "resourceType": "Encounter",
        "status": "finished",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "IMP" if encounter_type == "inpatient" else "AMB",
            "display": "inpatient encounter" if encounter_type == "inpatient" else "ambulatory"
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "period": {
            "start": date.isoformat() + "Z",
            "end": (date + timedelta(days=3)).isoformat() + "Z"
        }
    }
    return encounter


def create_condition(patient_id, condition_data, onset_date):
    """Create a Condition resource"""
    condition = {
        "resourceType": "Condition",
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active"
            }]
        },
        "code": {
            "coding": [{
                "system": "http://hl7.org/fhir/sid/icd-10",
                "code": condition_data["code"],
                "display": condition_data["display"]
            }]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "onsetDateTime": onset_date.isoformat() + "Z"
    }
    return condition


def create_observation(patient_id, loinc_code, display, value, unit, date):
    """Create an Observation resource (vital sign)"""
    observation = {
        "resourceType": "Observation",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": loinc_code,
                "display": display
            }]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": date.isoformat() + "Z",
        "valueQuantity": {
            "value": value,
            "unit": unit,
            "system": "http://unitsofmeasure.org"
        }
    }
    return observation


def create_medication_request(patient_id, medication_data, authored_date):
    """Create a MedicationRequest resource"""
    med_request = {
        "resourceType": "MedicationRequest",
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [{
                "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                "code": medication_data["code"],
                "display": medication_data["display"]
            }]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "authoredOn": authored_date.isoformat() + "Z"
    }
    return med_request


def create_allergy_intolerance(patient_id, allergy_data):
    """Create an AllergyIntolerance resource"""
    return {
        "resourceType": "AllergyIntolerance",
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                "code": "active",
                "display": "Active"
            }]
        },
        "verificationStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                "code": "confirmed",
                "display": "Confirmed"
            }]
        },
        "type": "allergy",
        "criticality": allergy_data["criticality"],
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": allergy_data["substance_code"],
                "display": allergy_data["substance_display"]
            }],
            "text": allergy_data["substance_display"]
        },
        "patient": {
            "reference": f"Patient/{patient_id}"
        },
        "reaction": [{
            "manifestation": [{
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "display": allergy_data["reaction_display"]
                }],
                "text": allergy_data["reaction_display"]
            }],
            "severity": "severe" if allergy_data["criticality"] == "high" else "mild"
        }]
    }


def post_resource(resource):
    """Post a resource to FHIR server"""
    resource_type = resource["resourceType"]
    url = f"{FHIR_BASE_URL}/{resource_type}"
    
    try:
        response = requests.post(url, json=resource, headers=HEADERS)
        response.raise_for_status()
        # IRIS returns 201 with empty body; extract ID from Location header
        if response.content:
            created = response.json()
            return created.get("id")
        location = response.headers.get("Location", "")
        # Location format: .../Patient/123/_history/1
        parts = location.rstrip("/").split("/")
        # Find the resource type and return the id after it
        if resource_type in parts:
            idx = parts.index(resource_type)
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return None
    except Exception as e:
        print(f"Error creating {resource_type}: {str(e)}")
        return None


def generate_patient_data(risk_profile):
    """Generate complete patient data based on risk profile"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    # Age based on risk
    if risk_profile == "high":
        age = random.randint(70, 85)
    elif risk_profile == "moderate":
        age = random.randint(60, 75)
    else:
        age = random.randint(40, 65)
    
    birth_date = (datetime.now() - timedelta(days=age*365)).date().isoformat()
    gender = random.choice(["male", "female"])
    
    print(f"Creating patient: {first_name} {last_name} ({age} years, {risk_profile} risk)")
    
    # Create patient
    patient = create_patient(first_name, last_name, birth_date, gender)
    patient_id = post_resource(patient)
    
    if not patient_id:
        return
    
    print(f"  Created Patient/{patient_id}")
    
    # Create encounters
    encounter_count = 3 if risk_profile == "high" else (2 if risk_profile == "moderate" else 1)
    for i in range(encounter_count):
        enc_date = datetime.now() - timedelta(days=random.randint(10, 150))
        encounter = create_encounter(patient_id, enc_date)
        enc_id = post_resource(encounter)
        if enc_id:
            print(f"  Created Encounter/{enc_id}")
    
    # Create conditions
    condition_count = 3 if risk_profile == "high" else (2 if risk_profile == "moderate" else 1)
    for i in range(condition_count):
        condition_data = random.choice(HIGH_RISK_CONDITIONS)
        onset_date = datetime.now() - timedelta(days=random.randint(365, 1825))
        condition = create_condition(patient_id, condition_data, onset_date)
        cond_id = post_resource(condition)
        if cond_id:
            print(f"  Created Condition/{cond_id} - {condition_data['display']}")
    
    # Create vital sign observations
    obs_date = datetime.now() - timedelta(days=random.randint(1, 30))
    
    # Heart rate
    hr = random.randint(75, 95) if risk_profile == "low" else random.randint(95, 115)
    obs = create_observation(patient_id, "8867-4", "Heart rate", hr, "beats/minute", obs_date)
    obs_id = post_resource(obs)
    if obs_id:
        print(f"  Created Observation/{obs_id} - Heart Rate")
    
    # Blood pressure
    sbp = random.randint(110, 135) if risk_profile == "low" else random.randint(140, 170)
    obs = create_observation(patient_id, "8480-6", "Systolic blood pressure", sbp, "mm[Hg]", obs_date)
    post_resource(obs)
    
    dbp = random.randint(65, 85) if risk_profile == "low" else random.randint(85, 100)
    obs = create_observation(patient_id, "8462-4", "Diastolic blood pressure", dbp, "mm[Hg]", obs_date)
    post_resource(obs)
    
    # Create medication requests
    med_count = 8 if risk_profile == "high" else (5 if risk_profile == "moderate" else 3)
    for i in range(med_count):
        med_data = random.choice(MEDICATIONS)
        auth_date = datetime.now() - timedelta(days=random.randint(1, 90))
        med_request = create_medication_request(patient_id, med_data, auth_date)
        med_id = post_resource(med_request)
        if med_id:
            print(f"  Created MedicationRequest/{med_id}")

    # Create AllergyIntolerance resources
    if risk_profile == "high":
        allergy_pool = HIGH_RISK_ALLERGIES
        allergy_count = random.randint(1, 3)
    elif risk_profile == "moderate":
        allergy_pool = MODERATE_RISK_ALLERGIES + HIGH_RISK_ALLERGIES[:1]
        allergy_count = random.randint(0, 1)
    else:
        allergy_pool = MODERATE_RISK_ALLERGIES
        allergy_count = random.randint(0, 1)

    selected_allergies = random.sample(allergy_pool, min(allergy_count, len(allergy_pool)))
    for allergy_data in selected_allergies:
        allergy = create_allergy_intolerance(patient_id, allergy_data)
        allergy_id = post_resource(allergy)
        if allergy_id:
            print(f"  Created AllergyIntolerance/{allergy_id} - {allergy_data['substance_display']}")

    print(f"  ✓ Patient {first_name} {last_name} created successfully\n")


def main():
    """Generate sample data for different risk profiles"""
    print("=" * 60)
    print("Smart Discharge Navigator - Sample Data Loader")
    print("=" * 60)
    print()
    
    # Generate patients with different risk profiles
    print("Generating HIGH RISK patients...")
    for i in range(3):
        generate_patient_data("high")
    
    print("Generating MODERATE RISK patients...")
    for i in range(3):
        generate_patient_data("moderate")
    
    print("Generating LOW RISK patients...")
    for i in range(2):
        generate_patient_data("low")
    
    print("=" * 60)
    print("Sample data loading complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
