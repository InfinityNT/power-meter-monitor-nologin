"""
Database handler for storing power meter data in MS Access
Supports separate production and test databases with different schemas
"""
import logging
import os
import pyodbc
from datetime import datetime
from config.settings import CONFIG

logger = logging.getLogger('powermeter.core.database_handler')

class DatabaseHandler:
    """Handler for storing power meter data in MS Access database"""
    
    def __init__(self, use_test_db=False):
        """
        Initialize database handler
        
        Args:
            use_test_db (bool): If True, use test database; otherwise use production database
        """
        self.use_test_db = use_test_db
        
        if use_test_db:
            self.enabled = CONFIG.get('USE_TEST_DATABASE', False)
            self.db_path = CONFIG.get('TEST_DATABASE_PATH')
            self.table_name = CONFIG.get('TEST_DATABASE_TABLE', 'test_meter_readings')
        else:
            self.enabled = CONFIG.get('USE_DATABASE', False)
            self.db_path = CONFIG.get('DATABASE_PATH')
            self.table_name = CONFIG.get('DATABASE_TABLE', 'meter_readings')
        
        self.connection = None
        
        if self.enabled:
            self._ensure_database_exists()
            self._create_table_if_needed()
    
    def _ensure_database_exists(self):
        """Ensure the database directory and file exist"""
        if not self.db_path:
            logger.error(f"Database path not configured for {'test' if self.use_test_db else 'production'} database")
            self.enabled = False
            return
            
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")
        
        # If database doesn't exist, it will be created when we connect
        if not os.path.exists(self.db_path):
            logger.info(f"{'Test' if self.use_test_db else 'Production'} database will be created at: {self.db_path}")
    
    def _get_connection(self):
        """Get or create database connection"""
        if self.connection is None:
            try:
                # Connection string for MS Access
                conn_str = (
                    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                    f'DBQ={self.db_path};'
                )
                self.connection = pyodbc.connect(conn_str)
                logger.info(f"Connected to {'test' if self.use_test_db else 'production'} MS Access database")
            except Exception as e:
                logger.error(f"Failed to connect to database: {str(e)}")
                self.enabled = False
                return None
        return self.connection
    
    def _create_table_if_needed(self):
        """Create the meter readings table if it doesn't exist"""
        conn = self._get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Check if table exists
            tables = cursor.tables(table=self.table_name, tableType='TABLE').fetchall()
            if tables:
                logger.info(f"Table '{self.table_name}' already exists")
                return
            
            # Create table based on database type
            if self.use_test_db:
                create_table_sql = self._get_test_table_schema()
            else:
                create_table_sql = self._get_production_table_schema()
            
            cursor.execute(create_table_sql)
            conn.commit()
            logger.info(f"Created {'test' if self.use_test_db else 'production'} table '{self.table_name}'")
            
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
            self.enabled = False
        finally:
            cursor.close()
    
    def _get_production_table_schema(self):
        """Get the production database table schema (no test-specific columns)"""
        return f"""
        CREATE TABLE {self.table_name} (
            id COUNTER,
            [timestamp] DATETIME,
            power_kw DOUBLE,
            reactive_power_kvar DOUBLE,
            apparent_power_kva DOUBLE,
            energy_kwh DOUBLE,
            power_factor DOUBLE,
            current_avg DOUBLE,
            voltage_ll_avg DOUBLE,
            voltage_ln_avg DOUBLE,
            frequency DOUBLE,
            phase1_power_kw DOUBLE,
            phase1_current DOUBLE,
            phase1_voltage_ln DOUBLE,
            phase1_pf DOUBLE,
            phase2_power_kw DOUBLE,
            phase2_current DOUBLE,
            phase2_voltage_ln DOUBLE,
            phase2_pf DOUBLE,
            phase3_power_kw DOUBLE,
            phase3_current DOUBLE,
            phase3_voltage_ln DOUBLE,
            phase3_pf DOUBLE,
            data_scalar INTEGER,
            PRIMARY KEY (id)
        )
        """
    
    def _get_test_table_schema(self):
        """Get the test database table schema (includes test metadata)"""
        return f"""
        CREATE TABLE {self.table_name} (
            id COUNTER,
            [timestamp] DATETIME,
            test_name VARCHAR(255),
            test_type VARCHAR(100),
            test_duration DOUBLE,
            test_status VARCHAR(50),
            notes MEMO,
            power_kw DOUBLE,
            reactive_power_kvar DOUBLE,
            apparent_power_kva DOUBLE,
            energy_kwh DOUBLE,
            power_factor DOUBLE,
            current_avg DOUBLE,
            voltage_ll_avg DOUBLE,
            voltage_ln_avg DOUBLE,
            frequency DOUBLE,
            phase1_power_kw DOUBLE,
            phase1_current DOUBLE,
            phase1_voltage_ln DOUBLE,
            phase1_pf DOUBLE,
            phase2_power_kw DOUBLE,
            phase2_current DOUBLE,
            phase2_voltage_ln DOUBLE,
            phase2_pf DOUBLE,
            phase3_power_kw DOUBLE,
            phase3_current DOUBLE,
            phase3_voltage_ln DOUBLE,
            phase3_pf DOUBLE,
            data_scalar INTEGER,
            simulated YESNO,
            PRIMARY KEY (id)
        )
        """
    
    def store_reading(self, data):
        """Store a power meter reading in the database"""
        if not self.enabled:
            return False
            
        conn = self._get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # Prepare the data
            system_data = data.get('system', {})
            phase1_data = data.get('phase_1', {})
            phase2_data = data.get('phase_2', {})
            phase3_data = data.get('phase_3', {})
            
            if self.use_test_db:
                # Test database includes test metadata
                insert_sql = f"""
                INSERT INTO {self.table_name} (
                    [timestamp], test_name, test_type, test_duration, test_status, notes,
                    power_kw, reactive_power_kvar, apparent_power_kva, energy_kwh, power_factor,
                    current_avg, voltage_ll_avg, voltage_ln_avg, frequency,
                    phase1_power_kw, phase1_current, phase1_voltage_ln, phase1_pf,
                    phase2_power_kw, phase2_current, phase2_voltage_ln, phase2_pf,
                    phase3_power_kw, phase3_current, phase3_voltage_ln, phase3_pf,
                    data_scalar, simulated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = (
                    datetime.fromtimestamp(data.get('timestamp', 0)),
                    data.get('test_name', 'Unknown Test'),
                    data.get('test_type', 'simulation'),
                    data.get('test_duration', 0),
                    data.get('test_status', 'running'),
                    data.get('notes', ''),
                    system_data.get('power_kw') or data.get('power_kw', 0),
                    system_data.get('reactive_power_kvar') or data.get('reactive_power_kvar', 0),
                    system_data.get('apparent_power_kva') or data.get('apparent_power_kva', 0),
                    system_data.get('energy_kwh') or data.get('energy_kwh', 0),
                    system_data.get('displacement_pf') or data.get('power_factor', 0),
                    system_data.get('current_avg') or data.get('current_avg', 0),
                    system_data.get('voltage_ll_avg') or data.get('voltage_ll_avg', 0),
                    system_data.get('voltage_ln_avg') or data.get('voltage_ln_avg', 0),
                    data.get('frequency', 0),
                    phase1_data.get('power_kw', 0),
                    phase1_data.get('current', 0),
                    phase1_data.get('voltage_ln', 0),
                    phase1_data.get('displacement_pf', 0),
                    phase2_data.get('power_kw', 0),
                    phase2_data.get('current', 0),
                    phase2_data.get('voltage_ln', 0),
                    phase2_data.get('displacement_pf', 0),
                    phase3_data.get('power_kw', 0),
                    phase3_data.get('current', 0),
                    phase3_data.get('voltage_ln', 0),
                    phase3_data.get('displacement_pf', 0),
                    data.get('data_scalar', 0),
                    1 if data.get('simulated', False) else 0
                )
            else:
                # Production database (no test metadata)
                insert_sql = f"""
                INSERT INTO {self.table_name} (
                    [timestamp], power_kw, reactive_power_kvar, apparent_power_kva,
                    energy_kwh, power_factor, current_avg, voltage_ll_avg, voltage_ln_avg,
                    frequency, phase1_power_kw, phase1_current, phase1_voltage_ln, phase1_pf,
                    phase2_power_kw, phase2_current, phase2_voltage_ln, phase2_pf,
                    phase3_power_kw, phase3_current, phase3_voltage_ln, phase3_pf,
                    data_scalar
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = (
                    datetime.fromtimestamp(data.get('timestamp', 0)),
                    system_data.get('power_kw') or data.get('power_kw', 0),
                    system_data.get('reactive_power_kvar') or data.get('reactive_power_kvar', 0),
                    system_data.get('apparent_power_kva') or data.get('apparent_power_kva', 0),
                    system_data.get('energy_kwh') or data.get('energy_kwh', 0),
                    system_data.get('displacement_pf') or data.get('power_factor', 0),
                    system_data.get('current_avg') or data.get('current_avg', 0),
                    system_data.get('voltage_ll_avg') or data.get('voltage_ll_avg', 0),
                    system_data.get('voltage_ln_avg') or data.get('voltage_ln_avg', 0),
                    data.get('frequency', 0),
                    phase1_data.get('power_kw', 0),
                    phase1_data.get('current', 0),
                    phase1_data.get('voltage_ln', 0),
                    phase1_data.get('displacement_pf', 0),
                    phase2_data.get('power_kw', 0),
                    phase2_data.get('current', 0),
                    phase2_data.get('voltage_ln', 0),
                    phase2_data.get('displacement_pf', 0),
                    phase3_data.get('power_kw', 0),
                    phase3_data.get('current', 0),
                    phase3_data.get('voltage_ln', 0),
                    phase3_data.get('displacement_pf', 0),
                    data.get('data_scalar', 0)
                )
            
            cursor.execute(insert_sql, values)
            conn.commit()
            
            logger.debug(f"Stored reading in {'test' if self.use_test_db else 'production'} database")
            return True
            
        except Exception as e:
            logger.error(f"Error storing reading: {str(e)}")
            # Try to reconnect on next attempt
            self.connection = None
            return False
        finally:
            cursor.close()
    
    def store_test_result(self, test_name, test_type, status, duration=0, notes="", meter_data=None):
        """
        Store a test result in the test database
        
        Args:
            test_name (str): Name of the test
            test_type (str): Type of test (simulation, network, database, etc.)
            status (str): Test status (pass, fail, running, etc.)
            duration (float): Test duration in seconds
            notes (str): Additional notes about the test
            meter_data (dict): Optional meter data associated with the test
        """
        if not self.use_test_db:
            logger.warning("store_test_result called on production database handler")
            return False
        
        # Create test data structure
        test_data = {
            'timestamp': datetime.now().timestamp(),
            'test_name': test_name,
            'test_type': test_type,
            'test_duration': duration,
            'test_status': status,
            'notes': notes,
            'simulated': True
        }
        
        # Include meter data if provided
        if meter_data:
            test_data.update(meter_data)
        
        return self.store_reading(test_data)
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            try:
                self.connection.close()
                logger.info(f"Closed {'test' if self.use_test_db else 'production'} database connection")
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")
            finally:
                self.connection = None
    
    def get_recent_readings(self, limit=100):
        """Get recent readings from the database"""
        if not self.enabled:
            return []
            
        conn = self._get_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            
            query = f"""
            SELECT TOP {limit} * FROM {self.table_name}
            ORDER BY timestamp DESC
            """
            
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting recent readings: {str(e)}")
            return []
        finally:
            cursor.close()


# Convenience functions for getting database handlers
def get_production_db():
    """Get a production database handler"""
    return DatabaseHandler(use_test_db=False)

def get_test_db():
    """Get a test database handler"""
    return DatabaseHandler(use_test_db=True)
