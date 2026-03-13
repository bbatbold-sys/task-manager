"""Task Manager — iPhone Notes inspired dark UI."""

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from src.models import Task
from src.storage import delete_task, load_tasks, next_id, save_tasks, update_task

STORAGE_PATH = Path(__file__).parent / "tasks.json"

st.set_page_config(page_title="Notes", page_icon="📝", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

/* ── Base ── */
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    background: #12141c !important;
    font-family: -apple-system, 'SF Pro Display', 'Inter', sans-serif !important;
    -webkit-font-smoothing: antialiased;
    color: #fff !important;
}
[data-testid="stSidebar"] { background: #0e1016 !important; border-right: 1px solid #1e2130 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1300px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #252840; border-radius: 99px; }

/* ── All text override ── */
p, span, div, label, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stMarkdown p,
[data-testid="stWidgetLabel"] > div,
[data-testid="stWidgetLabel"] > div > p { color: #fff !important; }

/* ── Page header ── */
.app-header {
    margin-bottom: 2.5rem;
}
.app-title {
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 700;
    color: #FFD60A !important;
    letter-spacing: -0.04em;
    line-height: 1;
}
.app-subtitle {
    font-size: clamp(0.75rem, 1.2vw, 0.85rem);
    font-weight: 400;
    color: #3a3a3c !important;
    margin-top: 0.3rem;
    letter-spacing: 0.01em;
}

/* ── Stats row ── */
.stats-grid { display: flex; gap: 0.75rem; margin-bottom: 2.5rem; flex-wrap: wrap; }
.stat-pill {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    background: #1e2130;
    border: 1px solid #252840;
    border-radius: 99px;
    padding: 0.5rem 1rem;
    transition: background 0.2s;
}
.stat-pill:hover { background: #252840; }
.stat-pill-num {
    font-size: clamp(0.9rem, 1.5vw, 1.1rem);
    font-weight: 700;
    letter-spacing: -0.02em;
}
.stat-pill-label {
    font-size: clamp(0.68rem, 1vw, 0.75rem);
    font-weight: 500;
    color: #636366 !important;
    letter-spacing: 0.01em;
}
.num-yellow { color: #FFD60A !important; }
.num-blue   { color: #0A84FF !important; }
.num-green  { color: #32D74B !important; }
.num-red    { color: #FF453A !important; }

/* ── Section label ── */
.section-label {
    font-size: clamp(0.7rem, 1vw, 0.78rem);
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
    padding-left: 0.2rem;
}
.sl-todo { color: #636366 !important; }
.sl-done { color: #32D74B !important; }

/* ── Task card (iPhone Notes style) ── */
.note-card {
    background: #1e2130;
    border-radius: 13px;
    padding: 0.95rem 1.1rem;
    margin-bottom: 2px;
    position: relative;
    overflow: hidden;
    cursor: default;
    transition: transform 0.18s cubic-bezier(0.34, 1.56, 0.64, 1),
                background 0.15s ease,
                box-shadow 0.2s ease;
}
.note-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 3px 0 0 3px;
    transition: opacity 0.2s;
}
.note-card.p-high::before   { background: #FF453A; }
.note-card.p-medium::before { background: #FFD60A; }
.note-card.p-low::before    { background: #32D74B; }
.note-card.done-note        { background: #181a26; opacity: 0.6; }
.note-card:hover            { background: #252840; transform: scale(1.005); box-shadow: 0 4px 24px rgba(0,0,0,0.4); }
.note-card:active           { transform: scale(0.995); }

.note-title {
    font-size: clamp(0.88rem, 1.4vw, 1rem);
    font-weight: 600;
    color: #fff !important;
    letter-spacing: -0.01em;
    line-height: 1.35;
    word-break: break-word;
}
.note-title.crossed {
    text-decoration: line-through;
    color: #48484a !important;
}
.note-body {
    font-size: clamp(0.75rem, 1.1vw, 0.83rem);
    font-weight: 400;
    color: #8e8e93 !important;
    margin-top: 0.25rem;
    line-height: 1.5;
    word-break: break-word;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.note-footer {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-top: 0.6rem;
    flex-wrap: wrap;
}
.note-chip {
    font-size: clamp(0.6rem, 0.85vw, 0.68rem);
    font-weight: 600;
    padding: 0.18rem 0.6rem;
    border-radius: 99px;
    letter-spacing: 0.02em;
    white-space: nowrap;
}
.nc-high    { background: rgba(255,69,58,0.18);  color: #FF6961 !important; }
.nc-medium  { background: rgba(255,214,10,0.15); color: #FFD60A !important; }
.nc-low     { background: rgba(50,215,75,0.15);  color: #32D74B !important; }
.nc-due     { background: rgba(10,132,255,0.15); color: #64ADFF !important; }
.nc-overdue { background: rgba(255,69,58,0.22);  color: #FF6961 !important;
              animation: urgentPulse 2s ease-in-out infinite; }
@keyframes urgentPulse { 0%,100%{opacity:1;} 50%{opacity:0.6;} }

.note-id {
    font-size: 0.62rem;
    color: #3a3a3c !important;
    margin-left: auto;
    font-variant-numeric: tabular-nums;
}

/* ── Action buttons (iOS-style colored) ── */
.action-row {
    display: flex;
    gap: 0.4rem;
    align-items: center;
    justify-content: flex-end;
    padding: 0.3rem 0;
}

/* Swipe-reveal effect via wrapper */
.card-wrapper {
    position: relative;
    margin-bottom: 0.35rem;
}
.swipe-actions {
    position: absolute;
    right: 0; top: 50%;
    transform: translateY(-50%) translateX(0px);
    display: flex;
    gap: 0.35rem;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease, transform 0.25s cubic-bezier(0.34,1.56,0.64,1);
    z-index: 10;
    padding-right: 0.5rem;
}
.card-wrapper:hover .swipe-actions {
    opacity: 1;
    pointer-events: all;
    transform: translateY(-50%) translateX(0);
}
.card-wrapper:hover .note-card {
    padding-right: 5.5rem;
}

.ios-btn {
    width: 36px; height: 36px;
    border-radius: 50%;
    border: none;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    cursor: pointer;
    transition: transform 0.15s cubic-bezier(0.34,1.56,0.64,1), filter 0.15s;
    flex-shrink: 0;
}
.ios-btn:hover  { transform: scale(1.15); filter: brightness(1.15); }
.ios-btn:active { transform: scale(0.92); }
.btn-done   { background: #32D74B; color: #000 !important; }
.btn-edit   { background: #0A84FF; color: #fff !important; }
.btn-delete { background: #FF453A; color: #fff !important; }

/* ── iOS custom checkbox ── */
.ios-check-wrap { position: relative; display: flex; align-items: center; }
[data-testid="stCheckbox"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stCheckbox"] > label > div:first-child {
    width: 22px !important; height: 22px !important;
    border-radius: 50% !important;
    border: 2px solid #3a3a3c !important;
    background: transparent !important;
    transition: all 0.2s cubic-bezier(0.34,1.56,0.64,1) !important;
}
[data-testid="stCheckbox"]:has(input:checked) > label > div:first-child {
    background: #32D74B !important;
    border-color: #32D74B !important;
    box-shadow: 0 0 8px rgba(50,215,75,0.5) !important;
}

/* ── Streamlit buttons → iOS action buttons ── */
.stButton button {
    font-family: -apple-system, 'SF Pro Text', 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    border-radius: 99px !important;
    padding: 0.35rem 0.9rem !important;
    transition: all 0.18s cubic-bezier(0.34,1.56,0.64,1) !important;
    border: none !important;
    letter-spacing: 0.01em !important;
}
.stButton button:hover  { transform: scale(1.05) !important; filter: brightness(1.1) !important; }
.stButton button:active { transform: scale(0.95) !important; }

/* Done button */
div[data-testid*="done"] .stButton button,
.btn-mark .stButton button {
    background: rgba(50,215,75,0.18) !important;
    color: #32D74B !important;
}
/* Undo button */
.btn-undo .stButton button {
    background: rgba(10,132,255,0.18) !important;
    color: #64ADFF !important;
}
/* Edit button */
.btn-edit-wrap .stButton button {
    background: rgba(10,132,255,0.18) !important;
    color: #64ADFF !important;
}
/* Delete button */
.btn-del .stButton button {
    background: rgba(255,69,58,0.18) !important;
    color: #FF6961 !important;
}

/* ── Add task form ── */
.sidebar-hdr {
    font-size: 0.72rem;
    font-weight: 700;
    color: #636366 !important;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 1rem;
}
input, textarea {
    background: #252840 !important;
    border: none !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-family: -apple-system, 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 0.8rem !important;
    caret-color: #FFD60A !important;
}
input::placeholder, textarea::placeholder { color: #636366 !important; }
input:focus, textarea:focus {
    box-shadow: 0 0 0 2px rgba(255,214,10,0.35) !important;
}
div[data-baseweb="select"] > div {
    background: #252840 !important;
    border: none !important;
    border-radius: 10px !important;
    color: #000 !important;
}
/* dropdown option list */
div[data-baseweb="select"] div[role="listbox"],
div[data-baseweb="select"] div[role="option"],
div[data-baseweb="popover"] div,
div[data-baseweb="menu"] li,
div[data-baseweb="menu"] div {
    background: #fff !important;
    color: #000 !important;
}
/* selected value text */
div[data-baseweb="select"] [data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="select"] span,
div[data-baseweb="select"] div { color: #000 !important; }
/* date input text */
div[data-baseweb="datepicker"] input,
input[type="text"][aria-label],
div[data-testid="stDateInput"] input { color: #000 !important; }
/* calendar popup */
div[data-baseweb="calendar"] { background: #fff !important; color: #000 !important; }
div[data-baseweb="calendar"] * { color: #000 !important; }
label, [data-testid="stWidgetLabel"] p {
    color: #8e8e93 !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
}
[data-testid="stFormSubmitButton"] button {
    background: #FFD60A !important;
    color: #000 !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.2rem !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 4px 15px rgba(255,214,10,0.25) !important;
    transition: all 0.2s cubic-bezier(0.34,1.56,0.64,1) !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    transform: scale(1.02) !important;
    box-shadow: 0 6px 20px rgba(255,214,10,0.35) !important;
}
[data-testid="stFormSubmitButton"] button:active { transform: scale(0.97) !important; }

/* ── Empty state ── */
.empty-note {
    text-align: center;
    padding: 3.5rem 1rem;
    color: #3a3a3c !important;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.02em;
}
.empty-icon { font-size: 2.5rem; margin-bottom: 0.75rem; opacity: 0.4; }

/* ── Divider ── */
.col-gap { border-left: 1px solid #1e2130; height: 100%; min-height: 400px; margin: 0 auto; }

/* ── Responsive ── */
@media (max-width: 1023px) {
    .block-container { padding: 1.5rem !important; }
    .app-title { font-size: 2rem; }
}
@media (max-width: 767px) {
    .block-container { padding: 1rem !important; }
    .app-title { font-size: 1.6rem; }
    .stats-grid { gap: 0.5rem; }
    .stat-pill { padding: 0.4rem 0.75rem; }
}

/* ── Slide-in animation for cards ── */
@keyframes slideUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.note-card { animation: slideUp 0.3s cubic-bezier(0.34,1.56,0.64,1) both; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-hdr">New Note</div>', unsafe_allow_html=True)
    with st.form("add_task_form", clear_on_submit=True):
        title       = st.text_input("Title", placeholder="Title", label_visibility="collapsed")
        description = st.text_area("Description", height=90, placeholder="Add a note…", label_visibility="collapsed")
        ca, cb      = st.columns(2)
        due_date    = ca.date_input("Due", value=None)
        priority    = cb.selectbox("Priority", ["medium", "high", "low"])
        submitted   = st.form_submit_button("＋ Add Note", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Title is required.")
        else:
            tid = next_id(STORAGE_PATH)
            t   = Task(id=tid, title=title.strip(), description=description.strip(),
                       due_date=str(due_date) if due_date else None, priority=priority)
            tasks = load_tasks(STORAGE_PATH)
            tasks.append(t)
            save_tasks(tasks, STORAGE_PATH)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-hdr">Filter</div>', unsafe_allow_html=True)
    fp = st.selectbox("", ["All priorities","High","Medium","Low"], label_visibility="collapsed")
    sq = st.text_input("", placeholder="🔍  Search…", label_visibility="collapsed")

# ── Header ────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%A, %d %B")
st.markdown(f"""
<div class="app-header">
    <div class="app-title">Notes</div>
    <div class="app-subtitle">{now_str}</div>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
all_tasks  = load_tasks(STORAGE_PATH)
total      = len(all_tasks)
done_count = sum(1 for t in all_tasks if t.status == "done")
todo_count = total - done_count
high_count = sum(1 for t in all_tasks if t.priority == "high" and t.status == "todo")

st.markdown(f"""
<div class="stats-grid">
    <div class="stat-pill">
        <span class="stat-pill-num num-yellow">{total}</span>
        <span class="stat-pill-label">Total</span>
    </div>
    <div class="stat-pill">
        <span class="stat-pill-num num-blue">{todo_count}</span>
        <span class="stat-pill-label">Pending</span>
    </div>
    <div class="stat-pill">
        <span class="stat-pill-num num-green">{done_count}</span>
        <span class="stat-pill-label">Done</span>
    </div>
    <div class="stat-pill">
        <span class="stat-pill-num num-red">{high_count}</span>
        <span class="stat-pill-label">Urgent</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────────────────────
filtered = load_tasks(STORAGE_PATH)
if sq:
    kw = sq.lower()
    filtered = [t for t in filtered if kw in t.title.lower() or kw in t.description.lower()]
if fp != "All priorities":
    filtered = [t for t in filtered if t.priority == fp.lower()]

PORDER     = {"high": 0, "medium": 1, "low": 2}
todo_tasks = sorted([t for t in filtered if t.status == "todo"], key=lambda t: PORDER[t.priority])
done_tasks = sorted([t for t in filtered if t.status == "done"], key=lambda t: PORDER[t.priority])
today      = datetime.today().date()

# ── Card renderer ─────────────────────────────────────────────────────────────
def render_card(task):
    is_done   = task.status == "done"
    title_cls = "note-title crossed" if is_done else "note-title"
    card_cls  = f"note-card p-{task.priority} {'done-note' if is_done else ''}"
    body_html = f'<div class="note-body">{task.description}</div>' if task.description else ""

    # Due chip
    due_html = ""
    if task.due_date:
        d       = datetime.strptime(task.due_date, "%Y-%m-%d").date()
        overdue = d < today and not is_done
        cls_    = "nc-overdue" if overdue else "nc-due"
        icon    = "⚠︎ " if overdue else "⏰ "
        due_html = f'<span class="note-chip {cls_}">{icon}{task.due_date}</span>'

    priority_html = f'<span class="note-chip nc-{task.priority}">{task.priority.capitalize()}</span>'

    # Columns: checkbox | card | actions
    c_chk, c_card, c_act = st.columns([0.05, 0.72, 0.23])

    with c_chk:
        st.markdown('<div style="height:0.9rem"></div>', unsafe_allow_html=True)
        checked = st.checkbox("", value=is_done, key=f"chk_{task.id}", label_visibility="collapsed")
        if checked != is_done:
            task.status     = "done" if checked else "todo"
            task.updated_at = datetime.now().isoformat(timespec="seconds")
            update_task(task, STORAGE_PATH)
            st.rerun()

    with c_card:
        st.markdown(f"""
        <div class="{card_cls}">
            <div class="{title_cls}">{task.title}</div>
            {body_html}
            <div class="note-footer">
                {priority_html}
                {due_html}
                <span class="note-id">#{task.id:03d}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    with c_act:
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        if is_done:
            st.markdown('<div class="btn-undo">', unsafe_allow_html=True)
            if st.button("↩ Undo", key=f"undo_{task.id}"):
                task.status     = "todo"
                task.updated_at = datetime.now().isoformat(timespec="seconds")
                update_task(task, STORAGE_PATH)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="btn-mark">', unsafe_allow_html=True)
            if st.button("✓ Done", key=f"done_{task.id}"):
                task.status     = "done"
                task.updated_at = datetime.now().isoformat(timespec="seconds")
                update_task(task, STORAGE_PATH)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        a1, a2 = st.columns(2)
        with a1:
            st.markdown('<div class="btn-edit-wrap">', unsafe_allow_html=True)
            if st.button("✎", key=f"edit_{task.id}", help="Edit"):
                st.session_state[f"ed_{task.id}"] = not st.session_state.get(f"ed_{task.id}", False)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with a2:
            st.markdown('<div class="btn-del">', unsafe_allow_html=True)
            if st.button("⌫", key=f"del_{task.id}", help="Delete"):
                delete_task(task.id, STORAGE_PATH)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Edit form
    if st.session_state.get(f"ed_{task.id}"):
        with st.container():
            st.markdown(f"""
            <div style="background:#1e2130;border-radius:13px;padding:1.1rem 1.2rem;
                        margin:0.25rem 0 0.75rem;border:1px solid #252840;">
                <span style="font-size:0.7rem;font-weight:700;color:#636366;
                             text-transform:uppercase;letter-spacing:0.08em;">
                    Editing #{task.id:03d}
                </span>
            </div>""", unsafe_allow_html=True)
            with st.form(f"ef_{task.id}"):
                e1, e2, e3 = st.columns([2, 1, 1])
                nt = e1.text_input("Title", value=task.title)
                np = e2.selectbox("Priority", ["medium","high","low"],
                                  index=["medium","high","low"].index(task.priority))
                dv = datetime.strptime(task.due_date,"%Y-%m-%d").date() if task.due_date else None
                nd = e3.date_input("Due date", value=dv)
                nb = st.text_area("Note", value=task.description, height=80)
                sc, cc = st.columns(2)
                sv = sc.form_submit_button("Save", use_container_width=True)
                cn = cc.form_submit_button("Cancel", use_container_width=True)
            if sv:
                task.title       = nt.strip() or task.title
                task.description = nb.strip()
                task.priority    = np
                task.due_date    = str(nd) if nd else None
                task.updated_at  = datetime.now().isoformat(timespec="seconds")
                update_task(task, STORAGE_PATH)
                st.session_state[f"ed_{task.id}"] = False
                st.rerun()
            if cn:
                st.session_state[f"ed_{task.id}"] = False
                st.rerun()

# ── Two-column layout ─────────────────────────────────────────────────────────
left, mid, right = st.columns([0.47, 0.02, 0.47], gap="small")

with left:
    st.markdown(f'<div class="section-label sl-todo">In Progress · {len(todo_tasks)}</div>',
                unsafe_allow_html=True)
    if not todo_tasks:
        st.markdown("""<div class="empty-note">
            <div class="empty-icon">📋</div>Nothing pending — you're all caught up!
        </div>""", unsafe_allow_html=True)
    else:
        for task in todo_tasks:
            render_card(task)

with mid:
    st.markdown('<div class="col-gap"></div>', unsafe_allow_html=True)

with right:
    st.markdown(f'<div class="section-label sl-done">Completed · {len(done_tasks)}</div>',
                unsafe_allow_html=True)
    if not done_tasks:
        st.markdown("""<div class="empty-note">
            <div class="empty-icon">✦</div>Complete a task to see it here
        </div>""", unsafe_allow_html=True)
    else:
        for task in done_tasks:
            render_card(task)
