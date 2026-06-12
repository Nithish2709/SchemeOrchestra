"""
SQLite-based Eligibility Engine
Replaces the JSON rules engine with SQL queries
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict

DB_PATH = Path(__file__).parent.parent / "schemes.db"


class SQLiteEligibilityEngine:
    """SQL-based eligibility checking engine"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
    
    def check_eligibility(self, user_profile: dict) -> List[Dict]:
        """
        Check eligibility using SQL query
        Returns list of eligible schemes
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        cursor = conn.cursor()
        
        # Extract profile data
        age = user_profile.get('age', 0)
        income = user_profile.get('income_annual', 0)
        caste = user_profile.get('caste', '').upper()
        gender = user_profile.get('gender', '').lower()
        education = user_profile.get('education_level', '').lower()
        first_grad = user_profile.get('first_graduate', False)
        state_resident = user_profile.get('state_resident', True)
        parent_ex = user_profile.get('parent_ex_serviceman', False)
        
        # Build SQL query with eligibility filters
        query = """
            SELECT * FROM schemes
            WHERE active = 1
            AND (state_resident = 0 OR state_resident = ?)
            AND (min_age IS NULL OR ? >= min_age)
            AND (max_age IS NULL OR ? <= max_age)
            AND (income_limit IS NULL OR ? <= income_limit)
            AND (gender = 'all' OR gender = ?)
            AND (first_graduate = 0 OR first_graduate = ?)
            AND (parent_ex_serviceman = 0 OR parent_ex_serviceman = ?)
        """
        
        params = [
            1 if state_resident else 0,
            age, age,
            income,
            gender,
            1 if first_grad else 0,
            1 if parent_ex else 0
        ]
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Filter by education and caste (comma-separated fields)
        eligible_schemes = []
        
        for row in rows:
            # Check education level
            edu_levels = row['education_level']
            if edu_levels and edu_levels != '':
                edu_list = [e.strip().lower() for e in edu_levels.split(',')]
                if education and education not in edu_list:
                    continue
            
            # Check caste
            castes = row['caste']
            if castes and castes != 'all':
                caste_list = [c.strip().upper() for c in castes.split(',')]
                
                # Handle minority special case
                is_minority = caste.upper() in ['MINORITY', 'MUSLIM', 'CHRISTIAN', 'SIKH', 'BUDDHIST', 'JAIN', 'PARSI']
                if 'MINORITY' in caste_list and is_minority:
                    pass  # Eligible
                elif caste.upper() not in caste_list:
                    continue
            
            # Convert row to dictionary
            scheme = dict(row)
            
            # Parse JSON fields
            scheme['documents_required'] = json.loads(scheme['documents_required']) if scheme['documents_required'] else []
            scheme['youtube_keywords'] = json.loads(scheme['youtube_keywords']) if scheme['youtube_keywords'] else []
            
            # Reconstruct benefits structure
            scheme['benefits'] = {
                'type': scheme['benefit_type'],
                'value': scheme['benefit_value'],
                'frequency': scheme['benefit_frequency']
            }
            
            # Reconstruct eligibility structure for compatibility
            scheme['eligibility'] = {
                'age_min': scheme['min_age'],
                'age_max': scheme['max_age'],
                'income_limit_annual': scheme['income_limit'],
                'caste': scheme['caste'],
                'gender': scheme['gender'],
                'education_level': scheme['education_level'].split(',') if scheme['education_level'] else [],
                'first_graduate': bool(scheme['first_graduate']),
                'state_resident': bool(scheme['state_resident'])
            }
            
            eligible_schemes.append(scheme)
        
        conn.close()
        return eligible_schemes
    
    def get_scheme_by_id(self, scheme_id: str) -> Dict:
        """Get single scheme by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM schemes WHERE scheme_id = ?", (scheme_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        scheme = dict(row)
        
        # Parse JSON fields
        scheme['documents_required'] = json.loads(scheme['documents_required']) if scheme['documents_required'] else []
        scheme['youtube_keywords'] = json.loads(scheme['youtube_keywords']) if scheme['youtube_keywords'] else []
        
        # Reconstruct structures
        scheme['benefits'] = {
            'type': scheme['benefit_type'],
            'value': scheme['benefit_value'],
            'frequency': scheme['benefit_frequency']
        }
        
        conn.close()
        return scheme
    
    def get_all_schemes(self) -> List[Dict]:
        """Get all active schemes"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM schemes WHERE active = 1")
        rows = cursor.fetchall()
        
        schemes = []
        for row in rows:
            scheme = dict(row)
            scheme['documents_required'] = json.loads(scheme['documents_required']) if scheme['documents_required'] else []
            scheme['youtube_keywords'] = json.loads(scheme['youtube_keywords']) if scheme['youtube_keywords'] else []
            scheme['benefits'] = {
                'type': scheme['benefit_type'],
                'value': scheme['benefit_value'],
                'frequency': scheme['benefit_frequency']
            }
            schemes.append(scheme)
        
        conn.close()
        return schemes


# Global instance
_engine = None

def get_eligibility_engine():
    """Get or create eligibility engine instance"""
    global _engine
    if _engine is None:
        _engine = SQLiteEligibilityEngine()
    return _engine


def check_eligibility(user_profile: dict) -> List[Dict]:
    """Main entry point for eligibility checking"""
    engine = get_eligibility_engine()
    return engine.check_eligibility(user_profile)


def get_scheme_by_id(scheme_id: str) -> Dict:
    """Get scheme by ID"""
    engine = get_eligibility_engine()
    return engine.get_scheme_by_id(scheme_id)


def get_all_schemes() -> List[Dict]:
    """Get all schemes"""
    engine = get_eligibility_engine()
    return engine.get_all_schemes()
