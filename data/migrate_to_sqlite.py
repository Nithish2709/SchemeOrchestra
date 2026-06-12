"""
SQLite Database Schema and Migration Script
Migrates JSON scheme data to SQLite database
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "schemes.db"
SCHEMES_DIR = Path(__file__).parent.parent / "data" / "schemes"

def create_database():
    """Create SQLite database with schemes table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing table if exists
    cursor.execute("DROP TABLE IF EXISTS schemes")
    
    # Create schemes table
    cursor.execute("""
        CREATE TABLE schemes (
            scheme_id TEXT PRIMARY KEY,
            name_en TEXT NOT NULL,
            name_ta TEXT,
            type TEXT,
            category TEXT,
            description_en TEXT,
            description_ta TEXT,
            
            -- Eligibility criteria
            min_age INTEGER,
            max_age INTEGER,
            income_limit INTEGER,
            caste TEXT,  -- Comma-separated or 'all'
            gender TEXT,
            education_level TEXT,  -- Comma-separated
            target_group TEXT,  -- Comma-separated
            first_graduate BOOLEAN,
            state_resident BOOLEAN,
            parent_ex_serviceman BOOLEAN,
            
            -- Benefits
            benefit_type TEXT,
            benefit_value TEXT,
            benefit_frequency TEXT,
            
            -- Documents (stored as JSON string)
            documents_required TEXT,
            
            -- Application
            apply_url TEXT,
            official_source TEXT,
            last_updated TEXT,
            active BOOLEAN DEFAULT 1,
            
            -- Search optimization (for RAG)
            youtube_keywords TEXT,  -- JSON array as string
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for fast eligibility queries
    cursor.execute("CREATE INDEX idx_education ON schemes(education_level)")
    cursor.execute("CREATE INDEX idx_income ON schemes(income_limit)")
    cursor.execute("CREATE INDEX idx_age ON schemes(min_age, max_age)")
    cursor.execute("CREATE INDEX idx_category ON schemes(category)")
    cursor.execute("CREATE INDEX idx_active ON schemes(active)")
    
    conn.commit()
    conn.close()
    print(f"[OK] Database created at {DB_PATH}")


def migrate_schemes_from_json():
    """Migrate all schemes from JSON files to SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total_migrated = 0
    
    # Load all JSON scheme files
    for json_file in SCHEMES_DIR.glob("*.json"):
        if "template" in json_file.name:
            continue
            
        with open(json_file, 'r', encoding='utf-8') as f:
            schemes = json.load(f)
        
        for scheme in schemes:
            # Skip invalid structures (like nested 'schemes' lists)
            if 'schemes' in scheme:
                continue
                
            # Extract basic info with fallbacks
            name_en = scheme.get('name_en') or scheme.get('current_name') or scheme.get('scheme_name')
            if not name_en:
                continue # Skip if we absolutely cannot find a name
                
            scheme_id = scheme.get('scheme_id') or f"UNKNOWN_SCH_{total_migrated}"
            
            # Extract eligibility criteria
            elig = scheme.get('eligibility', {})
            
            # Handle caste
            caste_value = elig.get('caste', 'all')
            if isinstance(caste_value, list):
                caste_value = ','.join(caste_value)
            
            # Handle education level
            edu_level = elig.get('education_level', '')
            if isinstance(edu_level, list):
                edu_level = ','.join(edu_level)
            
            # Handle target group
            target = elig.get('target_group', '')
            if isinstance(target, list):
                target = ','.join(target)
            
            # Handle gender
            gender_value = elig.get('gender', 'all')
            if isinstance(gender_value, list):
                gender_value = ','.join(gender_value)
            
            # Extract benefits
            benefits = scheme.get('benefits', {})
            
            # Insert into database
            cursor.execute("""
                INSERT OR REPLACE INTO schemes VALUES (
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?
                )
            """, (
                scheme_id,
                name_en,
                scheme.get('name_ta'),
                scheme.get('type'),
                scheme.get('category'),
                scheme.get('description_en'),
                scheme.get('description_ta'),
                
                # Eligibility
                elig.get('age_min'),
                elig.get('age_max'),
                elig.get('income_limit_annual'),
                caste_value,
                gender_value,
                edu_level,
                target,
                elig.get('first_graduate', False),
                elig.get('state_resident', True),
                elig.get('parent_ex_serviceman', False),
                
                # Benefits
                benefits.get('type') if isinstance(benefits, dict) else None,
                benefits.get('value') if isinstance(benefits, dict) else str(benefits),
                benefits.get('frequency') if isinstance(benefits, dict) else None,
                
                # Documents
                json.dumps(scheme.get('documents_required', [])),
                
                # Application
                scheme.get('apply_url'),
                scheme.get('official_source'),
                scheme.get('last_updated'),
                scheme.get('active', True),
                
                # Search
                json.dumps(scheme.get('youtube_keywords', [])),
                
                datetime.now().isoformat()
            ))
            
            total_migrated += 1
    
    conn.commit()
    conn.close()
    
    print(f"[OK] Migrated {total_migrated} schemes to database")
    return total_migrated


def verify_migration():
    """Verify the migration was successful"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Count total schemes
    cursor.execute("SELECT COUNT(*) FROM schemes")
    total = cursor.fetchone()[0]
    print(f"[OK] Total schemes in database: {total}")
    
    # Show sample schemes
    cursor.execute("SELECT scheme_id, name_en, category FROM schemes LIMIT 5")
    print("\nSample schemes:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} ({row[2]})")
    
    conn.close()


if __name__ == "__main__":
    print("Starting database migration...\n")
    create_database()
    migrate_schemes_from_json()
    verify_migration()
    print("\n[OK] Migration complete!")
