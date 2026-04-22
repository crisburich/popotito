import streamlit as st
import json
from pathlib import Path

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quiz Interactivo",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }

/* Option buttons: make them look like cards */
div[data-testid="stButton"] > button {
    text-align: left !important;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    font-size: 0.95rem;
    line-height: 1.4;
    white-space: normal !important;
    height: auto !important;
}

/* Question number */
.q-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.2rem;
}

/* Neutral option row (after answering, non-selected non-correct) */
.opt-neutral {
    padding: 0.6rem 1rem;
    border-radius: 8px;
    border: 1px solid #ddd;
    font-size: 0.95rem;
    margin-bottom: 0.4rem;
    color: #555;
    background: #fafafa;
}

/* Welcome topic card subtitle */
.topic-sub { font-size: 0.85rem; color: #777; margin-top: 0.2rem; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # Streamlit Cloud runs from the repo root, so use a relative path directly.
    # Fallback to __file__-relative path for local development.
    candidates = [
        Path("data/questions.json"),
        Path(__file__).parent / "data" / "questions.json",
    ]
    for path in candidates:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(
        "No se encontró data/questions.json. "
        "Asegurate de que la carpeta 'data/' con el archivo esté commiteada en el repo."
    )

data = load_data()
topics_list = data["topics"]
topics_by_id = {t["id"]: t for t in topics_list}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "topic_id" not in st.session_state:
    st.session_state.topic_id = None
# answers: { topic_id: { q_index(int): chosen_option(int) } }
if "answers" not in st.session_state:
    st.session_state.answers = {}


def select_topic(tid: str):
    st.session_state.topic_id = tid
    if tid not in st.session_state.answers:
        st.session_state.answers[tid] = {}


def record_answer(tid: str, qi: int, opt: int):
    st.session_state.answers[tid][qi] = opt


def reset_topic(tid: str):
    st.session_state.answers[tid] = {}


# ── HELPERS ───────────────────────────────────────────────────────────────────
LETTERS = ["A", "B", "C", "D", "E"]


def topic_progress(tid: str):
    topic = topics_by_id[tid]
    n = len(topic["questions"])
    ans = st.session_state.answers.get(tid, {})
    answered = len(ans)
    correct = sum(
        1 for qi, chosen in ans.items()
        if chosen == topic["questions"][qi]["correct"]
    )
    return n, answered, correct


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎓 Quiz Interactivo")
    st.caption("Seleccioná un tema para empezar")
    st.divider()

    for topic in topics_list:
        tid = topic["id"]
        n, answered, correct = topic_progress(tid)
        is_active = st.session_state.topic_id == tid

        if answered == 0:
            sub = f"{n} preguntas"
        elif answered < n:
            sub = f"{answered}/{n} respondidas"
        else:
            pct = int(correct / n * 100)
            sub = f"✅ {correct}/{n} correctas ({pct}%)"

        label = f"{'▶ ' if is_active else ''}{topic['title']}\n\n{sub}"

        if st.button(
            label,
            key=f"nav_{tid}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            select_topic(tid)
            st.rerun()

    # Reset button for active topic
    if st.session_state.topic_id:
        st.divider()
        if st.button("🔄 Reiniciar quiz actual", use_container_width=True):
            reset_topic(st.session_state.topic_id)
            st.rerun()


# ── WELCOME SCREEN ────────────────────────────────────────────────────────────
if st.session_state.topic_id is None:
    st.markdown("## Bienvenido 👋")
    st.markdown("Elegí un tema desde el panel lateral, o hacé clic en una de las tarjetas:")
    st.write("")

    cols = st.columns(min(3, len(topics_list)))
    for i, topic in enumerate(topics_list):
        tid = topic["id"]
        n, answered, correct = topic_progress(tid)
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{topic['title']}**")
                st.markdown(
                    f"<div class='topic-sub'>{n} preguntas</div>",
                    unsafe_allow_html=True,
                )
                st.write("")
                if st.button("Comenzar →", key=f"start_{tid}", use_container_width=True):
                    select_topic(tid)
                    st.rerun()

    st.stop()


# ── QUIZ SCREEN ───────────────────────────────────────────────────────────────
topic = topics_by_id[st.session_state.topic_id]
tid = topic["id"]
questions = topic["questions"]
n, answered, correct_count = topic_progress(tid)
ans_map = st.session_state.answers.get(tid, {})

# ── Header + metrics ──
st.title(topic["title"])
if topic.get("description"):
    st.caption(topic["description"])

c1, c2, c3 = st.columns(3)
c1.metric("Total", f"{n} preguntas")
c2.metric("Respondidas", f"{answered}/{n}")
c3.metric(
    "Correctas",
    str(correct_count) if answered > 0 else "—",
    delta=f"{int(correct_count / answered * 100)}%" if answered > 0 else None,
    delta_color="normal",
)

st.progress(answered / n, text=f"Progreso: {answered} de {n}")
st.divider()

# ── Questions ─────────────────────────────────────────────────────────────────
for qi, q in enumerate(questions):
    user_ans = ans_map.get(qi)
    correct = q["correct"]

    with st.container(border=True):
        st.markdown(
            f"<div class='q-label'>Pregunta {qi + 1} de {n}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**{q['question']}**")
        st.write("")

        if user_ans is None:
            # ── Unanswered: render clickable option buttons ──────────────────
            for j, opt in enumerate(q["options"]):
                if st.button(
                    f"{LETTERS[j]}.  {opt}",
                    key=f"{tid}_q{qi}_o{j}",
                    use_container_width=True,
                ):
                    record_answer(tid, qi, j)
                    st.rerun()
        else:
            # ── Answered: show result ────────────────────────────────────────
            for j, opt in enumerate(q["options"]):
                if j == correct:
                    st.success(f"**{LETTERS[j]}.** {opt} &nbsp; ✓")
                elif j == user_ans:
                    st.error(f"**{LETTERS[j]}.** {opt} &nbsp; ✗")
                else:
                    st.markdown(
                        f"<div class='opt-neutral'>{LETTERS[j]}. {opt}</div>",
                        unsafe_allow_html=True,
                    )

            # ── Explanation expander ─────────────────────────────────────────
            with st.expander("📖 Ver explicación"):
                st.info(q["explanation"])

    st.write("")  # breathing room between cards

# ── Final score ───────────────────────────────────────────────────────────────
if answered == n:
    st.divider()
    pct = int(correct_count / n * 100)
    if pct >= 80:
        st.success(f"### 🎉 ¡Excelente! Puntaje final: {correct_count}/{n} ({pct}%)")
    elif pct >= 60:
        st.warning(f"### 👍 Bien. Puntaje final: {correct_count}/{n} ({pct}%)")
    else:
        st.error(f"### 📚 Seguí estudiando. Puntaje: {correct_count}/{n} ({pct}%)")

    if st.button("🔄 Reiniciar este quiz", type="primary"):
        reset_topic(tid)
        st.rerun()
