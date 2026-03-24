import streamlit as st

from app.ui.forms import render_settings_form
from app.ui.renderers import build_output, render_output
from core.defaults import get_default_settings


FORM_STYLE = """
<style>
div[data-testid="InputInstructions"] {
    display: none;
}
</style>
"""


def main() -> None:
    st.set_page_config(page_title="531weighted", page_icon="🏋️", layout="wide")
    st.markdown(FORM_STYLE, unsafe_allow_html=True)

    st.title("531weighted")
    st.caption("Generate a 5/3/1 cycle plan or competition attempt suggestions.")

    default_settings = get_default_settings()
    left_column, right_column = st.columns([0.95, 1.25], gap="large")

    with left_column:
        settings, submitted = render_settings_form(default_settings)
        if submitted:
            st.session_state["generated_output"] = build_output(settings)
            st.session_state["selected_output_section"] = "program"
            st.session_state["selected_output_label"] = "5/3/1 Plan"

    with right_column:
        st.subheader("Output")

        generated_output = st.session_state.get("generated_output")

        if generated_output:
            selected_output_section = _render_output_selector()
            render_output(generated_output, selected_output_section)
        else:
            st.info(
                "Enter your lifts on the left and press Generate to see your outputs."
            )


def _render_output_selector() -> str:
    if "selected_output_label" not in st.session_state:
        st.session_state["selected_output_label"] = _get_selected_output_label(
            st.session_state.get("selected_output_section", "program")
        )

    selected_label = st.segmented_control(
        "Output View",
        options=["5/3/1 Plan", "Competition Attempts"],
        key="selected_output_label",
        selection_mode="single",
        label_visibility="collapsed",
        width="stretch",
    )

    selected_output_section = (
        "program" if selected_label == "5/3/1 Plan" else "attempts"
    )
    st.session_state["selected_output_section"] = selected_output_section
    return selected_output_section


def _get_selected_output_label(selected_output_section: str) -> str:
    if selected_output_section == "attempts":
        return "Competition Attempts"

    return "5/3/1 Plan"


if __name__ == "__main__":
    main()
