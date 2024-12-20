from airflow import DAG
from airflow.models import Connection
from airflow.operators.python import PythonOperator  # Import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.utils.dates import days_ago
from airflow.settings import Session
from sqlalchemy.orm import sessionmaker

# Define Snowflake connection details
SNOWFLAKE_CONN_ID = 'my_snowflake_conn'
SNOWFLAKE_CONN_DETAILS = {
    "conn_type": "snowflake",
    "login": "prakashsf7",  # Replace with your Snowflake username
    "password": "Prakash@303",  # Replace with your Snowflake password
    "host": "gkbdmnc-jw27443",  # Replace with your Snowflake host
    "schema": "AIRFLOW_SC",  # Replace with your Snowflake schema
    "extra": '{"account": "gkbdmnc-jw27443", "warehouse": "AIRFLOW_DEV", "database": "AIRFLOW_DB", "role": "ACCOUNTADMIN"}'  # Additional Snowflake settings
}

# Create the connection in the Airflow database
def create_snowflake_connection():
    session = Session()  # Use Session() directly
    conn = session.query(Connection).filter(Connection.conn_id == SNOWFLAKE_CONN_ID).first()
    if not conn:
        # Create a new Snowflake connection if it doesn't exist
        conn = Connection(conn_id=SNOWFLAKE_CONN_ID, **SNOWFLAKE_CONN_DETAILS)
        session.add(conn)
        session.commit()
        print(f"Connection {SNOWFLAKE_CONN_ID} created successfully.")
    else:
        print(f"Connection {SNOWFLAKE_CONN_ID} already exists.")
    session.close()  # Close the session after committing

# Define the SQL query to create a table
CREATE_TABLE_SQL = """
CREATE OR REPLACE TABLE my_table (
    id INT,
    name STRING,
    created_at TIMESTAMP_LTZ
);
"""

# SQL to create a new table in Snowflake
create_NEW_table_sql = """
CREATE OR REPLACE TABLE my_new_table (
    id INT,
    name STRING,
    created_at TIMESTAMP
);
"""

# SQL to insert data into the table
insert_data_sql = """
INSERT INTO my_new_table (id, name, created_at)
VALUES 
    (1, 'John Doe', CURRENT_TIMESTAMP),
    (2, 'Jane Doe', CURRENT_TIMESTAMP);
"""



# Define the DAG
with DAG(
    dag_id='snowflake_create_table_dag',
    default_args={'owner': 'airflow', 'retries': 1},
    start_date=days_ago(1),
    #schedule_interval=None,  # Set to None to run manually
    schedule_interval='*/15 * * * *',  # Run this task every 15 minutes
    catchup=False,
) as dag:

    # Task 1: Create the Snowflake connection
    create_connection_task = PythonOperator(
        task_id='create_snowflake_connection',
        python_callable=create_snowflake_connection,
    )

    # Task 2: Create a table in Snowflake
    create_table_task = SnowflakeOperator(
        task_id='create_snowflake_table',
        sql=CREATE_TABLE_SQL,
        snowflake_conn_id=SNOWFLAKE_CONN_ID,  # Use the connection ID created above
    )


        # Task 3: Create a table in Snowflake
    create_NEWtable_task = SnowflakeOperator(
        task_id='create_snowflake_NEW_table',
        sql=create_NEW_table_sql,
        snowflake_conn_id=SNOWFLAKE_CONN_ID,  # Use the connection ID created above
    )

            # Task 3: Create a table in Snowflake
    INSERT_DATA_INTO_table_task = SnowflakeOperator(
        task_id='INSERT_snowflake_NEW_table',
        sql=insert_data_sql,
        snowflake_conn_id=SNOWFLAKE_CONN_ID,  # Use the connection ID created above
    )



    # Set dependencies: Create connection first, then create the table
    create_connection_task >> create_table_task >> create_NEWtable_task >> INSERT_DATA_INTO_table_task
