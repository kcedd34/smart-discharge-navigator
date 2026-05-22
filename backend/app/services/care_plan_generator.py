"""
Discharge Care Plan Generator

Generates FHIR CarePlan and Task resources based on risk assessment.
Follows the Single Responsibility Principle (SRP).
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.models.patient import RiskAssessment, RiskLevel, DischargePlan, DischargePlanTask
from app.core.fhir_client import fhir_client


class CarePlanGenerator:
    """
    Discharge Care Plan Generator
    
    Creates comprehensive discharge plans including:
    - FHIR CarePlan resource
    - FHIR Task resources for each discharge activity
    - Patient-friendly instructions
    """
    
    def __init__(self):
        self.fhir_client = fhir_client
    
    async def generate_discharge_plan(
        self,
        patient_id: str,
        patient_name: str,
        risk_assessment: RiskAssessment,
        medications: List[Dict[str, Any]]
    ) -> DischargePlan:
        """
        Generate comprehensive discharge plan
        
        Args:
            patient_id: FHIR Patient ID
            patient_name: Patient name for display
            risk_assessment: Calculated risk assessment
            medications: List of MedicationRequest resources
            
        Returns:
            DischargePlan with CarePlan ID and tasks
        """
        # Create FHIR CarePlan resource
        care_plan_resource = self._create_care_plan_resource(
            patient_id,
            patient_name,
            risk_assessment
        )
        
        # Save CarePlan to FHIR server
        created_care_plan = await self.fhir_client.create_resource(
            "CarePlan",
            care_plan_resource
        )
        care_plan_id = created_care_plan.get("id") if created_care_plan else None
        
        # Generate discharge tasks
        tasks = self._generate_discharge_tasks(risk_assessment, care_plan_id)
        
        # Create FHIR Task resources
        task_ids = []
        for task in tasks:
            task_resource = self._create_task_resource(
                patient_id,
                task,
                care_plan_id
            )
            created_task = await self.fhir_client.create_resource(
                "Task",
                task_resource
            )
            if created_task:
                task_ids.append(created_task.get("id"))
        
        # Generate patient instructions
        patient_instructions = self._generate_patient_instructions(
            patient_name,
            risk_assessment,
            medications,
            tasks
        )
        
        # Extract medication names
        medication_names = self._extract_medication_names(medications)
        
        # Generate follow-up appointments
        follow_ups = self._generate_follow_up_schedule(risk_assessment)
        
        return DischargePlan(
            patient_id=patient_id,
            care_plan_id=care_plan_id,
            title=f"Discharge Plan for {patient_name}",
            description=f"Comprehensive discharge plan based on {risk_assessment.risk_level.value} readmission risk",
            tasks=tasks,
            medications=medication_names,
            follow_up_appointments=follow_ups,
            patient_instructions=patient_instructions
        )
    
    def _create_care_plan_resource(
        self,
        patient_id: str,
        patient_name: str,
        risk_assessment: RiskAssessment
    ) -> Dict[str, Any]:
        """Create FHIR CarePlan resource"""
        now = datetime.utcnow().isoformat() + "Z"
        
        return {
            "resourceType": "CarePlan",
            "status": "active",
            "intent": "plan",
            "title": f"Hospital Discharge Plan - {patient_name}",
            "description": f"Discharge care plan for patient at {risk_assessment.risk_level.value} risk of readmission",
            "subject": {
                "reference": f"Patient/{patient_id}",
                "display": patient_name
            },
            "period": {
                "start": now
            },
            "created": now,
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/us/core/CodeSystem/careplan-category",
                            "code": "assess-plan",
                            "display": "Assessment and Plan of Treatment"
                        }
                    ]
                }
            ],
            "activity": [
                {
                    "detail": {
                        "kind": "Task",
                        "code": {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "306206005",
                                    "display": "Discharge planning"
                                }
                            ]
                        },
                        "status": "in-progress",
                        "description": rec
                    }
                }
                for rec in risk_assessment.recommendations
            ]
        }
    
    def _generate_discharge_tasks(
        self,
        risk_assessment: RiskAssessment,
        care_plan_id: str
    ) -> List[DischargePlanTask]:
        """Generate discharge tasks based on risk level"""
        tasks = []
        base_date = datetime.utcnow()
        
        # Universal tasks
        tasks.append(DischargePlanTask(
            title="Medication Reconciliation",
            description="Review all discharge medications with patient and ensure understanding of dosing",
            priority="high",
            due_date=base_date + timedelta(hours=2)
        ))
        
        tasks.append(DischargePlanTask(
            title="Provide Discharge Instructions",
            description="Provide written discharge instructions in patient's preferred language",
            priority="high",
            due_date=base_date + timedelta(hours=2)
        ))
        
        # Risk-specific tasks
        if risk_assessment.risk_level in [RiskLevel.HIGH, RiskLevel.MODERATE]:
            tasks.append(DischargePlanTask(
                title="Schedule Follow-up Appointment",
                description=f"Schedule follow-up appointment within {'7 days' if risk_assessment.risk_level == RiskLevel.HIGH else '14 days'}",
                priority="high",
                due_date=base_date + timedelta(days=1)
            ))
            
            tasks.append(DischargePlanTask(
                title="Arrange Post-Discharge Call",
                description="Schedule post-discharge phone call within 48-72 hours",
                priority="high",
                due_date=base_date + timedelta(days=2)
            ))
        
        if risk_assessment.risk_level == RiskLevel.HIGH:
            tasks.append(DischargePlanTask(
                title="Initiate Transitional Care",
                description="Refer to transitional care program or home health services",
                priority="high",
                due_date=base_date + timedelta(hours=4)
            ))
            
            tasks.append(DischargePlanTask(
                title="Provide 24/7 Contact Information",
                description="Ensure patient has 24/7 contact number for care team",
                priority="high",
                due_date=base_date + timedelta(hours=1)
            ))
        
        # Check for polypharmacy
        polypharmacy_factor = next(
            (f for f in risk_assessment.risk_factors if f.name == "Polypharmacy"),
            None
        )
        if polypharmacy_factor and polypharmacy_factor.value >= 0.6:
            tasks.append(DischargePlanTask(
                title="Pharmacy Consultation",
                description="Schedule pharmacy consultation for medication management review",
                priority="medium",
                due_date=base_date + timedelta(days=3)
            ))
        
        return tasks
    
    def _create_task_resource(
        self,
        patient_id: str,
        task: DischargePlanTask,
        care_plan_id: str
    ) -> Dict[str, Any]:
        """Create FHIR Task resource"""
        priority_map = {
            "high": "urgent",
            "medium": "routine",
            "low": "routine"
        }
        
        task_resource = {
            "resourceType": "Task",
            "status": "ready",
            "intent": "plan",
            "priority": priority_map.get(task.priority, "routine"),
            "description": task.title,
            "for": {
                "reference": f"Patient/{patient_id}"
            },
            "authoredOn": datetime.utcnow().isoformat() + "Z",
            "code": {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/CodeSystem/task-code",
                        "code": "fulfill",
                        "display": "Fulfill the focal request"
                    }
                ],
                "text": task.title
            }
        }
        
        if care_plan_id:
            task_resource["basedOn"] = [
                {
                    "reference": f"CarePlan/{care_plan_id}"
                }
            ]
        
        if task.due_date:
            task_resource["executionPeriod"] = {
                "end": task.due_date.isoformat() + "Z"
            }
        
        return task_resource
    
    def _generate_patient_instructions(
        self,
        patient_name: str,
        risk_assessment: RiskAssessment,
        medications: List[Dict[str, Any]],
        tasks: List[DischargePlanTask]
    ) -> str:
        """Generate plain-language instructions for patient"""
        instructions = f"""DISCHARGE INSTRUCTIONS FOR {patient_name.upper()}

**Your Discharge Summary:**
You are being discharged from the hospital today. Based on our assessment, you have a {risk_assessment.risk_level.value} risk of returning to the hospital in the next 30 days. This means it's very important that you follow these instructions carefully.

**WHAT YOU NEED TO DO AFTER LEAVING THE HOSPITAL:**

1. **Take Your Medications:**
   - Take all medications exactly as prescribed
   - Don't skip doses or stop taking medications without talking to your doctor
   - Total medications: {len(medications)} prescriptions
   - If you have trouble affording your medications, please call us

2. **Watch for Warning Signs:**
   - If you experience any new or worsening symptoms, call your doctor immediately
   - Go to the emergency room if you have severe symptoms like chest pain, trouble breathing, or severe pain

3. **Follow-Up Appointments:**
   - It is VERY IMPORTANT that you attend your follow-up appointments
   - If you cannot make an appointment, call to reschedule - do not just skip it

4. **Who to Call if You Have Questions:**
   - Your doctor's office: [To be filled by care team]
   - 24/7 Nurse Line: [To be filled by care team]
   - In an emergency, call 911

**IMPORTANT REMINDERS:**
"""
        
        for rec in risk_assessment.recommendations:
            instructions += f"\n- {rec}"
        
        if risk_assessment.risk_level == RiskLevel.HIGH:
            instructions += "\n\n**EXTRA SUPPORT:**\nBecause you are at higher risk, we will call you within 2-3 days to check on you. Please answer this call - we want to help keep you healthy and out of the hospital!"
        
        instructions += "\n\n**Questions?** Don't hesitate to call your care team. We are here to help you stay healthy."
        
        return instructions
    
    def _extract_medication_names(self, medications: List[Dict[str, Any]]) -> List[str]:
        """Extract medication names from MedicationRequest resources"""
        names = []
        for med in medications:
            try:
                med_codeable = med.get("medicationCodeableConcept", {})
                coding = med_codeable.get("coding", [])
                if coding:
                    names.append(coding[0].get("display", "Unknown medication"))
                else:
                    names.append(med_codeable.get("text", "Unknown medication"))
            except Exception:
                names.append("Unknown medication")
        return names
    
    def _generate_follow_up_schedule(self, risk_assessment: RiskAssessment) -> List[str]:
        """Generate follow-up appointment schedule"""
        follow_ups = []
        
        if risk_assessment.risk_level == RiskLevel.HIGH:
            follow_ups.append("Primary Care Physician: Within 7 days")
            follow_ups.append("Specialist (if applicable): Within 14 days")
            follow_ups.append("Post-discharge phone call: Within 2-3 days")
        elif risk_assessment.risk_level == RiskLevel.MODERATE:
            follow_ups.append("Primary Care Physician: Within 14 days")
            follow_ups.append("Specialist (if applicable): Within 30 days")
        else:
            follow_ups.append("Primary Care Physician: Within 30 days")
        
        return follow_ups


# Singleton instance
care_plan_generator = CarePlanGenerator()
