"""
Enhanced Clinical Formatter for Agentic Outputs
Formats agentic agent results for clinician display
"""
from typing import Dict, Any, List
import re


def format_emotion_clinical(emotion_result: Dict[str, Any]) -> List[str]:
    """Format emotion agent results for clinical display"""
    # Handle case where emotion_result might be a list directly
    if isinstance(emotion_result, list):
        emotions = emotion_result
    else:
        emotions = emotion_result.get("emotions", [])
    
    if not emotions:
        return ["- No clinically significant emotional distress identified"]
    
    formatted = []
    for e in emotions:
        intensity = e.get("intensity", 0)
        emotion_name = e.get("emotion", "unknown")
        clinical_term = e.get("clinical_term", emotion_name)
        significance = e.get("significance", "medium")
        
        if intensity >= 0.7:
            level = "Marked"
            icon = "🔴"
        elif intensity >= 0.4:
            level = "Moderate"
            icon = "🟡"
        else:
            continue
        
        formatted.append(
            f"{icon} **{level} {clinical_term}** "
            f"(intensity: {intensity:.2f}, {significance} significance)"
        )
    
    return formatted or ["- No clinically significant emotional distress identified"]


def format_metaphor_clinical(metaphor_result: Dict[str, Any]) -> List[str]:
    """Format metaphor agent results for clinical display"""
    # Handle case where metaphor_result might be a string (legacy format)
    if isinstance(metaphor_result, str):
        return [f"- {metaphor_result}"] if metaphor_result else ["- No metaphorical language identified"]
    
    translation = metaphor_result.get("clinical_translation", "")
    metaphors = metaphor_result.get("metaphors", [])
    confidence = metaphor_result.get("confidence", "medium")
    uncertainties = metaphor_result.get("uncertainties", [])
    
    formatted = []
    
    if translation:
        confidence_icon = "🟢" if confidence == "high" else "🟡" if confidence == "medium" else "🟠"
        formatted.append(
            f"{confidence_icon} **Clinical Translation:** {translation} "
            f"({confidence} confidence)"
        )
    
    if metaphors:
        formatted.append(f"**Identified Metaphors:** {', '.join(metaphors)}")
    
    if uncertainties:
        formatted.append(f"**Uncertainties:** {', '.join(uncertainties)}")
    
    return formatted or ["- No metaphorical language identified"]


def format_risk_clinical(risk_result: Dict[str, Any]) -> List[str]:
    """Format risk agent results for clinical display"""
    # Handle case where risk_result might be a dict with just risk_level (legacy format)
    if not isinstance(risk_result, dict):
        risk_result = {"risk_level": str(risk_result) if risk_result else "low"}
    
    risk_level = risk_result.get("risk_level", "low")
    confidence = risk_result.get("confidence", "medium")
    red_flags = risk_result.get("red_flags", [])
    missing_info = risk_result.get("missing_info", [])
    rationale = risk_result.get("rationale", "")
    urgency_score = risk_result.get("urgency_score", 0.0)
    
    formatted = []
    
    # Risk level with icon
    risk_icons = {
        "high": "🔴",
        "moderate": "🟡",
        "low": "🟢"
    }
    icon = risk_icons.get(risk_level, "⚪")
    
    formatted.append(
        f"{icon} **{risk_level.upper()} Clinical Urgency** "
        f"(confidence: {confidence}, urgency score: {urgency_score:.2f})"
    )
    
    if rationale:
        formatted.append(f"*Rationale:* {rationale}")
    
    if red_flags:
        formatted.append(f"**🚨 Red Flags:** {', '.join(red_flags)}")
    
    if missing_info:
        formatted.append(f"**⚠️ Missing Information:** {', '.join(missing_info)}")
    
    return formatted


def clean_summary(text: str) -> str:
    """Clean and normalize clinical summary text"""
    if not text:
        return ""
    
    # Ensure text is a string
    if not isinstance(text, str):
        text = str(text)
    
    # Remove bullet/dot garbage
    text = re.sub(r"[•·\.]{2,}", " ", text)
    
    # Remove leftover structural labels / headings / meta lines
    forbidden = [
        # Section labels
        "Associated Emotional State",
        "Clinical Impression",
        "Uncertainties",
        "Information Gaps",
        "Context",
        "Emotional signals",
        "Risk assessment",
        "Associated E",
        "Presenting Description:",
        "Symptom Interpretation:",
        "Emotional State:",
        "Risk Assessment:",
        "Clinical Impression:",
        "Uncertainties:",
        "Notes for Clinician:",
        # Synthesis metadata / headings
        "Clinical Synthesis Note Date",
        "Clinical Synthesis Agent ID",
        "Clinical Synthesis Agent Analysis",
        "Reasoning and Synthesis",
        "## Clinical Synthesis Agent Analysis",
        "### Reasoning and Synthesis",
    ]

    for f in forbidden:
        text = text.replace(f, "")

    # If the summary still contains markdown-style headings, strip leading hashes
    text = re.sub(r"^#+\s*", "", text.strip())
    
    # Normalize medical tone
    replacements = {
        "the patient": "Patient",
        "The patient": "Patient",
        "reports": "describes",
        "appears to": "is noted to",
        "suggests": "is suggestive of"
    }
    
    for k, v in replacements.items():
        text = text.replace(k, v)
    
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


def format_for_clinician(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format agentic results for clinician display"""
    
    # Extract structured summary if available
    summary_data = result.get("summary", {})
    structured = {}
    full_summary = ""
    
    try:
        if isinstance(summary_data, dict):
            structured = summary_data.get("structured", {})
            if not isinstance(structured, dict):
                structured = {}
            
            # Try multiple ways to get the summary text
            full_summary = summary_data.get("full_summary", "")
            if not full_summary:
                full_summary = summary_data.get("raw_summary", "")
            if not full_summary and structured:
                full_summary = structured.get("clinical_impression", "")
            
            # Ensure full_summary is a string - handle all possible types
            if isinstance(full_summary, dict):
                # If it's still a dict, try to extract text or convert to string
                full_summary = full_summary.get("clinical_impression", str(full_summary))
            elif isinstance(full_summary, list):
                # If it's a list, join it
                full_summary = " ".join(str(item) for item in full_summary)
            elif not isinstance(full_summary, str):
                full_summary = str(full_summary) if full_summary else ""
        elif isinstance(summary_data, str):
            full_summary = summary_data
        elif isinstance(summary_data, list):
            full_summary = " ".join(str(item) for item in summary_data)
        else:
            full_summary = str(summary_data) if summary_data else ""
    except Exception as e:
        # Fallback if there's any error extracting summary
        try:
            full_summary = str(summary_data) if summary_data else "Summary unavailable"
        except:
            full_summary = "Summary unavailable"
        structured = {}
    
    # Format emotions
    emotions = format_emotion_clinical(result.get("emotions", {}))
    
    # Format metaphor
    metaphor = format_metaphor_clinical(result.get("metaphor", {}))
    
    # Format risk
    risk = format_risk_clinical(result.get("risk", {}))
    
    # Extract uncertainties and notes from structured summary
    # Ensure they are lists, not other types
    uncertainties = structured.get("uncertainties", [])
    if not isinstance(uncertainties, list):
        uncertainties = [str(uncertainties)] if uncertainties else []
    
    notes = structured.get("notes_for_clinician", [])
    if not isinstance(notes, list):
        notes = [str(notes)] if notes else []
    
    # Add default notes if none provided
    if not notes:
        notes = [
            "Correlate with vital signs and clinical examination",
            "Interpret in full clinical context",
            "This is a support tool, not a diagnostic system"
        ]
    
    # Clean summary - ensure it's a string
    try:
        if not isinstance(full_summary, str):
            full_summary = str(full_summary) if full_summary else ""
        cleaned_summary = clean_summary(full_summary) if full_summary else "Clinical summary unavailable."
    except Exception as e:
        # If cleaning fails, use raw summary or fallback
        cleaned_summary = str(full_summary) if full_summary else "Clinical summary unavailable."
    
    # If structured summary available, use it
    try:
        if structured and isinstance(structured, dict):
            clinical_impression = structured.get("clinical_impression")
            if clinical_impression:
                if isinstance(clinical_impression, str):
                    cleaned_summary = clean_summary(clinical_impression)
                else:
                    cleaned_summary = clean_summary(str(clinical_impression))
    except Exception:
        pass  # Keep the cleaned_summary from above
    
    return {
        "patient_voice": result.get("patient_voice", ""),
        "emotions": emotions,
        "metaphor": metaphor,
        "risk": risk,
        "summary": cleaned_summary,
        "uncertainties": uncertainties,
        "notes": notes,
        "agent_reasoning": result.get("agent_reasoning", {}),
        "metadata": result.get("processing_metadata", {})
    }


