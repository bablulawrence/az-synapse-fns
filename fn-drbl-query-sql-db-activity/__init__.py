import logging
import struct
import json
from time import time
from collections import namedtuple
import pyodbc
from azure.identity import DefaultAzureCredential
from pyapacheatlas.core import PurviewClient

Params = namedtuple('Params', ['server', 'database', 'output', 'query'])

def get_access_token():
        creds = DefaultAzureCredential()
        token = creds.get_token("https://database.windows.net/.default")
        tokenb = bytes(token.token, "UTF-8")
        exptoken = b''

        for i in tokenb:
            exptoken += bytes({i})
            exptoken += bytes(1)
            tokenstruct = struct.pack("=i", len(exptoken)) + exptoken    
        return tokenstruct

def execute_query(cursor, query): 
    cursor.execute(query)
    rows = []
    for row in cursor:
        rows += [[elem for elem in row]]
    return rows

def main(params: Params) -> str:
    logging.info('Starting execution of activity function')       
  
    driver="{ODBC Driver 17 for SQL Server}"
    server, database, output, query = params    

    if (server and database and  output and  query):
        conn_string = f"DRIVER={driver};SERVER={server};DATABASE={database}"
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        try:
            access_token = get_access_token()
            with pyodbc.connect(conn_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: access_token}) as conn:
                with conn.cursor() as cursor:
                    if (output == 'json'):
                        return execute_query(cursor, query)
                    elif (output == 'stats'):
                        start_time = time()
                        execute_query(cursor, query)
                        end_time = time()
                        return(end_time - start_time)
                    else: 
                        return 'Invalid output type'

        except Exception as e: 
            logging.exception(e)
            return str(e)
    else:
        return 'One or more required parameters are missing'

        