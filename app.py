"""Task Manager — feature-rich light-mode UI."""

import csv
import io
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent))

from src.models import Subtask, Task, TaskNote, TimeEntry
from src.storage import delete_task, load_tasks, next_id, save_tasks, update_task

STORAGE_PATH = Path(__file__).parent / "tasks.json"

# ── Tag colour palette (cycles by index) ──────────────────────────────────────
TAG_COLORS = [
    ("#dbeafe", "#2563eb"),  # blue
    ("#dcfce7", "#16a34a"),  # green
    ("#fef3c7", "#d97706"),  # amber
    ("#fce7f3", "#db2777"),  # pink
    ("#ede9fe", "#7c3aed"),  # violet
    ("#ffedd5", "#ea580c"),  # orange
    ("#f0fdf4", "#15803d"),  # emerald
    ("#e0f2fe", "#0284c7"),  # sky
]

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Task Manager", page_icon="📝", layout="wide")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

/* ── Base ── */
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    background: #f0f2f5 !important;
    font-family: -apple-system, 'SF Pro Display', 'Inter', sans-serif !important;
    -webkit-font-smoothing: antialiased;
    color: #1c1c1e !important;
}
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e5e7eb !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1400px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 99px; }

/* ── All text override ── */
p, span, div, label, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stMarkdown p,
[data-testid="stWidgetLabel"] > div,
[data-testid="stWidgetLabel"] > div > p { color: #1c1c1e !important; }

/* ── Page header ── */
.app-header { margin-bottom: 2rem; }
.app-title {
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 700;
    color: #1c1c1e !important;
    letter-spacing: -0.04em;
    line-height: 1;
}
.app-subtitle {
    font-size: clamp(0.75rem, 1.2vw, 0.85rem);
    font-weight: 400;
    color: #6b7280 !important;
    margin-top: 0.3rem;
    letter-spacing: 0.01em;
}

/* ── Stats row ── */
.stats-grid { display: flex; gap: 0.75rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.stat-pill {
    display: flex; align-items: center; gap: 0.55rem;
    background: #ffffff; border: 1px solid #e5e7eb; border-radius: 99px;
    padding: 0.5rem 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    transition: background 0.2s, box-shadow 0.2s;
}
.stat-pill:hover { background: #f9fafb; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.stat-pill-num { font-size: clamp(0.9rem,1.5vw,1.1rem); font-weight: 700; letter-spacing: -0.02em; }
.stat-pill-label { font-size: clamp(0.68rem,1vw,0.75rem); font-weight: 500; color: #9ca3af !important; }
.num-yellow { color: #d97706 !important; }
.num-blue   { color: #2563eb !important; }
.num-green  { color: #16a34a !important; }
.num-red    { color: #dc2626 !important; }
.num-gray   { color: #6b7280 !important; }
.num-purple { color: #7c3aed !important; }

/* ── Streak pill ── */
.streak-pill {
    display:inline-flex;align-items:center;gap:0.4rem;
    background:linear-gradient(135deg,#fbbf24,#f59e0b);
    color:#fff !important;border-radius:99px;
    padding:0.5rem 1rem;font-weight:700;font-size:0.82rem;
    box-shadow:0 2px 8px rgba(245,158,11,0.35);
}

/* ── Weekly chart ── */
.weekly-chart {
    background:#fff;border:1px solid #e5e7eb;border-radius:13px;
    padding:1rem 1.2rem;margin-bottom:1.5rem;
    box-shadow:0 1px 3px rgba(0,0,0,0.06);
}
.weekly-chart-title {
    font-size:0.7rem;font-weight:700;color:#9ca3af !important;
    text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem;
}
.weekly-bars { display:flex;gap:0.5rem;align-items:flex-end;height:60px; }
.weekly-bar-wrap { display:flex;flex-direction:column;align-items:center;gap:0.25rem;flex:1; }
.weekly-bar {
    width:100%;border-radius:4px 4px 0 0;
    background:#2563eb;min-height:3px;
    transition:height 0.3s ease;
}
.weekly-bar.today { background:#16a34a; }
.weekly-bar-label { font-size:0.6rem;font-weight:600;color:#9ca3af !important; }
.weekly-bar-num   { font-size:0.62rem;font-weight:700;color:#374151 !important; }

/* ── Bulk action bar ── */
.bulk-bar {
    background:#2563eb;border-radius:12px;padding:0.6rem 1rem;
    display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem;
    box-shadow:0 4px 15px rgba(37,99,235,0.3);
}
.bulk-bar-text { color:#fff !important;font-weight:600;font-size:0.82rem; }

/* ── Project badge ── */
.project-badge {
    display:inline-flex;align-items:center;gap:0.25rem;
    background:#ede9fe;color:#7c3aed !important;
    border-radius:6px;padding:0.15rem 0.5rem;
    font-size:0.62rem;font-weight:700;letter-spacing:0.02em;
}

/* ── Section label ── */
.section-label {
    font-size: clamp(0.7rem, 1vw, 0.78rem);
    font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
    margin-bottom: 0.6rem; padding-left: 0.2rem;
}
.sl-todo  { color: #6b7280 !important; }
.sl-done  { color: #16a34a !important; }
.sl-proj  { color: #7c3aed !important; }

/* ── Task card ── */
.note-card {
    background: #ffffff; border-radius: 13px;
    padding: 0.95rem 1.1rem; margin-bottom: 2px;
    position: relative; overflow: hidden; cursor: default;
    border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    transition: transform 0.18s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.2s ease;
    animation: slideUp 0.3s cubic-bezier(0.34,1.56,0.64,1) both;
}
.note-card::before {
    content:'';position:absolute;left:0;top:0;bottom:0;
    width:3px;border-radius:3px 0 0 3px;
}
.note-card.p-high::before   { background: #dc2626; }
.note-card.p-medium::before { background: #d97706; }
.note-card.p-low::before    { background: #16a34a; }
.note-card.done-note        { background: #f9fafb; opacity: 0.7; }
.note-card:hover            { transform: scale(1.003); box-shadow: 0 4px 16px rgba(0,0,0,0.1); }

.note-title {
    font-size: clamp(0.88rem,1.4vw,1rem);font-weight:600;
    color:#1c1c1e !important;letter-spacing:-0.01em;line-height:1.35;word-break:break-word;
}
.note-title.crossed { text-decoration:line-through;color:#9ca3af !important; }
.note-body {
    font-size:clamp(0.75rem,1.1vw,0.83rem);font-weight:400;color:#6b7280 !important;
    margin-top:0.25rem;line-height:1.5;word-break:break-word;
    display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;
}
.note-footer { display:flex;align-items:center;gap:0.4rem;margin-top:0.6rem;flex-wrap:wrap; }
.note-chip {
    font-size:clamp(0.6rem,0.85vw,0.68rem);font-weight:600;
    padding:0.18rem 0.6rem;border-radius:99px;letter-spacing:0.02em;white-space:nowrap;
}
.nc-high    { background:#fee2e2;color:#dc2626 !important; }
.nc-medium  { background:#fef3c7;color:#d97706 !important; }
.nc-low     { background:#dcfce7;color:#16a34a !important; }
.nc-due     { background:#dbeafe;color:#2563eb !important; }
.nc-overdue { background:#fee2e2;color:#dc2626 !important;
              animation:urgentPulse 2s ease-in-out infinite; }
.nc-recurring { background:#ede9fe;color:#7c3aed !important; }
@keyframes urgentPulse { 0%,100%{opacity:1;} 50%{opacity:0.6;} }

/* ── Tag chips ── */
.tag-chip {
    font-size:0.62rem;font-weight:700;padding:0.15rem 0.5rem;
    border-radius:99px;letter-spacing:0.02em;white-space:nowrap;
}

/* ── Progress bar ── */
.subtask-progress-wrap { margin-top:0.5rem; }
.subtask-progress-bar-bg {
    background:#f3f4f6;border-radius:99px;height:5px;overflow:hidden;
}
.subtask-progress-bar-fill {
    height:5px;border-radius:99px;background:#2563eb;
    transition:width 0.4s ease;
}
.subtask-progress-label {
    font-size:0.6rem;color:#9ca3af !important;font-weight:500;margin-top:0.2rem;
}

/* ── Time tracking ── */
.time-track-row {
    font-size:0.72rem;color:#6b7280 !important;
    display:flex;align-items:center;gap:0.5rem;margin-top:0.3rem;
}
.time-running { color:#2563eb !important;font-weight:700; }

/* ── Note ID ── */
.note-id { font-size:0.62rem;color:#d1d5db !important;margin-left:auto;font-variant-numeric:tabular-nums; }

/* ── Action icon buttons ── */
.stButton button {
    font-family:-apple-system,'SF Pro Text','Inter',sans-serif !important;
    font-size:1rem !important;font-weight:600 !important;
    border-radius:50% !important;width:36px !important;height:36px !important;
    padding:0 !important;transition:all 0.18s cubic-bezier(0.34,1.56,0.64,1) !important;
    border:none !important;background:#f3f4f6 !important;color:#374151 !important;
}
.stButton button:hover  { transform:scale(1.1) !important; }
.stButton button:active { transform:scale(0.92) !important; }

/* ── Checkbox ── */
[data-testid="stCheckbox"] {
    display:flex !important;align-items:center !important;justify-content:center !important;
}
[data-testid="stCheckbox"] > label > div:first-child {
    width:22px !important;height:22px !important;border-radius:50% !important;
    border:2px solid #d1d5db !important;background:transparent !important;
    transition:all 0.2s cubic-bezier(0.34,1.56,0.64,1) !important;
}
[data-testid="stCheckbox"]:has(input:checked) > label > div:first-child {
    background:#16a34a !important;border-color:#16a34a !important;
    box-shadow:0 0 8px rgba(22,163,74,0.3) !important;
}

/* ── Sidebar form ── */
.sidebar-hdr {
    font-size:0.72rem;font-weight:700;color:#9ca3af !important;
    text-transform:uppercase;letter-spacing:0.09em;margin-bottom:1rem;
}
input, textarea {
    background:#f9fafb !important;border:1px solid #e5e7eb !important;
    border-radius:10px !important;color:#1c1c1e !important;
    font-family:-apple-system,'Inter',sans-serif !important;
    font-size:0.88rem !important;padding:0.6rem 0.8rem !important;caret-color:#2563eb !important;
}
input::placeholder,textarea::placeholder { color:#9ca3af !important; }
div[data-baseweb="input"] input,
div[data-testid="stTextInput"] input { color:#1c1c1e !important; }
input:focus,textarea:focus {
    box-shadow:0 0 0 2px rgba(37,99,235,0.25) !important;border-color:#2563eb !important;
}
div[data-baseweb="select"] > div {
    background:#f9fafb !important;border:1px solid #e5e7eb !important;
    border-radius:10px !important;color:#1c1c1e !important;
}
div[data-baseweb="select"] div[role="listbox"],
div[data-baseweb="select"] div[role="option"],
div[data-baseweb="popover"] div,
div[data-baseweb="menu"] li,
div[data-baseweb="menu"] div { background:#ffffff !important;color:#1c1c1e !important; }
div[data-baseweb="select"] [data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="select"] span,
div[data-baseweb="select"] div { color:#1c1c1e !important; }
div[data-baseweb="datepicker"] input,
input[type="text"][aria-label],
div[data-testid="stDateInput"] input { color:#1c1c1e !important; }
div[data-baseweb="calendar"] { background:#fff !important;color:#1c1c1e !important; }
div[data-baseweb="calendar"] * { color:#1c1c1e !important; }
label,[data-testid="stWidgetLabel"] p {
    color:#6b7280 !important;font-size:0.75rem !important;font-weight:500 !important;
}
[data-testid="stFormSubmitButton"] button {
    background:#2563eb !important;color:#ffffff !important;
    font-weight:700 !important;font-size:0.85rem !important;
    border-radius:12px !important;padding:0.6rem 1.2rem !important;
    width:100% !important;letter-spacing:0.01em !important;
    box-shadow:0 4px 15px rgba(37,99,235,0.25) !important;
    transition:all 0.2s cubic-bezier(0.34,1.56,0.64,1) !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    transform:scale(1.02) !important;box-shadow:0 6px 20px rgba(37,99,235,0.35) !important;
}
[data-testid="stFormSubmitButton"] button:active { transform:scale(0.97) !important; }

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background:#f3f4f6 !important;color:#374151 !important;
    border-radius:10px !important;font-size:0.8rem !important;
    font-weight:600 !important;width:auto !important;height:auto !important;
    padding:0.5rem 1rem !important;border-radius:10px !important;
}

/* ── Empty state ── */
.empty-note {
    text-align:center;padding:3.5rem 1rem;color:#9ca3af !important;
    font-size:0.85rem;font-weight:500;letter-spacing:0.02em;
}
.empty-icon { font-size:2.5rem;margin-bottom:0.75rem;opacity:0.4; }

/* ── Divider ── */
.col-gap { border-left:1px solid #e5e7eb;height:100%;min-height:400px;margin:0 auto; }

/* ── Pomodoro widget ── */
.pomo-wrap {
    background:#f9fafb;border:1px solid #e5e7eb;border-radius:13px;
    padding:1rem;text-align:center;margin-top:0.5rem;
}

/* ── Animations ── */
@keyframes slideUp {
    from { opacity:0;transform:translateY(12px); }
    to   { opacity:1;transform:translateY(0); }
}

/* ── Responsive ── */
@media(max-width:1023px) { .block-container{padding:1.5rem !important;} }
@media(max-width:767px)  {
    .block-container{padding:1rem !important;}
    .stats-grid{gap:0.5rem;}
    .stat-pill{padding:0.4rem 0.75rem;}
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _today() -> date:
    return datetime.today().date()


def _next_due(due_date_str: str, recurring: str) -> str:
    """Return the next due date string for a recurring task."""
    try:
        d = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        d = _today()
    if recurring == "daily":
        d += timedelta(days=1)
    elif recurring == "weekly":
        d += timedelta(weeks=1)
    elif recurring == "monthly":
        # Same day next month (clamp to end of month)
        month = d.month + 1
        year = d.year
        if month > 12:
            month = 1
            year += 1
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        d = date(year, month, min(d.day, last_day))
    return str(d)


def _tag_style(tag: str, all_tags: list) -> tuple:
    """Return (bg, fg) css colours for a tag based on its sorted position."""
    sorted_tags = sorted(set(all_tags))
    idx = sorted_tags.index(tag) if tag in sorted_tags else 0
    return TAG_COLORS[idx % len(TAG_COLORS)]


def _total_tracked_seconds(task: Task) -> int:
    return sum(e.duration_seconds() for e in task.time_entries)


def _fmt_duration(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def _compute_streak(tasks: list) -> int:
    """Count consecutive days ending today where at least one task was completed."""
    done_dates = set()
    for t in tasks:
        if t.status == "done" and t.updated_at:
            done_dates.add(t.updated_at[:10])
    streak = 0
    check = _today()
    while str(check) in done_dates:
        streak += 1
        check -= timedelta(days=1)
    return streak


def _weekly_counts(tasks: list) -> list:
    """Return list of (day_label, count, is_today) for the last 7 days."""
    today = _today()
    result = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        ds = str(d)
        count = sum(1 for t in tasks if t.status == "done" and t.updated_at and t.updated_at[:10] == ds)
        label = d.strftime("%a")[0]  # M T W T F S S
        result.append((label, count, d == today))
    return result


def _build_csv(tasks: list) -> str:
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([
        "id", "title", "description", "due_date", "priority", "status",
        "project", "tags", "recurring", "archived",
        "subtasks_total", "subtasks_done", "time_tracked_seconds",
        "notes_count", "created_at", "updated_at",
    ])
    for t in tasks:
        writer.writerow([
            t.id, t.title, t.description, t.due_date or "", t.priority, t.status,
            t.project or "", ";".join(t.tags), t.recurring or "", t.archived,
            len(t.subtasks), sum(1 for s in t.subtasks if s.done),
            _total_tracked_seconds(t), len(t.notes),
            t.created_at, t.updated_at,
        ])
    return out.getvalue()


def _get_all_tags(tasks: list) -> list:
    tags = set()
    for t in tasks:
        tags.update(t.tags)
    return sorted(tags)


def _get_all_projects(tasks: list) -> list:
    projs = set()
    for t in tasks:
        if t.project:
            projs.add(t.project)
    return sorted(projs)


# ─────────────────────────────────────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────────────────────────────────────
if "timers" not in st.session_state:
    st.session_state.timers = {}   # {task_id: iso_start_str}
if "bulk_selected" not in st.session_state:
    st.session_state.bulk_selected = set()


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
all_tasks_raw = load_tasks(STORAGE_PATH)
all_tags_global = _get_all_tags(all_tasks_raw)
all_projects_global = _get_all_projects(all_tasks_raw)

with st.sidebar:
    st.markdown('<div class="sidebar-hdr">New Task</div>', unsafe_allow_html=True)
    with st.form("add_task_form", clear_on_submit=True):
        title_input = st.text_input(
            "Title", placeholder="Task title…", label_visibility="collapsed",
            key="new_task_title"
        )
        description_input = st.text_area(
            "Description", height=70, placeholder="Add a note…", label_visibility="collapsed"
        )
        ca, cb = st.columns(2)
        due_date_input = ca.date_input("Due", value=None)
        priority_input = cb.selectbox("Priority", ["medium", "high", "low"])
        cc, cd = st.columns(2)
        project_input = cc.text_input("Project", placeholder="Project…")
        recurring_input = cd.selectbox("Repeat", ["none", "daily", "weekly", "monthly"])
        tags_input = st.multiselect("Tags (pick existing)", options=all_tags_global)
        new_tags_input = st.text_input("New tags (comma-separated)", placeholder="work, urgent…")
        subtasks_input = st.text_area("Subtasks (one per line)", height=60, placeholder="Step 1\nStep 2")
        submitted = st.form_submit_button("＋ Add Task", use_container_width=True)

    if submitted:
        if not title_input.strip():
            st.error("Title is required.")
        else:
            tid = next_id(STORAGE_PATH)
            typed = [t.strip() for t in new_tags_input.split(",") if t.strip()]
            raw_tags = list(dict.fromkeys(tags_input + typed))
            raw_subtasks = [Subtask(text=s.strip()) for s in subtasks_input.splitlines() if s.strip()]
            t = Task(
                id=tid,
                title=title_input.strip(),
                description=description_input.strip(),
                due_date=str(due_date_input) if due_date_input else None,
                priority=priority_input,
                tags=raw_tags,
                subtasks=raw_subtasks,
                project=project_input.strip() or None,
                recurring=recurring_input if recurring_input != "none" else None,
                order=tid,
            )
            tasks = load_tasks(STORAGE_PATH)
            tasks.append(t)
            save_tasks(tasks, STORAGE_PATH)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-hdr">Filters & View</div>', unsafe_allow_html=True)

    fp = st.selectbox("Priority", ["All priorities", "High", "Medium", "Low"])
    sq = st.text_input("Search", placeholder="🔍  Search…", label_visibility="collapsed")

    project_filter_opts = ["All projects"] + all_projects_global
    fp_proj = st.selectbox("Project", project_filter_opts)

    tag_filter_opts = ["All tags"] + all_tags_global
    fp_tag = st.selectbox("Tag", tag_filter_opts)

    today_only = st.checkbox("Today view (due today)")
    show_archive = st.checkbox("Show archive")
    group_by_proj = st.checkbox("Group by project")

    st.markdown('<div class="sidebar-hdr" style="margin-top:1rem;">Sort</div>', unsafe_allow_html=True)
    sort_by = st.selectbox("Sort by", ["Priority", "Due date", "Created", "Title", "Manual"])

    st.markdown("<hr style='border-color:#e5e7eb;margin:1rem 0'>", unsafe_allow_html=True)

    # ── Pomodoro ──────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-hdr">Pomodoro Timer</div>', unsafe_allow_html=True)
    components.html("""
<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:13px;padding:14px 10px;text-align:center;font-family:-apple-system,'Inter',sans-serif;">
  <div id="pomo-mode" style="font-size:0.65rem;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Work</div>
  <div id="pomo-display" style="font-size:2.4rem;font-weight:700;color:#1c1c1e;letter-spacing:-0.03em;line-height:1;margin-bottom:10px;">25:00</div>
  <div style="display:flex;gap:6px;justify-content:center;">
    <button id="pomo-play" onclick="pomoToggle()" style="background:#2563eb;color:#fff;border:none;border-radius:8px;padding:6px 14px;font-size:0.78rem;font-weight:700;cursor:pointer;">▶ Start</button>
    <button onclick="pomoReset()" style="background:#f3f4f6;color:#374151;border:none;border-radius:8px;padding:6px 12px;font-size:0.78rem;font-weight:600;cursor:pointer;">↺ Reset</button>
  </div>
</div>
<script>
var WORK=25*60, BREAK=5*60;
var remaining=WORK, running=false, isBreak=false, interval=null;
function updateDisplay(){
  var m=Math.floor(remaining/60), s=remaining%60;
  document.getElementById('pomo-display').textContent=(m<10?'0':'')+m+':'+(s<10?'0':'')+s;
  document.getElementById('pomo-mode').textContent=isBreak?'Break':'Work';
  document.getElementById('pomo-display').style.color=isBreak?'#16a34a':'#1c1c1e';
}
function pomoToggle(){
  if(!running && window.Notification && Notification.permission==='default'){Notification.requestPermission();}
  if(running){
    clearInterval(interval);running=false;
    document.getElementById('pomo-play').textContent='▶ Resume';
    document.getElementById('pomo-play').style.background='#2563eb';
  } else {
    running=true;
    document.getElementById('pomo-play').textContent='⏸ Pause';
    document.getElementById('pomo-play').style.background='#dc2626';
    interval=setInterval(function(){
      remaining--;
      if(remaining<=0){
        clearInterval(interval);running=false;
        isBreak=!isBreak;remaining=isBreak?BREAK:WORK;
        document.getElementById('pomo-play').textContent='▶ Start';
        document.getElementById('pomo-play').style.background='#2563eb';
        var msg=isBreak?'☕ Break time! Take 5 minutes.':'💼 Break over — back to work!';
        if(window.Notification){
          if(Notification.permission==='granted'){new Notification('Pomodoro',{body:msg});}
          else if(Notification.permission!=='denied'){Notification.requestPermission().then(function(p){if(p==='granted')new Notification('Pomodoro',{body:msg});});}
        }
      }
      updateDisplay();
    },1000);
  }
}
function pomoReset(){
  clearInterval(interval);running=false;isBreak=false;remaining=WORK;
  document.getElementById('pomo-play').textContent='▶ Start';
  document.getElementById('pomo-play').style.background='#2563eb';
  updateDisplay();
}
updateDisplay();
</script>
""", height=145)


# ─────────────────────────────────────────────────────────────────────────────
# Load & filter tasks
# ─────────────────────────────────────────────────────────────────────────────
all_tasks = load_tasks(STORAGE_PATH)
today_date = _today()
today_str = str(today_date)

# Process pending status changes before rendering
if "_status_action" in st.session_state:
    _action = st.session_state.pop("_status_action")
    for _t in all_tasks:
        if _t.id == _action["id"]:
            _t.status = _action["status"]
            _t.updated_at = _now_iso()
            update_task(_t, STORAGE_PATH)
            if _action["status"] == "done" and _t.recurring:
                _next = _next_due(_t.due_date or today_str, _t.recurring)
                _new_t = Task(
                    id=next_id(STORAGE_PATH), title=_t.title, description=_t.description,
                    due_date=_next, priority=_t.priority, tags=list(_t.tags),
                    subtasks=[Subtask(text=s.text) for s in _t.subtasks],
                    recurring=_t.recurring, project=_t.project, order=_t.order,
                )
                _tlist = load_tasks(STORAGE_PATH)
                _tlist.append(_new_t)
                save_tasks(_tlist, STORAGE_PATH)
            break
    all_tasks = load_tasks(STORAGE_PATH)

# Separate archived / active
if show_archive:
    working_tasks = [t for t in all_tasks if t.archived]
else:
    working_tasks = [t for t in all_tasks if not t.archived]

# Search
if sq:
    kw = sq.lower()
    working_tasks = [
        t for t in working_tasks
        if kw in t.title.lower() or kw in t.description.lower()
        or any(kw in tag.lower() for tag in t.tags)
        or (t.project and kw in t.project.lower())
    ]

# Priority filter
if fp != "All priorities":
    working_tasks = [t for t in working_tasks if t.priority == fp.lower()]

# Project filter
if fp_proj != "All projects":
    working_tasks = [t for t in working_tasks if t.project == fp_proj]

# Tag filter
if fp_tag != "All tags":
    working_tasks = [t for t in working_tasks if fp_tag in t.tags]

# Today filter
if today_only:
    working_tasks = [t for t in working_tasks if t.due_date == today_str]

# Sort
PORDER = {"high": 0, "medium": 1, "low": 2}

def _sort_key(t: Task):
    if sort_by == "Priority":
        return (PORDER.get(t.priority, 1), t.order)
    elif sort_by == "Due date":
        return (t.due_date or "9999-99-99", PORDER.get(t.priority, 1))
    elif sort_by == "Created":
        return (t.created_at, PORDER.get(t.priority, 1))
    elif sort_by == "Title":
        return (t.title.lower(), 0)
    else:  # Manual
        return (t.order, 0)

todo_tasks = sorted([t for t in working_tasks if t.status == "todo"], key=_sort_key)
done_tasks = sorted([t for t in working_tasks if t.status == "done"], key=_sort_key)


# ─────────────────────────────────────────────────────────────────────────────
# Stats
# ─────────────────────────────────────────────────────────────────────────────
active_tasks = [t for t in all_tasks if not t.archived]
total_count = len(active_tasks)
done_count = sum(1 for t in active_tasks if t.status == "done")
todo_count = total_count - done_count
high_count = sum(1 for t in active_tasks if t.priority == "high" and t.status == "todo")
overdue_count = sum(
    1 for t in active_tasks
    if t.status == "todo" and t.due_date
    and datetime.strptime(t.due_date, "%Y-%m-%d").date() < today_date
)
streak = _compute_streak(all_tasks)

now_str = datetime.now().strftime("%A, %d %B")
st.html(f"""
<div class="app-header">
    <div class="app-title">Task Manager</div>
    <div class="app-subtitle">{now_str}</div>
</div>
""")

streak_html = f'<div class="streak-pill">🔥 {streak}-day streak</div>' if streak > 0 else ""
st.html(f"""
<div class="stats-grid">
    <div class="stat-pill">
        <span class="stat-pill-num num-yellow">{total_count}</span>
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
    <div class="stat-pill">
        <span class="stat-pill-num num-red">{overdue_count}</span>
        <span class="stat-pill-label">Overdue</span>
    </div>
    {streak_html}
</div>
""")


# ─────────────────────────────────────────────────────────────────────────────
# Weekly summary chart
# ─────────────────────────────────────────────────────────────────────────────
weekly_data = _weekly_counts(all_tasks)
max_count = max((c for _, c, _ in weekly_data), default=1) or 1
bar_html = ""
for label, count, is_today in weekly_data:
    pct = max(int((count / max_count) * 52), 3)
    today_cls = "today" if is_today else ""
    bar_html += f"""
    <div class="weekly-bar-wrap">
        <div class="weekly-bar-num">{count if count else ""}</div>
        <div class="weekly-bar {today_cls}" style="height:{pct}px;"></div>
        <div class="weekly-bar-label">{label}</div>
    </div>"""

st.html(f"""
<div class="weekly-chart">
    <div class="weekly-chart-title">Tasks completed — last 7 days</div>
    <div class="weekly-bars">{bar_html}</div>
</div>
""")


# ─────────────────────────────────────────────────────────────────────────────
# Bulk action bar
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.bulk_selected:
    sel_count = len(st.session_state.bulk_selected)
    st.html(f'<div class="bulk-bar"><span class="bulk-bar-text">{sel_count} task(s) selected</span></div>')
    bc1, bc2, bc3, bc4 = st.columns([1, 1, 1, 3])
    if bc1.button("✓ Done", key="bulk_done"):
        tasks_all = load_tasks(STORAGE_PATH)
        new_tasks = []
        for t in tasks_all:
            if t.id in st.session_state.bulk_selected:
                t.status = "done"
                t.updated_at = _now_iso()
                # Handle recurring
                if t.recurring and t.status == "done":
                    next_due = _next_due(t.due_date or today_str, t.recurring)
                    new_t = Task(
                        id=next_id(STORAGE_PATH),
                        title=t.title, description=t.description,
                        due_date=next_due, priority=t.priority,
                        tags=list(t.tags), subtasks=[Subtask(text=s.text) for s in t.subtasks],
                        recurring=t.recurring, project=t.project, order=t.order,
                    )
                    new_tasks.append(new_t)
            tasks_all_updated = tasks_all
        tasks_all = load_tasks(STORAGE_PATH)
        for t in tasks_all:
            if t.id in st.session_state.bulk_selected:
                t.status = "done"
                t.updated_at = _now_iso()
        save_tasks(tasks_all + new_tasks, STORAGE_PATH)
        st.session_state.bulk_selected = set()
        st.rerun()
    if bc2.button("📦 Archive", key="bulk_archive"):
        tasks_all = load_tasks(STORAGE_PATH)
        for t in tasks_all:
            if t.id in st.session_state.bulk_selected:
                t.archived = True
                t.updated_at = _now_iso()
        save_tasks(tasks_all, STORAGE_PATH)
        st.session_state.bulk_selected = set()
        st.rerun()
    if bc3.button("🗑 Delete", key="bulk_delete"):
        tasks_all = load_tasks(STORAGE_PATH)
        tasks_all = [t for t in tasks_all if t.id not in st.session_state.bulk_selected]
        save_tasks(tasks_all, STORAGE_PATH)
        st.session_state.bulk_selected = set()
        st.rerun()
    if bc4.button("✕ Clear selection", key="bulk_clear"):
        st.session_state.bulk_selected = set()
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Card renderer
# ─────────────────────────────────────────────────────────────────────────────
def _he(s: str) -> str:
    """HTML-escape a string for safe injection into HTML attributes/text."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def render_card(task: Task, all_tags: list, is_manual: bool = False):
    is_done = task.status == "done"
    title_cls = "note-title crossed" if is_done else "note-title"
    card_cls = f"note-card p-{task.priority} {'done-note' if is_done else ''}"
    _desc = _he(task.description).replace("\n", " ").replace("\r", "")
    body_html = f'<div class="note-body">{_desc}</div>' if task.description else ""

    # Due chip
    due_html = ""
    if task.due_date:
        try:
            d = datetime.strptime(task.due_date, "%Y-%m-%d").date()
            overdue = d < today_date and not is_done
            cls_ = "nc-overdue" if overdue else "nc-due"
            icon = "⚠︎ " if overdue else "⏰ "
            due_html = f'<span class="note-chip {cls_}">{icon}{task.due_date}</span>'
        except ValueError:
            pass

    priority_html = f'<span class="note-chip nc-{task.priority}">{task.priority.capitalize()}</span>'

    recurring_html = ""
    if task.recurring:
        recurring_html = f'<span class="note-chip nc-recurring">↻ {task.recurring}</span>'

    # Tags
    tags_html = ""
    for tag in task.tags:
        bg, fg = _tag_style(tag, all_tags)
        tags_html += f'<span class="tag-chip" style="background:{bg};color:{fg};">{_he(tag)}</span>'

    # Project badge
    project_html = ""
    if task.project:
        project_html = f'<span class="project-badge">◈ {_he(task.project)}</span>'

    # Subtask progress
    progress_html = ""
    if task.subtasks:
        done_sub = sum(1 for s in task.subtasks if s.done)
        total_sub = len(task.subtasks)
        pct = int((done_sub / total_sub) * 100) if total_sub else 0
        progress_html = (
            f'<div class="subtask-progress-wrap">'
            f'<div class="subtask-progress-bar-bg">'
            f'<div class="subtask-progress-bar-fill" style="width:{pct}%;"></div>'
            f'</div>'
            f'<div class="subtask-progress-label">{done_sub}/{total_sub} subtasks</div>'
            f'</div>'
        )

    card_html = (
        f'<div class="{card_cls}">'
        f'<div class="{title_cls}">{_he(task.title)}</div>'
        f'{body_html}'
        f'<div class="note-footer">'
        f'{priority_html}{due_html}{recurring_html}{tags_html}{project_html}'
        f'<span class="note-id">#{task.id:03d}</span>'
        f'</div>'
        f'{progress_html}'
        f'</div>'
    )

    # ── Columns ──────────────────────────────────────────────────────────────
    if is_manual:
        c_card, c_done, c_up, c_dn, c_edit, c_del = st.columns(
            [0.55, 0.09, 0.08, 0.08, 0.10, 0.10]
        )
    else:
        c_card, c_done, c_edit, c_del = st.columns([0.68, 0.11, 0.11, 0.10])

    with c_card:
        st.markdown(card_html, unsafe_allow_html=True)

    with c_done:
        st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
        if is_done:
            if st.button("↩", key=f"undo_{task.id}", help="Undo"):
                st.session_state["_status_action"] = {"id": task.id, "status": "todo"}
        else:
            if st.button("✓", key=f"done_{task.id}", help="Mark done"):
                st.session_state["_status_action"] = {"id": task.id, "status": "done"}

    if is_manual:
        with c_up:
            st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
            if st.button("↑", key=f"up_{task.id}", help="Move up"):
                tasks_all = load_tasks(STORAGE_PATH)
                same_status = [t for t in tasks_all if t.status == task.status and not t.archived]
                same_status_sorted = sorted(same_status, key=lambda x: x.order)
                idx = next((i for i, t in enumerate(same_status_sorted) if t.id == task.id), None)
                if idx is not None and idx > 0:
                    a, b = same_status_sorted[idx - 1], same_status_sorted[idx]
                    a.order, b.order = b.order, a.order
                    update_task(a, STORAGE_PATH)
                    update_task(b, STORAGE_PATH)
                st.rerun()

        with c_dn:
            st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
            if st.button("↓", key=f"dn_{task.id}", help="Move down"):
                tasks_all = load_tasks(STORAGE_PATH)
                same_status = [t for t in tasks_all if t.status == task.status and not t.archived]
                same_status_sorted = sorted(same_status, key=lambda x: x.order)
                idx = next((i for i, t in enumerate(same_status_sorted) if t.id == task.id), None)
                if idx is not None and idx < len(same_status_sorted) - 1:
                    a, b = same_status_sorted[idx], same_status_sorted[idx + 1]
                    a.order, b.order = b.order, a.order
                    update_task(a, STORAGE_PATH)
                    update_task(b, STORAGE_PATH)
                st.rerun()

    with c_edit:
        st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
        if st.button("✎", key=f"edit_{task.id}", help="Edit"):
            st.session_state[f"ed_{task.id}"] = not st.session_state.get(f"ed_{task.id}", False)
            st.rerun()

    with c_del:
        st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
        if st.button("⌫", key=f"del_{task.id}", help="Delete"):
            delete_task(task.id, STORAGE_PATH)
            st.session_state.bulk_selected.discard(task.id)
            st.rerun()

    # ── Subtasks + Notes expander (level-2, inside render_card) ──────────────
    has_subtasks = bool(task.subtasks)
    has_notes = bool(task.notes)

    if has_subtasks or has_notes:
        exp_label_parts = []
        if has_subtasks:
            done_sub = sum(1 for s in task.subtasks if s.done)
            exp_label_parts.append(f"Subtasks ({done_sub}/{len(task.subtasks)})")
        if has_notes:
            exp_label_parts.append(f"Notes ({len(task.notes)})")
        exp_label = " · ".join(exp_label_parts)

        with st.expander(exp_label, expanded=False):
            # Subtasks

            if has_subtasks:
                st.markdown("**Checklist**")
                for i, sub in enumerate(task.subtasks):
                    checked = st.checkbox(
                        sub.text, value=sub.done, key=f"sub_{task.id}_{i}"
                    )
                    if checked != sub.done:
                        task.subtasks[i].done = checked
                        task.updated_at = _now_iso()
                        update_task(task, STORAGE_PATH)
                        st.rerun()

            # Add subtask inline
            with st.form(f"add_sub_{task.id}", clear_on_submit=True):
                new_sub = st.text_input("Add subtask", placeholder="New subtask…", key=f"newsub_{task.id}")
                if st.form_submit_button("＋ Subtask"):
                    if new_sub.strip():
                        task.subtasks.append(Subtask(text=new_sub.strip()))
                        task.updated_at = _now_iso()
                        update_task(task, STORAGE_PATH)
                        st.rerun()

            st.markdown("---")

            # Notes
            if has_notes:
                st.markdown("**Notes**")
                for note in task.notes:
                    st.html(
                        f'<div style="background:#f9fafb;border-radius:8px;padding:0.5rem 0.75rem;'
                        f'margin-bottom:0.4rem;font-size:0.8rem;">'
                        f'<span style="color:#9ca3af;font-size:0.65rem;">{note.created_at}</span><br>'
                        f'{note.text}</div>'
                    )

            with st.form(f"add_note_{task.id}", clear_on_submit=True):
                new_note = st.text_area("Add note", height=60, placeholder="Write a note…", key=f"newnote_{task.id}")
                if st.form_submit_button("＋ Note"):
                    if new_note.strip():
                        task.notes.append(TaskNote(text=new_note.strip()))
                        task.updated_at = _now_iso()
                        update_task(task, STORAGE_PATH)
                        st.rerun()

            st.markdown("---")

    # ── Time tracking (outside expander so buttons always work) ──────────────
    total_s = _total_tracked_seconds(task)
    running = task.id in st.session_state.timers
    tc1, tc2 = st.columns([0.75, 0.25])
    with tc1:
        if running:
            start_iso = st.session_state.timers[task.id]
            try:
                elapsed = int((datetime.now() - datetime.fromisoformat(start_iso)).total_seconds())
            except Exception:
                elapsed = 0
            st.html(f'<div class="time-track-row time-running">⏱ {_fmt_duration(elapsed)} running &nbsp;·&nbsp; total {_fmt_duration(total_s)}</div>')
        elif total_s > 0:
            st.html(f'<div class="time-track-row">⏱ {_fmt_duration(total_s)} tracked</div>')
    with tc2:
        if running:
            if st.button("⏹ Stop", key=f"stop_timer_{task.id}"):
                start_iso = st.session_state.timers.pop(task.id)
                entry = TimeEntry(start=start_iso, end=_now_iso())
                task.time_entries.append(entry)
                task.updated_at = _now_iso()
                update_task(task, STORAGE_PATH)
                st.rerun()
        else:
            if st.button("▶ Start", key=f"start_timer_{task.id}"):
                st.session_state.timers[task.id] = _now_iso()
                st.rerun()

    # ── Edit panel ────────────────────────────────────────────────────────────
    if st.session_state.get(f"ed_{task.id}"):
        st.html(f"""
        <div style="background:#f0f2f5;border-radius:13px;padding:1.1rem 1.2rem;
                    margin:0.25rem 0 0.75rem;border:1px solid #e5e7eb;">
            <span style="font-size:0.7rem;font-weight:700;color:#6b7280;
                         text-transform:uppercase;letter-spacing:0.08em;">
                Editing #{task.id:03d}
            </span>
        </div>""")
        with st.form(f"ef_{task.id}"):
            e1, e2, e3 = st.columns([2, 1, 1])
            nt = e1.text_input("Title", value=task.title)
            np = e2.selectbox(
                "Priority", ["medium", "high", "low"],
                index=["medium", "high", "low"].index(task.priority)
            )
            dv = datetime.strptime(task.due_date, "%Y-%m-%d").date() if task.due_date else None
            nd = e3.date_input("Due date", value=dv)
            nb = st.text_area("Note", value=task.description, height=70)

            f1, f2 = st.columns(2)
            n_proj = f1.text_input("Project", value=task.project or "")
            rec_opts = ["none", "daily", "weekly", "monthly"]
            rec_val = task.recurring if task.recurring else "none"
            n_rec = f2.selectbox("Repeat", rec_opts, index=rec_opts.index(rec_val))

            _tag_opts = sorted(set(all_tags_global + list(task.tags)))
            n_tags = st.multiselect("Tags (pick existing)", options=_tag_opts, default=list(task.tags))
            n_new_tags = st.text_input("Add new tags (comma-separated)", placeholder="tag1, tag2…", key=f"newtags_{task.id}")

            sc, cc, ac = st.columns(3)
            sv = sc.form_submit_button("Save", use_container_width=True)
            cn = cc.form_submit_button("Cancel", use_container_width=True)
            arch = ac.form_submit_button(
                "Archive" if not task.archived else "Unarchive",
                use_container_width=True
            )

        if sv:
            task.title = nt.strip() or task.title
            task.description = nb.strip()
            task.priority = np
            task.due_date = str(nd) if nd else None
            task.project = n_proj.strip() or None
            task.recurring = n_rec if n_rec != "none" else None
            _typed_tags = [t.strip() for t in n_new_tags.split(",") if t.strip()]
            task.tags = list(dict.fromkeys(n_tags + _typed_tags))
            task.updated_at = _now_iso()
            update_task(task, STORAGE_PATH)
            st.session_state[f"ed_{task.id}"] = False
            st.rerun()
        if cn:
            st.session_state[f"ed_{task.id}"] = False
            st.rerun()
        if arch:
            task.archived = not task.archived
            task.updated_at = _now_iso()
            update_task(task, STORAGE_PATH)
            st.session_state[f"ed_{task.id}"] = False
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Main task layout
# ─────────────────────────────────────────────────────────────────────────────
is_manual = sort_by == "Manual"

if group_by_proj:
    # ── Group by project ─────────────────────────────────────────────────────
    projects_in_view = sorted(set(
        (t.project or "(No project)") for t in working_tasks
    ))
    for proj in projects_in_view:
        proj_tasks = [
            t for t in working_tasks
            if (t.project or "(No project)") == proj
        ]
        proj_todo = sorted([t for t in proj_tasks if t.status == "todo"], key=_sort_key)
        proj_done = sorted([t for t in proj_tasks if t.status == "done"], key=_sort_key)
        color = "#7c3aed"
        st.html(f'<div class="section-label sl-proj">◈ {proj} <span style="color:#9ca3af;font-weight:400;">({len(proj_tasks)} tasks)</span></div>')
        for task in proj_todo + proj_done:
            render_card(task, all_tags_global, is_manual=is_manual)
        st.html("<hr style='border-color:#e5e7eb;margin:1.5rem 0'>")

else:
    # ── Default: todo | done two-column layout ────────────────────────────────
    left, mid, right = st.columns([0.47, 0.02, 0.47], gap="small")

    with left:
        st.html(f'<div class="section-label sl-todo">In Progress · {len(todo_tasks)}</div>')
        if not todo_tasks:
            st.html('<div class="empty-note"><div class="empty-icon">📋</div>Nothing pending — you\'re all caught up!</div>')
        else:
            for task in todo_tasks:
                render_card(task, all_tags_global, is_manual=is_manual)

    with mid:
        st.html('<div class="col-gap"></div>')

    with right:
        st.html(f'<div class="section-label sl-done">Completed · {len(done_tasks)}</div>')
        if not done_tasks:
            st.html('<div class="empty-note"><div class="empty-icon">✦</div>Complete a task to see it here</div>')
        else:
            for task in done_tasks:
                render_card(task, all_tags_global, is_manual=is_manual)


# ─────────────────────────────────────────────────────────────────────────────
# Export CSV
# ─────────────────────────────────────────────────────────────────────────────
st.html("<hr style='border-color:#e5e7eb;margin:2rem 0 1rem'>")
exp_col, _ = st.columns([1, 4])
with exp_col:
    csv_data = _build_csv(all_tasks)
    st.download_button(
        label="⬇ Export CSV",
        data=csv_data,
        file_name=f"tasks_{today_str}.csv",
        mime="text/csv",
        key="export_csv",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Keyboard shortcut — 'n' focuses the new task title input
# ─────────────────────────────────────────────────────────────────────────────
components.html("""
<script>
(function(){
  window.parent.document.addEventListener('keydown', function(e){
    var tag = e.target.tagName.toLowerCase();
    if(tag === 'input' || tag === 'textarea' || e.ctrlKey || e.metaKey || e.altKey) return;
    if(e.key === 'n' || e.key === 'N'){
      // Find the sidebar title input by its placeholder
      var inputs = window.parent.document.querySelectorAll('input[placeholder="Task title…"]');
      if(inputs.length > 0){
        inputs[0].focus();
        e.preventDefault();
      }
    }
  });
})();
</script>
""", height=0)

# Trigger rerun for any pending status action (outside all column contexts)
if "_status_action" in st.session_state:
    st.rerun()
