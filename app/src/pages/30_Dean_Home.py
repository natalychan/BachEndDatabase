import logging
logger = logging.getLogger(__name__)

import os
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from modules.nav import SideBarLinks
# from streamlit_extras.app_logo import add_logo  # unused right now

st.set_page_config(layout='wide')

# Sidebar
SideBarLinks()

API_BASE = os.getenv("API_BASE", "http://api:4000/api").rstrip("/")
TIMEOUT = int(os.getenv("API_TIMEOUT", "8"))

first_name = st.session_state.get("first_name", "Colleague")
st.title(f"Welcome Dean, {first_name}.")
st.header("Dean Overview")

left_top, right_top = st.columns(2, gap="large")
left_bottom, right_bottom = st.columns(2, gap="large")

@st.cache_data(ttl=60, show_spinner=False)
def get_json(path, params=None):
    r = requests.get(f"{API_BASE}{path}", params=params or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=60, show_spinner=False)
def list_colleges():
    # use avg GPA endpoint to derive names (field: 'college')
    data = get_json("/colleges/averages/gpa")
    return sorted(pd.DataFrame(data)["college"].dropna().astype(str).unique().tolist())

@st.cache_data(ttl=60, show_spinner=False)
def enrollment_trend(cname: str) -> pd.DataFrame:
    data = get_json(f"/colleges/{cname}/enrollment-trend")
    df = pd.DataFrame(data)
    if not {"period", "enrollment"}.issubset(df.columns):
        return pd.DataFrame(columns=["period","enrollment"])
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    df["enrollment"] = pd.to_numeric(df["enrollment"], errors="coerce").fillna(0)
    df = df.dropna(subset=["period"]).sort_values("period")
    df["CollegeName"] = cname
    return df

# --- Top-right panel ---
with right_top:
    st.caption("Enrollment Trends")

    API_BASE = os.getenv("API_BASE", "http://api:4000/api").rstrip("/")
    TIMEOUT = int(os.getenv("API_TIMEOUT", "8"))

    def _get(path, params=None):
        url = f"{API_BASE}{path if path.startswith('/') else '/'+path}"
        r = requests.get(url, params=params or {}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    # 1) Get college names
    try:
        data_gpa = _get("/colleges/averages/gpa")
        df_names = pd.DataFrame(data_gpa)
        if "college" not in df_names.columns:
            raise ValueError("Expected 'college' in /colleges/averages/gpa response")
        college_names = sorted(df_names["college"].dropna().astype(str).unique().tolist())
    except Exception as e:
        st.warning(f"Could not load colleges — {e}")
        college_names = []

    # 2) Picker
    selected = st.multiselect(
        "Select departments to compare",
        options=college_names,
        default=college_names[: min(3, len(college_names))],
        label_visibility="collapsed",
        key="enroll_trend_select",
    )

    # 3) Pull trends
    frames = []
    for cname in selected:
        try:
            rows = _get(f"/colleges/{cname}/enrollment-trend")
            df = pd.DataFrame(rows)
            if {"period", "enrollment"}.issubset(df.columns):
                df["period"] = pd.to_numeric(df["period"], errors="coerce")
                df["enrollment"] = pd.to_numeric(df["enrollment"], errors="coerce").fillna(0)
                df = df.dropna(subset=["period"]).sort_values("period")
                df["CollegeName"] = cname
                frames.append(df[["period", "enrollment", "CollegeName"]])
        except Exception:
            # ignore a single department failure
            continue

    if not frames:
        st.info("No enrollment trend data available yet.")
    else:
        df_trend = pd.concat(frames, ignore_index=True)
        fig = px.line(
            df_trend, x="period", y="enrollment", color="CollegeName", markers=True,
            labels={"period": "Year", "enrollment": "Enrollment"}
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), legend_title_text="Dept")
        st.plotly_chart(fig, use_container_width=True)


# ---------------- LEFT TOP: 4 KPI sub-panels ----------------
with left_top:
    sub_lt, sub_rt = st.columns(2, gap="medium")
    sub_lb, sub_rb = st.columns(2, gap="medium")

    # We'll reuse the same GPA endpoint to get the list of colleges dynamically.
    try:
        r = requests.get(f"{API_BASE}/colleges/averages/gpa", timeout=TIMEOUT)
        r.raise_for_status()
        data_gpa = r.json()
        df_gpa_all = pd.DataFrame(data_gpa)
        if "college" not in df_gpa_all.columns:
            raise ValueError("Expected field 'college' in avg GPA response")
        college_names = sorted(df_gpa_all["college"].dropna().astype(str).unique().tolist())
    except Exception as e:
        # Fallback list if API not ready
        st.caption(f"Using sample colleges — {e}")
        college_names = ["Music", "Dance", "Theatre", "Media", "Design"]

    # ---- Enrollment per College ----
    with sub_lt:
        st.caption("Enrollment per College")
        try:
            rows = []
            for cname in college_names:
                url = f"{API_BASE}/colleges/{cname}/enrollment"
                res = requests.get(url, timeout=TIMEOUT)
                if res.status_code == 200:
                    payload = res.json()  # { "total_enrollment": N }
                    total = payload.get("total_enrollment", 0)
                else:
                    total = 0
                rows.append({"CollegeName": cname, "Enrollment": total})

            df_enroll = pd.DataFrame(rows)

        except Exception as e:
            st.caption(f"Using sample data — {e}")
            df_enroll = pd.DataFrame({
                "CollegeName": ["Music", "Dance", "Theatre", "Media", "Design"],
                "Enrollment": np.array([0, 0, 0, 0, 0])
            })

        fig = px.bar(
            df_enroll,
            x="CollegeName",
            y="Enrollment",
            labels={"CollegeName": "College", "Enrollment": "Enrollment"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Student / Teacher Ratio ----
    with sub_rt:
        st.caption("Student / Teacher Ratio (by College)")
        try:
            url = f"{API_BASE}/colleges/metrics/student-teacher-ratio"
            r = requests.get(url, timeout=TIMEOUT)
            r.raise_for_status()
            df_ratio = pd.DataFrame(r.json())
            need = {"college", "student_teacher_ratio"}
            if not need.issubset(df_ratio.columns):
                raise ValueError(f"Missing fields: {need - set(df_ratio.columns)}")
            # Map to requested display key
            df_ratio["CollegeName"] = df_ratio["college"].astype(str)
            df_ratio["StudentsPerTeacher"] = pd.to_numeric(
                df_ratio["student_teacher_ratio"], errors="coerce"
            ).fillna(0)

        except Exception as e:
            st.caption(f"Using sample data — {e}")
            df_ratio = pd.DataFrame({
                "CollegeName": ["Music", "Dance", "Theatre", "Media", "Design"],
                "StudentsPerTeacher": np.round(np.random.uniform(8, 22, 5), 1)
            })

        fig = px.bar(
            df_ratio,
            x="CollegeName",
            y="StudentsPerTeacher",
            labels={"CollegeName": "College", "StudentsPerTeacher": "Students per Teacher"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Average GPA by College ----
    with sub_lb:
        st.caption("Average GPA by College")
        try:
            if "df_gpa_all" not in locals() or df_gpa_all.empty:
                r = requests.get(f"{API_BASE}/colleges/averages/gpa", timeout=TIMEOUT)
                r.raise_for_status()
                df_gpa_all = pd.DataFrame(r.json())

            if not {"college", "average_gpa"}.issubset(df_gpa_all.columns):
                raise ValueError("Expected fields 'college' and 'average_gpa'")

            df_gpa = pd.DataFrame({
                "CollegeName": df_gpa_all["college"].astype(str),
                "AverageGPA": pd.to_numeric(df_gpa_all["average_gpa"], errors="coerce")
            })

        except Exception as e:
            st.caption(f"Using sample data — {e}")
            df_gpa = pd.DataFrame({
                "CollegeName": ["Music", "Dance", "Theatre", "Media", "Design"],
                "AverageGPA": np.round(np.random.uniform(2.6, 3.7, 5), 2)
            })

        fig = px.bar(
            df_gpa,
            x="CollegeName",
            y="AverageGPA",
            labels={"CollegeName": "College", "AverageGPA": "Avg GPA"},
            range_y=[0, 4]
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Budget by College
    with sub_rb:
        st.caption("Budget by College ($)")
        try:
            rows = []
            for cname in college_names:
                url = f"{API_BASE}/colleges/{cname}/budget"
                res = requests.get(url, timeout=TIMEOUT)
                if res.status_code == 200:
                    payload = res.json()  # { collegeName, budget, status, dean }
                    budget = pd.to_numeric(payload.get("budget", 0), errors="coerce")
                else:
                    budget = 0
                rows.append({"CollegeName": cname, "Budget": float(budget) if pd.notna(budget) else 0.0})

            df_budget = pd.DataFrame(rows)

        except Exception as e:
            st.caption(f"Using sample data — {e}")
            df_budget = pd.DataFrame({
                "CollegeName": ["Music", "Dance", "Theatre", "Media", "Design"],
                "Budget": np.array([0, 0, 0, 0, 0], dtype=float)
            })

        fig = px.bar(
            df_budget,
            x="CollegeName",
            y="Budget",
            labels={"CollegeName": "College", "Budget": "Budget ($)"},
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------- LEFT BOTTOM: Course Performance Overview ----------------
with left_bottom:
    st.subheader("Course Performance Overview")

    API_BASE = os.getenv("API_BASE", "http://api:4000/api").rstrip("/")
    TIMEOUT = int(os.getenv("API_TIMEOUT", "8"))

    def _get(path, params=None):
        url = f"{API_BASE}{path if path.startswith('/') else '/'+path}"
        r = requests.get(url, params=params or {}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    # 1) Load college names from avg GPA endpoint
    try:
        data_gpa = _get("/colleges/averages/gpa")
        df_names = pd.DataFrame(data_gpa)
        if "college" not in df_names.columns:
            raise ValueError("Expected 'college' in /colleges/averages/gpa response")
        college_names = sorted(df_names["college"].dropna().astype(str).unique().tolist())
    except Exception as e:
        st.warning(f"Could not load colleges — {e}")
        college_names = []

    # 2) Picker
    selected = st.multiselect(
        "Departments",
        options=college_names,
        default=college_names[: min(3, len(college_names))],
        key="perf_overview_select",
    )

    # 3)Get performance per selected college and build the table
    rows = []
    for cname in selected:
        try:
            perf = _get(f"/colleges/{cname}/performance")
            # perf["by_course"] -> list of {course_id, course_name, avg_student_gpa}
            for row in perf.get("by_course", []):
                rows.append({
                    "CollegeName": cname,
                    "course_id": row.get("course_id"),
                    "course_name": row.get("course_name"),
                    "avg_student_gpa": row.get("avg_student_gpa"),
                })
        except Exception as e:
            #one college failing shouldn't block the table
            st.caption(f"Note: {cname} performance fetch failed — {e}")

    if not rows:
        st.info("No course performance data available yet.")
    else:
        df_perf = pd.DataFrame(rows)
        # Clean types for nice sorting
        df_perf["avg_student_gpa"] = pd.to_numeric(df_perf["avg_student_gpa"], errors="coerce")
        #sort by GPA descending
        sort_desc = st.checkbox("Sort by Avg GPA (desc)", value=True, key="sort_gpa_desc")
        if sort_desc:
            df_perf = df_perf.sort_values(["CollegeName", "avg_student_gpa"], ascending=[True, False])
        else:
            df_perf = df_perf.sort_values(["CollegeName", "course_name"])

        # Display
        st.dataframe(
            df_perf.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

# ---------------- RIGHT BOTTOM: Quick Lists ----------------
with right_bottom:
    st.subheader("Attention Lists")

    API_BASE = os.getenv("API_BASE", "http://api:4000/api").rstrip("/")
    TIMEOUT = int(os.getenv("API_TIMEOUT", "8"))

    def _get(path, params=None):
        url = f"{API_BASE}{path if path.startswith('/') else '/'+path}"
        r = requests.get(url, params=params or {}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    # Pull college names from avg GPA endpoint (field: 'college')
    try:
        names_df = pd.DataFrame(_get("/colleges/averages/gpa"))
        if "college" not in names_df.columns:
            raise ValueError("Expected 'college' in /colleges/averages/gpa response")
        college_names = sorted(names_df["college"].dropna().astype(str).unique().tolist())
    except Exception as e:
        st.warning(f"Could not load departments — {e}")
        college_names = []

    dept = st.selectbox(
        "Department",
        options=college_names,
        index=0 if college_names else None,
        key="lists_dept_select",
    )

    # Layout: 2x2
    c1, c2 = st.columns(2, gap="medium")
    c3, c4 = st.columns(2, gap="medium")

    # --- 1) Vacant Courses (no assigned professor) ---
    with c1:
        st.caption("Vacant Courses (no professor)")
        try:
            vac = pd.DataFrame(_get("/courses/vacancies"))
            # Expected fields: course_id, course_name, time, enrollment, is_vacant
            if "is_vacant" in vac.columns:
                vac_only = vac[vac["is_vacant"].astype(bool)].copy()
            else:
                vac_only = pd.DataFrame(columns=["course_id","course_name","enrollment"])
            show = vac_only[["course_id","course_name","enrollment"]].head(5) if not vac_only.empty else vac_only
            st.dataframe(show.rename(columns={
                "course_id":"Course ID","course_name":"Course","enrollment":"Enroll"
            }), use_container_width=True, hide_index=True)
        except Exception as e:
            st.caption(f"Unable to load vacancies — {e}")

    # --- 2) Highest Enrollment (selected dept) ---
    with c2:
        st.caption("Most Enrolled Courses (dept)")
        try:
            if dept:
                ce = pd.DataFrame(_get(f"/colleges/{dept}/course-enrollments"))
                # Fields: course_name, course_id, enrolled_students
                ce["enrolled_students"] = pd.to_numeric(ce["enrolled_students"], errors="coerce").fillna(0)
                top = ce.sort_values("enrolled_students", ascending=False).head(5)
                st.dataframe(top.rename(columns={
                    "course_id":"Course ID","course_name":"Course","enrolled_students":"Enroll"
                }), use_container_width=True, hide_index=True)
            else:
                st.caption("Select a department to view.")
        except Exception as e:
            st.caption(f"Unable to load course enrollments — {e}")

    # --- 3) High GPA Students (selected dept) ---
    # NOTE: Your existing route filters by gpa >= gpaMin, so this is "high GPA" not "low GPA".
    with c3:
        st.caption("High GPA Students (dept)")
        try:
            if dept:
                gpa_min = st.slider("GPA minimum", 0.0, 4.0, 3.5, 0.1, key="high_gpa_min")
                stu = pd.DataFrame(_get(f"/colleges/{dept}/students", params={"gpaMin": gpa_min}))
                # Expected fields from your route: userId, firstName, lastName, gpa, school_rank
                if not stu.empty:
                    stu["Name"] = (stu["firstName"].astype(str) + " " + stu["lastName"].astype(str)).str.strip()
                    stu["gpa"] = pd.to_numeric(stu["gpa"], errors="coerce")
                    show = stu[["userId","Name","gpa","school_rank"]].head(5)
                    st.dataframe(show.rename(columns={
                        "userId":"ID","gpa":"GPA","school_rank":"Rank"
                    }), use_container_width=True, hide_index=True)
                else:
                    st.caption("No students at or above this GPA.")
            else:
                st.caption("Select a department to view.")
        except Exception as e:
            st.caption(f"Unable to load students — {e}")

    # --- 4) Low Enrollment (selected dept) ---
    with c4:
        st.caption("Low Enrollment Courses (dept)")
        try:
            if dept:
                ce = pd.DataFrame(_get(f"/colleges/{dept}/course-enrollments"))
                ce["enrolled_students"] = pd.to_numeric(ce["enrolled_students"], errors="coerce").fillna(0)
                # Threshold control (purely client-side)
                min_enroll = st.slider("Max enroll to flag", 0, 50, 10, 1, key="low_enroll_max")
                low = ce[ce["enrolled_students"] <= min_enroll].sort_values("enrolled_students", ascending=True).head(5)
                st.dataframe(low.rename(columns={
                    "course_id":"Course ID","course_name":"Course","enrolled_students":"Enroll"
                }), use_container_width=True, hide_index=True)
            else:
                st.caption("Select a department to view.")
        except Exception as e:
            st.caption(f"Unable to load course enrollments — {e}")
