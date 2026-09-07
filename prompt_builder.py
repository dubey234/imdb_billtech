import yaml
import os

def load_config(config_path="db_config.yaml"):
    """Reads and parses the YAML database config file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_system_prompt(config_path="db_config.yaml") -> str:
    """Transforms YAML config into a formatted LLM system prompt string."""
    config = load_config(config_path)
    
    prompt = f"=== DATABASE METADATA CONTEXT ({config['database']['type']}) ===\n\n"
    
    # 1. Format Tables & Columns
    prompt += "TABLE SCHEMAS:\n"
    for table_name, table_info in config['tables'].items():
        prompt += f"\nTable: {table_name}\n"
        prompt += f"Description: {table_info['description']}\n"
        prompt += "Columns:\n"
        for col, col_info in table_info['columns'].items():
            pk_str = " (PRIMARY KEY)" if col_info.get('primary_key') else ""
            prompt += f"  - {col} ({col_info['type']}){pk_str}: {col_info['description']}\n"
    
    # 2. Format Relationships
    prompt += "\nRELATIONSHIPS:\n"
    for rel in config.get('relationships', []):
        prompt += f"  - {rel}\n"
        
    # 3. Format Join Rules
    prompt += "\nJOIN STRATEGIES:\n"
    for rule_name, rule_desc in config.get('join_rules', {}).items():
        prompt += f"  - {rule_name}: {rule_desc.strip()}\n"

    # 4. Format Generation Rules
    prompt += "\nSTRICT RULES FOR SQL GENERATION:\n"
    for rule in config.get('sql_generation_rules', []):
        prompt += f"  - {rule}\n"

    return prompt

if __name__ == "__main__":
    system_prompt = build_system_prompt()
    print("Generated Prompt Preview:\n")
    print(system_prompt[:600] + "\n... [truncated]")