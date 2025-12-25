import streamlit as st
from orchestrator import run_clarify
from formatter.clinical_formatter import format_for_clinician

st.set_page_config(layout="wide")
st.title("🧠 CLARIFY.MD")

st.caption(
    "Clinical language interpretation support system. "
    "Not a diagnostic or treatment tool."
)

patient_text = st.text_area(
    "Patient Narrative",
    height=180,
    placeholder="Describe what you’re feeling..."
)

if st.button("Clarify"):
    with st.spinner("Interpreting patient language..."):
        raw_result = run_clarify(patient_text)
        formatted = format_for_clinician(raw_result)

    col1, col2 = st.columns(2)

    # LEFT: Patient Voice
    with col1:
        st.subheader("🗣️ Patient Voice")
        # st.write(formatted["patient_voice"])

    # RIGHT: Clinical Interpretation
    with col2:
        st.subheader("🧠 Clinical Interpretation")

        # Emotional Signals
        st.markdown("### 💓 Emotional Signals")
        for e in formatted["emotions"]:
            st.markdown(e)

        # Metaphor Interpretation
        st.markdown("### 🧩 Symptom Interpretation")
        for m in formatted["metaphor"]:
            st.markdown(m)

        # Risk Indicators
        st.markdown("### 🚨 Clinical Risk Indicators")
        for r in formatted["risk"]:
            st.markdown(r)


        st.markdown("### 📄 Clinical Summary")
        st.write(formatted["summary"])

        if formatted["uncertainties"]:
            st.markdown("**Uncertainties:**")
            for u in formatted["uncertainties"]:
                st.markdown(f"- {u}")

        if formatted["notes"]:
            st.markdown("**Notes for Clinician:**")
            for n in formatted["notes"]:
                st.markdown(f"- {n}")
