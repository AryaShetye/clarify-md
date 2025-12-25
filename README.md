# CLARIFY.MD: Agentic Clinical Language Interpreter

## Executive Summary

**CLARIFY.MD** is an agentic AI system that addresses the critical "translation gap" between emotionally expressed patient narratives and structured clinical reasoning. Patients describe symptoms using metaphors, emotional language, and ambiguity—patterns that can obscure clinical red flags and introduce diagnostic bias. CLARIFY.MD performs semantic interpretation and signal extraction to bridge this gap while preserving patient voice and maintaining strict non-diagnostic boundaries.

**This is not a medical scribe, chatbot, or LLM wrapper.** CLARIFY.MD implements a multi-agent architecture with bounded responsibilities, deterministic safety overrides, and explicit uncertainty surfacing—architectural decisions that distinguish it from single-prompt language models.

---

## Problem Statement: The Translation Gap

Medical errors often stem from failures in listening. Patients communicate symptoms using:
- **Metaphorical language** ("rubber band in my head", "bird fluttering in empty cage")
- **Emotional expression** (fear, panic, confusion) that may mask or amplify physical symptoms
- **Ambiguity** that requires clinical interpretation, not transcription

Traditional approaches (medical scribes, chatbots) transcribe or summarize but do not perform semantic interpretation. A single-prompt LLM approach is insufficient because:
1. **Hallucination risk**: Single models may confidently synthesize incorrect clinical interpretations
2. **Bias amplification**: Emotional content may downgrade physical risk assessment
3. **Uncertainty hiding**: Models may present interpretations without flagging information gaps
4. **Lack of interpretability**: Black-box reasoning prevents clinical validation

---

## System Architecture: What CLARIFY.MD Implements

### Doctor Dashboard + CLARIFY.MD USP (Clinical Language Interpretation)

The current evolution adds a **Doctor Dashboard** around the existing
CLARIFY.MD agentic core. The dashboard is **not** an EMR – it is a
lightweight, single-clinician view that organizes patient narratives
and timestamped CLARIFY.MD interpretations.

- **Doctor context (single clinician):** Non-identifying `Doctor` entity.
- **Patient list:** In-memory / JSON-backed `Patient` records.
- **Encounter history:** `Encounter` objects with timestamps, narrative,
  and full CLARIFY.MD raw output.
- **USP Panel:** Each encounter embeds the CLARIFY.MD
  🧠 *Clinical Language Interpretation* panel as a read-only view.

The dashboard does **not** add diagnosis, treatment, billing, or
prescribing. It simply surfaces the existing agentic interpretation in
clinician workflow.

### Multi-Agent Architecture with Bounded Responsibilities

CLARIFY.MD uses a **multi-agent orchestration pattern** where each agent has a **bounded, specialized responsibility**. This architectural choice prevents hallucination, enables interpretability, and allows deterministic safety overrides.

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                           Doctor Dashboard (Streamlit)                        │
│  - Single clinician context (non-EMR)                                         │
│  - Patient list + encounter history                                           │
│  - Each encounter embeds CLARIFY.MD "Clinical Language Interpretation" panel  │
│                               │                                               │
│                               ▼                                               │
│                     Patient Narrative Input (per encounter)                   │
│                               ▼                                               │
│                    ┌──────────────────────────────────────┐                   │
│                    │  Agentic Orchestrator               │                   │
│                    │  (CLARIFY.MD Implementation)        │                   │
│                    │  - Parallel agent execution         │                   │
│                    │  - Agent collaboration logic        │                   │
│                    │  - Safety & deterministic overrides │                   │
│                    └──────────────┬──────────────────────┘                   │
│                                   │                                          │
│                  ┌────────────────┼────────────────┐                          │
│                  │                │                │                          │
│                  ▼                ▼                ▼                          │
│              ┌──────────┐    ┌──────────┐    ┌──────────┐                    │
│              │ Metaphor │    │ Emotion  │    │   Risk   │                    │
│              │  Agent   │    │  Agent   │    │  Agent   │                    │
│              │ (CLARIFY │    │ (CLARIFY │    │ (CLARIFY │                    │
│              │  logic + │    │  logic + │    │  logic + │                    │
│              │  Gemini) │    │  Gemini) │    │  Gemini) │                    │
│              └────┬─────┘    └────┬─────┘    └────┬─────┘                    │
│                   │              │              │                             │
│                   └──────────────┼──────────────┘                             │
│                                  │                                            │
│                                  ▼                                            │
│                          ┌──────────────┐                                     │
│                          │  Synthesis   │                                     │
│                          │   Agent      │                                     │
│                          │ (CLARIFY +   │                                     │
│                          │  Gemini)     │                                     │
│                          └───────┬──────┘                                     │
│                                  │                                            │
│                                  ▼                                            │
│                    ┌──────────────────────────────────────┐                   │
│                    │  Safety Guardrails (CLARIFY.MD)      │                   │
│                    │  - Forbidden term detection          │                   │
│                    │  - Uncertainty enforcement           │                   │
│                    │  - Deterministic risk overrides      │                   │
│                    └──────────────────────────────────────┘                   │
│                                  │                                            │
│                                  ▼                                            │
│                    ┌──────────────────────────────────────┐                   │
│                    │  Clinical Formatter (CLARIFY.MD)     │                   │
│                    │  - Structured output generation      │                   │
│                    │  - Visual risk coding                │                   │
│                    │  - Patient voice preservation        │                   │
│                    └──────────────────────────────────────┘                   │
│                                  │                                            │
│                                  ▼                                            │
│                     Doctor Dashboard – Encounter View                          │
│                     (read-only CLARIFY.MD interpretation)                      │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities: What Each Agent Does

#### 1. Metaphor Translation Agent
**CLARIFY.MD Implementation:**
- Semantic mapping from figurative language to clinical terminology
- RAG-based medical ontology retrieval (not LLM-generated)
- Confidence scoring and uncertainty flagging
- **Bounded scope**: Translation only, no diagnosis

**Gemini Role:** Reasoning engine for metaphor identification and clinical concept matching

**Why Separate Agent:** Prevents metaphor interpretation from being contaminated by emotional or risk assessment biases

#### 2. Emotional Biomarker Agent
**CLARIFY.MD Implementation:**
- Quantifies emotional states as clinical signals (intensity 0.0-1.0)
- Maps emotions to clinical terminology (anxiety-related distress, low mood, etc.)
- Filters low-signal emotions (< 0.4 threshold)
- **Bounded scope**: Signal extraction, not pathology assignment

**Gemini Role:** Reasoning engine for emotion detection and intensity quantification

**Why Separate Agent:** Ensures emotional signals are extracted independently, preventing emotional bias from downgrading physical risk

#### 3. Risk & Red-Flag Agent
**CLARIFY.MD Implementation:**
- **Hybrid approach**: Rule-based deterministic overrides + AI reasoning
- High-risk escalation logic (chest pain, trauma, loss of consciousness) uses deterministic rules, not LLM judgment
- Missing information identification
- Red flag extraction with clinical context
- **Bounded scope**: Urgency assessment, not diagnosis

**Gemini Role:** Reasoning engine for nuanced risk assessment in ambiguous cases

**Why Separate Agent:** Critical risk assessment cannot be left solely to LLM reasoning. Deterministic overrides ensure high-risk symptoms are never missed.

#### 4. Clinical Synthesis Agent
**CLARIFY.MD Implementation:**
- Integrates findings from all agents
- Produces structured, non-diagnostic clinical language
- Separates patient voice from clinical interpretation
- Highlights uncertainties explicitly
- **Bounded scope**: Summary generation, never diagnosis or treatment

**Gemini Role:** Reasoning engine for structured summary generation

**Why Separate Agent:** Prevents unsafe synthesis where one agent's error propagates. Enables interpretability through agent reasoning transparency.

---

## What Gemini Provides vs. What CLARIFY.MD Implements

### Gemini's Role (Reasoning Engine)
- **Language understanding**: Interprets patient narratives
- **Reasoning capability**: Step-by-step analysis within agent boundaries
- **Clinical knowledge**: Medical terminology and concept matching
- **Text generation**: Structured output formatting

### CLARIFY.MD's Implementation (System Architecture)
- **Multi-agent orchestration**: Coordinates parallel execution, manages agent collaboration
- **RAG system**: Medical ontology retrieval (structured knowledge, not LLM-generated)
- **Safety guardrails**: Forbidden term detection, uncertainty enforcement, deterministic risk overrides
- **Clinical formatting**: Structured output generation, visual risk coding, patient voice preservation
- **Agent separation logic**: Prevents bias propagation, enables interpretability
- **Uncertainty surfacing**: Explicit identification and presentation of information gaps

**Key Distinction:** Gemini provides reasoning *within* agents. CLARIFY.MD provides the architecture, safety, orchestration, and clinical logic that makes the system safe and interpretable.

---

### Safety & Clinical Responsibility

### Non-Diagnostic Architecture
CLARIFY.MD is explicitly architected as a **support tool**, not a diagnostic system:
- **No diagnosis**: System never diagnoses conditions
- **No treatment**: System never suggests treatments
- **Bounded scope**: Each agent has limited, non-diagnostic responsibilities
- **Uncertainty surfacing**: Information gaps are explicitly identified, not hidden

### Uncertainty Handling
Unlike systems that hide uncertainty, CLARIFY.MD **surfaces uncertainty explicitly**:
- Missing information is actively identified and presented
- Confidence scores are displayed for all interpretations
- Ambiguities are flagged, not resolved
- Information gaps are listed for clinician review

### Emotional Bias Prevention
**Critical safety feature:** Emotional content does not downgrade physical risk assessment.
- Emotional signals are extracted independently
- Risk assessment uses deterministic overrides for high-risk symptoms
- Emotional intensity does not influence physical symptom interpretation
- Patient anxiety about symptoms is preserved as clinical signal, not dismissed

### Deterministic High-Risk Escalation (System-Owned)
High-risk escalation is **never** left to Gemini alone:
- CLARIFY.MD applies rule-based overrides for critical phrases such as:
  - "chest pain", "shortness of breath", "difficulty breathing"
  - focal neurological language (e.g., face drooping, slurred speech,
    weakness on one side)
  - loss of consciousness ("fainted", "passed out", "blackout")
- These rules can only **escalate** risk to HIGH; model output cannot
  downgrade below HIGH when such phrases are present.
- The override is implemented in `AgenticOrchestrator._apply_deterministic_risk_overrides`
  and surfaced to the UI via processing metadata.

### Safety Guardrails (Deterministic, Not LLM-Based)
- **Forbidden term detection**: Scans outputs for diagnostic/treatment language
- **Sanitization**: Replaces forbidden terms with neutral alternatives
- **Uncertainty enforcement**: Ensures uncertainties are always flagged
- **Required disclaimers**: Adds clinical context reminders automatically

---

## Novelty: Differentiation from Existing Solutions

### Not a Medical Scribe
- **Scribes transcribe**: CLARIFY.MD interprets semantically
- **Scribes summarize**: CLARIFY.MD extracts signals and flags uncertainties
- **Scribes preserve structure**: CLARIFY.MD translates metaphors and quantifies emotions

### Not a Chatbot
- **Chatbots respond**: CLARIFY.MD interprets and structures
- **Chatbots may diagnose**: CLARIFY.MD explicitly does not diagnose
- **Chatbots hide uncertainty**: CLARIFY.MD surfaces uncertainty explicitly

### Not an LLM Wrapper
- **Wrappers prompt LLMs**: CLARIFY.MD implements multi-agent architecture
- **Wrappers trust LLM output**: CLARIFY.MD applies deterministic safety overrides
- **Wrappers are black-box**: CLARIFY.MD provides agent reasoning transparency

### What CLARIFY.MD Does Uniquely
1. **Semantic interpretation**: Translates metaphors to clinical language while preserving patient voice
2. **Signal extraction**: Quantifies emotional states as clinical biomarkers
3. **Hybrid risk assessment**: Combines AI reasoning with deterministic overrides
4. **Uncertainty surfacing**: Explicitly identifies and presents information gaps
5. **Agent separation**: Prevents bias propagation through architectural boundaries

---

## Why Agentic AI: Architectural Justification

### Single-Prompt LLM Limitations
A single-prompt approach fails for this problem because **clinical language
interpretation is not a single-step generation problem**, especially when
wrapped in a Doctor Dashboard:
1. **Hallucination risk**: Single models may synthesize incorrect interpretations confidently
2. **Bias amplification**: Emotional content may contaminate physical risk assessment
3. **Uncertainty hiding**: Models may present interpretations without flagging gaps
4. **Lack of interpretability**: Black-box reasoning prevents clinical validation

### Agent Separation Benefits
1. **Prevents hallucination**: Bounded responsibilities prevent error propagation
2. **Enables interpretability**: Each agent's reasoning is transparent and can be
   inspected per-encounter in the Doctor Dashboard.
3. **Allows deterministic overrides**: Critical risk assessment uses rules, not LLM
   judgment, with explicit high-risk escalation for chest pain, dyspnea, and
   neurological red flags.
4. **Prevents bias**: Emotional signals extracted independently from risk assessment
   ensure that distress never suppresses physical risk.
5. **Improves reliability**: Agent collaboration refines findings without unsafe
   synthesis; the dashboard simply *organizes* these outputs, it does not merge
   or reinterpret them.

### Agent Collaboration Pattern
Agents collaborate to refine findings, but **synthesis is controlled**:
- Each agent reasons independently first
- Agents share findings for refinement
- Synthesis agent integrates with explicit uncertainty flagging
- Safety guardrails validate final output

---

## Impact: Decoding the Human Side of Illness

### Clinical Communication Gap
Medical errors often stem from failures in listening. Patients use metaphors and emotions that clinicians may misinterpret or filter out. CLARIFY.MD addresses this by:
- **Preserving patient voice**: Original narrative displayed alongside clinical interpretation
- **Translating metaphors**: Figurative language converted to clinical terminology
- **Quantifying emotions**: Emotional states extracted as clinical signals
- **Flagging uncertainties**: Information gaps explicitly identified

### Reduced Risk of "Lost in Translation"
- **Metaphor interpretation**: Prevents clinical miscommunication from figurative language
- **Emotional signal extraction**: Ensures emotional distress is recognized as clinical signal
- **Risk escalation**: Deterministic overrides ensure high-risk symptoms are never missed
- **Uncertainty surfacing**: Prevents false confidence from incomplete information

### Clinical Empathy
- **Patient dignity**: Original voice preserved alongside clinical translation
- **Context preservation**: Emotional and metaphorical context maintained
- **Non-pathologizing**: Emotions quantified as signals, not assigned as pathology
- **Clinician support**: System supports, never replaces, clinical judgment

---

## Technical Implementation

### Technology Stack
- **Google Gemini API**: Used as reasoning engine within agents (not as the system itself)
- **Python 3.8+**: Backend orchestration and agent implementation
- **Streamlit**: Clinical interface for Doctor Dashboard + CLARIFY.MD panel
- **RAG System**: Structured medical ontology for metaphor translation (not LLM-generated)
- **Dashboard Storage**: Local JSON + in-memory cache (demo); can be swapped
  for Google Cloud Storage / Firestore via `DashboardStorage` interface.

### Key Components
- **`orchestrator_v2.py`**: Multi-agent orchestration logic (CLARIFY.MD implementation)
- **`agents/base_agent.py`**: Base agent class with reasoning, RAG, and collaboration patterns
- **`safety_guardrails.py`**: Deterministic safety validation (not LLM-based)
- **`formatter/clinical_formatter_v2.py`**: Structured output generation and visual risk coding
- **`gemini_config.py`**: Gemini API configuration (reasoning engine only)

---

## Usage

### Quick Start
1. Install dependencies: `pip install -r requirements_v2.txt`
2. Set `GOOGLE_API_KEY` in `.env` file
3. Run: `streamlit run app_v2.py`

### Doctor Dashboard Workflow
1. Open the **Doctor Dashboard** view in the sidebar.
2. Create a lightweight patient record (display name + optional notes).
3. For each encounter:
   - Paste the patient's narrative in their own words.
   - Run **Clinical Language Interpretation (CLARIFY.MD)**.
   - Review the structured interpretation, risk level, and uncertainties.
4. Previous encounters remain visible as a timestamped history with
   read-only CLARIFY.MD outputs.

### CLARIFY.MD Playground Workflow
1. Switch to the **CLARIFY.MD Playground** view.
2. Paste any patient narrative (or use presets).
3. Inspect agent reasoning and safety guardrails without creating patients.

### Clinical Workflow
1. **Input**: Patient narrative (metaphorical, emotional, ambiguous)
2. **Processing**: Multi-agent analysis with reasoning transparency
3. **Output**: 
   - Patient voice (preserved)
   - Clinical interpretation (metaphor translation, emotional signals, risk assessment)
   - Uncertainties (explicitly flagged)
   - Notes for clinician (contextual reminders)

---

## Safety & Ethics: Non-Negotiable Constraints

**CLARIFY.MD is a support tool, not a diagnostic system.**

- ❌ **NO diagnosis**: System never diagnoses conditions
- ❌ **NO treatment**: System never suggests treatments
- ✅ **Uncertainty flagging**: Always highlights information gaps
- ✅ **Clinician authority**: Always defers to clinical judgment
- ✅ **Patient dignity**: Preserves patient voice and context
- ✅ **Deterministic safety**: High-risk escalation uses rules, not LLM judgment

**Always correlate findings with clinical examination. Interpret in full clinical context. Clinician remains the decision authority.**

---

## Project Structure

```
clarify-md/
├── app_v2.py                 # Streamlit UI: Doctor Dashboard + CLARIFY.MD playground
├── orchestrator_v2.py        # Multi-agent orchestration (CLARIFY.MD)
├── safety_guardrails.py      # Deterministic safety validation (CLARIFY.MD)
├── dashboard_models.py       # Doctor/Patient/Encounter models + local storage (CLARIFY.MD)
├── google_integrations.py    # Google-first stubs (Vertex AI Search, Drive ingestion)
├── gemini_config.py          # Gemini API config (reasoning engine inside agents)
├── agents/
│   ├── base_agent.py         # Agent architecture (CLARIFY.MD)
│   ├── metaphor_agent_v2.py  # Semantic mapping (CLARIFY.MD + Gemini)
│   ├── emotion_agent_v2.py   # Signal extraction (CLARIFY.MD + Gemini)
│   ├── risk_agent_v2.py      # Hybrid risk assessment (CLARIFY.MD + Gemini)
│   └── synthesis_agent_v2.py # Structured synthesis (CLARIFY.MD + Gemini)
└── formatter/
    └── clinical_formatter_v2.py # Output formatting (CLARIFY.MD)
```

---

## Acknowledgments

- **Google Gemini API**: Provides reasoning engine capabilities within agent boundaries
- **Medical ontology concepts**: Derived from clinical literature (RAG system)
- **Clinical safety principles**: Based on healthcare AI best practices

---

**CLARIFY.MD: Decoding the human side of illness, preserving patient voice, supporting clinical judgment.**

