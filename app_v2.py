"""
CLARIFY.MD - Enhanced Agentic AI Streamlit App

This file now exposes **two** tightly-related experiences:
1. Doctor Dashboard (non-EMR):
   - Single-clinician context
   - Lightweight patient list & encounter history (local/demo only)
   - Timestamped, read-only CLARIFY.MD interpretations per encounter
2. CLARIFY.MD Playground:
   - Original hackathon view for single narratives

Architectural constraints respected:
- No changes to agent classes or `run_clarify` function signature.
- CLARIFY.MD remains the USP: "Clinical Language Interpretation" panel
  embedded inside each patient encounter view.
- Gemini remains a **bounded reasoning engine inside agents**, not a
  monolithic LLM wrapper for the entire app.
"""
import streamlit as st
from orchestrator_v2 import run_clarify, run_what_if
from formatter.clinical_formatter_v2 import format_for_clinician
from dashboard_models import DashboardStorage
from firebase_auth import get_firebase_client
import time
from datetime import datetime
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="CLARIFY.MD - Agentic Clinical Interpreter",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for hackathon polish
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .patient-voice-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .clinical-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .risk-high {
        background: #fee;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 5px;
    }
    .risk-moderate {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
    }
    .risk-low {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
    }
    .agent-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🧠 CLARIFY.MD</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Agentic AI Clinical Language Interpreter | '
    'Translating Patient Voice into Clinical Clarity</div>',
    unsafe_allow_html=True
)

# Sidebar with role selection and (optional) Firebase login
with st.sidebar:
    st.header("ℹ️ About CLARIFY.MD")
    st.markdown("""
    **CLARIFY.MD** is a clinical language interpreter, not an EMR and not a
    diagnostic system.

    System ownership (CLARIFY.MD):
    - Agent orchestration & collaboration
    - Risk escalation logic with deterministic overrides
    - Uncertainty detection & surfacing
    - Safety guardrails & output normalization

    Gemini's role (within agents only):
    - Language understanding
    - Bounded reasoning
    - Structured text generation

    **⚠️ Safety:**
    - High-risk symptoms (e.g., chest pain, dyspnea, focal neurology) are
      NEVER downgraded by model output; deterministic rules enforce
      escalation.
    - Always correlate with clinical examination and local pathways.
    """)

    st.markdown("---")
    role = st.radio("Role", ["Doctor", "Patient"], index=0)

    # Variables used for routing later
    view = None
    patient_mode = None

    if role == "Doctor":
        st.markdown("### Doctor Login (Firebase)")
        client = get_firebase_client()
        if client is None:
            st.info("Firebase not configured (no FIREBASE_API_KEY). Running in demo mode as a local doctor.")
            if "doctor_id" not in st.session_state:
                st.session_state.doctor_id = "doctor-1"
                st.session_state.doctor_email = "demo@clarify.local"
        else:
            if "doctor_id" in st.session_state and st.session_state.get("doctor_email"):
                st.success(f"Logged in as: {st.session_state.doctor_email}")
                public_doctor_id = st.session_state.doctor_id
                st.markdown(f"**Your Doctor ID (share with patients):** `{public_doctor_id}`")
                if st.button("Log out"):
                    st.session_state.pop("doctor_id", None)
                    st.session_state.pop("doctor_email", None)
                    st.rerun()
            else:
                with st.form("doctor_login_form"):
                    email = st.text_input("Email")
                    password = st.text_input("Password", type="password")
                    submitted_login = st.form_submit_button("Sign in")
                if submitted_login:
                    try:
                        user = client.sign_in_with_email_and_password(email, password)
                        st.session_state.doctor_id = user.uid
                        st.session_state.doctor_email = user.email
                        st.success(f"Logged in as: {user.email}")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        st.markdown("---")
        st.markdown("### Views")
        view = st.radio(
            "Navigation",
            ["Doctor Dashboard", "CLARIFY.MD Playground"],
            index=0,
        )

        st.markdown("---")
        st.markdown("### 🎯 Agentic Features")
        st.markdown("""
        - ✅ Multi-agent orchestration (metaphor, emotion, risk, synthesis)
        - ✅ Visual risk indicators & uncertainty surfacing
        - ✅ Agent reasoning transparency (expanders)
        - ✅ RAG over medical ontology (Vertex AI Search–ready)
        """)

    else:  # Patient role
        st.markdown("### Patient Tools")
        st.info("You can explore CLARIFY.MD privately or share your story with a doctor.")

        # Simple consent / start-session gate for patients
        if not st.session_state.get("patient_authenticated"):
            agreed = st.checkbox("I understand this is not a diagnostic or treatment tool.")
            start = st.button("Start as patient", disabled=not agreed)
            if start:
                st.session_state.patient_authenticated = True
                st.rerun()
        else:
            patient_mode = st.radio(
                "Choose a mode",
                ["Share my story with my doctor", "Private What-If simulator"],
                index=0,
            )

# Initialize dashboard storage (local + in-memory) only for doctor role
doctor_storage_key = st.session_state.get("doctor_id", "doctor-1") if 'role' in locals() and role == "Doctor" else None
if 'role' in locals() and role == "Doctor":
    if "dashboard_storage" not in st.session_state or getattr(st.session_state.dashboard_storage, "path", "").find(doctor_storage_key) == -1:
        st.session_state.dashboard_storage = DashboardStorage(path=f"dashboard_state_{doctor_storage_key}.json")


def maybe_transcribe_audio(audio_file) -> str:
    """Best-effort speech-to-text helper.

    For this prototype, this function is a soft stub: if a local
    speech-to-text library is available (e.g. whisper), it can be
    plugged in here. Otherwise we simply inform the user and return
    an empty string, allowing manual input to proceed.
    """
    try:
        import whisper  # type: ignore
    except Exception:
        st.info("Speech input is not fully configured on this instance. Please type your narrative manually.")
        return ""

    import tempfile
    import os

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.read())
        tmp_path = tmp.name
    model = whisper.load_model("tiny")
    result = model.transcribe(tmp_path)
    os.remove(tmp_path)
    return result.get("text", "").strip()


def render_clarify_panel(patient_text: str, raw_result: dict) -> None:
    """Embed the CLARIFY.MD Clinical Language Interpretation panel.

    This is a pure VIEW layer that wraps the existing agentic pipeline
    (`run_clarify` + `format_for_clinician`). It does not alter agent
    behavior or safety logic.
    """
    formatted = format_for_clinician(raw_result)

    st.markdown("## 🧠 Clinical Language Interpretation")

    # Two-column layout
    col_left, col_right = st.columns([1, 1])

    # LEFT: Patient Voice + agent metadata
    with col_left:
        st.markdown('<div class="patient-voice-box">', unsafe_allow_html=True)
        st.markdown("### 🗣️ Patient Voice")
        st.markdown(f"*{formatted['patient_voice']}*")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### 🤖 Agentic Processing")
        metadata = formatted.get("metadata", {})
        st.markdown(f"""
        - **Agents Used:** {metadata.get('agents_used', 4)}
        - **RAG Enabled:** {'✅' if metadata.get('rag_enabled') else '❌'}
        - **Collaboration:** {'✅' if metadata.get('collaboration_enabled') else '❌'}
        - **Deterministic Risk Overrides:** {'✅' if metadata.get('deterministic_risk_overrides') else '❌'}
        """)

    # RIGHT: Clinical interpretation sections
    with col_right:
        st.markdown('<div class="clinical-box">', unsafe_allow_html=True)
        st.markdown("### 🧠 Clinical Interpretation")

        st.markdown("#### 💓 Emotional Signals")
        for e in formatted["emotions"]:
            st.markdown(e)

        st.markdown("---")

        st.markdown("#### 🧩 Symptom Interpretation")
        for m in formatted["metaphor"]:
            st.markdown(m)

        st.markdown("---")

        st.markdown("#### 🚨 Clinical Risk Indicators")
        risk_level = formatted.get("risk", [""])[0] if formatted.get("risk") else ""

        if "HIGH" in str(risk_level).upper():
            st.markdown('<div class="risk-high">', unsafe_allow_html=True)
        elif "MODERATE" in str(risk_level).upper():
            st.markdown('<div class="risk-moderate">', unsafe_allow_html=True)
        else:
            st.markdown('<div class="risk-low">', unsafe_allow_html=True)

        for r in formatted["risk"]:
            st.markdown(r)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Full-width sections
    st.markdown("---")
    st.markdown("### 📄 Clinical Summary")
    st.info(formatted["summary"])

    col_u, col_n = st.columns(2)
    with col_u:
        if formatted["uncertainties"]:
            st.markdown("### ⚠️ Uncertainties & Information Gaps")
            for u in formatted["uncertainties"]:
                st.warning(f"• {u}")
    with col_n:
        if formatted["notes"]:
            st.markdown("### 📋 Notes for Clinician")
            for n in formatted["notes"]:
                st.info(f"• {n}")

    # Agent reasoning (transparent, read-only)
    with st.expander("🔬 Agent Reasoning & Transparency"):
        reasoning = formatted.get("agent_reasoning", {})
        if reasoning:
            st.markdown("#### 🧩 Metaphor Agent Reasoning")
            st.text(reasoning.get("metaphor", "No reasoning available"))

            st.markdown("#### 💓 Emotion Agent Reasoning")
            st.text(reasoning.get("emotion", "No reasoning available"))

            st.markdown("#### 🚨 Risk Agent Reasoning")
            st.text(reasoning.get("risk", "No reasoning available"))

            st.markdown("#### 📄 Synthesis Agent Reasoning")
            st.text(reasoning.get("synthesis", "No reasoning available"))
        else:
            st.info("Agent reasoning not available in this view")


# ----------------------
# Doctor Dashboard view
# ----------------------

def render_doctor_dashboard() -> None:
    storage: DashboardStorage = st.session_state.dashboard_storage

    st.markdown("### 👩‍⚕️ Doctor Dashboard (Non-EMR)")
    st.caption(
        "Single-clinician view with patient list, encounter history, and "
        "embedded CLARIFY.MD Clinical Language Interpretation panel."
    )

    col_patients, col_detail = st.columns([1, 2])

    # LEFT: Patient list & creation
    with col_patients:
        st.subheader("Patients")
        patients = storage.list_patients()

        # Show compact list with demographics for quick scanning
        for p in patients[:5]:
            demo_bits = []
            if p.age is not None:
                demo_bits.append(f"{p.age}y")
            if p.weight_kg is not None:
                demo_bits.append(f"{p.weight_kg}kg")
            if p.blood_group:
                demo_bits.append(p.blood_group)
            subtitle = ", ".join(demo_bits) if demo_bits else "No demographics recorded"
            st.caption(f"• {p.display_name} ({subtitle})")

        patient_options = ["➕ Add New Patient"] + [p.display_name for p in patients]
        selected_label = st.selectbox("Select patient", patient_options)

        if selected_label == "➕ Add New Patient":
            with st.form("create_patient_form", clear_on_submit=True):
                name = st.text_input("Patient name", "Sample Patient")
                col_a, col_b = st.columns(2)
                with col_a:
                    age = st.number_input("Age (years)", min_value=0, max_value=120, step=1, value=30)
                    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.5, value=70.0)
                with col_b:
                    blood_group = st.selectbox(
                        "Blood group",
                        ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                        index=0,
                    )
                notes = st.text_area("Clinical context / notes (optional)", height=80)
                created = st.form_submit_button("Create patient")
            if created:
                patient = storage.create_patient(
                    display_name=name,
                    notes=notes,
                    age=int(age) if age else None,
                    weight_kg=float(weight) if weight else None,
                    blood_group=blood_group or None,
                )
                st.success(f"Created patient: {patient.display_name}")
                st.rerun()
            selected_patient = None
        else:
            selected_patient = next((p for p in patients if p.display_name == selected_label), None)

    # RIGHT: Encounter history + CLARIFY.MD panel
    with col_detail:
        if not selected_patient:
            st.info("Select a patient on the left or create a new one to begin.")
            return

        st.subheader(f"Encounter History – {selected_patient.display_name}")

        # Quick patient snapshot for clinician convenience
        demo_bits = []
        if selected_patient.age is not None:
            demo_bits.append(f"Age: {selected_patient.age}y")
        if selected_patient.weight_kg is not None:
            demo_bits.append(f"Weight: {selected_patient.weight_kg}kg")
        if selected_patient.blood_group:
            demo_bits.append(f"Blood group: {selected_patient.blood_group}")
        if demo_bits:
            st.caption(" | ".join(demo_bits))

        # New encounter form
        with st.form("new_encounter_form"):
            narrative = st.text_area(
                "Patient narrative",
                height=160,
                placeholder="Enter the patient's description in their own words...",
            )
            audio_file = st.file_uploader(
                "Optional: upload an audio recording (speech input)",
                type=["wav", "mp3", "m4a"],
                key="doctor_audio_upload",
            )
            if audio_file is not None:
                transcript = maybe_transcribe_audio(audio_file)
                if transcript:
                    narrative = transcript
            submitted = st.form_submit_button("Run Clinical Language Interpretation with CLARIFY.MD")

        if submitted and narrative.strip():
            progress = st.progress(0)
            status = st.empty()
            steps = [
                "Initializing agentic pipeline...",
                "🧩 Metaphor Agent analyzing...",
                "💓 Emotion Agent extracting...",
                "🚨 Risk Agent evaluating (with deterministic overrides)...",
                "📄 Synthesis Agent generating structured summary...",
                "✨ Applying safety guardrails & formatting...",
            ]
            for i, step in enumerate(steps):
                status.text(step)
                progress.progress((i + 1) / len(steps))
                time.sleep(0.2)

            raw_result = run_clarify(narrative)
            encounter = storage.add_encounter(selected_patient.id, narrative, raw_result)

            progress.empty()
            status.empty()
            st.success(
                f"Encounter saved at {encounter.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')} "
                f"(risk: {encounter.risk_level.upper()})"
            )

        # Show encounter list
        if selected_patient.encounters:
            st.markdown("#### Previous Encounters")
            for e in reversed(selected_patient.encounters):
                badge = e.risk_level.upper() if e.risk_level else "UNKNOWN"
                ts = e.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                st.markdown(f"- **{ts}** – Risk: `{badge}` – Narrative preview: _{e.patient_narrative[:80]}..._")
        else:
            st.info("No encounters recorded yet for this patient.")

        # Patient-level summary across narrative history
        if selected_patient.encounters:
            st.markdown("---")
            st.markdown("### 🧾 Patient Narrative History Overview")
            total = len(selected_patient.encounters)
            highest_risk = max(
                (e.risk_level or "low" for e in selected_patient.encounters),
                key=lambda rl: {"low": 0, "moderate": 1, "high": 2}.get(rl, 0),
            )
            last_ts = selected_patient.encounters[-1].created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            st.info(
                f"Total encounters: {total} | Highest recorded risk: {highest_risk.upper()} | "
                f"Last encounter: {last_ts}"
            )

        # Show most recent encounter with embedded CLARIFY.MD panel + follow-up refinement
        if selected_patient.encounters:
            latest = selected_patient.encounters[-1]
            st.markdown("---")
            st.markdown("### 🧠 Latest Encounter – Clinical Language Interpretation")
            render_clarify_panel(latest.patient_narrative, latest.clarify_raw_result)

            # Follow-up questions for clinician, derived from uncertainties/missing info
            with st.expander("🧾 Follow-up questions to refine analysis"):
                result = latest.clarify_raw_result
                risk = result.get("risk", {}) if isinstance(result, dict) else {}
                missing_info = []
                if isinstance(risk, dict):
                    mi = risk.get("missing_info", []) or []
                    if isinstance(mi, list):
                        missing_info = [str(x) for x in mi]
                    else:
                        missing_info = [str(mi)]
                uncertainties = result.get("uncertainties", []) or []
                if not isinstance(uncertainties, list):
                    uncertainties = [str(uncertainties)]

                followup_prompts = []
                for mi in missing_info:
                    followup_prompts.append(f"Please clarify: {mi}.")
                for u in uncertainties:
                    followup_prompts.append(f"Add clinical context for: {u}.")

                if followup_prompts:
                    st.markdown("#### Suggested follow-up prompts")
                    for q in followup_prompts:
                        st.markdown(f"- {q}")
                else:
                    st.caption("No specific follow-up prompts generated; you may still add notes below.")

                # If any patient documents were uploaded for this patient, expose them here
                from pathlib import Path as _Path  # local alias to avoid confusion
                if 'doctor_storage_key' in globals() and doctor_storage_key:
                    doc_dir = _Path("patient_documents") / doctor_storage_key / selected_patient.id
                    if doc_dir.exists():
                        with st.expander("📎 Patient documents"):
                            for f in doc_dir.iterdir():
                                with open(f, "rb") as fh:
                                    st.download_button(f"Download {f.name}", fh, file_name=f.name)

                notes_key = f"followup_notes_{selected_patient.id}_{latest.id}"
                followup_notes = st.text_area(
                    "Clinician follow-up notes (will be appended for refined analysis)",
                    key=notes_key,
                    height=120,
                )
                refine = st.button(
                    "Run refined Clinical Language Interpretation",
                    key=f"refine_{selected_patient.id}_{latest.id}",
                )

                if refine and followup_notes.strip():
                    combined_text = (
                        latest.patient_narrative
                        + "\n\nClinician follow-up notes (structured context):\n"
                        + followup_notes.strip()
                    )
                    with st.spinner("Running refined CLARIFY.MD analysis..."):
                        refined_result = run_clarify(combined_text)
                    st.markdown("---")
                    st.markdown("#### 🔁 Refined Interpretation (with clinician follow-up context)")
                    render_clarify_panel(combined_text, refined_result)


# ----------------------
# Patient Portal views
# ----------------------

def render_patient_share_with_doctor() -> None:
    """Patient-facing flow: share narrative + documents with a specific doctor.

    This uses a Doctor ID (doctor's internal id) to select the correct
    DashboardStorage file and stores a new patient and encounter for
    that doctor only.
    """
    st.markdown("### 🩺 Share my story with my doctor")
    st.info("Use this mode when your doctor has given you a Doctor ID and wants to review your narrative.")

    doctor_code = st.text_input("Doctor ID (provided by your doctor)")
    name = st.text_input("Your name")
    col_a, col_b = st.columns(2)
    with col_a:
        age = st.number_input("Age (years)", min_value=0, max_value=120, step=1)
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.5)
    with col_b:
        blood_group = st.selectbox("Blood group", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], index=0)

    narrative = st.text_area("Describe your symptoms or story in your own words", height=200)
    audio_file = st.file_uploader(
        "Optional: upload an audio recording (speech input)",
        type=["wav", "mp3", "m4a"],
        key="patient_share_audio",
    )
    if audio_file is not None:
        transcript = maybe_transcribe_audio(audio_file)
        if transcript:
            narrative = transcript

    docs = st.file_uploader(
        "Upload any relevant documents (lab reports, discharge summaries, images)",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="patient_share_docs",
    )

    submitted = st.button("Share with my doctor using CLARIFY.MD")

    if submitted:
        if not doctor_code.strip():
            st.error("Please enter a Doctor ID.")
            return
        if not name.strip():
            st.error("Please enter your name.")
            return
        if not narrative.strip():
            st.error("Please enter or record your narrative.")
            return

        # In this prototype, Doctor ID maps directly to a dashboard_state file.
        storage = DashboardStorage(path=f"dashboard_state_{doctor_code}.json")
        patient = storage.create_patient(
            display_name=name,
            notes=None,
            age=int(age) if age else None,
            weight_kg=float(weight) if weight else None,
            blood_group=blood_group or None,
        )
        result = run_clarify(narrative)
        encounter = storage.add_encounter(patient.id, narrative, result)

        # Save documents to disk so the doctor can access them later
        if docs:
            doc_dir = Path("patient_documents") / doctor_code / patient.id
            doc_dir.mkdir(parents=True, exist_ok=True)
            for f in docs:
                (doc_dir / f.name).write_bytes(f.read())

        short_patient_id = patient.id.split("-")[0]
        st.success(
            f"Your story has been shared with Doctor `{doctor_code}`. "
            f"Your Patient ID for this doctor is `{short_patient_id}`."
        )
        st.markdown("---")
        st.markdown("### 🔍 How your doctor will see this encounter")
        render_clarify_panel(narrative, result)


def render_patient_what_if_simulator() -> None:
    """Patient-facing privacy-preserving simulator.

    Narratives and documents here are NOT stored or associated with any
    doctor or patient id.
    """
    st.markdown("### 🧪 Private What-If Simulator")
    st.info("This simulation is private. Narratives here are not stored and are not visible to any doctor.")

    baseline = st.text_area("Baseline story (how you would normally describe it)", height=160)
    hypothetical = st.text_area(
        "What-if version (try a different way of describing the same situation)",
        height=160,
        help="Optional: change wording, include/exclude details, or emphasize different aspects.",
    )

    audio_file = st.file_uploader(
        "Optional: upload an audio recording for the baseline story (speech input)",
        type=["wav", "mp3", "m4a"],
        key="patient_sim_audio",
    )
    if audio_file is not None:
        transcript = maybe_transcribe_audio(audio_file)
        if transcript:
            baseline = transcript

    if st.button("Run private CLARIFY.MD What-If analysis"):
        if not baseline.strip():
            st.error("Please enter or record a baseline narrative.")
            return

        if not hypothetical.strip():
            # If no hypothetical is provided, just run a single baseline analysis
            result = run_clarify(baseline)
            st.markdown("---")
            st.markdown("#### Baseline interpretation")
            render_clarify_panel(baseline, result)

            # High-level, non-diagnostic consequences for the single baseline story
            try:
                single_context = {
                    "baseline": {
                        "metaphor": result.get("metaphor", {}),
                        "emotions": result.get("emotions", {}),
                        "risk": result.get("risk", {}),
                        "summary": result.get("summary", {}),
                    },
                    "hypothetical": {
                        "metaphor": {},
                        "emotions": {},
                        "risk": {},
                        "summary": {},
                    },
                }
                # Reuse What-If agent via orchestrator to get consequence text for baseline only
                from orchestrator_v2 import get_orchestrator

                comparison_only = get_orchestrator().what_if_agent.execute(single_context)
                baseline_consequences = comparison_only.get("baseline_consequences")
                if baseline_consequences:
                    st.markdown("---")
                    st.markdown("#### 🔍 Possible consequences based on this story (non-diagnostic)")
                    st.info(baseline_consequences)
            except Exception:
                # Soft-fail: consequences are a UX enhancement only
                pass

            st.warning(
                "This result is **not** stored or shared. If you want your doctor to see an interpretation, "
                "use the 'Share my story with my doctor' mode."
            )
            return

        # Full what-if pipeline using agents + Gemini
        with st.spinner("Running private CLARIFY.MD What-If analysis..."):
            what_if_result = run_what_if(baseline, hypothetical)

        st.markdown("---")
        st.markdown("#### Baseline interpretation")
        render_clarify_panel(baseline, what_if_result["baseline"])

        st.markdown("---")
        st.markdown("#### What-if interpretation")
        render_clarify_panel(hypothetical, what_if_result["hypothetical"])

        # Show non-diagnostic consequence explanations for each narrative
        comparison = what_if_result.get("comparison", {})
        baseline_consequences = comparison.get("baseline_consequences")
        hypothetical_consequences = comparison.get("hypothetical_consequences")

        if baseline_consequences or hypothetical_consequences:
            st.markdown("---")
            st.markdown("#### 🔍 Possible consequences based on each story (non-diagnostic)")
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**Baseline story**")
                st.info(baseline_consequences or "No additional consequence explanation available.")
            with cols[1]:
                st.markdown("**What-if story**")
                st.info(hypothetical_consequences or "No additional consequence explanation available.")

        st.markdown("---")
        st.markdown("#### 🧠 What-If Explanation (agentic comparison)")
        comparison = what_if_result["comparison"]
        st.info(comparison.get("what_if_explanation", "No comparison available."))

        st.warning(
            "These simulations are **not** stored or shared and do not constitute diagnosis or treatment. "
            "Only your clinician can interpret this in full clinical context."
        )

def render_patient_portal(mode: str) -> None:
    if mode == "Share my story with my doctor":
        render_patient_share_with_doctor()
    else:
        render_patient_what_if_simulator()


# ---------------------------
# Legacy playground view (v2)
# ---------------------------

def render_clarify_playground() -> None:
    st.markdown("### 📝 Patient Narrative Input")
    default_text = st.session_state.get(
        "playground_patient_text",
        "I feel like a rubber band inside my head is being pulled tighter and tighter. I'm afraid it's going to snap.",
    )
    patient_text = st.text_area(
        "Enter patient narrative",
        height=200,
        value=default_text,
        help="Enter the patient's description of their symptoms or concerns",
        key="playground_patient_text",
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button(
            "🔍 Clarify Patient Language",
            type="primary",
            use_container_width=True,
            key="playground_process_button",
        )

    if process_button and patient_text.strip():
        # Show processing progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Simulate agent processing steps
        steps = [
            "Initializing agentic AI system...",
            "🧩 Metaphor Translation Agent analyzing...",
            "💓 Emotional Biomarker Agent extracting...",
            "🚨 Risk Assessment Agent evaluating...",
            "📄 Clinical Synthesis Agent generating summary...",
            "✨ Formatting results for clinician...",
        ]

        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(0.3)  # Simulate processing

        # Run actual processing
        status_text.text("Processing with Google Gemini AI (within agents)...")
        try:
            raw_result = run_clarify(patient_text)
            # Debug: Check raw_result structure
            if not isinstance(raw_result, dict):
                st.error(f"Unexpected result type: {type(raw_result)}")
                st.stop()

            progress_bar.progress(1.0)
            status_text.text("✅ Analysis complete!")
            time.sleep(0.5)

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

            st.markdown("---")
            st.markdown("## 📊 Clinical Interpretation Results")
            render_clarify_panel(patient_text, raw_result)

            # Demo features highlight
            st.markdown("---")
            st.success("""
            🎉 **Hackathon Features Demonstrated:**
            - ✅ Multi-agent orchestration with Google Gemini
            - ✅ Real-time processing with progress indicators
            - ✅ Visual risk level coding
            - ✅ Confidence scoring and uncertainty highlighting
            - ✅ Agent reasoning transparency
            - ✅ RAG-enhanced medical ontology matching
            - ✅ Deterministic high-risk escalation independent of model output
            """)

        except Exception as e:
            st.error(f"❌ Error processing patient narrative: {str(e)}")
            st.info("Please check your GOOGLE_API_KEY in the .env file")
            import traceback
            error_traceback = traceback.format_exc()
            st.code(
                f"Error details: {e}\n\nFull traceback:\n{error_traceback}",
                language="python",
            )
            st.expander("🔍 Debug Information").write(
                f"**Error Type:** {type(e).__name__}\n\n**Full Traceback:**\n```\n{error_traceback}\n```"
            )

    elif process_button:
        st.warning("⚠️ Please enter a patient narrative to analyze.")

    # Example narratives for demo
    with st.expander("📚 Example Patient Narratives (Click to use)"):
        examples = [
            {
                "title": "Headache with Metaphor",
                "text": "I feel like a rubber band inside my head is being pulled tighter and tighter. I'm afraid it's going to snap. The pressure has been building all day.",
            },
            {
                "title": "Chest Discomfort",
                "text": "My chest feels hollow, like there is a bird fluttering around in an empty cage. I can't catch my breath and I'm really scared.",
            },
            {
                "title": "High Risk - Trauma",
                "text": "I slipped in the shower and landed hard on my hip. Now I can't put any weight on it at all. The pain is excruciating.",
            },
            {
                "title": "Emotional Distress",
                "text": "Everything feels foggy and I can't think straight. I'm panicking about everything and I don't know what's wrong with me.",
            },
        ]

        for example in examples:
            if st.button(f"Use: {example['title']}", key=f"example_{example['title']}"):
                st.session_state.playground_patient_text = example["text"]
                st.rerun()


# -----------------
# Main view routing
# -----------------

if 'role' in locals() and role == "Doctor":
    # Require successful doctor login before showing any doctor views
    if "doctor_id" not in st.session_state or not st.session_state.get("doctor_email"):
        st.info("Please log in as a doctor using the sidebar to access the dashboard and CLARIFY.MD playground.")
    else:
        if view == "Doctor Dashboard":
            render_doctor_dashboard()
        else:
            render_clarify_playground()
else:
    # Patient portal views operate without touching doctor storage
    if not st.session_state.get("patient_authenticated"):
        st.info(
            "Please start as a patient using the sidebar (review the note and click 'Start as patient') "
            "before using the patient tools."
        )
    else:
        render_patient_portal(patient_mode or "Private What-If simulator")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 2rem;'>"
    "🧠 CLARIFY.MD | Built with Google Gemini Agentic AI (reasoning engine inside agents) | "
    "Not a diagnostic or treatment tool | For clinical support only"
    "</div>",
    unsafe_allow_html=True,
)

