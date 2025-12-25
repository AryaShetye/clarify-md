# 🏗️ CLARIFY.MD - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (app_v2.py)                  │
│  - Patient input interface                                   │
│  - Real-time progress indicators                            │
│  - Visual risk coding                                       │
│  - Agent reasoning transparency                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Agentic Orchestrator (orchestrator_v2.py)      │
│  - Coordinates multi-agent execution                        │
│  - Manages agent collaboration                              │
│  - Applies safety guardrails                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Metaphor    │ │  Emotion     │ │  Risk        │
│  Agent       │ │  Agent       │ │  Agent       │
│              │ │              │ │              │
│  - Reasoning │ │  - Reasoning │ │  - Reasoning │
│  - RAG       │ │  - RAG       │ │  - RAG       │
│  - Translate │ │  - Extract   │ │  - Assess    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  Synthesis Agent │
              │  - Integrates    │
              │  - Structures    │
              │  - Summarizes    │
              └────────┬─────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Safety Guardrails (safety_guardrails.py)          │
│  - Validates outputs                                        │
│  - Sanitizes forbidden terms                                │
│  - Adds disclaimers                                         │
│  - Enforces uncertainty flagging                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│      Clinical Formatter (clinical_formatter_v2.py)           │
│  - Formats for clinician display                           │
│  - Adds visual indicators                                   │
│  - Structures output                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Streamlit UI  │
              │   (Display)     │
              └─────────────────┘
```

## Agent Architecture

### Base Agent Pattern

All agents inherit from `BaseAgent` which provides:

1. **Reasoning Capability**: `reason()` method for step-by-step thinking
2. **RAG Integration**: `use_rag()` method for ontology retrieval
3. **Collaboration**: `collaborate()` method for agent-to-agent communication
4. **Gemini Integration**: Uses Google Gemini API via `GeminiAgent`

### Individual Agents

#### 1. Metaphor Translation Agent
- **Input**: Patient narrative with metaphorical language
- **Process**:
  1. Reason about metaphors in text
  2. Retrieve relevant medical concepts (RAG)
  3. Translate metaphors to clinical terminology
  4. Flag uncertainties
- **Output**: Clinical translation with confidence and uncertainties

#### 2. Emotional Biomarker Agent
- **Input**: Patient narrative
- **Process**:
  1. Reason about emotional states
  2. Retrieve emotional biomarker mappings (RAG)
  3. Extract emotions with intensity scores
  4. Map to clinical terminology
- **Output**: List of emotions with intensity, clinical terms, significance

#### 3. Risk Assessment Agent
- **Input**: Patient narrative
- **Process**:
  1. Reason about clinical urgency
  2. Retrieve risk indicators (RAG)
  3. Assess risk level (low/moderate/high)
  4. Identify red flags and missing information
- **Output**: Risk level, confidence, red flags, missing info, rationale

#### 4. Clinical Synthesis Agent
- **Input**: Combined context from all agents
- **Process**:
  1. Reason about synthesis approach
  2. Integrate all findings
  3. Generate structured clinical summary
  4. Extract structured components
- **Output**: Structured clinical note with all sections

## Data Flow

### Processing Pipeline

1. **Input Stage**
   - Patient narrative entered in Streamlit UI
   - Text validation and preprocessing

2. **Parallel Agent Execution**
   - All three analysis agents run simultaneously
   - Each agent performs:
     - Reasoning phase
     - RAG retrieval
     - Analysis execution
   - Results collected in parallel

3. **Context Assembly**
   - Orchestrator combines agent results
   - Creates synthesis context
   - Prepares for synthesis agent

4. **Synthesis Stage**
   - Synthesis agent receives full context
   - Generates structured summary
   - Extracts structured components

5. **Safety Validation**
   - Safety guardrails applied
   - Forbidden terms checked
   - Disclaimers added
   - Uncertainties enforced

6. **Formatting Stage**
   - Results formatted for display
   - Visual indicators added
   - Risk level color coding
   - Confidence scores displayed

7. **Output Stage**
   - Formatted results displayed in UI
   - Agent reasoning available (expandable)
   - Metadata shown

## Key Design Patterns

### 1. Singleton Pattern
- `ModelRegistry` (legacy) - Single instance of models
- `AgenticOrchestrator` - Single instance via `get_orchestrator()`

### 2. Strategy Pattern
- Each agent implements `BaseAgent` interface
- Agents can be swapped or extended

### 3. Template Method Pattern
- `BaseAgent.reason()` provides template
- Subclasses implement `execute()` method

### 4. Facade Pattern
- `orchestrator_v2.py` provides simple interface
- Hides complexity of multi-agent coordination

### Technology Stack

### Core
- **Python 3.8+**: Backend language
- **Google Gemini API**: Agentic reasoning engine inside agents (free tier, AI Studio compatible)
- **Streamlit**: Web UI framework (Doctor Dashboard + CLARIFY.MD panel)

### Google-first Extensions (conceptual hooks)
- **Vertex AI / Vertex AI Search (optional)**: Future-ready path to replace the
  local ontology in `get_medical_ontology()` with a managed medical index.
- **Google Cloud Storage / Firestore (optional)**: Can back the `DashboardStorage`
  interface for patient/encounter history instead of local JSON.
- **Google Drive / Colab (optional)**: Training and experimentation notebooks
  can load/export datasets (e.g., `data/clarify_md_dataset.json`) via Drive for
  fine-tuning emotion/risk models.

### Key Libraries
- `google-generativeai`: Gemini API client
- `streamlit`: UI framework
- `python-dotenv`: Environment management
- `json`: Data serialization
- `re`: Text processing

## RAG Implementation

### Medical Ontology Structure
```python
{
    "metaphors": {
        "pressure/tightness": ["tension", "cephalalgia", ...],
        "hollow/empty": ["palpitations", "chest discomfort", ...],
        ...
    },
    "emotional_biomarkers": {
        "fear": ["anxiety-related distress", ...],
        ...
    },
    "risk_indicators": {
        "high": ["chest pain", "shortness of breath", ...],
        ...
    }
}
```

### RAG Process
1. Query text analyzed for key terms
2. Ontology searched for matching concepts
3. Top matches retrieved (top 5)
4. Matches used to inform agent reasoning

### Future Enhancement
- Vector database (Pinecone, Weaviate)
- Semantic search
- Embedding-based retrieval

## Safety Architecture

### Multi-Layer Safety

1. **Prompt-Level**: System prompts explicitly forbid diagnosis/treatment
2. **Agent-Level**: Each agent has safety constraints in prompts
3. **Output-Level**: Safety guardrails validate and sanitize outputs
4. **UI-Level**: Disclaimers and warnings displayed prominently

### Safety Mechanisms

- **Term Detection**: Scans for forbidden diagnostic/treatment terms
- **Sanitization**: Replaces forbidden terms with neutral alternatives
- **Disclaimer Enforcement**: Adds required disclaimers to all outputs
- **Uncertainty Flagging**: Ensures uncertainties are always highlighted

## Performance Considerations

### Optimization Strategies

1. **Parallel Processing**: Agents run simultaneously
2. **Caching**: Agent instances reused (singleton)
3. **API Efficiency**: Batch requests where possible
4. **Streaming**: Progress indicators for user feedback

### Scalability

- **Horizontal**: Add more agents easily
- **Vertical**: Optimize individual agents
- **API Limits**: Respect Google Gemini rate limits
- **Error Handling**: Graceful degradation on API failures

## Extension Points

### Easy Extensions

1. **New Agents**: Inherit from `BaseAgent`
2. **New RAG Sources**: Extend ontology or add vector DB
3. **New Formatters**: Create new formatter classes
4. **New UI Views**: Add Streamlit components

### Integration Points

1. **EHR Integration**: API wrapper around orchestrator
2. **Voice Input**: Add speech-to-text preprocessing
3. **Multi-language**: Add language-specific agents
4. **Batch Processing**: Process multiple narratives

## Security Considerations

### Current Implementation
- API key stored in `.env` (not committed)
- No patient data persistence
- No database connections

### Production Considerations
- HIPAA compliance required
- Encrypted data storage
- Audit logging
- Access controls
- Data retention policies

---

**Architecture designed for hackathon → production scalability**
