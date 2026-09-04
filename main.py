import streamlit as st
import sqlite3
import hashlib
from datetime import time, datetime, timedelta


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="wide"
)



# ==========================================
# DATABASE CONNECTION
# ==========================================

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(
    BASE_DIR,
    "ai_study_planner_new.db"
)


def get_connection():

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    return conn


# ==========================================
# CREATE DATABASE TABLE
# ==========================================

def create_table():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()

    conn.close()


create_table()

# ==========================================
# PASSWORD HASH
# ==========================================

def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ==========================================
# CREATE USER
# ==========================================

def create_user(username, password):

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users (username, password)
            VALUES (?, ?)
            """,
            (
                username,
                hash_password(password)
            )
        )

        conn.commit()
        conn.close()

        return True, "Account created successfully!"

    except sqlite3.IntegrityError:

        return False, "Username already exists. Choose another username."

    except Exception as e:

        return False, str(e)


# ==========================================
# LOGIN USER
# ==========================================

def login_user(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT username FROM users
        WHERE username = ? AND password = ?
        """,
        (
            username,
            hash_password(password)
        )
    )

    user = cursor.fetchone()

    conn.close()

    return user


# ==========================================
# RESET PASSWORD
# ==========================================

def reset_user_password(username, new_password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT username FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    if user:

        cursor.execute(
            """
            UPDATE users
            SET password = ?
            WHERE username = ?
            """,
            (
                hash_password(new_password),
                username
            )
        )

        conn.commit()
        conn.close()

        return True

    conn.close()

    return False


# ==========================================
# SESSION STATE
# ==========================================

if "logged_in" not in st.session_state:

    st.session_state["logged_in"] = False


if "current_user" not in st.session_state:

    st.session_state["current_user"] = ""


if "completed_tasks" not in st.session_state:

    st.session_state["completed_tasks"] = 0


# ==========================================
# CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f7fb;
}

.login-title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
}

.main-title {
    font-size: 36px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# LOGIN / SIGNUP / FORGOT PASSWORD
# ==========================================

if not st.session_state["logged_in"]:

    left, right = st.columns([1, 1])

    with left:

        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            padding: 50px;
            border-radius: 25px;
            min-height: 500px;
        ">

        <h1>📚 AI Study Planner</h1>

        <h2>Plan Smarter.<br>Study Better.</h2>

        <br>

        <h3>✨ Smart Planning</h3>
        <p>Create personalized study schedules.</p>

        <h3>📊 Track Progress</h3>
        <p>Monitor your study progress.</p>

        <h3>🎯 Achieve Goals</h3>
        <p>Stay focused and motivated.</p>

        </div>
        """, unsafe_allow_html=True)


    with right:

        st.write("")
        st.write("")

        login_tab, create_tab, forgot_tab = st.tabs([
            "🔐 Login",
            "📝 Create Account",
            "🔑 Forgot Password"
        ])


        # ==================================
        # LOGIN
        # ==================================

        with login_tab:

            st.header("Welcome Back 👋")

            username = st.text_input(
                "👤 Username",
                key="login_user"
            )

            password = st.text_input(
                "🔑 Password",
                type="password",
                key="login_pass"
            )

            if st.button(
                "🚀 Login",
                key="login_button",
                use_container_width=True
            ):

                if not username or not password:

                    st.warning(
                        "Please enter Username and Password."
                    )

                else:

                    user = login_user(
                        username.strip(),
                        password
                    )

                    if user:

                        st.session_state["logged_in"] = True

                        st.session_state["current_user"] = user[0]

                        st.success(
                            "🎉 Login Successful!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "❌ Incorrect Username or Password."
                        )


        # ==================================
        # CREATE ACCOUNT
        # ==================================

        with create_tab:

            st.header("Create Your Account")

            new_username = st.text_input(
                "👤 Choose Username",
                key="create_user"
            )

            new_password = st.text_input(
                "🔑 Create Password",
                type="password",
                key="create_pass"
            )

            confirm_password = st.text_input(
                "🔐 Confirm Password",
                type="password",
                key="confirm_pass"
            )

            if st.button(
                "✨ Create Account",
                key="create_button",
                use_container_width=True
            ):

                new_username = new_username.strip()

                if not new_username:

                    st.warning(
                        "Please enter a Username."
                    )

                elif not new_password:

                    st.warning(
                        "Please enter a Password."
                    )

                elif new_password != confirm_password:

                    st.error(
                        "❌ Password and Confirm Password do not match."
                    )

                elif len(new_password) < 4:

                    st.warning(
                        "Password must contain at least 4 characters."
                    )

                else:

                    success, message = create_user(
                        new_username,
                        new_password
                    )

                    if success:

                        st.success(
                            "🎉 Account Created Successfully! "
                            "Now go to Login tab."
                        )

                    else:

                        st.error(
                            f"❌ {message}"
                        )


        # ==================================
        # FORGOT PASSWORD
        # ==================================

        with forgot_tab:

            st.header("Reset Password")

            reset_username = st.text_input(
                "👤 Username",
                key="reset_user"
            )

            new_reset_password = st.text_input(
                "🔑 New Password",
                type="password",
                key="reset_new_pass"
            )

            confirm_reset_password = st.text_input(
                "🔐 Confirm New Password",
                type="password",
                key="reset_confirm_pass"
            )

            if st.button(
                "🔄 Reset Password",
                key="reset_button",
                use_container_width=True
            ):

                if not reset_username:

                    st.warning(
                        "Please enter your Username."
                    )

                elif not new_reset_password:

                    st.warning(
                        "Please enter a new Password."
                    )

                elif (
                    new_reset_password
                    != confirm_reset_password
                ):

                    st.error(
                        "❌ Passwords do not match."
                    )

                else:

                    success = reset_user_password(
                        reset_username.strip(),
                        new_reset_password
                    )

                    if success:

                        st.success(
                            "🎉 Password reset successfully! "
                            "Now login with your new password."
                        )

                    else:

                        st.error(
                            "❌ Username not found."
                        )


    st.stop()


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("📚 AI Study Planner")

st.sidebar.success(
    f"👤 {st.session_state['current_user']}"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📚 Study Planner",
        "📊 Progress"
    ]
)

st.sidebar.divider()

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state["logged_in"] = False
    st.session_state["current_user"] = ""

    st.rerun()


# ==========================================
# DASHBOARD
# ==========================================

if page == "🏠 Dashboard":

    st.markdown(
        f"<div class='main-title'>Welcome, "
        f"{st.session_state['current_user']} 👋</div>",
        unsafe_allow_html=True
    )

    st.write(
        "Plan smarter and achieve your study goals."
    )

    st.divider()

    st.subheader("💡 Today's Motivation")

    st.success(
        "🌟 Small progress every day creates big success!"
    )


# ==========================================
# STUDY PLANNER
# ==========================================

elif page == "📚 Study Planner":

    st.title("📚 AI Study Planner")

    st.write(
        "Create your personalized study schedule."
    )

    st.divider()


    # Student Details

    st.subheader("👤 Student Details")

    col1, col2 = st.columns(2)

    with col1:

        name = st.text_input(
            "👤 Name",
            value=st.session_state["current_user"]
        )

        subject = st.text_input(
            "📚 Subject Name"
        )

        difficulty = st.selectbox(
            "📊 Difficulty Level",
            [
                "Easy",
                "Medium",
                "Hard"
            ]
        )


    with col2:

        exam_date = st.date_input(
            "📅 Exam Date"
        )

        goal = st.text_input(
            "🎯 Study Goal"
        )


    # Difficulty Based Time

    if difficulty == "Easy":

        duration = 30
        recommended_hours = 2

    elif difficulty == "Medium":

        duration = 60
        recommended_hours = 4

    else:

        duration = 90
        recommended_hours = 6


    st.info(
        f"📌 {difficulty} Level: "
        f"Recommended study time is "
        f"{recommended_hours} hours per day."
    )


    # Time Schedule

    st.subheader(
        "⏰ Set Your Study Time"
    )

    t1, t2, t3, t4 = st.columns(4)


    with t1:

        morning = st.time_input(
            "🌅 Morning",
            value=time(6, 0)
        )

        morning_end = (
            datetime.combine(
                datetime.today(),
                morning
            )
            +
            timedelta(minutes=duration)
        ).time()

        st.caption(
            f"Ends at "
            f"{morning_end.strftime('%I:%M %p')}"
        )


    with t2:

        afternoon = st.time_input(
            "☀️ Afternoon",
            value=time(13, 0)
        )

        afternoon_end = (
            datetime.combine(
                datetime.today(),
                afternoon
            )
            +
            timedelta(minutes=duration)
        ).time()

        st.caption(
            f"Ends at "
            f"{afternoon_end.strftime('%I:%M %p')}"
        )


    with t3:

        evening = st.time_input(
            "🌆 Evening",
            value=time(18, 0)
        )

        evening_end = (
            datetime.combine(
                datetime.today(),
                evening
            )
            +
            timedelta(minutes=duration)
        ).time()

        st.caption(
            f"Ends at "
            f"{evening_end.strftime('%I:%M %p')}"
        )


    with t4:

        night = st.time_input(
            "🌙 Night",
            value=time(21, 0)
        )

        night_end = (
            datetime.combine(
                datetime.today(),
                night
            )
            +
            timedelta(minutes=duration)
        ).time()

        st.caption(
            f"Ends at "
            f"{night_end.strftime('%I:%M %p')}"
        )


    st.divider()


    # Daily Tasks

    st.subheader("📋 Daily Tasks")

    task1 = st.checkbox(
        "📖 Read study materials",
        key="task1"
    )

    task2 = st.checkbox(
        "✍️ Practice questions",
        key="task2"
    )

    task3 = st.checkbox(
        "🔄 Revise the topic",
        key="task3"
    )

    task4 = st.checkbox(
        "🧠 Learn something extra",
        key="task4"
    )

    completed = sum([
        task1,
        task2,
        task3,
        task4
    ])

    st.session_state["completed_tasks"] = completed

    progress = int(
        completed / 4 * 100
    )

    st.write(
        f"### Tasks Completed: {completed}/4"
    )

    st.progress(progress)

    st.write(
        f"📈 Study Progress: {progress}%"
    )


    st.divider()


    # Study Tips

    st.subheader("💡 Study Tips")

    st.info(
        "🧘 Study in a quiet place."
    )

    st.info(
        "☕ Take short breaks."
    )

    st.info(
        "✍️ Practice regularly."
    )

    st.info(
        "🔄 Revise every day."
    )


    # Generate Study Plan

    st.divider()

    if st.button(
        "🤖 Generate Study Plan",
        use_container_width=True
    ):

        if name and subject and goal:

            st.success(
                "🎉 Your Study Plan is Ready!"
            )

            st.subheader(
                "📚 Your Daily Study Plan"
            )

            st.write(
                f"🌅 Morning: Learn {subject} concepts"
            )

            st.write(
                f"☀️ Afternoon: Practice {subject} questions"
            )

            st.write(
                f"🌆 Evening: Revise important topics"
            )

            st.write(
                f"🌙 Night: Quick revision"
            )


            st.subheader(
                "🤖 AI Recommendation"
            )

            if difficulty == "Easy":

                st.info(
                    "Focus on learning concepts."
                )

            elif difficulty == "Medium":

                st.info(
                    "Balance learning and practice."
                )

            else:

                st.warning(
                    "Spend extra time on difficult topics."
                )


        else:

            st.error(
                "Please enter Name, Subject and Study Goal."
            )


# ==========================================
# PROGRESS PAGE
# ==========================================

elif page == "📊 Progress":

    st.title("📊 Study Progress")

    completed = st.session_state[
        "completed_tasks"
    ]

    progress = int(
        completed / 4 * 100
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "📋 Total Tasks",
        "4"
    )

    c2.metric(
        "✅ Completed",
        f"{completed}/4"
    )

    c3.metric(
        "📈 Progress",
        f"{progress}%"
    )

    st.progress(progress)

    if progress == 100:

        st.success(
            "🎉 Excellent! All tasks completed."
        )

    elif progress > 0:

        st.info(
            "👏 Keep going!"
        )

    else:

        st.warning(
            "🚀 Start your study tasks."
        )