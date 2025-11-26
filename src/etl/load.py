"""Load module: Insert transformed data into MySQL database."""

import logging
from typing import List, Dict, Any
import mysql.connector
from mysql.connector import Error as MySQLError

logger = logging.getLogger(__name__)


class DatabaseLoader:
    """Manages database connections and loading operations."""
    
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to MySQL database: {self.database}")
        except MySQLError as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_sql_file(self, sql_file_path: str):
        """Execute SQL commands from file."""
        try:
            with open(sql_file_path, "r", encoding="utf-8") as f:
                sql_content = f.read()
            
            # Remove SQL comments
            lines = sql_content.split('\n')
            cleaned_lines = []
            for line in lines:
                if '--' in line:
                    line = line[:line.index('--')]
                cleaned_lines.append(line)
            sql_content = '\n'.join(cleaned_lines)
            
            statements = sql_content.split(";")
            for statement in statements:
                statement = statement.strip()
                if statement:
                    logger.debug(f"Executing: {statement[:100]}...")
                    self.cursor.execute(statement)
                    try:
                        self.cursor.fetchall()
                    except:
                        pass
            
            self.connection.commit()
            logger.info(f"Successfully executed SQL from {sql_file_path}")
        except MySQLError as e:
            logger.error(f"Failed to execute SQL: {e}")
            self.connection.rollback()
            raise
    
    def load_properties(self, property_rows: List[Dict[str, Any]]):
        insert_sql = """
        INSERT INTO properties (
            property_title, address, street_address, city, state, zip_code,
            latitude, longitude, property_type, year_built, sqft_total,
            sqft_basement, sqft_mu, bed, bath, layout, pool, parking,
            basement_yes_no, water, sewage, htw, commercial, highway, train,
            flood, occupancy, net_yield, irr, taxes, tax_rate, market, source,
            neighborhood_rating, school_average, subdivision, reviewed_status,
            most_recent_status, selling_reason, final_reviewer,
            seller_retained_broker, rent_restricted
        ) VALUES (
            %(property_title)s, %(address)s, %(street_address)s, %(city)s,
            %(state)s, %(zip_code)s, %(latitude)s, %(longitude)s,
            %(property_type)s, %(year_built)s, %(sqft_total)s, %(sqft_basement)s,
            %(sqft_mu)s, %(bed)s, %(bath)s, %(layout)s, %(pool)s, %(parking)s,
            %(basement_yes_no)s, %(water)s, %(sewage)s, %(htw)s, %(commercial)s,
            %(highway)s, %(train)s, %(flood)s, %(occupancy)s, %(net_yield)s,
            %(irr)s, %(taxes)s, %(tax_rate)s, %(market)s, %(source)s,
            %(neighborhood_rating)s, %(school_average)s, %(subdivision)s,
            %(reviewed_status)s, %(most_recent_status)s, %(selling_reason)s,
            %(final_reviewer)s, %(seller_retained_broker)s, %(rent_restricted)s
        )
        """
        try:
            self.cursor.executemany(insert_sql, property_rows)
            self.connection.commit()
            logger.info(f"Inserted {self.cursor.rowcount} properties")
        except MySQLError as e:
            logger.error(f"Failed to insert properties: {e}")
            self.connection.rollback()
            raise
    
    def load_valuations(self, valuation_rows: List[Dict[str, Any]]):
        insert_sql = """
        INSERT INTO valuations (
            property_id, valuation_index, list_price, previous_rent, arv,
            rent_zestimate, low_fmr, high_fmr, zestimate, expected_rent,
            redfin_value
        ) VALUES (
            %(property_id)s, %(valuation_index)s, %(list_price)s,
            %(previous_rent)s, %(arv)s, %(rent_zestimate)s, %(low_fmr)s,
            %(high_fmr)s, %(zestimate)s, %(expected_rent)s, %(redfin_value)s
        )
        """
        try:
            self.cursor.executemany(insert_sql, valuation_rows)
            self.connection.commit()
            logger.info(f"Inserted {self.cursor.rowcount} valuations")
        except MySQLError as e:
            logger.error(f"Failed to insert valuations: {e}")
            self.connection.rollback()
            raise
    
    def load_hoa_fees(self, hoa_rows: List[Dict[str, Any]]):
        insert_sql = """
        INSERT INTO hoa_fees (property_id, hoa_index, hoa_amount, hoa_flag)
        VALUES (%(property_id)s, %(hoa_index)s, %(hoa_amount)s, %(hoa_flag)s)
        """
        try:
            self.cursor.executemany(insert_sql, hoa_rows)
            self.connection.commit()
            logger.info(f"Inserted {self.cursor.rowcount} HOA records")
        except MySQLError as e:
            logger.error(f"Failed to insert HOA fees: {e}")
            self.connection.rollback()
            raise
    
    def load_rehab_assessments(self, rehab_rows: List[Dict[str, Any]]):
        insert_sql = """
        INSERT INTO rehab_assessments (
            property_id, rehab_index, underwriting_rehab, rehab_calculation,
            paint, flooring_flag, foundation_flag, roof_flag, hvac_flag,
            kitchen_flag, bathroom_flag, appliances_flag, windows_flag,
            landscaping_flag, trashout_flag
        ) VALUES (
            %(property_id)s, %(rehab_index)s, %(underwriting_rehab)s,
            %(rehab_calculation)s, %(paint)s, %(flooring_flag)s,
            %(foundation_flag)s, %(roof_flag)s, %(hvac_flag)s,
            %(kitchen_flag)s, %(bathroom_flag)s, %(appliances_flag)s,
            %(windows_flag)s, %(landscaping_flag)s, %(trashout_flag)s
        )
        """
        try:
            self.cursor.executemany(insert_sql, rehab_rows)
            self.connection.commit()
            logger.info(f"Inserted {self.cursor.rowcount} rehab records")
        except MySQLError as e:
            logger.error(f"Failed to insert rehab assessments: {e}")
            self.connection.rollback()
            raise


def load_to_database(
    host: str,
    user: str,
    password: str,
    database: str,
    facts: Dict[str, List[Dict[str, Any]]],
    sql_init_file: str = None
):
    """Main loading function."""
    loader = DatabaseLoader(host, user, password, database)
    
    try:
        loader.connect()
        
        if sql_init_file:
            loader.execute_sql_file(sql_init_file)
        
        if facts.get("properties"):
            loader.load_properties(facts["properties"])
        
        if facts.get("valuations"):
            loader.load_valuations(facts["valuations"])
        
        if facts.get("hoa_fees"):
            loader.load_hoa_fees(facts["hoa_fees"])
        
        if facts.get("rehab_assessments"):
            loader.load_rehab_assessments(facts["rehab_assessments"])
        
        logger.info("All data loaded successfully")
    
    finally:
        loader.disconnect()
