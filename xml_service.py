import os
import pytz
import time
import requests
import servicemanager
import logging
from datetime import datetime
import xml.etree.ElementTree as ET
import win32serviceutil, win32event, win32service
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from apscheduler.schedulers.background import BackgroundScheduler
from model import EDSdata
from requests.auth import HTTPDigestAuth
 
DATABASE_URL = "mssql+pyodbc://sa:RPSsql12345@localhost:1433/Dell5edsData?driver=ODBC+Driver+17+for+SQL+Server"
 
engine = create_engine(DATABASE_URL)
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
script_dir = os.path.abspath(os.path.dirname(__file__))
omd_file = os.path.join(script_dir, "OMD LAB PDU-01.txt")
 
fetch_interval = 290 #seconds
 
logging.basicConfig(
    filename="service_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s -%(message)s"
)
 
logging.info("Service Started!")
 
class EdsToSqlService(win32serviceutil.ServiceFramework):
    _svc_name_ = "EDSDataFetchService"
    _svc_display_name_ = "EDS Data Fetch Service"
    _svc_description_ = "Fetches EDS Data and Stores in SQL Database"
 
    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.scheduler = BackgroundScheduler()
 
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        try:
            self.scheduler.shutdown()
        except Exception as e:
            logging.error(f"Scheduler shutdown error: {e}")
   
    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        try:
            self.scheduler.add_job(self.fetchAndStore_XmlData, 'interval', seconds=fetch_interval, max_instances=1)
            logging.info("Job Scheduled: fetchAndStore_XmlData every %s seconds", fetch_interval)
 
            self.scheduler.start()
            logging.info("Scheduler statred successfully.")
        except Exception as e:
            logging.error(f"Error starting scheduler: {e}")
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
 
    def fetchAndStore_XmlData(self):
        db = sessionlocal()
        try:
            with open(omd_file, "r") as file:
                urls = [line.strip() for line in file if line.strip()]
                logging.info(f"Extracted URLs: {urls}")
 
                now_ist = datetime.now(pytz.timezone("Asia/Kolkata"))
                datetime_str = now_ist.strftime("%Y-%m-%d %H:%M:%S")
                date_str = now_ist.date()
                time_str = now_ist.time().strftime("%H:%M:%S")
 
                logging.info(f"Timestamp for this fetch cycle: {datetime_str}")
 
                for url in urls:
                    try:
                        logging.info(f"fetching data from {url}")
                       
                        #Authentication
                        username = 'Suresh'
                        password = 'Suresh'
                        response = requests.get(url, auth=HTTPDigestAuth(username, password))
 
                        if response.status_code == 200:
                            logging.info(f"Login Successful for {url}")
                            root = ET.fromstring(response.content)
                            variable_elements = root.findall(".//variable")
                            for variable_element in variable_elements:
                                d_name = variable_element.find("id").text
                                d_value = float(variable_element.find("value").text)
 
                                data_record = EDSdata(
                                    d_name = d_name,
                                    d_value = d_value,
                                    date_time = datetime_str,
                                    date = date_str,
                                    time = time_str
                                )
 
                                try:
                                    db.add(data_record)
                                    db.commit()
                                    logging.info(f"OMD Data Stored Successfully. Total records: {len(data_record)}")
                                except Exception as db_error:
                                    db.rollback()
                                    logging.error(f"Error, Storing Databas in Database: {db_error}")
                        else:
                            logging.error(f"Failed to fetch XML data from {url}. Status Code: {response.status_code}")
                    except Exception as e:
                        logging.error(f"Error Fetching data from {url}: {e}")
        except Exception as e:
            logging.error(f"Error Reading urls or processing data: {e}")
        finally:
            db.close()          
 
if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(EdsToSqlService)
    # service = EdsToSqlService()
    # service.SvcDoRun()