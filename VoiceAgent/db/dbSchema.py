from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class PatientData:
    patient_name: str
    birthdate: str
    appointment_reason: str
    desired_date: str