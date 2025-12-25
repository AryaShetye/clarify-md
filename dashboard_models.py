"""
Doctor Dashboard domain models and lightweight storage.

This module is an EXTENSION of the existing CLARIFY.MD system.
It does NOT modify agent logic or orchestration. It provides a
non-EMR doctor dashboard context around the existing CLARIFY.MD
agentic pipeline.

Ownership:
- CLARIFY.MD: data modeling for doctor, patients, encounters,
  and storing structured CLARIFY.MD interpretations.
- Gemini: unchanged; still acts only as reasoning engine inside agents.

Persistence strategy:
- Default: in-memory (suitable for Streamlit session / hackathon).
- Optional: JSON file persistence for demo replay.

Google-first strategy hooks:
- This module is storage-agnostic. A future Google Cloud Storage
  or Firestore backend can implement the same interface without
  changing the dashboard or agent code.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import uuid
import os

# -----------------------------
# Core domain data structures
# -----------------------------

@dataclass
class Doctor:
    """Single-clinician context for the dashboard.

    NOTE: CLARIFY.MD is a clinical language interpreter, not an EMR.
    The Doctor entity is intentionally lightweight and non-identifying.
    """

    id: str
    display_name: str = "Dr. Demo Clinician"


@dataclass
class Encounter:
    """A single patient encounter with a CLARIFY.MD interpretation.

    This is a READ-ONLY view of the CLARIFY.MD agentic pipeline output
    at a point in time. The dashboard does not modify or re-interpret
    agent outputs.
    """

    id: str
    patient_id: str
    doctor_id: str
    created_at: datetime
    patient_narrative: str
    clarify_raw_result: Dict[str, Any]
    risk_level: str
    uncertainty_flags: List[str] = field(default_factory=list)


@dataclass
class Patient:
    """Lightweight, non-EMR patient representation.

    Stores only minimal structured demographics for clinical context
    (name, age, weight, blood group). This is still NOT an EMR and is
    intended for hackathon / prototype use.
    """

    id: str
    display_name: str
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    blood_group: Optional[str] = None
    notes: Optional[str] = None
    encounters: List[Encounter] = field(default_factory=list)


# ------------------------------------
# Simple JSON / in-memory storage API
# ------------------------------------

class DashboardStorage:
    """Abstracts storage for doctor dashboard state.

    Default implementation is local JSON file + in-memory cache.
    This can be replaced by Google Cloud Storage / Firestore
    without changing the dashboard or CLARIFY.MD agents.
    """

    def __init__(self, path: str = "dashboard_state.json") -> None:
        self.path = path
        self._doctor: Optional[Doctor] = None
        self._patients: Dict[str, Patient] = {}
        self._loaded = False

    # ------------
    # Load / save
    # ------------

    def _load(self) -> None:
        if self._loaded:
            return
        self._loaded = True

        if not os.path.exists(self.path):
            # Start with an empty, single-clinician context
            self._doctor = Doctor(id="doctor-1")
            self._patients = {}
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            # Fail open in demo mode – do not block the app
            self._doctor = Doctor(id="doctor-1")
            self._patients = {}
            return

        doctor_data = data.get("doctor") or {"id": "doctor-1", "display_name": "Dr. Demo Clinician"}
        self._doctor = Doctor(**doctor_data)

        self._patients = {}
        for p in data.get("patients", []):
            encounters: List[Encounter] = []
            for e in p.get("encounters", []):
                try:
                    encounters.append(
                        Encounter(
                            id=e["id"],
                            patient_id=e["patient_id"],
                            doctor_id=e.get("doctor_id", doctor_data["id"]),
                            created_at=datetime.fromisoformat(e["created_at"]),
                            patient_narrative=e.get("patient_narrative", ""),
                            clarify_raw_result=e.get("clarify_raw_result", {}),
                            risk_level=e.get("risk_level", "unknown"),
                            uncertainty_flags=e.get("uncertainty_flags", []),
                        )
                    )
                except Exception:
                    # Skip malformed encounters instead of failing
                    continue

            patient = Patient(
                id=p["id"],
                display_name=p.get("display_name", "Patient"),
                age=p.get("age"),
                weight_kg=p.get("weight_kg"),
                blood_group=p.get("blood_group"),
                notes=p.get("notes"),
                encounters=encounters,
            )
            self._patients[patient.id] = patient

    def _save(self) -> None:
        """Persist current state to JSON.

        NOTE: For hackathon/demo use only. In production, this would be
        replaced by a proper clinical data store (e.g., FHIR / EMR, or
        a Google Cloud Storage / Firestore-backed service).
        """

        if not self._loaded:
            return

        try:
            payload = {
                "doctor": asdict(self._doctor) if self._doctor else None,
                "patients": [
                    {
                        **asdict(p),
                        "encounters": [
                            {
                                **asdict(e),
                                "created_at": e.created_at.isoformat(),
                            }
                            for e in p.encounters
                        ],
                    }
                    for p in self._patients.values()
                ],
            }
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
        except Exception:
            # Silent failure by design for hackathon demo – dashboard remains in-memory.
            pass

    # ---------------
    # Public methods
    # ---------------

    @property
    def doctor(self) -> Doctor:
        self._load()
        assert self._doctor is not None
        return self._doctor

    def list_patients(self) -> List[Patient]:
        self._load()
        # Return patients sorted by most recent encounter
        return sorted(
            self._patients.values(),
            key=lambda p: (p.encounters[-1].created_at if p.encounters else datetime.min),
            reverse=True,
        )

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        self._load()
        return self._patients.get(patient_id)

    def create_patient(
        self,
        display_name: str,
        notes: Optional[str] = None,
        age: Optional[int] = None,
        weight_kg: Optional[float] = None,
        blood_group: Optional[str] = None,
    ) -> Patient:
        """Create a new patient with minimal structured demographics.

        This remains non-EMR: no identifiers like MRN, address, or
        contact details are stored. Demographics are used only to
        contextualize CLARIFY.MD interpretations for the clinician.
        """
        self._load()
        patient_id = str(uuid.uuid4())
        patient = Patient(
            id=patient_id,
            display_name=display_name.strip() or "Unnamed Patient",
            age=age,
            weight_kg=weight_kg,
            blood_group=blood_group,
            notes=notes,
        )
        self._patients[patient.id] = patient
        self._save()
        return patient

    def add_encounter(
        self,
        patient_id: str,
        patient_narrative: str,
        clarify_raw_result: Dict[str, Any],
    ) -> Encounter:
        """Attach a new encounter with CLARIFY.MD interpretation to a patient.

        The encounter stores the FULL raw CLARIFY.MD result to preserve
        agent transparency. The dashboard only reads from this structure.
        """

        self._load()
        patient = self._patients.get(patient_id)
        if not patient:
            raise ValueError(f"Unknown patient_id: {patient_id}")

        created_at = datetime.utcnow()
        risk_data = clarify_raw_result.get("risk", {})
        risk_level = None
        uncertainty_flags: List[str] = []

        # Handle both old (list of strings) and new (formatted list) risk formats
        if isinstance(risk_data, dict):
            risk_level = risk_data.get("risk_level") or risk_data.get("level") or "unknown"
            uncertainty_flags = list(clarify_raw_result.get("uncertainties", []) or [])
        elif isinstance(risk_data, list) and risk_data:
            # Extract level from first line if present
            first = str(risk_data[0])
            if "HIGH" in first.upper():
                risk_level = "high"
            elif "MODERATE" in first.upper():
                risk_level = "moderate"
            elif "LOW" in first.upper():
                risk_level = "low"
            else:
                risk_level = "unknown"
            uncertainty_flags = list(clarify_raw_result.get("uncertainties", []) or [])
        else:
            risk_level = "unknown"

        encounter = Encounter(
            id=str(uuid.uuid4()),
            patient_id=patient.id,
            doctor_id=self.doctor.id,
            created_at=created_at,
            patient_narrative=patient_narrative,
            clarify_raw_result=clarify_raw_result,
            risk_level=risk_level,
            uncertainty_flags=uncertainty_flags,
        )

        patient.encounters.append(encounter)
        # Keep encounters sorted by time ascending for natural history
        patient.encounters.sort(key=lambda e: e.created_at)
        self._save()
        return encounter


# ----------------------------------
# Google Cloud–friendly abstractions
# ----------------------------------

class AbstractCloudStorageBackend:
    """Interface for a Google Cloud–backed dashboard storage.

    This is intentionally minimal and not used by default. A production
    implementation could use:
    - Google Cloud Storage (JSON blobs per doctor/patient)
    - or Firestore / Cloud SQL for structured storage

    The Doctor Dashboard code only depends on the DashboardStorage
    interface above; swapping in a cloud-backed implementation should
    not require changes to agents or orchestrator.
    """

    def load_state(self) -> Dict[str, Any]:  # pragma: no cover - illustrative stub
        raise NotImplementedError("Implement using Google Cloud Storage / Firestore in production.")

    def save_state(self, state: Dict[str, Any]) -> None:  # pragma: no cover - illustrative stub
        raise NotImplementedError("Implement using Google Cloud Storage / Firestore in production.")
