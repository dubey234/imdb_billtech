import duckdb
from llm_handler import generate_sql_query, format_answer, validate_sql_query

class IMDbChatbot:
    def __init__(self, db_path='imdb_data.duckdb'):
        self.db_path = db_path
        self.last_sql = ""
    
    def query_database(self, sql_query: str) -> tuple[str, bool]:
        """Execute SQL query and return results as formatted string"""
        try:
            conn = duckdb.connect(self.db_path, read_only=True)
            
            # Validate query safety
            if not validate_sql_query(sql_query):
                return "❌ Invalid query - only SELECT operations on movies table are allowed.", False
            
            # Execute query
            result = conn.execute(sql_query).fetchall()
            
            if not result:
                return "No results found.", False
            
            # Get column names
            columns = [desc[0] for desc in conn.description]
            
            # Format results nicely
            header = " | ".join(columns)
            separator = "-" * len(header)
            
            formatted = f"{header}\n{separator}\n"
            for row in result:
                formatted += " | ".join(str(v)[:50] if v else "N/A" for v in row) + "\n"
            
            conn.close()
            return formatted, True
        
        except Exception as e:
            return f"Database error: {str(e)}", False
    
    def answer_question(self, user_question: str) -> dict:
        """
        Main chatbot function
        Returns: dict with answer, sql_query, and success status
        """
        
        # Step 1: Generate SQL from question
        self.last_sql = generate_sql_query(user_question)
        
        # Step 2: Execute query
        data_results, success = self.query_database(self.last_sql)
        
        if not success:
            return {
                "answer": data_results,
                "sql_query": self.last_sql,
                "success": False
            }
        
        # Step 3: Format answer
        answer = format_answer(user_question, data_results)
        
        return {
            "answer": answer,
            "sql_query": self.last_sql,
            "raw_data": data_results,
            "success": True
        }

# Global chatbot instance
chatbot = IMDbChatbot()
