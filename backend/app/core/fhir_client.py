"""
FHIR Client Wrapper

Abstracts FHIR server interactions following the Dependency Inversion Principle (DIP).
Provides a clean interface for FHIR resource operations.
"""

import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import base64

from app.core.config import settings


class FHIRClient:
    """
    FHIR Client for InterSystems IRIS for Health
    
    Handles all HTTP interactions with the FHIR server including authentication,
    resource retrieval, and resource creation.
    """
    
    def __init__(self):
        self.base_url = settings.FHIR_BASE_URL.rstrip('/')
        self.username = settings.IRIS_USERNAME
        self.password = settings.IRIS_PASSWORD
        self._setup_auth()
    
    def _setup_auth(self):
        """Setup Basic Authentication headers"""
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json"
        }
    
    async def get_resource(self, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single FHIR resource by ID
        
        Args:
            resource_type: FHIR resource type (e.g., 'Patient', 'Encounter')
            resource_id: Resource ID
            
        Returns:
            Resource dict or None if not found
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise
            except Exception as e:
                print(f"Error fetching {resource_type}/{resource_id}: {str(e)}")
                raise
    
    async def search_resources(
        self, 
        resource_type: str, 
        params: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for FHIR resources
        
        Args:
            resource_type: FHIR resource type to search
            params: Search parameters
            
        Returns:
            List of matching resources
        """
        url = f"{self.base_url}/{resource_type}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url, 
                    headers=self.headers, 
                    params=params or {},
                    timeout=30.0
                )
                response.raise_for_status()
                bundle = response.json()
                
                # Extract resources from Bundle
                resources = []
                if bundle.get('entry'):
                    resources = [entry['resource'] for entry in bundle['entry']]
                
                return resources
            except Exception as e:
                print(f"Error searching {resource_type}: {str(e)}")
                return []
    
    async def create_resource(self, resource_type: str, resource: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new FHIR resource
        
        Args:
            resource_type: FHIR resource type
            resource: Resource data
            
        Returns:
            Created resource with server-assigned ID
        """
        url = f"{self.base_url}/{resource_type}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, 
                    headers=self.headers, 
                    json=resource,
                    timeout=30.0
                )
                response.raise_for_status()
                # IRIS returns HTTP 201 with empty body — extract ID from Location header
                if response.content:
                    return response.json()
                location = response.headers.get("Location", "")
                parts = location.rstrip("/").split("/")
                if resource_type in parts:
                    idx = parts.index(resource_type)
                    if idx + 1 < len(parts):
                        return {"id": parts[idx + 1], "resourceType": resource_type}
                return {"resourceType": resource_type}
            except Exception as e:
                print(f"Error creating {resource_type}: {str(e)}")
                raise
    
    async def get_patient_encounters(
        self, 
        patient_id: str, 
        days: int = 180
    ) -> List[Dict[str, Any]]:
        """
        Get recent encounters for a patient
        
        Args:
            patient_id: Patient ID
            days: Number of days to look back
            
        Returns:
            List of Encounter resources
        """
        params = {
            "patient": patient_id,
            "_sort": "-date",
            "_count": "100"
        }
        return await self.search_resources("Encounter", params)
    
    async def get_patient_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get active conditions for a patient
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of Condition resources
        """
        params = {
            "patient": patient_id,
            "clinical-status": "active",
            "_sort": "-onset-date"
        }
        return await self.search_resources("Condition", params)
    
    async def get_patient_observations(
        self, 
        patient_id: str,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get observations for a patient
        
        Args:
            patient_id: Patient ID
            category: Observation category (e.g., 'vital-signs', 'laboratory')
            
        Returns:
            List of Observation resources
        """
        params = {
            "patient": patient_id,
            "_sort": "-date",
            "_count": "100"
        }
        if category:
            params["category"] = category
        
        return await self.search_resources("Observation", params)
    
    async def get_patient_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get active medication requests for a patient
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of MedicationRequest resources
        """
        params = {
            "patient": patient_id,
            "status": "active"
        }
        return await self.search_resources("MedicationRequest", params)


# Singleton instance
fhir_client = FHIRClient()
