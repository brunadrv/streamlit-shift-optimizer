"""SDI Labor Planning Shift Optimizer — Demo App

Self-contained prototype with hardcoded dummy data.
No Snowflake or Google Sheets connections required.
Safe to share publicly — contains no credentials or internal table names.
"""

from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, DataReturnMode, GridOptionsBuilder, GridUpdateMode, JsCode

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Labor Planning Shift Optimizer",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main-header    { font-size:1.5rem; font-weight:bold; color:#2E4057; margin-bottom:1rem; }
.section-header { font-size:1.4rem; font-weight:bold; color:#2E4057; margin:1.5rem 0 0.75rem;
                  border-bottom:2px solid #ddd; padding-bottom:0.4rem; }
.metric-large   { font-size:2.4rem; font-weight:bold; color:#1f77b4; }
.metric-label   { font-size:0.95rem; color:#666; margin-bottom:0.25rem; }
.metric-change  { font-size:0.9rem; font-weight:bold; }
.up   { color:#2ca02c; }
.down { color:#d62728; }
.shift-breakdown { font-size:0.75rem; color:#777; line-height:1.5; margin-top:4px; }
.demo-banner { background:#fff3cd; padding:12px 16px; border-radius:6px;
               margin-bottom:16px; font-size:0.9rem; border-left:4px solid #ffc107; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "hedge_rates" not in st.session_state:
    st.session_state.hedge_rates = {}
if "page_view" not in st.session_state:
    st.session_state.page_view = "Rollup View"

# ---------------------------------------------------------------------------
# Constants (inlined from apps/queries.py — no imports from apps/ needed)
# ---------------------------------------------------------------------------

LOCATIONS: dict[str, str] = {
    "NJ Newark":  "NJ Newark",
    "TX Irving":  "TX Irving",
    "AZ Phoenix": "AZ Phoenix",
    "CO Aurora":  "CO Aurora",
}

WORKER_TYPE_ORDER = ["FTE", "TEMP", "NEW HIRES", "FLEX", "WW/GS", "VEH/MEH", "PTO"]

DEFAULT_ATTENDANCE: dict[str, float] = {
    "FTE":       0.90,
    "TEMP":      0.84,
    "NEW HIRES": 0.50,
    "FLEX":      0.50,
    "WW/GS":     1.00,
    "VEH/MEH":   0.80,
    "PTO":       0.50,
}

# ---------------------------------------------------------------------------
# Dummy data generation
# ---------------------------------------------------------------------------

# Base rostered headcounts per (department, shift, worker_type)
_BASE_COUNTS: dict[str, dict] = {
    "Production": {
        "AM": {"FTE": 72, "TEMP": 50, "VEH/MEH": 6},
        "PM": {"FTE": 58, "TEMP": 40, "VEH/MEH": 6},
    },
    "Kitchen": {
        "AM": {"FTE": 42, "TEMP": 26},
        "PM": {"FTE": 35, "TEMP": 22},
    },
    "Sanitation": {
        "AM": {"FTE": 14, "TEMP": 10},
        "PM": {"FTE": 12, "TEMP": 8},
    },
    "Warehouse": {
        "AM": {"FTE": 22, "TEMP": 14, "FLEX": 4},
        "PM": {"FTE": 18, "TEMP": 12, "FLEX": 3},
    },
}

# Scale headcounts per DC so locations look distinct
_DC_SCALE: dict[str, float] = {
    "NJ Newark":  1.15,
    "TX Irving":  0.90,
    "AZ Phoenix": 1.00,
    "CO Aurora":  0.85,
}

# Day-of-week staffing factor (Sun = closed in this demo)
_DOW_SCALE: dict[str, float] = {
    "Mon": 1.00, "Tue": 0.98, "Wed": 1.02,
    "Thu": 0.97, "Fri": 0.95, "Sat": 0.60, "Sun": 0.0,
}


def get_roster_data(dc: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Return a realistic hardcoded roster DataFrame for the given DC + dates."""
    scale = _DC_SCALE.get(dc, 1.0)
    rows: list[dict] = []
    for d in pd.date_range(start_date, end_date):
        dow = d.strftime("%a")
        day_scale = _DOW_SCALE.get(dow, 0.0)
        if day_scale == 0.0:
            continue
        for dept, shifts in _BASE_COUNTS.items():
            for shift, wt_counts in shifts.items():
                for wt, base_count in wt_counts.items():
                    count = max(0, round(base_count * scale * day_scale))
                    for i in range(count):
                        rows.append({
                            "ASSOCIATE_ID":    f"{dept[:2].upper()}{shift[0]}{wt[:2]}{i:04d}",
                            "DEPARTMENT":      dept,
                            "WORKER_TYPE_RAW": wt,
                            "DC":              dc,
                            "SHIFT":           shift,
                            "SHIFT_DATE":      d.date(),
                            "DOW":             dow,
                            "WORKER_TYPE":     wt,
                        })
    if not rows:
        return pd.DataFrame(columns=["ASSOCIATE_ID", "DEPARTMENT", "WORKER_TYPE_RAW",
                                     "DC", "SHIFT", "SHIFT_DATE", "DOW", "WORKER_TYPE"])
    return pd.DataFrame(rows)


def get_punches(dc: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Return simulated clock-in records at the T4W attendance-rate fraction."""
    scale = _DC_SCALE.get(dc, 1.0)
    rows: list[dict] = []
    for d in pd.date_range(start_date, end_date):
        dow = d.strftime("%a")
        day_scale = _DOW_SCALE.get(dow, 0.0)
        if day_scale == 0.0:
            continue
        for dept, shifts in _BASE_COUNTS.items():
            for shift, wt_counts in shifts.items():
                pin  = "06:15" if shift == "AM" else "14:15"
                pout = "14:45" if shift == "AM" else "22:45"
                for wt, base_count in wt_counts.items():
                    roster_n = max(0, round(base_count * scale * day_scale))
                    punch_n  = round(roster_n * DEFAULT_ATTENDANCE.get(wt, 0.9))
                    for i in range(punch_n):
                        rows.append({
                            "ASSOCIATE_ID":    f"{dept[:2].upper()}{shift[0]}{wt[:2]}{i:04d}",
                            "PUNCH_DATE":      d.date(),
                            "DOW":             dow,
                            "PUNCH_IN":        pin,
                            "PUNCH_OUT":       pout,
                            "MINUTES_WORKED":  510,
                            "DEPARTMENT":      dept,
                            "WORKER_TYPE_RAW": wt,
                            "WORKER_TYPE":     wt,
                            "SHIFT":           shift,
                        })
    if not rows:
        return pd.DataFrame(columns=["ASSOCIATE_ID", "PUNCH_DATE", "DOW", "PUNCH_IN",
                                     "PUNCH_OUT", "MINUTES_WORKED", "DEPARTMENT",
                                     "WORKER_TYPE_RAW", "WORKER_TYPE", "SHIFT"])
    return pd.DataFrame(rows)


def get_needed_hc(dc_label: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Returns empty — app falls back to Expected × 1.22 buffer."""
    return pd.DataFrame(columns=["DEPARTMENT", "SHIFT", "SHIFT_DATE", "NEEDED_HC"])


def get_attendance_assumptions(dc_label: str) -> dict:
    """Returns empty — app falls back to DEFAULT_ATTENDANCE rates."""
    return {}


# ---------------------------------------------------------------------------
# Core HC logic — identical to app.py
# ---------------------------------------------------------------------------

def compute_expected_hc(
    roster_counts: dict[str, int],
    attendance_map: dict[tuple, float],
    dept: str,
    dow: str,
    shift: str,
    hedge_pct: float,
) -> dict[str, int]:
    expected: dict[str, int] = {}
    for wt in WORKER_TYPE_ORDER:
        base = attendance_map.get((dept, dow, shift, wt), DEFAULT_ATTENDANCE.get(wt, 0.9))
        if wt in ("FTE", "TEMP"):
            rate = max(0.0, min(1.0, base + hedge_pct / 100.0))
        else:
            rate = base
        expected[wt] = round(roster_counts.get(wt, 0) * rate)
    return expected


def aggregate_shift(
    roster_df: pd.DataFrame,
    punches_df: pd.DataFrame,
    department: str,
    d: date,
    shift: str,
) -> dict:
    r_mask = (
        (roster_df["DEPARTMENT"] == department)
        & (pd.to_datetime(roster_df["SHIFT_DATE"]).dt.date == d)
        & (roster_df["SHIFT"] == shift)
    )
    r_sub = roster_df[r_mask]

    p_mask = (
        (not punches_df.empty)
        and (punches_df["DEPARTMENT"] == department)
        & (pd.to_datetime(punches_df["PUNCH_DATE"]).dt.date == d)
        & (punches_df["SHIFT"] == shift)
    )
    p_sub = punches_df[p_mask] if not punches_df.empty else pd.DataFrame()

    roster_counts: dict[str, int] = {}
    punch_counts:  dict[str, int] = {}
    for wt in WORKER_TYPE_ORDER:
        wt_roster = r_sub[r_sub["WORKER_TYPE"] == wt]
        roster_counts[wt] = int(wt_roster["ASSOCIATE_ID"].nunique())
        if not p_sub.empty:
            wt_punches = p_sub[p_sub["WORKER_TYPE"] == wt]
            punch_counts[wt] = int(wt_punches["ASSOCIATE_ID"].nunique())
        else:
            punch_counts[wt] = 0

    return {
        "roster":     roster_counts,
        "punches":    punch_counts,
        "employees":  r_sub.to_dict("records"),
        "punch_rows": p_sub.to_dict("records") if not p_sub.empty else [],
    }


def build_shift_metrics(
    roster_df: pd.DataFrame,
    punches_df: pd.DataFrame,
    needed_hc_df: pd.DataFrame,
    attendance_map: dict[tuple, float],
    dept: str,
    selected_dates: list[date],
    shifts: list[str],
    hedge_rates: dict[str, float],
) -> dict[str, dict]:
    metrics: dict[str, dict] = {}
    for d in selected_dates:
        dow = d.strftime("%a")
        for shift in shifts:
            key       = f"{d.strftime('%Y-%m-%d')} {dow} {shift}"
            hedge_key = f"{d.strftime('%Y-%m-%d')}_{shift}"
            hedge     = float(hedge_rates.get(hedge_key, 0.0))

            agg      = aggregate_shift(roster_df, punches_df, dept, d, shift)
            expected = compute_expected_hc(agg["roster"], attendance_map, dept, dow, shift, hedge)

            total_expected = sum(expected.values())
            total_punches  = sum(agg["punches"].values())

            needed = 0
            if needed_hc_df is not None and not needed_hc_df.empty:
                mask = (
                    (needed_hc_df["DEPARTMENT"] == dept)
                    & (needed_hc_df["SHIFT_DATE"] == d)
                    & (needed_hc_df["SHIFT"] == shift)
                )
                needed = int(needed_hc_df[mask]["NEEDED_HC"].sum())
            if needed == 0:
                needed = round(total_expected * 1.22)

            metrics[key] = {
                "roster":         agg["roster"],
                "expected":       expected,
                "punches":        agg["punches"],
                "employees":      agg["employees"],
                "punch_rows":     agg["punch_rows"],
                "total_expected": total_expected,
                "total_needed":   needed,
                "total_gap":      total_expected - needed,
                "total_punches":  total_punches,
                "hedge":          hedge,
                "date":           d,
                "shift":          shift,
                "dow":            dow,
            }
    return metrics


# ---------------------------------------------------------------------------
# AG-Grid: HC breakdown table — identical to app.py
# ---------------------------------------------------------------------------

def build_hc_aggrid(shift_metrics: dict[str, dict]):
    columns_list = sorted(shift_metrics.keys())
    col_fields   = {key: f"S{i + 1}" for i, key in enumerate(columns_list)}

    def _att_rate(m: dict, wt: str) -> float:
        ros = m["roster"].get(wt, 0)
        exp = m["expected"].get(wt, 0)
        return (exp / ros) if ros > 0 else 0.0

    def _hdr(label: str) -> dict:
        row = {"Metric": label, "_type": "header"}
        for key in columns_list:
            row[col_fields[key]] = ""
        return row

    def _row(label: str, fn, row_type: str = "data") -> dict:
        row = {"Metric": label, "_type": row_type}
        for key in columns_list:
            row[col_fields[key]] = fn(shift_metrics[key])
        return row

    rows = [
        _hdr("OVERVIEW"),
        _row("Needed Headcount",          lambda m: m["total_needed"]),
        _row("Expected Headcount",         lambda m: m["total_expected"]),
        _row("Expected HC vs. Needed HC",  lambda m: m["total_expected"] - m["total_needed"], "gap"),
        _row("Actual Punches",             lambda m: m["total_punches"]),
        _row("Actual Attendance",
             lambda m: (m["total_punches"] / m["total_expected"]) if m["total_expected"] > 0 else 0.0,
             "pct"),
        _hdr("EXPECTED HEADCOUNTS"),
        _row("Expected HC — HF",      lambda m: m["expected"].get("FTE", 0)),
        _row("Expected HC — Temps",   lambda m: m["expected"].get("TEMP", 0)),
        _row("Expected HC — VEH/MEH", lambda m: m["expected"].get("VEH/MEH", 0)),
        _hdr("ROSTER HEADCOUNTS"),
        _row("Roster HC — HF",        lambda m: m["roster"].get("FTE", 0)),
        _row("Roster HC — Temps",     lambda m: m["roster"].get("TEMP", 0)),
        _row("Roster HC — VEH/MEH",   lambda m: m["roster"].get("VEH/MEH", 0)),
        _row("Roster HC — Day Labor",
             lambda m: m["roster"].get("FLEX", 0) + m["roster"].get("WW/GS", 0)),
        _hdr("ATTENDANCE"),
        _row("Attendance Assumption HF",    lambda m: _att_rate(m, "FTE"),     "pct"),
        _row("Attendance Assumption Temps", lambda m: _att_rate(m, "TEMP"),    "pct"),
        _row("Attendance Assumption VEH",   lambda m: _att_rate(m, "VEH/MEH"), "pct"),
    ]

    df = pd.DataFrame(rows)

    row_style = JsCode("""
    function(p) {
        var t = p.data['_type'];
        if (t === 'header') return {'background-color':'#2E4057','color':'white',
            'font-weight':'bold','font-size':'10px','letter-spacing':'0.05em'};
        return null;
    }""")

    left_style = JsCode("""
    function(p) {
        if (p.data['_type'] === 'header')
            return {'background-color':'#2E4057','color':'white',
                    'font-weight':'bold','padding-left':'10px'};
        return {'background-color':'#fafafa'};
    }""")

    val_style = JsCode("""
    function(p) {
        if (p.data['_type'] === 'header')
            return {'background-color':'#2E4057','color':'white','text-align':'center'};
        var s = {'text-align':'center','font-size':'11px'};
        if (p.data['_type'] === 'gap') {
            var v = parseFloat(p.value);
            if (!isNaN(v) && v !== 0) {
                if (v < 0) { s['color']='#8b0000'; s['font-weight']='600'; }
                else       { s['color']='#2d6f2f'; s['font-weight']='600'; }
            }
        }
        return s;
    }""")

    val_fmt = JsCode("""
    function(p) {
        if (p.data['_type'] === 'header' || p.value === '' || p.value == null) return '';
        var v = parseFloat(p.value);
        if (isNaN(v)) return p.value;
        if (p.data['_type'] === 'gap') return (v > 0 ? '+' : '') + v;
        if (p.data['_type'] === 'pct') return v > 0 ? (v * 100).toFixed(1) + '%' : '—';
        return v;
    }""")

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=False, sortable=False, filter=False)
    gb.configure_grid_options(
        rowHeight=32, headerHeight=55,
        suppressMovableColumns=True,
        getRowStyle=row_style,
        suppressColumnVirtualisation=True,
    )

    col_defs = [{
        "field":      "Metric",
        "headerName": "",
        "cellStyle":  left_style,
        "editable":   False,
        "minWidth": 240, "width": 265,
        "pinned": "left", "suppressSizeToFit": True,
    }]

    date_groups: dict[str, list[str]] = {}
    for key in columns_list:
        parts = key.split(" ")
        grp   = f"{parts[0]} {parts[1]}"
        date_groups.setdefault(grp, []).append(key)

    for grp, keys in date_groups.items():
        segs     = grp.split("-")
        last     = segs[-1].split(" ")
        friendly = f"{segs[1]}/{last[0]} {last[1]}" if len(segs) == 3 else grp
        children = []
        for key in keys:
            shift_n = key.split()[-1]
            children.append({
                "field":          col_fields[key],
                "headerName":     shift_n,
                "editable":       False,
                "cellStyle":      val_style,
                "valueFormatter": val_fmt,
                "minWidth": 85, "width": 95,
            })
        col_defs.append({"headerName": friendly, "children": children})

    opts = gb.build()
    opts["columnDefs"] = col_defs

    custom_css = {
        ".ag-header-group-cell": {
            "font-size": "11px", "font-weight": "600",
            "border-right": "1px solid #dee2e6 !important", "text-align": "center",
        },
        ".ag-header-cell": {
            "font-size": "10px", "font-weight": "500",
            "border-right": "1px solid #dee2e6 !important",
        },
        ".ag-cell": {
            "border-right": "1px solid #dee2e6 !important",
            "border-bottom": "1px solid #dee2e6 !important",
        },
        ".ag-root-wrapper": {"border": "1px solid #dee2e6"},
    }

    return df, opts, custom_css, 55 + len(rows) * 33 + 40


# ---------------------------------------------------------------------------
# KPI helpers — identical to app.py
# ---------------------------------------------------------------------------

def render_kpi(label: str, value: int, tooltip: str) -> None:
    st.markdown(
        f'<div class="metric-label">{label}'
        f'  <span title="{tooltip}" style="cursor:help;color:#999;font-size:0.8rem;">ⓘ</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="metric-large">{value:,}</div>', unsafe_allow_html=True)


def shift_breakdown_html(
    shift_metrics: dict[str, dict],
    metric: str,
    selected_dates: list[date],
    shifts: list[str],
) -> str:
    lines = []
    for d in selected_dates:
        dow = d.strftime("%a")
        parts = []
        for shift in shifts:
            key = f"{d.strftime('%Y-%m-%d')} {dow} {shift}"
            val = shift_metrics.get(key, {}).get(metric, 0)
            parts.append(f"{shift}: {val:,}")
        lines.append(f"{dow} {' | '.join(parts)}")
    return "<br>".join(lines)


# ---------------------------------------------------------------------------
# Roster table helper
# ---------------------------------------------------------------------------

def build_roster_table(employees: list[dict]) -> None:
    if not employees:
        st.info("No roster records for this slot.")
        return
    df = pd.DataFrame(employees)[["ASSOCIATE_ID", "WORKER_TYPE", "DEPARTMENT", "SHIFT"]].rename(
        columns={"ASSOCIATE_ID": "ID", "WORKER_TYPE": "Type", "DEPARTMENT": "Dept", "SHIFT": "Shift"}
    )
    st.dataframe(df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Rollup View — identical to app.py
# ---------------------------------------------------------------------------

def rollup_view(dc: str, dc_label: str) -> None:
    st.markdown('<h1 class="main-header">Labor Planning — Rollup View</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="demo-banner">🔔 <strong>Demo mode</strong> — simulated data only. '
        "Needed HC uses a ×1.22 buffer; attendance rates use T4W defaults.</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1, 2])
    with c1:
        week_start = st.date_input(
            "Week starting (Monday)",
            value=date.today() - timedelta(days=date.today().weekday()),
            key="rollup_week_start",
        )
    with c2:
        avail = [week_start + timedelta(days=i) for i in range(7)]
        selected_dates = st.multiselect(
            "Dates", options=avail, default=avail[:5],
            format_func=lambda d: d.strftime("%Y-%m-%d %a"),
            key="rollup_dates",
        )

    if not selected_dates:
        st.warning("Select at least one date.")
        return

    week_end   = week_start + timedelta(days=6)
    roster_df  = get_roster_data(dc, week_start.isoformat(), week_end.isoformat())
    punches_df = get_punches(dc, week_start.isoformat(), week_end.isoformat())
    needed_df  = get_needed_hc(dc_label, week_start.isoformat(), week_end.isoformat())
    att_map    = get_attendance_assumptions(dc_label)

    if roster_df.empty:
        st.info("No roster data for the selected period.")
        return

    departments = sorted(roster_df["DEPARTMENT"].dropna().unique())
    if not departments:
        st.info("No departments found.")
        return

    shifts = ["AM", "PM"]
    slots  = [(d, s) for d in selected_dates for s in shifts]
    col_fields: dict[tuple, str] = {slot: f"S{i + 1}" for i, slot in enumerate(slots)}

    # Build per-(dept, date, shift) metric values
    raw: dict[tuple, dict] = {}
    for dept in departments:
        dept_metrics = build_shift_metrics(
            roster_df, punches_df, needed_df, att_map,
            dept, selected_dates, shifts, hedge_rates={},
        )
        for d in selected_dates:
            dow = d.strftime("%a")
            for shift in shifts:
                mkey = f"{d.strftime('%Y-%m-%d')} {dow} {shift}"
                m    = dept_metrics.get(mkey, {})
                exp  = m.get("total_expected", 0)
                pun  = m.get("total_punches",  0)
                need = m.get("total_needed",   0)
                raw[(dept, d, shift)] = {
                    "needed":   need,
                    "expected": exp,
                    "punches":  pun,
                    "exp_gap":  exp - need,
                    "act_gap":  pun - exp,
                }

    SECTIONS = [
        ("Total Needed HC",       "needed",   False),
        ("Total Expected HC",     "expected", False),
        ("Total Expected HC Gap", "exp_gap",  True),
        ("Total Actual Punches",  "punches",  False),
        ("Total Actual HC Gap",   "act_gap",  True),
    ]

    all_rows: list[dict] = []
    for section_label, metric_key, is_gap in SECTIONS:
        # TOTAL row (green)
        total_row = {"Label": section_label, "_type": "total", "_is_gap": is_gap}
        for slot, field in col_fields.items():
            d, s = slot
            total_row[field] = sum(
                raw.get((dept, d, s), {}).get(metric_key, 0) for dept in departments
            )
        all_rows.append(total_row)
        # Dept sub-rows
        for dept in departments:
            dept_row = {"Label": dept, "_type": "dept", "_is_gap": is_gap}
            for slot, field in col_fields.items():
                d, s = slot
                dept_row[field] = raw.get((dept, d, s), {}).get(metric_key, 0)
            all_rows.append(dept_row)

    df = pd.DataFrame(all_rows)

    row_style = JsCode("""
    function(p) {
        if (p.data['_type'] === 'total')
            return {'background-color':'#e8f6e8','font-weight':'600'};
        return null;
    }""")

    label_style = JsCode("""
    function(p) {
        if (p.data['_type'] === 'total')
            return {'font-weight':'600','font-size':'11px','padding-left':'8px',
                    'background-color':'#e8f6e8','color':'#1a4d1a'};
        return {'font-size':'11px','padding-left':'22px','color':'#444'};
    }""")

    val_style = JsCode("""
    function(p) {
        var s = {'text-align':'center','font-size':'11px'};
        if (p.data['_type'] === 'total') s['background-color'] = '#e8f6e8';
        if (p.data['_is_gap']) {
            var v = parseFloat(p.value);
            if (!isNaN(v) && v !== 0) {
                if (v < 0) { s['color']='#8b0000'; s['font-weight']='600'; }
                else       { s['color']='#2d6f2f'; s['font-weight']='600'; }
            }
        }
        return s;
    }""")

    val_fmt = JsCode("""
    function(p) {
        if (p.value == null) return '';
        var v = parseFloat(p.value);
        if (isNaN(v)) return '';
        if (p.data['_is_gap']) return (v > 0 ? '+' : '') + v;
        if (v === 0 && p.data['_type'] !== 'total') return '';
        return v;
    }""")

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=False, sortable=False, filter=False)
    gb.configure_grid_options(
        rowHeight=28, headerHeight=65,
        suppressMovableColumns=True,
        getRowStyle=row_style,
        suppressColumnVirtualisation=True,
    )

    col_defs = [{
        "field":      "Label",
        "headerName": dc_label,
        "cellStyle":  label_style,
        "editable":   False,
        "minWidth": 210, "width": 230,
        "pinned": "left", "suppressSizeToFit": True,
    }]

    date_groups: dict[str, list] = {}
    for slot in slots:
        d, s = slot
        grp  = d.strftime("%m/%d %a")
        date_groups.setdefault(grp, []).append(slot)

    for grp, grp_slots in date_groups.items():
        children = []
        for slot in grp_slots:
            children.append({
                "field":          col_fields[slot],
                "headerName":     slot[1],
                "cellStyle":      val_style,
                "valueFormatter": val_fmt,
                "editable":       False,
                "minWidth": 72, "width": 78,
            })
        col_defs.append({"headerName": grp, "children": children})

    opts = gb.build()
    opts["columnDefs"] = col_defs

    custom_css = {
        ".ag-header-group-cell": {
            "font-size": "11px", "font-weight": "600",
            "border-right": "1px solid #dee2e6 !important", "text-align": "center",
        },
        ".ag-header-cell": {
            "font-size": "10px", "font-weight": "500",
            "border-right": "1px solid #dee2e6 !important",
        },
        ".ag-cell": {
            "border-right": "1px solid #dee2e6 !important",
            "border-bottom": "1px solid #dee2e6 !important",
        },
        ".ag-root-wrapper": {"border": "1px solid #dee2e6"},
    }

    st.markdown('<div class="section-header">Department Summary</div>', unsafe_allow_html=True)
    AgGrid(
        df, gridOptions=opts, update_mode=GridUpdateMode.NO_UPDATE,
        data_return_mode=DataReturnMode.AS_INPUT,
        fit_columns_on_grid_load=False, theme="streamlit",
        height=65 + len(all_rows) * 30 + 40,
        allow_unsafe_jscode=True, custom_css=custom_css,
    )


# ---------------------------------------------------------------------------
# Detailed View — identical to app.py
# ---------------------------------------------------------------------------

def detailed_view(dc: str, dc_label: str) -> None:
    st.markdown('<h1 class="main-header">Labor Planning — Detailed View</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="demo-banner">🔔 <strong>Demo mode</strong> — simulated data only. '
        "Needed HC uses a ×1.22 buffer; attendance rates use T4W defaults.</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.markdown("**Week starting**")
        week_start = st.date_input(
            "", value=date.today() - timedelta(days=date.today().weekday()),
            label_visibility="collapsed", key="det_week",
        )
    with c2:
        st.markdown("**Shifts**")
        shifts = st.multiselect(
            "", ["AM", "PM"], default=["AM", "PM"],
            label_visibility="collapsed", key="det_shifts",
        )

    if not shifts:
        st.warning("Select at least one shift.")
        return

    week_end   = week_start + timedelta(days=6)
    roster_df  = get_roster_data(dc, week_start.isoformat(), week_end.isoformat())
    punches_df = get_punches(dc, week_start.isoformat(), week_end.isoformat())
    needed_df  = get_needed_hc(dc_label, week_start.isoformat(), week_end.isoformat())
    att_map    = get_attendance_assumptions(dc_label)

    departments = sorted(roster_df["DEPARTMENT"].dropna().unique()) if not roster_df.empty else []

    cd1, cd2, _ = st.columns([1.2, 1.4, 1])
    with cd1:
        st.markdown("**Department**")
        if departments:
            dept = st.selectbox("", departments, label_visibility="collapsed", key="det_dept")
        else:
            st.info("No departments in roster data for this week.")
            return
    with cd2:
        st.markdown("**Dates**")
        avail_dates    = [week_start + timedelta(days=i) for i in range(7)]
        selected_dates = st.multiselect(
            "", options=avail_dates, default=avail_dates[:5],
            format_func=lambda d: d.strftime("%Y-%m-%d %a"),
            label_visibility="collapsed", key="det_dates",
        )

    if not selected_dates:
        st.warning("Select at least one date.")
        return

    shift_metrics = build_shift_metrics(
        roster_df, punches_df, needed_df, att_map,
        dept, selected_dates, shifts, st.session_state.hedge_rates,
    )

    total_needed   = sum(m["total_needed"]   for m in shift_metrics.values())
    total_expected = sum(m["total_expected"] for m in shift_metrics.values())
    total_gap      = total_expected - total_needed
    total_punches  = sum(m["total_punches"]  for m in shift_metrics.values())

    st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi("Needed HC", total_needed, "Expected × 1.22 buffer (demo fallback)")
        st.markdown(
            f'<div class="shift-breakdown">'
            f'{shift_breakdown_html(shift_metrics, "total_needed", selected_dates, shifts)}'
            f'</div>', unsafe_allow_html=True,
        )
    with k2:
        render_kpi("Expected HC", total_expected, "Roster × T4W attendance rate")
        st.markdown(
            f'<div class="shift-breakdown">'
            f'{shift_breakdown_html(shift_metrics, "total_expected", selected_dates, shifts)}'
            f'</div>', unsafe_allow_html=True,
        )
    with k3:
        gc = "#d62728" if total_gap < 0 else "#28a745"
        st.markdown(
            f'<div class="metric-label">Gap in HC '
            f'<span title="Expected − Needed" style="cursor:help;color:#999;font-size:0.8rem;">ⓘ</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="metric-large" style="color:{gc};">{total_gap:+,}</div>',
                    unsafe_allow_html=True)
        if total_gap < 0:
            pct = abs(round(total_gap / total_needed * 100)) if total_needed else 0
            st.markdown(f'<div class="metric-change down">↘ Understaffed by {pct}%</div>',
                        unsafe_allow_html=True)
        elif total_gap > 0:
            pct = abs(round(total_gap / total_needed * 100)) if total_needed else 0
            st.markdown(f'<div class="metric-change up">↗ Overstaffed by {pct}%</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-change">✅ Fully staffed</div>',
                        unsafe_allow_html=True)
    with k4:
        render_kpi("Actual Punches", total_punches, "Simulated clock-in records")
        st.markdown(
            f'<div class="shift-breakdown">'
            f'{shift_breakdown_html(shift_metrics, "total_punches", selected_dates, shifts)}'
            f'</div>', unsafe_allow_html=True,
        )

    if roster_df.empty:
        st.info("No roster data for this week.")
        return

    st.markdown(f'<div class="section-header">{dept} — Shift Detail</div>',
                unsafe_allow_html=True)
    hc_df, hc_opts, hc_css, hc_h = build_hc_aggrid(shift_metrics)
    AgGrid(
        hc_df, gridOptions=hc_opts,
        update_mode=GridUpdateMode.NO_UPDATE,
        data_return_mode=DataReturnMode.AS_INPUT,
        fit_columns_on_grid_load=False, theme="streamlit",
        height=hc_h, allow_unsafe_jscode=True, custom_css=hc_css,
    )

    st.markdown(
        f"---\n**SDI Labor Planning Demo** | {datetime.now().strftime('%Y-%m-%d %H:%M')} | {dc_label}",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    st.sidebar.markdown("# 🏭 Labor Planning")
    st.sidebar.markdown("---")

    loc_labels     = list(LOCATIONS.keys())
    st.sidebar.markdown("**Location**")
    selected_label = st.sidebar.selectbox(
        "", loc_labels, label_visibility="collapsed", key="sidebar_dc",
    )
    dc = LOCATIONS[selected_label]

    st.sidebar.markdown("---")
    page_view = st.sidebar.radio(
        "View",
        ["Rollup View", "Detailed View"],
        index=0 if st.session_state.page_view == "Rollup View" else 1,
    )
    st.session_state.page_view = page_view

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Rollup View** — dept-level summary across dates.\n\n"
        "**Detailed View** — full HC × Attendance breakdown."
    )

    if page_view == "Rollup View":
        rollup_view(dc, selected_label)
    else:
        detailed_view(dc, selected_label)


if __name__ == "__main__":
    main()
