"""Streamlit entry point for Japan B2B Lead Radar."""

import streamlit as st

from lead_radar.config import has_secret

st.set_page_config(page_title="Japan B2B Lead Radar", page_icon="📡", layout="wide")

st.title("Japan B2B Lead Radar")
st.caption("Which Japanese companies to contact first, and why.")

with st.sidebar:
    st.header("Ideal customer profile")
    st.info("ICP filters arrive in Phase 1.")

st.subheader("Setup status")
if has_secret("GBIZINFO_API_TOKEN"):
    st.success("gBizINFO API token found.")
else:
    st.warning(
        "gBizINFO API token not found. Add GBIZINFO_API_TOKEN to .streamlit/secrets.toml "
        "(see .streamlit/secrets.toml.example)."
    )

st.markdown(
    "Every signal in this app will show its source, its date, and a link to the source record. "
    "Missing values are shown as **No data**; nothing is estimated."
)

# Footer: attribution required by the data sources (see docs/data-source-notes.md).
st.divider()
st.caption(
    "出典：[「Gビズインフォ」](https://info.gbiz.go.jp/)（経済産業省）を加工して作成 ・ "
    "出典：[国税庁法人番号公表サイト](https://www.houjin-bangou.nta.go.jp/)（国税庁）を加工して作成 ・ "
    "出典：[EDINET閲覧（提出）サイト](https://disclosure2.edinet-fsa.go.jp/)をもとに作成、"
    "[PDL1.0](https://www.digital.go.jp/resources/open_data/public_data_license_v1.0)  \n"
    "This app is not endorsed by METI, the National Tax Agency, or the FSA. "
    "Data is processed by Japan B2B Lead Radar."
)
