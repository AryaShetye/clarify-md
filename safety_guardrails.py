"""
Safety Guardrails and Ethical Constraints for CLARIFY.MD
Ensures the system never diagnoses, suggests treatment, or replaces clinical judgment
"""
from typing import Dict, Any, List
import re


class SafetyGuardrails:
    """Safety and ethical constraints for CLARIFY.MD"""
    
    # Forbidden diagnostic terms
    DIAGNOSTIC_TERMS = [
        "diagnosis", "diagnose", "diagnosed", "diagnostic",
        "disease", "disorder", "syndrome", "condition",
        "pathology", "pathological", "pathologic"
    ]
    
    # Forbidden treatment terms
    TREATMENT_TERMS = [
        "prescribe", "prescription", "medication", "drug",
        "treatment", "treat", "therapy", "therapeutic",
        "surgery", "surgical", "procedure", "intervention"
    ]
    
    # Required disclaimers
    REQUIRED_DISCLAIMERS = [
        "This is a support tool, not a diagnostic system",
        "Always correlate with clinical examination",
        "Interpret in full clinical context"
    ]
    
    @staticmethod
    def check_forbidden_terms(text: str, category: str = "diagnostic") -> List[str]:
        """Check if text contains forbidden terms"""
        forbidden = SafetyGuardrails.DIAGNOSTIC_TERMS if category == "diagnostic" else SafetyGuardrails.TREATMENT_TERMS
        found = []
        
        text_lower = text.lower()
        for term in forbidden:
            if term in text_lower:
                found.append(term)
        
        return found
    
    @staticmethod
    def sanitize_output(text) -> str:
        """Remove or neutralize forbidden terms from output"""
        # Handle different input types
        if isinstance(text, dict):
            # If it's a dict, extract the text content
            sanitized = text.get("full_summary", text.get("raw_summary", text.get("clinical_impression", str(text))))
        elif isinstance(text, list):
            # If it's a list, join it
            sanitized = " ".join(str(item) for item in text)
        elif not isinstance(text, str):
            sanitized = str(text) if text else ""
        else:
            sanitized = text
        
        # Ensure sanitized is a string before regex operations
        if not isinstance(sanitized, str):
            sanitized = str(sanitized) if sanitized else ""
        
        # Replace diagnostic language with neutral alternatives
        replacements = {
            "diagnosis": "clinical impression",
            "diagnose": "assess",
            "disease": "condition",
            "disorder": "presentation",
            "pathology": "clinical finding"
        }
        
        for forbidden, replacement in replacements.items():
            sanitized = re.sub(
                re.escape(forbidden),
                replacement,
                sanitized,
                flags=re.IGNORECASE
            )
        
        return sanitized
    
    @staticmethod
    def validate_output(result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that output doesn't contain forbidden content"""
        violations = []
        
        # Extract text fields safely
        summary_data = result.get("summary", "")
        metaphor_data = result.get("metaphor", {})
        risk_data = result.get("risk", {})
        
        # Extract text from summary (handle dict structure)
        if isinstance(summary_data, dict):
            summary_text = summary_data.get("full_summary", summary_data.get("raw_summary", str(summary_data)))
        else:
            summary_text = str(summary_data) if summary_data else ""
        
        # Extract text from metaphor
        if isinstance(metaphor_data, dict):
            metaphor_text = metaphor_data.get("clinical_translation", "")
        else:
            metaphor_text = str(metaphor_data) if metaphor_data else ""
        
        # Extract text from risk
        if isinstance(risk_data, dict):
            risk_text = str(risk_data.get("rationale", ""))
        else:
            risk_text = str(risk_data) if risk_data else ""
        
        # Check all text fields
        text_fields = [summary_text, metaphor_text, risk_text]
        
        for field in text_fields:
            if isinstance(field, str) and field:
                diagnostic_violations = SafetyGuardrails.check_forbidden_terms(field, "diagnostic")
                treatment_violations = SafetyGuardrails.check_forbidden_terms(field, "treatment")
                
                if diagnostic_violations:
                    violations.extend([f"Diagnostic term found: {v}" for v in diagnostic_violations])
                if treatment_violations:
                    violations.extend([f"Treatment term found: {v}" for v in treatment_violations])
        
        # Sanitize summary if violations found (preserve dict structure)
        if violations:
            result["safety_violations"] = violations
            # Sanitize the summary, preserving structure if it's a dict
            if isinstance(summary_data, dict):
                # Sanitize the text fields within the dict
                if "full_summary" in summary_data and summary_data["full_summary"]:
                    summary_data["full_summary"] = SafetyGuardrails.sanitize_output(summary_data["full_summary"])
                if "raw_summary" in summary_data and summary_data["raw_summary"]:
                    summary_data["raw_summary"] = SafetyGuardrails.sanitize_output(summary_data["raw_summary"])
                if "structured" in summary_data and isinstance(summary_data["structured"], dict):
                    if "clinical_impression" in summary_data["structured"]:
                        summary_data["structured"]["clinical_impression"] = SafetyGuardrails.sanitize_output(
                            summary_data["structured"]["clinical_impression"]
                        )
                result["summary"] = summary_data
            else:
                result["summary"] = SafetyGuardrails.sanitize_output(summary_data)
        
        return result
    
    @staticmethod
    def add_disclaimers(result: Dict[str, Any]) -> Dict[str, Any]:
        """Add required safety disclaimers to output"""
        notes = result.get("notes", [])
        
        for disclaimer in SafetyGuardrails.REQUIRED_DISCLAIMERS:
            if disclaimer not in notes:
                notes.append(disclaimer)
        
        result["notes"] = notes
        return result
    
    @staticmethod
    def enforce_uncertainty_flagging(result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure uncertainties are always flagged.

        Additionally, if the narrative and risk rationale suggest the
        input contains **no clinical information at all** (e.g. a pure
        general-knowledge question), add an explicit uncertainty so the
        clinician is aware that CLARIFY.MD is operating outside of its
a typical input domain.
        """
        uncertainties = result.get("uncertainties", []) or []

        # If no uncertainties found, add default ones
        if not uncertainties:
            uncertainties = [
                "Symptom onset not clearly specified",
                "Severity and progression unclear",
                "Full clinical context required",
            ]

        # Heuristic: detect clearly non-clinical narratives from risk rationale.
        # This does NOT change risk level; it only surfaces an additional
        # uncertainty item for clinician awareness.
        risk = result.get("risk", {})
        rationale_text = ""
        if isinstance(risk, dict):
            rationale_text = str(risk.get("rationale", "") or "").lower()
        else:
            rationale_text = str(risk or "").lower()

        if (
            "no clinical information" in rationale_text
            or "contains absolutely no clinical information" in rationale_text
        ):
            msg = (
                "Narrative appears non-clinical (e.g. general knowledge or "
                "non-health-related content); confirm context before "
                "interpreting output."
            )
            if msg not in uncertainties:
                uncertainties.append(msg)

        result["uncertainties"] = uncertainties
        return result


def apply_safety_guardrails(result: Dict[str, Any]) -> Dict[str, Any]:
    """Apply all safety guardrails to result"""
    # Validate output
    result = SafetyGuardrails.validate_output(result)
    
    # Add disclaimers
    result = SafetyGuardrails.add_disclaimers(result)
    
    # Enforce uncertainty flagging
    result = SafetyGuardrails.enforce_uncertainty_flagging(result)
    
    return result

