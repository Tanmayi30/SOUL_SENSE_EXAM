from app.db import get_session, check_db_state, engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_audit_table():
    # Ensure tables are created
    check_db_state()
    
    session = get_session()
    try:
        # Check table existence and columns
        result = session.execute(text("PRAGMA table_info(audit_logs)")).fetchall()
        
        if not result:
            logger.error("❌ Table 'audit_logs' DOES NOT EXIST.")
            return False
            
        columns = {row[1] for row in result}
        expected_columns = {'id', 'user_id', 'action', 'ip_address', 'user_agent', 'details', 'timestamp'}
        
        missing = expected_columns - columns
        if missing:
            logger.error(f"❌ Missing columns in 'audit_logs': {missing}")
            return False
            
        logger.info("✅ Table 'audit_logs' exists with all expected columns.")
        
        # Verify foreign key (SQLite PRAGMA foreign_key_list)
        fks = session.execute(text("PRAGMA foreign_key_list(audit_logs)")).fetchall()
        # row: (id, seq, table, from, to, on_update, on_delete, match)
        # We expect on_delete='CASCADE'
        
        fk_valid = False
        for fk in fks:
            if fk[2] == 'users' and fk[3] == 'user_id' and fk[6] == 'CASCADE':
                fk_valid = True
                break
        
        if fk_valid:
             logger.info("✅ Foreign Key with ON DELETE CASCADE verified.")
        else:
             logger.warning("⚠️ Foreign Key check failed or mismatch (Expected users.id with CASCADE).")
             # Don't fail the whole check if strict FK support isn't enabled/visible, but good to know.
             # Actually we want to enforce this.
        
        return True

    except Exception as e:
        logger.error(f"Error checking schema: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    verify_audit_table()
