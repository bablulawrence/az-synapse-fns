import azure.functions as func
import logging
import json
import pyodbc
import os
from time import time


def execute_query(cursor, query): 
    cursor.execute(query)
    rows = []
    for row in cursor:
        rows += [[elem for elem in row]]
    return rows

    
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Starting execution')
    login = os.environ['SQL_LOGIN']
    password = os.environ['SQL_PWD']
    driver="{ODBC Driver 17 for SQL Server}"
    try:
        req_body = req.get_json()
        logging.error(req_body)
    except ValueError:
        pass
    else:
        server = req_body.get('server')
        database = req_body.get('database')
        output = req_body.get('output')
        query = req_body.get('query')

    if (not server or not database or not output or not query):
        func.HttpResponse("One or more required parameters are missing", status_code = 400)

    conn_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={login};PWD={password};autocommit=True"
    try:
        with pyodbc.connect(conn_string) as conn:
            with conn.cursor() as cursor:
                if (output and output == 'stats'):
                    start_time = time()
                    execute_query(cursor, query)
                    end_time = time()
                    return func.HttpResponse(json.dumps({ "executionTime" : end_time - start_time }),
                                        mimetype="application/json",
                                        status_code = 200) 
                else:
                    rows = execute_query(cursor, query)
                    return func.HttpResponse(json.dumps(rows), mimetype="application/json", status_code=200)
                
    except Exception as e: 
        logging.exception(e)
        return func.HttpResponse(str(e), status_code=500)
    