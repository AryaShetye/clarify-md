from agents.base_agent import BaseAgent
from typing import Dict, Any


class WhatIfAgent(BaseAgent):
    """Agent that compares baseline vs hypothetical CLARIFY.MD outputs.

    It does NOT diagnose or recommend treatment. It only explains how
    the interpreted metaphors, emotional signals, risk level, and
    uncertainties differ between two narratives.

    Extended behavior for the patient What-If simulator:
    - Also generates *non-diagnostic* consequence explanations for each
      narrative, framed in terms of urgency perception and why timely
      clinical review may matter.
    - Consequences MUST be expressed with conditional language ("could",
      "might", "may") and must never mention specific diseases or
      treatments.
    """

    def __init__(self) -> None:
        system_prompt = """You are a What-If Comparison Agent for CLARIFY.MD.

Your task:
- Compare two CLARIFY.MD analyses of patient narratives:
  1) Baseline narrative
  2) Hypothetical / modified narrative

- Focus ONLY on:
  - Metaphor interpretation
  - Emotional biomarkers
  - Risk level and red flags
  - Uncertainties and missing information
  - High-level, non-diagnostic explanations of why these patterns
    could matter for how urgently a clinician might want to review
    the situation.

CRITICAL RULES:
- NEVER diagnose or suggest treatment.
- Do NOT name specific diseases, conditions, or procedures.
- Use neutral, patient-friendly language.
- Use conditional language like "could", "might", or "may" when you
  describe any possible consequences.
- Highlight where changes in wording increase or decrease *perceived*
  risk or clarity, but do NOT claim clinical outcomes.
- Always mention that final risk assessment belongs to the clinician.
"""
        super().__init__("What-If Comparison Agent", system_prompt)

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Context contains baseline and hypothetical CLARIFY.MD results.

        Expected structure (subset):
        {
            "baseline": {
                "metaphor": ...,
                "emotions": ...,
                "risk": {"risk_level", "red_flags", ...},
                "summary": ...,
            },
            "hypothetical": { ... }
        }
        """
        # Reason about the comparison first (for transparency)
        reasoning = self.reason(str(context))

        # 1) Comparative explanation
        comparison_prompt = f"""Compare these two CLARIFY.MD analyses.

BASELINE:
{context['baseline']}

HYPOTHETICAL:
{context['hypothetical']}

Explain in simple, non-diagnostic language:

1. How metaphor interpretations differ (if at all).
2. How emotional signals differ.
3. How risk level / red flags / uncertainties differ.
4. What this means for how clearly the story communicates urgency and
   why a clinician might see one description as needing more timely
   attention than the other.

Keep it short (2-3 paragraphs). End with a reminder that only a doctor
can make clinical judgments.
"""
        explanation = self.agent.generate(
            comparison_prompt,
            temperature=0.2,
            max_tokens=400,
        )

        # 2) Narrative-specific consequence explanations (non-diagnostic)
        baseline_consequence_prompt = f"""You are helping a patient understand, in
very general terms, why their baseline story might matter for how
quickly a clinician wants to review it.

BASELINE ANALYSIS (from CLARIFY.MD):
{context['baseline']}

Write 2-4 short bullet points describing **possible consequences** if
this situation is important and is not assessed promptly. Follow
STRICT rules:
- Do NOT name specific diseases, diagnoses, or treatments.
- Focus on categories like: symptoms could worsen, important warning
  signs might be missed, or delays could increase the need for urgent
  review.
- Use conditional language only ("could", "might", "may").
- End with one final sentence reminding the patient to contact a
  clinician or emergency services if symptoms are severe, new, or
  rapidly worsening.
"""
        baseline_consequences = self.agent.generate(
            baseline_consequence_prompt,
            temperature=0.2,
            max_tokens=300,
        )

        hypothetical_consequence_prompt = f"""Now do the same for the
hypothetical / modified story.

HYPOTHETICAL ANALYSIS (from CLARIFY.MD):
{context['hypothetical']}

Write 2-4 short bullet points describing **possible consequences** if
this situation is important and is not assessed promptly. Follow the
SAME STRICT rules:
- Do NOT name specific diseases, diagnoses, or treatments.
- Focus on categories like: symptoms could worsen, important warning
  signs might be missed, or delays could increase the need for urgent
  review.
- Use conditional language only ("could", "might", "may").
- End with one final sentence reminding the patient to contact a
  clinician or emergency services if symptoms are severe, new, or
  rapidly worsening.
"""
        hypothetical_consequences = self.agent.generate(
            hypothetical_consequence_prompt,
            temperature=0.2,
            max_tokens=300,
        )

        return {
            "reasoning": reasoning.get("reasoning", ""),
            "what_if_explanation": explanation,
            "baseline_consequences": baseline_consequences,
            "hypothetical_consequences": hypothetical_consequences,
        }
