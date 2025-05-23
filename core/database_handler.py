"""
Database handler for storing power meter data in MS Access
"""
import logging
import os
import pyodbc
from datetime import datetime
from config.settings import CONFIG

logger = logging.getLogger('powermeter.core.database_handler')

class DatabaseHandler:
    """Handler for storing power meter data in MS Access database"""
    
    def __init__(self):
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
            logger.error("DATABASE_PATH not configured")
            self.enabled = False
            return
            
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")
        
        # If database doesn't exist, it will be created when we connect
        if not os.path.exists(self.db_path):
            logger.info(f"Database will be created at: {self.db_path}")
    
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
                logger.info("Connected to MS Access database")
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
            
            # Create table
            create_table_sql = f"""
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
                simulated YESNO,
                PRIMARY KEY (id)
            )
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            logger.info(f"Created table '{self.table_name}'")
            
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
            self.enabled = False
        finally:
            cursor.close()
    
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
            
            # Insert query
            insert_sql = f"""
            INSERT INTO {self.table_name} (
                [timestamp], power_kw, reactive_power_kvar, apparent_power_kva,
                energy_kwh, power_factor, current_avg, voltage_ll_avg, voltage_ln_avg,
                frequency, phase1_power_kw, phase1_current, phase1_voltage_ln, phase1_pf,
                phase2_power_kw, phase2_current, phase2_voltage_ln, phase2_pf,
                phase3_power_kw, phase3_current, phase3_voltage_ln, phase3_pf,
                data_scalar, simulated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Values to insert
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
                data.get('data_scalar', 0),
                1 if data.get('simulated', False) else 0
            )
            
            cursor.execute(insert_sql, values)
            conn.commit()
            
            logger.debug("Stored reading in database")
            return True
            
        except Exception as e:
            logger.error(f"Error storing reading: {str(e)}")
            # Try to reconnect on next attempt
            self.connection = None
            return False
        finally:
            cursor.close()
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Closed database connection")
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