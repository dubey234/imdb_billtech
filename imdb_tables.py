import os
import duckdb

DB_PATH = 'imdb_data.duckdb'
LOCAL_DIR = r'C:\Users\Archit\Downloads\project_chatbot\archive'

def load_local_tsv_tables():
    print("=" * 65)
    print("🚀 Loading Local IMDb TSV Files into DuckDB (1,000 Rows Each)")
    print("=" * 65)

    conn = duckdb.connect(DB_PATH)

    # 1. Load title.basics -> Table: title_basics
    basics_path = os.path.join(LOCAL_DIR, 'title.basics.tsv').replace('\\', '/')
    print(f"\n⏳ [1/4] Processing '{basics_path}'...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE title_basics AS 
        SELECT 
            tconst, 
            titleType, 
            primaryTitle, 
            originalTitle, 
            TRY_CAST(isAdult AS INT) AS isAdult, 
            TRY_CAST(startYear AS INT) AS startYear, 
            TRY_CAST(endYear AS INT) AS endYear, 
            TRY_CAST(runtimeMinutes AS INT) AS runtimeMinutes, 
            genres 
        FROM read_csv_auto('{basics_path}', delim='\t', nullstr='\\N', ignore_errors=true) 
        LIMIT 1000;
    """)
    print("   ✅ Table 'title_basics' created successfully.")

    # 2. Load title.ratings -> Table: title_ratings
    ratings_path = os.path.join(LOCAL_DIR, 'title.ratings.tsv').replace('\\', '/')
    print(f"\n⏳ [2/4] Processing '{ratings_path}'...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE title_ratings AS 
        SELECT 
            tconst, 
            TRY_CAST(averageRating AS FLOAT) AS averageRating, 
            TRY_CAST(numVotes AS BIGINT) AS numVotes 
        FROM read_csv_auto('{ratings_path}', delim='\t', nullstr='\\N', ignore_errors=true) 
        LIMIT 1000;
    """)
    print("   ✅ Table 'title_ratings' created successfully.")

    # 3. Load name.basics -> Table: name_basics
    names_path = os.path.join(LOCAL_DIR, 'name.basics.tsv').replace('\\', '/')
    print(f"\n⏳ [3/4] Processing '{names_path}'...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE name_basics AS 
        SELECT 
            nconst, 
            primaryName, 
            TRY_CAST(birthYear AS INT) AS birthYear, 
            TRY_CAST(deathYear AS INT) AS deathYear, 
            primaryProfession, 
            knownForTitles 
        FROM read_csv_auto('{names_path}', delim='\t', nullstr='\\N', ignore_errors=true) 
        LIMIT 1000;
    """)
    print("   ✅ Table 'name_basics' created successfully.")

    # 4. Load title.principals -> Table: title_principals
    principals_path = os.path.join(LOCAL_DIR, 'title.principals.tsv').replace('\\', '/')
    print(f"\n⏳ [4/4] Processing '{principals_path}'...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE title_principals AS 
        SELECT 
            tconst, 
            TRY_CAST(ordering AS INT) AS ordering, 
            nconst, 
            category, 
            job, 
            characters 
        FROM read_csv_auto('{principals_path}', delim='\t', nullstr='\\N', ignore_errors=true) 
        LIMIT 1000;
    """)
    print("   ✅ Table 'title_principals' created successfully.")

    # Verification Summary
    print("\n" + "=" * 65)
    print("📊 Summary of Tables Created:")
    tables = ['title_basics', 'title_ratings', 'name_basics', 'title_principals']
    for tbl in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {tbl};").fetchone()[0]
        print(f"   • {tbl}: {count:,} rows")
    print("=" * 65)

    conn.close()

if __name__ == "__main__":
    load_local_tsv_tables()