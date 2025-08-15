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

# --- REQUIRE: dean_id in session ---
dean_id = st.session_state.get("dean_id")
if dean_id is None:
    st.error("No dean_id in session. Set st.session_state['dean_id'] at login.")
    st.stop()

# --- Resolve the dean's college once ---
@st.cache_data(ttl=300, show_spinner=False)
def get_dean_college(_dean_id: int) -> str | None:
    """
    Calls GET /metrics/deans/<id>/college -> {"collegeName": "..."} or {}
    """
    try:
        data = get_json(f"/metrics/deans/{_dean_id}/college")
        return (data or {}).get("collegeName")
    except Exception:
        return None

# Prefer session value if set, otherwise fetch from API
dean_college = st.session_state.get("college") or get_dean_college(dean_id)

if not dean_college:
    st.warning("Could not determine your college yet. Some panels may be empty.")
else:
    # cache it in session for the rest of the app
    st.session_state['college'] = dean_college

# --- Top-right panel ---
with right_top:
    st.caption("Enrollment Trends (by Course)")

    API_BASE = os.getenv("API_BASE", "http://api:4000/api").rstrip("/")
    TIMEOUT = int(os.getenv("API_TIMEOUT", "8"))

    def _get(path, params=None):
        url = f"{API_BASE}{path if path.startswith('/') else '/'+path}"
        r = requests.get(url, params=params or {}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    # 1) Build the selectable list from THIS dean's courses
    dean_id = st.session_state.get("dean_id")
    course_options = []
    try:
        data = _get(f"/metrics/deans/{dean_id}/courses")
        df_courses = pd.DataFrame(data)
        if not df_courses.empty and {"course_id","course_name"}.issubset(df_courses.columns):
            course_options = (
                df_courses[["course_id","course_name"]]
                .dropna()
                .astype({"course_id": int, "course_name": str})
                .to_dict("records")
            )
        else:
            raise ValueError("Missing fields in /metrics/deans/<id>/courses response")
    except Exception as e:
        st.warning(f"Could not load courses — {e}")
        course_options = []

    label_to_id = {row["course_name"]: row["course_id"] for row in course_options}
    course_names = list(label_to_id.keys())

    # 2) Picker (course names)
    selected_courses = st.multiselect(
        "Select courses to compare",
        options=course_names,
        default=course_names[: min(3, len(course_names))],
        label_visibility="collapsed",
        key="enroll_trend_course_select",
    )

    # 3) Pull per-course enrollment trends
    frames = []
    for cname in selected_courses:
        cid = label_to_id.get(cname)
        if cid is None:
            continue
        try:
            rows = _get(f"/metrics/courses/{cid}/enrollment-trend")
            df = pd.DataFrame(rows)
            if {"period", "enrollment"}.issubset(df.columns):
                df["period"] = pd.to_numeric(df["period"], errors="coerce")
                df["enrollment"] = pd.to_numeric(df["enrollment"], errors="coerce").fillna(0)
                df = df.dropna(subset=["period"]).sort_values("period")
                df["CourseName"] = cname
                frames.append(df[["period", "enrollment", "CourseName"]])
        except Exception:
            continue  # ignore a single course failure

    if not frames:
        st.info("No enrollment trend data available yet.")
    else:
        df_trend = pd.concat(frames, ignore_index=True)
        fig = px.line(
            df_trend,
            x="period",
            y="enrollment",
            color="CourseName",
            markers=True,
            labels={"period": "Year", "enrollment": "Enrollment", "CourseName": "Course"},
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), legend_title_text="Course")
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
        st.caption("Enrollment per Course")
        try:
            dean_id = st.session_state.get("dean_id")
            if dean_id is None:
                raise ValueError("No dean_id in session")

            # pull the dean's courses (already scoped to the dean's college)
            data = get_json(f"/metrics/deans/{dean_id}/courses")
            df_courses = pd.DataFrame(data)

            need = {"course_name", "enrollment"}
            if not need.issubset(df_courses.columns):
                raise ValueError(f"Missing fields: {need - set(df_courses.columns)}")

            df_enroll = df_courses.rename(columns={
                "course_name": "CourseName",
                "enrollment": "Enrollment"
            })[["CourseName", "Enrollment"]]

        except Exception as e:
            st.caption(f"Using sample data — {e}")
            df_enroll = pd.DataFrame({
                "CourseName": ["Course A", "Course B", "Course C", "Course D", "Course E"],
                "Enrollment": np.array([0, 0, 0, 0, 0])
            })

        fig = px.bar(
            df_enroll,
            x="CourseName",
            y="Enrollment",
            labels={"CourseName": "Course", "Enrollment": "Enrollment"},
        )
        st.plotly_chart(fig, use_container_width=True)


    # ---- Student / Teacher Ratio ----
    with sub_rt:
        st.caption("Student / Teacher Ratio (by Course)")
        try:
            info = get_json(f"/metrics/deans/{st.session_state['dean_id']}/college")
            dean_college = (info or {}).get("collegeName")
            params = {"college": dean_college} if dean_college else {}

            # New per-course endpoint
            data = get_json("/metrics/courses/student-teacher-ratio", params=params)
            df_ratio = pd.DataFrame(data)

            need = {"course_name", "students_per_teacher"}
            if not need.issubset(df_ratio.columns):
                raise ValueError(f"Missing fields: {need - set(df_ratio.columns)}")

            df_ratio = df_ratio.rename(columns={
                "course_name": "CourseName",
                "students_per_teacher": "StudentsPerTeacher"
            })
            df_ratio["StudentsPerTeacher"] = pd.to_numeric(
                df_ratio["StudentsPerTeacher"], errors="coerce"
            )

            # optional: sort biggest ratios first
            df_ratio = df_ratio.sort_values("StudentsPerTeacher", ascending=False)

        except Exception as e:
            st.caption(f"Using sample data — {e}")
            df_ratio = pd.DataFrame({
                "CourseName": ["Course A", "Course B", "Course C", "Course D", "Course E"],
                "StudentsPerTeacher": np.round(np.random.uniform(8, 22, 5), 1)
            })

        fig = px.bar(
            df_ratio,
            x="CourseName",
            y="StudentsPerTeacher",
            labels={"CourseName": "Course", "StudentsPerTeacher": "Students per Teacher"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Average GPA by College ----
    with sub_lb:
        st.caption("Average GPA by Course")
        try:
            info = get_json(f"/metrics/deans/{st.session_state['dean_id']}/college")
            dean_college = (info or {}).get("collegeName")  # e.g., "College of Composition"
            params = {"college": dean_college} if dean_college else {}

            data = get_json("/metrics/courses/averages/gpa", params=params)
            df_gpa_all = pd.DataFrame(data)
            if df_gpa_all.empty:
                # create empty frame with expected columns so the chart doesn’t error
                df_gpa_all = pd.DataFrame(columns=["course_name", "average_gpa"])

            # normalize: tolerate legacy keys if backend restart lags
            if "course_name" not in df_gpa_all.columns and "course" in df_gpa_all.columns:
                df_gpa_all = df_gpa_all.rename(columns={"course": "course_name"})
            if "average_gpa" not in df_gpa_all.columns and "avg_gpa" in df_gpa_all.columns:
                df_gpa_all = df_gpa_all.rename(columns={"avg_gpa": "average_gpa"})

            need = {"course_name", "average_gpa"}
            if not need.issubset(df_gpa_all.columns):
                # if empty, create an empty frame with expected cols to avoid a hard error
                if df_gpa_all.empty:
                    df_gpa_all = pd.DataFrame(columns=["course_name", "average_gpa"])
                else:
                    raise ValueError(f"Missing fields: {need - set(df_gpa_all.columns)}")

            df_gpa = pd.DataFrame({
                "CourseName": df_gpa_all.get("course_name", pd.Series([], dtype=str)).astype(str),
                "AverageGPA": pd.to_numeric(df_gpa_all.get("average_gpa", pd.Series([], dtype=float)), errors="coerce")
            }).fillna({"AverageGPA": 0.0})

            # optional: sort by GPA desc
            df_gpa = df_gpa.sort_values("AverageGPA", ascending=False)

        except Exception as e:
            st.caption(f"Using sample data — {e}")
            df_gpa = pd.DataFrame({
                "CourseName": ["Course A", "Course B", "Course C", "Course D", "Course E"],
                "AverageGPA": np.round(np.random.uniform(2.6, 3.7, 5), 2)
            })

        fig = px.bar(
            df_gpa,
            x="CourseName",
            y="AverageGPA",
            labels={"CourseName": "Course", "AverageGPA": "Avg GPA"},
            range_y=[0, 4]
        )
        st.plotly_chart(fig, use_container_width=True)

        # ---- Budget by Course ----
        with sub_rb:
            st.caption("Budget by Course ($)")
            try:
                info = get_json(f"/metrics/deans/{st.session_state['dean_id']}/college")
                dean_college = (info or {}).get("collegeName")
                params = {"college": dean_college} if dean_college else {}

                data = get_json("/metrics/courses/budget", params=params)
                df_budget = pd.DataFrame(data)

                need = {"course_name", "budget"}
                if not need.issubset(df_budget.columns):
                    if df_budget.empty:
                        df_budget = pd.DataFrame(columns=["course_name", "budget"])
                    else:
                        raise ValueError(f"Missing fields: {need - set(df_budget.columns)}")

                df_budget = df_budget.rename(columns={"course_name": "CourseName", "budget": "Budget"})
                df_budget["Budget"] = pd.to_numeric(df_budget["Budget"], errors="coerce").fillna(0)

                # optional: show top N by budget (they’re equal within a college, but allows cross-college view)
                # df_budget = df_budget.sort_values("Budget", ascending=False).head(20)

            except Exception as e:
                st.caption(f"Using sample data — {e}")
                df_budget = pd.DataFrame({
                    "CourseName": ["Course A", "Course B", "Course C", "Course D", "Course E"],
                    "Budget": np.array([0, 0, 0, 0, 0], dtype=float)
                })

            fig = px.bar(
                df_budget,
                x="CourseName",
                y="Budget",
                labels={"CourseName": "Course", "Budget": "Budget ($)"},
            )
            st.plotly_chart(fig, use_container_width=True)


    # ---------------- LEFT BOTTOM: Course Performance Overview (by Course) ----------------
    with left_bottom:
        st.subheader("Course Performance Overview")

        API_BASE = os.getenv("API_BASE", "http://api:4000/api").rstrip("/")
        TIMEOUT = int(os.getenv("API_TIMEOUT", "8"))

        def _get(path, params=None):
            url = f"{API_BASE}{path if path.startswith('/') else '/'+path}"
            r = requests.get(url, params=params or {}, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()

        # Resolve dean + college
        dean_id = st.session_state.get("dean_id")
        if dean_id is None:
            st.error("No dean_id in session. Set st.session_state['dean_id'] at login.")
            st.stop()

        # dean's college (from session or API)
        dean_college = st.session_state.get("college")
        if not dean_college:
            try:
                info = _get(f"/metrics/deans/{dean_id}/college")
                dean_college = (info or {}).get("collegeName")
                if dean_college:
                    st.session_state["college"] = dean_college
            except Exception:
                dean_college = None

        # 1) Dean's courses (authoritative list; used for picker + join keys)
        try:
            data_courses = _get(f"/metrics/deans/{dean_id}/courses")
            df_courses = pd.DataFrame(data_courses)
            need_courses = {"course_id", "course_name"}
            if not need_courses.issubset(df_courses.columns):
                raise ValueError(f"Dean courses missing: {need_courses - set(df_courses.columns)}")

            df_courses = (
                df_courses[["course_id", "course_name"]]
                .dropna()
                .astype({"course_id": "int64", "course_name": "string"})
                .sort_values("course_name")
            )
            name_to_id = dict(zip(df_courses["course_name"], df_courses["course_id"]))
            course_names = df_courses["course_name"].tolist()
        except Exception as e:
            st.warning(f"Could not load your courses — {e}")
            df_courses = pd.DataFrame(columns=["course_id", "course_name"])
            name_to_id = {}
            course_names = []

        # 2) Picker (by course name, but we'll map to IDs)
        selected_names = st.multiselect(
            "Courses",
            options=course_names,
            default=course_names[: min(5, len(course_names))],
            key="perf_overview_courses_select",
        )
        selected_ids = [name_to_id[n] for n in selected_names if n in name_to_id]

        # If user hasn't picked anything, show first few by default
        if not selected_ids and not df_courses.empty:
            selected_ids = df_courses["course_id"].head(5).tolist()
            selected_names = df_courses.set_index("course_id").loc[selected_ids]["course_name"].tolist()

        # 3) Load GPA list once, then INNER JOIN by course_id
        def load_gpa_df():
            # try scoped by college first
            params = {"college": dean_college} if dean_college else None
            try:
                data_gpa = _get("/metrics/courses/averages/gpa", params=params)
                df = pd.DataFrame(data_gpa)
            except Exception:
                df = pd.DataFrame()

            # if that came back empty (or missing cols), retry without filter
            need = {"course_id", "course_name", "average_gpa"}
            if df.empty or not need.issubset(df.columns):
                try:
                    data_gpa = _get("/metrics/courses/averages/gpa")
                    df = pd.DataFrame(data_gpa)
                except Exception:
                    df = pd.DataFrame(columns=list(need))

            # normalize columns
            rename_map = {}
            if "avg_gpa" in df.columns and "average_gpa" not in df.columns:
                rename_map["avg_gpa"] = "average_gpa"
            if "course" in df.columns and "course_name" not in df.columns:
                rename_map["course"] = "course_name"
            if rename_map:
                df = df.rename(columns=rename_map)

            # keep just what we need, clean types
            keep = [c for c in ["course_id", "course_name", "average_gpa"] if c in df.columns]
            df = df[keep] if keep else pd.DataFrame(columns=["course_id", "course_name", "average_gpa"])
            if "course_id" in df.columns:
                df["course_id"] = pd.to_numeric(df["course_id"], errors="coerce").astype("Int64")
            if "average_gpa" in df.columns:
                df["average_gpa"] = pd.to_numeric(df["average_gpa"], errors="coerce")
            return df

        df_gpa = load_gpa_df()

        # 4) Join dean courses with GPA on course_id, then filter to selected_ids
        if df_courses.empty:
            st.info("No courses found for your college.")
        else:
            df_join = pd.merge(
                df_courses, df_gpa, on=["course_id", "course_name"], how="left"
            )

            if selected_ids:
                df_join = df_join[df_join["course_id"].isin(selected_ids)]

            if df_join.empty:
                st.info("No course performance data available yet. Pick at least one course.")
            else:
                # tidy + sort
                df_join = df_join.rename(columns={
                    "course_id": "Course ID",
                    "course_name": "Course",
                    "average_gpa": "Avg GPA",
                })
                df_join["Avg GPA"] = pd.to_numeric(df_join["Avg GPA"], errors="coerce")

                sort_desc = st.checkbox(
                    "Sort by Avg GPA (desc)", value=True, key="sort_gpa_desc_course"
                )
                if sort_desc:
                    df_join = df_join.sort_values(["Avg GPA", "Course"], ascending=[False, True])
                else:
                    df_join = df_join.sort_values(["Course"])

                st.dataframe(
                    df_join.reset_index(drop=True)[["Course ID", "Course", "Avg GPA"]],
                    use_container_width=True,
                    hide_index=True,
                )


# ---------------- RIGHT BOTTOM: Quick Lists ----------------
# ---------------- RIGHT BOTTOM: Attention Lists (by Course, scoped to dean's college) ----------------
    with right_bottom:
        st.subheader("Attention Lists")

        API_BASE = os.getenv("API_BASE", "http://api:4000/api").rstrip("/")
        TIMEOUT = int(os.getenv("API_TIMEOUT", "8"))

        def _get(path, params=None):
            url = f"{API_BASE}{path if path.startswith('/') else '/'+path}"
            r = requests.get(url, params=params or {}, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()

        # Resolve dean + college
        dean_id = st.session_state.get("dean_id")
        if dean_id is None:
            st.error("No dean_id in session. Set st.session_state['dean_id'] at login.")
            st.stop()

        dean_college = st.session_state.get("college")
        if not dean_college:
            try:
                info = _get(f"/metrics/deans/{dean_id}/college")
                dean_college = (info or {}).get("collegeName")
                if dean_college:
                    st.session_state["college"] = dean_college
            except Exception:
                dean_college = None

        # Dean's courses for filter UI
        try:
            data_courses = _get(f"/metrics/deans/{dean_id}/courses")
            df_courses = pd.DataFrame(data_courses)
            need = {"course_id", "course_name"}
            if not need.issubset(df_courses.columns):
                raise ValueError(f"Dean courses missing: {need - set(df_courses.columns)}")
            df_courses = (
                df_courses[["course_id", "course_name"]]
                .dropna()
                .astype({"course_id": "int64", "course_name": "string"})
                .sort_values("course_name")
            )
            course_names = df_courses["course_name"].tolist()
            name_to_id = dict(zip(df_courses["course_name"], df_courses["course_id"]))
        except Exception as e:
            st.warning(f"Could not load your courses — {e}")
            df_courses = pd.DataFrame(columns=["course_id", "course_name"])
            course_names, name_to_id = [], {}

        # Multi-select filter (used everywhere below)
        selected_courses = st.multiselect(
            "Filter courses",
            options=course_names,
            default=course_names[: min(5, len(course_names))],
            key="attn_courses_select",
        )
        selected_ids = {name_to_id[n] for n in selected_courses if n in name_to_id}

        # Build enroll_df once (scoped to dean's college), then filter by selected_ids
        def load_enrollments_df(college: str | None):
            try:
                params = {"college": college} if college else {}
                df = pd.DataFrame(_get("/metrics/courses/enrollments", params=params))
                if "enrolled_students" not in df.columns and "enrollment" in df.columns:
                    df = df.rename(columns={"enrollment": "enrolled_students"})
                need = {"course_id", "course_name", "enrolled_students"}
                if not need.issubset(df.columns):
                    return pd.DataFrame(columns=list(need))
                df["enrolled_students"] = (
                    pd.to_numeric(df["enrolled_students"], errors="coerce").fillna(0).astype(int)
                )
                return df
            except Exception:
                return pd.DataFrame(columns=["course_id", "course_name", "enrolled_students"])

        enroll_df = load_enrollments_df(dean_college)
        if selected_ids:
            enroll_df = enroll_df[enroll_df["course_id"].isin(list(selected_ids))]

        col_left, col_right = st.columns(2, gap="medium")

        # --- Vacancies (left) ---
        with col_left:
            st.caption("Vacancies")
            mode = st.toggle(
                "Show vacancies based on ENROLLMENT (off = based on PROFESSOR)",
                value=False, key="vacancy_mode"
            )

            if not mode:
                st.caption("Mode: No professor assigned")
                try:
                    params = {"college": dean_college} if dean_college else {}
                    vac = pd.DataFrame(_get("/courses/vacancies", params=params))
                    if "is_vacant" in vac.columns:
                        vac = vac[vac["is_vacant"].astype(bool)]
                    else:
                        vac = pd.DataFrame(columns=["course_id", "course_name", "enrollment"])
                    if selected_ids:
                        vac = vac[vac["course_id"].isin(list(selected_ids))]
                    show = vac[["course_id", "course_name", "enrollment"]].head(5) if not vac.empty else vac
                    st.dataframe(
                        show.rename(columns={"course_id": "Course ID", "course_name": "Course", "enrollment": "Enroll"}),
                        use_container_width=True, hide_index=True
                    )
                except Exception as e:
                    st.caption(f"Unable to load vacancies — {e}")
            else:
                st.caption("Mode: Low/Zero enrollment")
                thresh = st.slider("Max enrollment to flag", 0, 50, 0, 1, key="vacancy_enroll_threshold")
                low = enroll_df[enroll_df["enrolled_students"] <= thresh] \
                        .sort_values("enrolled_students", ascending=True) \
                        .head(5)
                if low.empty:
                    st.caption("No courses meet the enrollment threshold.")
                else:
                    st.dataframe(
                        low.rename(columns={"course_id": "Course ID", "course_name": "Course", "enrolled_students": "Enroll"}),
                        use_container_width=True, hide_index=True
                    )

        # --- High GPA Students (right) ---
        with col_right:
            st.caption("High GPA Students (course)")
            try:
                if selected_courses:  # use multi-select courses
                    gpa_min = st.slider("GPA minimum", 0.0, 4.0, 3.5, 0.1, key="high_gpa_min_course")
                    for course_for_gpa in selected_courses:
                        cid = name_to_id.get(course_for_gpa)
                        if cid is None:
                            continue
                        stu = pd.DataFrame(_get(f"/metrics/courses/{cid}/students", params={"gpaMin": gpa_min}))
                        if not stu.empty:
                            stu["Name"] = (stu["firstName"].astype(str) + " " + stu["lastName"].astype(str)).str.strip()
                            stu["gpa"] = pd.to_numeric(stu["gpa"], errors="coerce")
                            show = stu[["userId", "Name", "gpa", "school_rank"]].head(5)
                            st.write(f"**{course_for_gpa}**")
                            st.dataframe(
                                show.rename(columns={"userId": "ID", "gpa": "GPA", "school_rank": "Rank"}),
                                use_container_width=True, hide_index=True
                            )
                        else:
                            st.caption(f"No students at or above GPA {gpa_min} for {course_for_gpa}.")
                else:
                    st.caption("No courses selected.")
            except Exception as e:
                st.caption(f"Unable to load students — {e}")