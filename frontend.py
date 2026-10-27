import os
from typing import Any

import requests
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SchemeSaathi | Government Scheme Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def get_api_base_url():
    """Read the backend URL from Streamlit Secrets or environment."""
    try:
        url = st.secrets.get("SCHEMESAATHI_API_URL", "")
    except Exception:
        url = ""

    if not url:
        url = os.getenv("SCHEMESAATHI_API_URL", "")

    if not url:
        url = "http://127.0.0.1:8000"

    return url.rstrip("/")


API_BASE_URL = get_api_base_url()

# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --green: #16803c;
        --green-dark: #075c2b;
        --green-light: #eaf6ed;
        --ink: #17211b;
        --muted: #65716a;
        --line: #e5ebe7;
        --surface: #ffffff;
        --background: #fbfdfb;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 85% 5%, rgba(221, 245, 228, 0.45), transparent 25%),
            var(--background);
        color: var(--ink);
    }

    #MainMenu, footer, [data-testid="stHeader"] {
        visibility: hidden;
    }

    [data-testid="stAppViewContainer"] > .main {
        padding-top: 0.7rem;
    }

    .block-container {
        max-width: 1220px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.5rem 0 1rem 0;
    }

    .brand-icon {
        width: 48px;
        height: 48px;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--green-light);
        font-size: 27px;
    }

    .brand-name {
        font-size: 1.35rem;
        line-height: 1.25;
        font-weight: 800;
        color: var(--ink);
        letter-spacing: -0.6px;
    }

    .brand-subtitle {
        font-size: 0.82rem;
        color: var(--muted);
        margin-top: 3px;
    }

    .top-rule {
        border: none;
        border-top: 1px solid var(--line);
        margin: 0.4rem 0 2rem 0;
    }

    .eyebrow {
        display: inline-block;
        background: var(--green-light);
        color: var(--green-dark);
        border: 1px solid #d7ecdc;
        border-radius: 999px;
        padding: 7px 13px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: clamp(2.2rem, 4vw, 3.4rem);
        line-height: 1.1;
        letter-spacing: -1.8px;
        font-weight: 800;
        color: #18221b;
        margin: 0 0 1rem 0;
    }

    .hero-title span {
        color: var(--green);
    }

    .hero-copy {
        font-size: 1.05rem;
        line-height: 1.8;
        color: #5f6b63;
        max-width: 680px;
        margin-bottom: 1.2rem;
    }

    .trust-row {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        color: #34443a;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 1.2rem 0 1.6rem 0;
    }

    .trust-item {
        display: flex;
        align-items: center;
        gap: 7px;
    }

    .trust-check {
        color: var(--green);
        font-weight: 800;
    }

    .hero-art {
        min-height: 260px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle, #e5f7e9 0%, rgba(245, 252, 246, 0.2) 68%, transparent 70%);
        border-radius: 28px;
        font-size: 8rem;
    }

    .search-panel {
        background: rgba(255,255,255,0.94);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1.1rem 1.25rem 1rem 1.25rem;
        box-shadow: 0 12px 35px rgba(24, 60, 35, 0.07);
        margin-top: 1.1rem;
        margin-bottom: 1.5rem;
    }

    .section-title {
        color: var(--ink);
        font-size: 1.25rem;
        font-weight: 750;
        letter-spacing: -0.3px;
        margin: 0 0 0.35rem 0;
    }

    .section-copy {
        color: var(--muted);
        font-size: 0.92rem;
        margin-bottom: 1rem;
    }

    .feature-card {
        height: 100%;
        min-height: 110px;
        background: white;
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 19px 20px;
        box-shadow: 0 5px 18px rgba(24, 60, 35, 0.035);
    }

    .feature-icon {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--green-light);
        color: var(--green);
        font-size: 1.25rem;
        margin-bottom: 10px;
    }

    .feature-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--ink);
        margin-bottom: 5px;
    }

    .feature-copy {
        font-size: 0.84rem;
        line-height: 1.6;
        color: var(--muted);
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--green) !important;
        box-shadow: 0 0 0 1px var(--green) !important;
    }

    .stButton > button {
        border-radius: 11px;
        min-height: 42px;
        font-weight: 600;
        border: 1px solid #dfe8e1;
        transition: all 0.15s ease;
    }

    .stButton > button[kind="primary"] {
        background: var(--green);
        border-color: var(--green);
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--green-dark);
        border-color: var(--green-dark);
        color: white;
    }

    .answer-card {
        background: white;
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.2rem 1.35rem;
        margin: 0.5rem 0 1rem 0;
    }

    .source-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    .source-name {
        font-weight: 700;
        color: var(--ink);
        margin-bottom: 5px;
    }

    .source-meta {
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.7;
    }

    .status-pill {
        display: inline-block;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 0.78rem;
        font-weight: 650;
        background: #eaf6ed;
        color: #126532;
    }

    .footer-note {
        border-top: 1px solid var(--line);
        margin-top: 2.5rem;
        padding-top: 1rem;
        color: #748078;
        font-size: 0.82rem;
        line-height: 1.7;
    }

    @media (max-width: 760px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .hero-title {
            letter-spacing: -1px;
        }
        .hero-art {
            min-height: 140px;
            font-size: 5rem;
            margin-top: 0.5rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SESSION STATE
# ============================================================

if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

if "question" not in st.session_state:
    st.session_state.question = ""

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

if "api_result" not in st.session_state:
    st.session_state.api_result = None

if "api_error" not in st.session_state:
    st.session_state.api_error = None


# ============================================================
# HELPERS
# ============================================================

def api_get(path: str, timeout: int = 8) -> tuple[bool, Any]:
    try:
        response = requests.get(
            f"{API_BASE_URL}{path}",
            timeout=timeout,
        )
        response.raise_for_status()
        return True, response.json()
    except requests.RequestException as exc:
        return False, str(exc)


def ask_api(question: str, top_k: int = 3) -> tuple[bool, Any]:
    payload = {
        "question": question,
        "top_k": top_k,
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/ask",
            json=payload,
            timeout=90,
        )
        response.raise_for_status()
        return True, response.json()
    except requests.HTTPError as exc:
        detail = ""
        try:
            detail = response.json().get("detail", "")
        except (ValueError, AttributeError):
            pass
        return False, detail or str(exc)
    except requests.RequestException as exc:
        return False, str(exc)


def run_question(question: str) -> None:
    cleaned = question.strip()

    if len(cleaned) < 3:
        st.warning("Please enter a question with at least 3 characters.")
        return

    with st.spinner("Searching scheme documents for relevant information..."):
        success, result = ask_api(cleaned)

    st.session_state.last_question = cleaned

    if success:
        st.session_state.api_result = result
        st.session_state.api_error = None
    else:
        st.session_state.api_result = None
        st.session_state.api_error = result


def render_sources(sources: list[dict[str, Any]]) -> None:
    if not sources:
        st.info(
            "No source metadata was returned. Check that your indexed "
            "scheme records contain source information."
        )
        return

    for index, source in enumerate(sources, start=1):
        name = source.get("scheme_name") or "Scheme document"
        title = source.get("source_title") or "Source not recorded"
        pages = source.get("source_pages") or []
        academic_year = source.get("academic_year") or "Unknown"
        verified = source.get("last_verified") or "Unknown"
        matched_text = source.get("matched_text") or ""
        url = source.get("source_url") or ""
        official = source.get("official", False)

        with st.container(border=True):
            st.markdown(f"**{index}. {name}**")
            st.caption(title)

            details = []
            if pages:
                details.append("Page(s): " + ", ".join(str(p) for p in pages))
            details.append(f"Academic year: {academic_year}")
            details.append(f"Last verified: {verified}")
            details.append(
                "Official source flag: "
                + ("Yes" if official else "Not verified")
            )
            st.caption(" · ".join(details))

            if matched_text:
                with st.expander("View retrieved passage"):
                    st.write(matched_text)

            if url.startswith(("https://", "http://")):
                st.markdown(f"[Open source document]({url})")


def render_answer() -> None:
    result = st.session_state.api_result

    if st.session_state.api_error:
        st.error(
            "We couldn't retrieve an answer from the API. "
            "Make sure the FastAPI backend is running."
        )
        with st.expander("Technical details"):
            st.code(str(st.session_state.api_error))
        return

    if not result:
        return

    st.markdown("---")
    st.markdown("### Results")
    st.caption(f"Your question: {st.session_state.last_question}")

    mode = result.get("mode", "extractive_rag")
    if mode == "extractive_rag":
        st.caption("Evidence retrieval mode · Answers show retrieved source text")

    answer = result.get("answer", "No answer was returned.")
    with st.container(border=True):
        st.markdown(answer)

    disclaimer = result.get("disclaimer")
    if disclaimer:
        st.info(disclaimer, icon="ℹ️")

    st.markdown("### Sources")
    render_sources(result.get("sources", []))


# ============================================================
# TOP NAVIGATION
# ============================================================

brand_col, nav_col = st.columns([2.2, 2.8], vertical_alignment="center")

with brand_col:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">🌿</div>
            <div>
                <div class="brand-name">SchemeSaathi</div>
                <div class="brand-subtitle">Government Scheme Assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_col:
    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        if st.button("Home", use_container_width=True):
            st.session_state.active_page = "Home"
    with nav2:
        if st.button("Discover schemes", use_container_width=True):
            st.session_state.active_page = "Schemes"
    with nav3:
        if st.button("How it works", use_container_width=True):
            st.session_state.active_page = "How it works"

st.markdown('<hr class="top-rule">', unsafe_allow_html=True)


# ============================================================
# API CONNECTION STATUS
# ============================================================

api_ok, health_data = api_get("/health")

status_col, count_col = st.columns([1, 3])

with status_col:
    if api_ok:
        st.markdown(
            '<span class="status-pill">● API connected</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-pill" style="background:#fff0ef;color:#a72b22;">● API disconnected</span>',
            unsafe_allow_html=True,
        )

with count_col:
    if api_ok:
        count = health_data.get("scheme_records", 0)
        indexed = health_data.get("chroma_records", 0)
        st.caption(
            f"{count} loaded records · {indexed} indexed in ChromaDB"
        )
    else:
        st.caption(
            "Start the FastAPI backend to search the scheme knowledge base."
        )


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.active_page == "Home":

    left, right = st.columns([1.2, 0.8], gap="large", vertical_alignment="center")

    with left:
        st.markdown(
            '<div class="eyebrow">✓ Government schemes made simple</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="hero-title">
                Find the right<br>
                <span>government scheme</span><br>
                for you.
            </div>
            <div class="hero-copy">
                Ask questions in everyday language and explore relevant
                scheme information, eligibility criteria, required documents
                and application instructions from the documents in our
                knowledge base.
            </div>
            <div class="trust-row">
                <div class="trust-item"><span class="trust-check">✓</span> Evidence-based retrieval</div>
                <div class="trust-item"><span class="trust-check">✓</span> Source details</div>
                <div class="trust-item"><span class="trust-check">✓</span> Simple to use</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="hero-art" role="img" aria-label="Government scheme documents">
                📋
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="search-panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">What would you like to know?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Ask about a scheme, its requirements, or how to apply.</div>',
        unsafe_allow_html=True,
    )

    with st.form("ask_scheme_form", clear_on_submit=False):
        question = st.text_input(
            "Your question",
            value=st.session_state.question,
            placeholder="e.g. What is the income limit for the SC scholarship?",
            label_visibility="collapsed",
        )

        submit_col, hint_col = st.columns([1, 3], vertical_alignment="center")
        with submit_col:
            submitted = st.form_submit_button(
                "Search schemes  →",
                type="primary",
                use_container_width=True,
            )
        with hint_col:
            st.caption("Searches the scheme documents indexed by SchemeSaathi.")

    if submitted:
        st.session_state.question = question
        run_question(question)

    st.markdown("**Try asking**")
    suggestions = [
        "What is the income limit for SC scholarship?",
        "What documents are required for a scholarship?",
        "How do I apply for a government scheme?",
        "What are the eligibility criteria?",
    ]

    suggestion_cols = st.columns(2)
    for index, suggestion in enumerate(suggestions):
        with suggestion_cols[index % 2]:
            if st.button(
                suggestion,
                key=f"suggestion_{index}",
                use_container_width=True,
            ):
                st.session_state.question = suggestion
                run_question(suggestion)

    st.markdown("</div>", unsafe_allow_html=True)

    # Render result after the question panel.
    render_answer()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### A simple way to get started")

    feature_cols = st.columns(3, gap="medium")

    features = [
        (
            "🔎",
            "Discover schemes",
            "Explore scheme records available in the knowledge base.",
        ),
        (
            "📄",
            "Understand requirements",
            "Review retrieved eligibility, document and application details.",
        ),
        (
            "↗️",
            "Verify the source",
            "Check source titles, page details and available source links.",
        ),
    ]

    for col, feature in zip(feature_cols, features):
        icon, title, copy = feature
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-copy">{copy}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# DISCOVER SCHEMES PAGE
# ============================================================

elif st.session_state.active_page == "Schemes":

    st.markdown(
        '<div class="eyebrow">Explore the knowledge base</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hero-title">Discover <span>schemes</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-copy">Browse the scheme records loaded into SchemeSaathi. '
        'Availability depends on the documents added to the knowledge base.</div>',
        unsafe_allow_html=True,
    )

    success, schemes_data = api_get("/schemes", timeout=15)

    if not success:
        st.error("Could not load schemes. Check that the backend is running.")
        st.code(str(schemes_data))
    elif not schemes_data:
        st.info("No scheme records are available yet.")
    else:
        search_text = st.text_input(
            "Search schemes",
            placeholder="Search by scheme name, state, or category...",
        )

        state_options = sorted({
            item.get("state", "").strip()
            for item in schemes_data
            if item.get("state", "").strip()
        })
        category_options = sorted({
            item.get("category", "").strip()
            for item in schemes_data
            if item.get("category", "").strip()
        })

        filter1, filter2 = st.columns(2)
        with filter1:
            selected_state = st.selectbox(
                "State",
                ["All states"] + state_options,
            )
        with filter2:
            selected_category = st.selectbox(
                "Category",
                ["All categories"] + category_options,
            )

        filtered = []
        for scheme in schemes_data:
            haystack = " ".join([
                str(scheme.get("name", "")),
                str(scheme.get("state", "")),
                str(scheme.get("category", "")),
                str(scheme.get("source_title", "")),
            ]).lower()

            if search_text.strip().lower() not in haystack:
                continue
            if selected_state != "All states" and scheme.get("state", "") != selected_state:
                continue
            if selected_category != "All categories" and scheme.get("category", "") != selected_category:
                continue

            filtered.append(scheme)

        st.caption(f"Showing {len(filtered)} of {len(schemes_data)} records")

        for scheme in filtered:
            with st.container(border=True):
                st.markdown(f"#### {scheme.get('name') or 'Unnamed scheme'}")

                meta = []
                if scheme.get("state"):
                    meta.append(f"State: {scheme['state']}")
                if scheme.get("category"):
                    meta.append(f"Category: {scheme['category']}")
                meta.append(f"Academic year: {scheme.get('academic_year') or 'Unknown'}")
                st.caption(" · ".join(meta))

                if scheme.get("source_title"):
                    st.write(f"**Source:** {scheme['source_title']}")

                if scheme.get("source_url", "").startswith(("https://", "http://")):
                    st.markdown(f"[Open source]({scheme['source_url']})")

                if st.button(
                    "Ask about this record",
                    key=f"ask_scheme_{scheme.get('id')}_{scheme.get('name')}",
                ):
                    st.session_state.question = (
                        f"Tell me about {scheme.get('name')}. "
                        "What eligibility criteria, documents and application steps are recorded?"
                    )
                    st.session_state.active_page = "Home"
                    st.rerun()


# ============================================================
# HOW IT WORKS PAGE
# ============================================================

elif st.session_state.active_page == "How it works":

    st.markdown(
        '<div class="eyebrow">Simple, transparent, source-aware</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hero-title">How <span>SchemeSaathi</span> works</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-copy">SchemeSaathi searches the scheme records and extracted document passages '
        'that have been added to its knowledge base.</div>',
        unsafe_allow_html=True,
    )

    steps = [
        (
            "01",
            "Ask a question",
            "Enter a question in everyday language, such as asking about an income limit, eligibility condition, or required document.",
        ),
        (
            "02",
            "Find relevant passages",
            "The backend converts the question into an embedding and uses ChromaDB to retrieve semantically similar indexed records.",
        ),
        (
            "03",
            "Review the evidence",
            "The app displays retrieved text and available source details. It does not use a generative LLM to create answers.",
        ),
        (
            "04",
            "Verify before applying",
            "Check the current official guidelines, deadlines, and requirements with the relevant government department.",
        ),
    ]

    for number, title, copy in steps:
        with st.container(border=True):
            a, b = st.columns([0.65, 5])
            with a:
                st.markdown(f"### {number}")
            with b:
                st.markdown(f"#### {title}")
                st.write(copy)

    st.warning(
        "SchemeSaathi is a prototype. Retrieval similarity is not an eligibility "
        "score, and the app cannot confirm that a person qualifies for a scheme."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer-note">
        <strong>SchemeSaathi</strong> · Government Scheme Assistant<br>
        Informational prototype only. Scheme information may be incomplete or outdated.
        Always verify current eligibility criteria, official application links and deadlines
        with the relevant government department.
    </div>
    """,
    unsafe_allow_html=True,
)
