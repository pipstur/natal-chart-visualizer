import rootutils

rootutils.setup_root(__file__, [".gitignore"], pythonpath=True)

import streamlit as st
from groq import Groq

MODEL = "qwen/qwen3.8-27b"

# This task (warm astrological narration, not math/code/agentic reasoning)
# doesn't benefit from thinking mode at all - it just costs tokens. "none"
# routes qwen3.8 into its non-thinking / instruct mode.
REASONING_EFFORT = "none"

SYSTEM_PROMPT = """You are a thoughtful, literate astrologer helping someone \
explore their own natal chart. You are given exact, precomputed placements \
in a DATA block below - never invent or guess a position, sign, house, or \
aspect; use only what's given. Write in a warm, curious register: describe \
tendencies and themes, not fixed outcomes or predictions - this is a lens \
for reflection, not a forecast.

Aim for roughly 120-200 words unless asked to go deeper. However you choose \
to pace it, always land on a complete closing sentence - never let a \
thought trail off unfinished. If you sense you're running long, wrap up \
early rather than getting cut off mid-idea.

Refuse to answer anything that is not related to Astrology or your interpretations."""


@st.cache_resource
def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


def stream_completion(messages, status=None, max_completion_tokens=600, temperature=0.7):
    """Core streaming call. Yields text chunks - hand straight to
    st.write_stream(), which both renders progressively and returns the
    full concatenated string once the generator is exhausted.

    `status`, if given, is a plain dict this function mutates in place with
    {"finish_reason": "stop" | "length" | ...} once the stream ends - since
    a generator can't `return` a value that survives being driven by
    st.write_stream(), the caller reads status["finish_reason"] *after*
    st.write_stream() returns, to check whether the reply was truncated.
    """
    client = get_groq_client()
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
        reasoning_effort=REASONING_EFFORT,
        reasoning_format="hidden",
        stream=True,
    )
    for chunk in stream:
        choice = chunk.choices[0]
        if choice.delta.content:
            yield choice.delta.content
        if choice.finish_reason is not None and status is not None:
            status["finish_reason"] = choice.finish_reason


def build_interpret_messages(selection_description):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"DATA:\n{selection_description}\n\nExplain this placement."},
    ]


def build_chat_messages(chart_context, history, question):
    return [
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\nDATA:\n{chart_context}"},
        *history,
        {"role": "user", "content": question},
    ]


def build_continuation_messages(prior_messages, partial_reply):
    """One bounded follow-up call to finish a truncated reply. Deliberately
    manual (a button the user clicks), not an automatic retry loop - at 8K
    TPM / 1K RPD, silently doubling every request on truncation would burn
    through the daily quota fast without you choosing to spend it."""
    return [
        *prior_messages,
        {"role": "assistant", "content": partial_reply},
        {
            "role": "user",
            "content": "Continue exactly where you left off. Do not repeat anything written.",
        },
    ]


def _stream_chat(messages, temperature=0.6, max_completion_tokens=600):
    """Yields text chunks as they arrive - hand straight to st.write_stream()."""
    client = get_groq_client()
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def interpret_selection_stream(selection_description):
    """selection_description: a short plain-text block describing exactly
    what's currently selected, e.g.
        "Sun opposition Moon, orb 5°33', applying.
         Sun: 12°24' Capricorn, 9th house.
         Moon: 7°04' Sagittarius, 7th house."
    Built by the caller from whatever's already in st.session_state.selection
    - kept as a plain string so this module doesn't need to know the shape
    of your selection dict or your point/aspect helper internals.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"DATA:\n{selection_description}\n\nExplain this placement."},
    ]
    yield from _stream_chat(messages, max_completion_tokens=600)


def chat_about_chart_stream(chart_context, history, question):
    """chart_context: full plain-text dump of the chart (see chart_context_block
    below for a template). history: list of prior {"role","content"} turns
    from this session (NOT re-sent with chart_context every time - see note).
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\nDATA:\n{chart_context}"},
        *history,
        {"role": "user", "content": question},
    ]
    yield from _stream_chat(messages, max_completion_tokens=1200)
