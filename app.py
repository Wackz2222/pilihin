import html
import os
from itertools import chain
from pathlib import Path

import streamlit as st

from catalog import CATEGORIES, format_budget_short, format_rupiah
from gemini_client import Advisor, ChatError, StreamResult
from prompt import build_system_instruction, recommend_request

st.set_page_config(
    page_title="Pilihin — Asisten Belanja Elektronik",
    page_icon=":material/devices:",
    layout="centered",
    initial_sidebar_state="expanded",
)
st.markdown(
    f"<style>{(Path(__file__).parent / 'assets' / 'style.css').read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

AVATARS = {"user": ":material/person:", "assistant": ":material/devices:"}


# ---------- Settings ----------


def get_setting(name: str, default: str | None = None) -> str | None:
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.environ.get(name, default)


@st.cache_resource(show_spinner=False)
def get_advisor(api_key: str, model: str, search: bool) -> Advisor:
    return Advisor(api_key, model, search)


API_KEY = get_setting("GEMINI_API_KEY")
MODEL = get_setting("GEMINI_MODEL", "gemini-3.5-flash")
SEARCH = (get_setting("GEMINI_SEARCH", "true") or "").lower() != "false"


# ---------- Session state ----------

st.session_state.setdefault("messages", [])
st.session_state.setdefault("pending_prompt", None)


def queue_prompt(text: str) -> None:
    st.session_state.pending_prompt = text


def reset_chat() -> None:
    st.session_state.messages = []
    st.session_state.pending_prompt = None


def apply_budget_preset(category: str) -> None:
    preset = st.session_state.get(f"preset_{category}")
    if preset:
        st.session_state[f"budget_{category}"] = preset


def clear_budget_preset(category: str) -> None:
    if st.session_state.get(f"preset_{category}") != st.session_state.get(
        f"budget_{category}"
    ):
        st.session_state[f"preset_{category}"] = None


# ---------- Sidebar: user profile ----------

with st.sidebar:
    with st.container(
        key="sidebar_head",
        horizontal=True,
        vertical_alignment="center",
        gap="small",
        wrap=False,
    ):
        st.markdown(
            """
            <div class="brand">
              <div class="brand-mark">P</div>
              <div>
                <div class="brand-name">Pilihin</div>
                <div class="brand-tag">Asisten belanja elektronik</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
            width="stretch",
        )
        st.button(
            "",
            key="new_chat",
            icon=":material/edit_square:",
            help="Percakapan baru",
            type="tertiary",
            on_click=reset_chat,
            disabled=not st.session_state.messages,
        )

    st.markdown('<p class="section-title">Profil kebutuhan</p>', unsafe_allow_html=True)

    category = st.segmented_control(
        "Kategori",
        options=list(CATEGORIES),
        format_func=lambda k: f"{CATEGORIES[k]['icon']} {CATEGORIES[k]['short']}",
        default="smartphone",
        required=True,
        key="category",
        width="stretch",
    )
    cat = CATEGORIES[category]

    budget = st.number_input(
        "Budget maksimal (Rp)",
        min_value=0,
        max_value=1_000_000_000,
        step=500_000,
        key=f"budget_{category}",
        on_change=clear_budget_preset,
        args=(category,),
        persist_state="session",
    )
    st.pills(
        "Pilihan budget cepat",
        options=cat["budgets"],
        format_func=format_budget_short,
        key=f"preset_{category}",
        on_change=apply_budget_preset,
        args=(category,),
        label_visibility="collapsed",
        persist_state="session",
    )
    st.caption(
        format_rupiah(budget) if budget else "Belum diisi — asisten akan menanyakannya."
    )

    purposes = st.pills(
        "Tujuan penggunaan",
        options=cat["purposes"],
        selection_mode="multi",
        key=f"purposes_{category}",
        persist_state="session",
    )

    components = []
    if category == "pc":
        components = st.pills(
            "Komponen yang dicari",
            options=cat["components"],
            selection_mode="multi",
            key="components_pc",
            persist_state="session",
        )

    priorities = st.pills(
        "Prioritas",
        options=cat["priorities"],
        selection_mode="multi",
        key=f"priorities_{category}",
        persist_state="session",
    )

    with st.expander("Preferensi lainnya", icon=":material/tune:"):
        brands = st.text_input(
            "Preferensi merek",
            placeholder="mis. suka Samsung, hindari merek X",
            key=f"brands_{category}",
            persist_state="session",
        )
        notes = st.text_area(
            "Catatan tambahan",
            placeholder=cat["notes_placeholder"],
            key=f"notes_{category}",
            height=90,
            persist_state="session",
        )

    profile = {
        "category": category,
        "budget": int(budget or 0),
        "purposes": purposes,
        "priorities": priorities,
        "components": components,
        "brands": brands.strip(),
        "notes": notes.strip(),
    }

    st.button(
        "Rekomendasikan sesuai profil",
        type="primary",
        icon=":material/auto_awesome:",
        width="stretch",
        on_click=queue_prompt,
        args=(recommend_request(profile),),
        disabled=not API_KEY,
    )
    st.caption(
        "Profil ikut terkirim di setiap pesan. Harga bersifat perkiraan — cek kembali di toko resmi."
    )


# ---------- Main area ----------


def profile_chips(p: dict) -> str:
    chips = [f"{CATEGORIES[p['category']]['label']}"]
    chips.append(
        f"Maks. {format_rupiah(p['budget'])}" if p["budget"] else "Budget belum diisi"
    )
    chips += p["purposes"][:3]
    return "".join(f'<span class="chip">{html.escape(c)}</span>' for c in chips)


def render_sources(sources: list) -> None:
    if not sources:
        return
    links = " · ".join(f"[{s['title']}]({s['uri']})" for s in sources[:6])
    st.caption(f":material/travel_explore: Sumber: {links}")


st.markdown(
    f"""
    <div class="page-header">
      <h1>Cari perangkat yang tepat, <span class="accent">tanpa ribet.</span></h1>
      <div class="chips">{profile_chips(profile)}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not API_KEY:
    st.warning(
        "**GEMINI_API_KEY belum diatur.** Tambahkan ke `.streamlit/secrets.toml` "
        "atau environment variable, lalu muat ulang halaman.",
        icon=":material/key:",
    )

typed = st.chat_input(
    "Tanya rekomendasi, mis. “HP kamera bagus budget 5 juta”",
    disabled=not API_KEY,
)
prompt = typed or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

if not st.session_state.messages:
    st.markdown(
        f"""
        <div class="welcome">
          <p class="welcome-title">Mulai dari mana?</p>
          <p class="welcome-sub">Isi profil di panel kiri lalu tekan <b>Rekomendasikan sesuai profil</b>,
          atau pilih salah satu pertanyaan {html.escape(cat['label'].lower())} berikut.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, suggestion in enumerate(cat["suggestions"]):
        cols[i % 2].button(
            suggestion,
            key=f"sugg_{i}",
            on_click=queue_prompt,
            args=(suggestion,),
            width="stretch",
            wrap=True,
            disabled=not API_KEY,
        )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=AVATARS[msg["role"]]):
        if msg["content"]:
            st.markdown(msg["content"])
        render_sources(msg.get("sources"))
        if msg.get("error"):
            st.error(msg["error"], icon=":material/error:")

if prompt and API_KEY:
    advisor = get_advisor(API_KEY, MODEL, SEARCH)
    result = StreamResult()
    error = None
    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        try:
            stream = advisor.stream(
                st.session_state.messages,
                lambda search: build_system_instruction(profile, search),
                result,
            )
            with st.spinner("Menganalisis kebutuhan Anda…"):
                first = next(stream, None)
            if first is not None:
                st.write_stream(chain([first], stream))
        except ChatError as exc:
            error = str(exc)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result.text,
            "sources": result.sources,
            "error": error,
        }
    )
    st.rerun()
