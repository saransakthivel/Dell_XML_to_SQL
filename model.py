from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Date, Time, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
import uuid
 
Base = declarative_base()
 
class EDSdata(Base):
    __tablename__ = 'OMDdata'
 
    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    d_name = Column(String)
    d_value = Column(Float)
    date_time = Column(DateTime)
    date = Column(Date)
    time = Column(Time)