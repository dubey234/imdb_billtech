import streamlit as st
import duckdb
import time
from chatbot import chatbot
from llm_handler import test_connection

DB_PATH = 'imdb_data.duckdb'

def inject_custom_css():
    """Injects custom CSS to replicate the dark theater playcard layout and badge UI."""
    st.markdown("""
        <style>
        /* Base page: Full-screen poster collage wall with dark radial overlay */
        .stApp {
            background-color: #0d1117;
            background-image: 
                radial-gradient(circle at center, rgba(13, 17, 23, 0.7) 0%, rgba(10, 12, 16, 0.95) 100%),
                url("https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=1920&auto=format&fit=crop");
            background-size: cover;
            background-attachment: fixed;
            color: #f0f6fc;
        }

        /* Top header card */
        .hero-banner {
            text-align: center;
            padding: 1.2rem 2rem;
            background: rgba(255, 255, 255, 0.92);
            border-radius: 18px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
            max-width: 850px;
            margin: 0 auto 1.5rem auto;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .imdb-logo {
            background-color: #f5c518;
            color: #000000;
            font-weight: 900;
            padding: 4px 14px;
            border-radius: 8px;
            font-size: 2.2rem;
            display: inline-block;
            margin-right: 10px;
            vertical-align: middle;
        }

        .hero-title-text {
            font-size: 2.6rem;
            font-weight: 800;
            color: #000000 !important; /* Pure black title */
            display: inline-block;
            vertical-align: middle;
            margin: 0;
        }

        .hero-sub-text {
            font-size: 1.1rem;
            color: #334155;
            margin-top: 0.4rem;
            font-weight: 500;
        }

        /* Center camera avatar icon badge */
        .camera-badge-container {
            text-align: center;
            margin: -0.8rem 0 1.2rem 0;
        }

        .camera-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 90px;
            height: 90px;
            background: radial-gradient(circle, #f5c518 0%, #111 80%);
            border: 4px solid #f5c518;
            border-radius: 50%;
            box-shadow: 0 0 25px rgba(245, 197, 24, 0.6);
            font-size: 2.6rem;
        }

        /* Suggestion card buttons */
        div.stButton > button {
            width: 100%;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.95);
            color: #111827;
            border: 2px solid #e5e7eb;
            padding: 14px;
            font-weight: 600;
            font-size: 0.92rem;
            text-align: left;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.25);
            transition: all 0.25s ease-in-out;
            min-height: 80px;
        }

        div.stButton > button:hover {
            border-color: #f5c518;
            background: #ffffff;
            color: #000000;
            transform: translateY(-4px);
            box-shadow: 0 15px 30px rgba(245, 197, 24, 0.4);
        }

        /* Customizing chat input field */
        .stChatInput {
            border-radius: 30px !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        }

        /* Dark sidebar theme */
        [data-testid="stSidebar"] {
            background-color: #0b0f17 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

def render_app():
    st.set_page_config(page_title="🎬 IMDb Chatbot", page_icon="🎬", layout="wide")
    inject_custom_css()

    # --- CENTER HEADER BANNER ---
    st.markdown("""
        <div class="hero-banner">
            <div>
                <span class="imdb-logo">IMDb</span>
                <h1 class="hero-title-text">Movie Chatbot</h1>
            </div>
            <div class="hero-sub-text">Ask me anything about movies, actors, and ratings!</div>
        </div>
        <div class="camera-badge-container">
            <div class="camera-badge">🎥</div>
        </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR: DUCKDB TABLE INSPECTION ---
    with st.sidebar:
        st.header("🗄️ Database Inspector")
        try:
            conn = duckdb.connect(DB_PATH, read_only=True)
            tables = conn.execute("SHOW TABLES;").fetchall()
            st.success(f"Connected: `{DB_PATH}`")
            
            for tbl in tables:
                table_name = tbl[0]
                row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
                st.markdown(f"🔹 **`{table_name}`**")
                st.caption(f"☑️ **Rows:** {row_count:,}")

                schema = conn.execute(f"DESCRIBE {table_name};").fetchall()
                cols = [f"`{col[0]}`" for col in schema]
                st.caption("Cols: " + ", ".join(cols))
                st.divider()
            conn.close()
        except Exception as e:
            st.error(f"Database Inspection Error: {e}")

    # --- API CHECK ---
    if 'api_tested' not in st.session_state:
        st.session_state.api_tested = test_connection()

    if not st.session_state.api_tested:
        st.error("❌ Gemini API connection failed.")
        st.stop()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # --- SUGGESTION CARDS ---
    col1, col2, col3, col4 = st.columns(4)
    prompt_to_submit = None

    with col1:
        if st.button("🚀 What are the top-rated sci-fi movies on IMDb right now?"):
            prompt_to_submit = "What are the top-rated sci-fi movies on IMDb right now?"

    with col2:
        if st.button("📢 List all films directed by Christopher Nolan."):
            prompt_to_submit = "List all films directed by Christopher Nolan."

    with col3:
        if st.button("🎭 Can you suggest some good comedy movies from the 1990s?"):
            prompt_to_submit = "Can you suggest some good comedy movies from the 1990s?"

    with col4:
        if st.button("⭐ Show me the movie roles of Leonardo DiCaprio."):
            prompt_to_submit = "Show me the movie roles of Leonardo DiCaprio."

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CHAT HISTORY ---
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if "thinking" in msg and msg["thinking"]:
                with st.expander("🔍 Query Engine Breakdown", expanded=False):
                    st.markdown(msg["thinking"])
            st.markdown(msg["content"])

    # --- INPUT EXECUTION ---
    user_input = st.chat_input("Type your movie question here...")
    final_query = prompt_to_submit or user_input

    if final_query:
        st.session_state.chat_history.append({"role": "user", "content": final_query})
        with st.chat_message("user"):
            st.markdown(final_query)

        with st.chat_message("assistant"):
            thinking_placeholder = st.empty()

            with thinking_placeholder.expander("🔍 Query Engine Breakdown (Searching...)", expanded=True):
                st.markdown("⏳ *Analyzing query and searching DuckDB database...*")
                time.sleep(0.3)

            try:
                res = chatbot.answer_question(final_query)

                if isinstance(res, dict):
                    ans = res.get("answer", "No response generated.")
                    generated_sql = res.get("sql_query", res.get("sql", "N/A"))
                    tables_used = res.get("tables", "title_basics, title_ratings")
                else:
                    ans = str(res)
                    generated_sql = "N/A"
                    tables_used = "title_basics"

                sql_block = f"```sql\n{generated_sql}\n```"
                thinking_logs = (
                    f"**1. Intent:** Natural Language to SQL Execution\n\n"
                    f"**2. Tables Inspected:** `{tables_used}`\n\n"
                    f"**3. SQL Query:**\n{sql_block}"
                )

                thinking_placeholder.expander("🔍 Query Engine Breakdown", expanded=False).markdown(thinking_logs)
                st.markdown(ans)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "thinking": thinking_logs,
                    "content": ans
                })

            except Exception as e:
                err_msg = f"❌ Query Error: {e}"
                st.error(err_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": err_msg})