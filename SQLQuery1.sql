--SELECT * FROM SYS.DATABASES;
 
--CREATE DATABASE Dell5edsData;
 
--USE Dell5edsData;
 
--CREATE TABLE OMDdata(
--  id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
--  d_name VARCHAR(100),
--  d_value FLOAT,
--  date_time DATETIME,
--  date DATE,
--  time TIME
--);
 
--SELECT *FROM sys.tables;
 
SELECT * FROM OMDdata ORDER BY date_time desc;
 