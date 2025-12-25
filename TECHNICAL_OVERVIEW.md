# CLARIFY.MD: Technical Overview

## System Architecture: Ownership and Responsibilities

This document clarifies what CLARIFY.MD implements versus what external components (Gemini API) provide.

---

## Architecture Ownership

### CLARIFY.MD Implements

1. **Multi-Agent Orchestration**
   - Parallel agent execution coordination
   - Agent collaboration logic
   - Result integration patterns
   - Error handling and fallback mechanisms

2. **RAG System (Medical Ontology)**
   - Structured medical concept retrieval
   - Metaphor-to-clinical-term mapping
   - Emotional biomarker classification
   - Risk indicator matching
   - **Not LLM-generated**: Uses structured dictionaries, extensible to vector databases

3. **Safety Guardrails (Deterministic)**
   - Forbidden term detection (regex-based, not LLM)
   - Output sanitization logic
   - Uncertainty enforcement
   - Required disclaimer injection
   - **Critical**: High-risk escalation uses deterministic rules, not LLM judgment

4. **Clinical Formatting**
   - Structured output generation
   - Visual risk coding (color-coded urgency levels)
   - Patient voice preservation
   - Uncertainty presentation
   - Agent reasoning transparency display

5. **Agent Separation Logic**
   - Bounded responsibility enforcement
   - Bias prevention through architectural boundaries
   - Interpretability through agent reasoning transparency
   - Collaboration patterns that prevent unsafe synthesis

### Gemini API Provides

1. **Reasoning Engine** (within agent boundaries)
   - Language understanding for patient narratives
   - Step-by-step reasoning for metaphor identification
   - Emotion detection and intensity quantification
   - Risk assessment reasoning (for non-critical cases)
   - Structured summary generation

2. **Clinical Knowledge**
   - Medical terminology understanding
   - Concept matching capabilities
   - Text generation for structured outputs

**Key Distinction:** Gemini is used as a reasoning engine *within* agents. CLARIFY.MD provides the architecture, safety, orchestration, and clinical logic that makes the system safe, interpretable, and clinically appropriate.

---

## Agent Architecture: Bounded Responsibilities

### Base Agent Pattern

All agents inherit from `BaseAgent`, which provides:

```python
class BaseAgent:
    - reason(input_text)      # Step-by-step reasoning (uses Gemini)
    - use_rag(query, category) # Medical ontology retrieval (CLARIFY.MD)
    - collaborate(other_results) # Agent collaboration (CLARIFY.MD)
    - execute(input_text)     # Agent-specific logic (CLARIFY.MD)
```

**Ownership:**
- `reason()`: Uses Gemini for reasoning, but CLARIFY.MD structures the reasoning prompt
- `use_rag()`: CLARIFY.MD implementation (structured ontology, not LLM)
- `collaborate()`: CLARIFY.MD implementation (agent interaction logic)
- `execute()`: CLARIFY.MD implementation (agent-specific processing)

### Individual Agent Responsibilities

#### 1. Metaphor Translation Agent

**CLARIFY.MD Implementation:**
- Semantic mapping logic (metaphor → clinical term)
- RAG retrieval from medical ontology
- Confidence scoring algorithm
- Uncertainty flagging logic
- **Bounded scope**: Translation only, no diagnosis

**Gemini Role:**
- Reasoning: Identifies metaphors in text
- Reasoning: Matches metaphors to clinical concepts
- Generation: Produces clinical translation text

**Why Separate Agent:**
Prevents metaphor interpretation from being contaminated by emotional or risk assessment biases. Enables independent validation of translation accuracy.

#### 2. Emotional Biomarker Agent

**CLARIFY.MD Implementation:**
- Intensity quantification algorithm (0.0-1.0 scale)
- Clinical terminology mapping (emotion → clinical term)
- Signal filtering (threshold: 0.4 for clinical significance)
- Significance classification (high/medium/low)
- **Bounded scope**: Signal extraction, not pathology assignment

**Gemini Role:**
- Reasoning: Detects emotional states in text
- Reasoning: Quantifies emotional intensity
- Generation: Produces clinical terminology for emotions

**Why Separate Agent:**
Ensures emotional signals are extracted independently, preventing emotional bias from downgrading physical risk assessment. Critical for safety.

#### 3. Risk & Red-Flag Agent

**CLARIFY.MD Implementation:**
- **Hybrid risk assessment**: Deterministic rules + AI reasoning
- High-risk escalation logic (deterministic, not LLM):
  - Chest pain → HIGH risk (rule-based)
  - Trauma + inability to bear weight → HIGH risk (rule-based)
  - Loss of consciousness → HIGH risk (rule-based)
- Missing information identification
- Red flag extraction with clinical context
- **Bounded scope**: Urgency assessment, not diagnosis

**Gemini Role:**
- Reasoning: Assesses risk in ambiguous/non-critical cases
- Reasoning: Identifies red flags in nuanced scenarios
- Generation: Produces risk rationale

**Why Separate Agent:**
**Critical safety feature**: High-risk symptoms cannot be left solely to LLM reasoning. Deterministic overrides ensure critical symptoms are never missed, even if LLM reasoning fails.

#### 4. Clinical Synthesis Agent

**CLARIFY.MD Implementation:**
- Integration logic (combines all agent findings)
- Structured output generation (non-diagnostic format)
- Patient voice separation (preserves original narrative)
- Uncertainty aggregation (collects uncertainties from all agents)
- **Bounded scope**: Summary generation, never diagnosis or treatment

**Gemini Role:**
- Reasoning: Synthesizes findings into structured summary
- Generation: Produces clinical note format

**Why Separate Agent:**
Prevents unsafe synthesis where one agent's error propagates. Enables interpretability through agent reasoning transparency. Allows safety guardrails to validate final output.

---

## Safety Architecture: Deterministic Overrides

### Multi-Layer Safety

1. **Prompt-Level** (Gemini)
   - System prompts explicitly forbid diagnosis/treatment
   - Agent-specific safety constraints

2. **Agent-Level** (CLARIFY.MD)
   - Bounded responsibilities prevent unsafe synthesis
   - Agent separation prevents bias propagation

3. **Output-Level** (CLARIFY.MD)
   - Safety guardrails validate outputs (deterministic, not LLM)
   - Forbidden term detection (regex-based)
   - Sanitization logic

4. **UI-Level** (CLARIFY.MD)
   - Disclaimers displayed prominently
   - Uncertainty highlighted visually
   - Risk level color coding

### Deterministic Risk Overrides

**Critical safety feature:** High-risk escalation uses deterministic rules, not LLM judgment.

```python
# Pseudocode: Risk Agent Logic
def assess_risk(patient_text):
    # Deterministic high-risk detection (CLARIFY.MD)
    if contains_high_risk_indicators(patient_text):
        return HIGH_RISK  # Rule-based, not LLM
    
    # AI reasoning for ambiguous cases (Gemini)
    ai_assessment = gemini_reason(patient_text)
    
    # CLARIFY.MD logic: Never downgrade from high risk
    if ai_assessment < HIGH_RISK:
        return ai_assessment
    else:
        return HIGH_RISK  # Safety override
```

**Why Deterministic Overrides:**
- LLMs may miss critical symptoms in ambiguous narratives
- Emotional content may bias risk assessment downward
- Deterministic rules ensure high-risk symptoms are never missed
- Provides safety net independent of LLM reasoning

---

## RAG System: Medical Ontology

### Current Implementation (Structured Dictionary)

```python
medical_ontology = {
    "metaphors": {
        "pressure/tightness": ["tension", "cephalalgia", "pressure sensation"],
        "hollow/empty": ["palpitations", "chest discomfort"],
        # ... more mappings
    },
    "emotional_biomarkers": {
        "fear": ["anxiety-related distress", "apprehension"],
        # ... more mappings
    },
    "risk_indicators": {
        "high": ["chest pain", "shortness of breath", "trauma"],
        # ... more mappings
    }
}
```

**Ownership:** CLARIFY.MD implementation (structured knowledge, not LLM-generated)

**Future Enhancement:** Vector database (Pinecone, Weaviate) for semantic search, but retrieval logic remains CLARIFY.MD implementation.

---

## Agent Collaboration Pattern

### Parallel Execution
1. All analysis agents run simultaneously (CLARIFY.MD orchestration)
2. Each agent reasons independently (Gemini within agent)
3. Results collected in parallel (CLARIFY.MD)

### Collaboration Phase
1. Agents share findings (CLARIFY.MD collaboration logic)
2. Agents refine based on others' results (optional, CLARIFY.MD controlled)
3. Synthesis agent integrates (CLARIFY.MD integration logic)

### Safety Validation
1. Safety guardrails applied (CLARIFY.MD deterministic validation)
2. Forbidden terms detected (regex-based, not LLM)
3. Uncertainties enforced (CLARIFY.MD logic)
4. Final output formatted (CLARIFY.MD formatting)

---

## Why Not Single-Prompt LLM?

### Limitations of Single-Prompt Approach

1. **Hallucination Risk**
   - Single models may synthesize incorrect interpretations confidently
   - No architectural boundaries to prevent error propagation
   - No interpretability to validate reasoning

2. **Bias Amplification**
   - Emotional content may contaminate physical risk assessment
   - No separation between emotion extraction and risk assessment
   - Bias may propagate through single reasoning path

3. **Uncertainty Hiding**
   - Models may present interpretations without flagging gaps
   - No explicit uncertainty surfacing mechanism
   - False confidence from incomplete information

4. **Lack of Interpretability**
   - Black-box reasoning prevents clinical validation
   - No way to understand how conclusions were reached
   - No agent reasoning transparency

### Agent Separation Benefits

1. **Prevents Hallucination**
   - Bounded responsibilities prevent error propagation
   - Each agent's reasoning is independently validatable
   - Synthesis agent can detect inconsistencies

2. **Enables Interpretability**
   - Each agent's reasoning is transparent
   - Clinicians can validate each agent's analysis
   - Agent reasoning displayed in UI

3. **Allows Deterministic Overrides**
   - Critical risk assessment uses rules, not LLM judgment
   - Safety net independent of LLM reasoning
   - High-risk symptoms never missed

4. **Prevents Bias**
   - Emotional signals extracted independently
   - Risk assessment uses deterministic overrides
   - No contamination between agent responsibilities

5. **Improves Reliability**
   - Agent collaboration refines findings
   - Multiple agents validate each other
   - Synthesis agent integrates with uncertainty flagging

---

## Code Ownership Summary

### CLARIFY.MD Owns
- `orchestrator_v2.py`: Multi-agent orchestration
- `agents/base_agent.py`: Agent architecture, RAG, collaboration
- `safety_guardrails.py`: Deterministic safety validation
- `formatter/clinical_formatter_v2.py`: Output formatting
- `gemini_config.py`: Gemini API configuration (but usage patterns are CLARIFY.MD)

### Gemini API Provides
- Reasoning engine (within agent boundaries)
- Language understanding
- Clinical knowledge
- Text generation

**Key Point:** Gemini is a tool used by CLARIFY.MD agents. CLARIFY.MD provides the architecture, safety, orchestration, and clinical logic that makes the system safe and interpretable.

---

## Conclusion

CLARIFY.MD is not an LLM wrapper. It is a thoughtfully engineered clinical AI system with:
- **Architectural ownership**: Multi-agent orchestration, RAG system, safety guardrails
- **Safety ownership**: Deterministic overrides, uncertainty surfacing, bias prevention
- **Clinical ownership**: Structured output, patient voice preservation, non-diagnostic boundaries

Gemini provides reasoning capabilities within agent boundaries. CLARIFY.MD provides everything else that makes the system safe, interpretable, and clinically appropriate.

