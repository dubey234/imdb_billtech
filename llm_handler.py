import os
import time
from dotenv import load_dotenv
from google import genai
from prompt_builder import build_system_prompt

load_dotenv()

# Configure Gemini Client
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file!")

client = genai.Client(api_key=api_key)

# Active Gemini model ID
MODEL_ID = 'gemini-3.6-flash'

def get_schema_info() -> str:
    """Dynamically loads and returns schema context built from db_config.yaml."""
    try:
        return build_system_prompt("db_config.yaml")
    except Exception as e:
        print(f"⚠️ Prompt Builder Error: {e}. Falling back to default schema.")
        return """
DATABASE SCHEMA (DuckDB):
Tables: title_basics, title_ratings, title_principals, name_basics
CRITICAL RULES:
1. DO NOT query 'movies'.
2. Always JOIN title_basics and title_ratings on tconst.
3. Return ONLY valid, raw DuckDB SQL.
"""

def generate_sql_query(user_question: str) -> str:
    """Convert natural language to SQL using Gemini"""
    prompt = f"""{get_schema_info()}

User Question: {user_question}

SQL Query:"""
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
        )
        sql_query = response.text.strip()
        
        if '```' in sql_query:
            sql_query = sql_query.split('```')[1].replace('sql', '').strip()
        
        return sql_query
    
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return "SELECT tb.primaryTitle, tr.averageRating FROM title_basics tb JOIN title_ratings tr ON tb.tconst = tr.tconst ORDER BY tr.averageRating DESC LIMIT 10;"

def format_answer(user_question: str, data_results: str) -> str:
    """Use Gemini to format query results into a natural answer"""
    if "No results found" in data_results or not data_results.strip():
        return "Sorry, I couldn't find any results for your question."
    
    prompt = f"""User Question: {user_question}

Data Retrieved:
{data_results}

Provide a concise, natural answer to the user's question based on the data above. Keep it to 2-3 sentences max."""
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"❌ Formatting Error: {e}")
        return f"Raw data: {data_results[:200]}"

def validate_sql_query(sql_query: str) -> bool:
    """Basic validation ensuring query is read-only and uses valid tables"""
    query_upper = sql_query.upper()
    dangerous_ops = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
    for op in dangerous_ops:
        if op in query_upper:
            return False
            
    valid_tables = ['TITLE_BASICS', 'TITLE_RATINGS', 'TITLE_PRINCIPALS', 'NAME_BASICS']
    return any(tbl in query_upper for tbl in valid_tables)

def test_connection():
    """Test if Gemini API is working using specified models"""
    global MODEL_ID
    fallback_models = ['gemini-3.6-flash', 'gemini-3.5-flash-lite', 'gemini-3.5-flash']
    
    for m in fallback_models:
        try:
            print(f"🔍 Testing active model: {m}")
            response = client.models.generate_content(
                model=m,
                contents="Say 'Hello, IMDb Chatbot ready!' in exactly one sentence.",
            )
            MODEL_ID = m
            print(f"✅ Gemini API connected using '{m}': {response.text}")
            return True
        except Exception as e:
            print(f"⚠️ Model '{m}' failed: {e}")
            
    return False