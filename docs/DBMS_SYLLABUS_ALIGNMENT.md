# DBMS syllabus alignment — MedCare Pharmacy

**Project:** DBMS Laboratory, Project No. 13 — Pharmacy Management System  
**Student level:** B.Tech, second year, first semester  
**Database tool for lab demonstration:** MySQL Community Server 8.4  
**Live web app database:** SQLite (unchanged)

## College-source note

The official Vardhaman College of Engineering academic site provides curriculum links, and the official CSE (Data Science) department site provides department information:
- https://academics.vardhaman.org/
- https://cse-ds.vardhaman.org/
- https://vardhaman.org/

The public pages found during this update did not expose a verifiable complete DBMS unit-wise syllabus in the retrieved text. Therefore, this project map is based on DBMS topics previously discussed for Project 13 and common introductory DBMS lab work; it is **not represented as a verbatim official syllabus**. Compare it with the current course handout before submission.

## Topic-to-project map

| DBMS topic | How MedCare demonstrates it |
|---|---|
| Database purpose and relational model | Pharmacy records split into related tables |
| ER model and relationships | Supplier → batch, medicine → batch, customer → sale, sale → sale items |
| Keys and constraints | Primary keys, foreign keys, NOT NULL, UNIQUE, CHECK |
| SQL data definition (DDL) | CREATE DATABASE, CREATE TABLE, CREATE VIEW |
| SQL data manipulation (DML) | INSERT, SELECT, UPDATE and DELETE practice |
| Filtering and sorting | WHERE, LIKE, ORDER BY |
| Aggregate functions | COUNT, SUM, AVG, MIN, MAX |
| Grouping | GROUP BY and HAVING |
| Joins | INNER JOIN and LEFT JOIN |
| Subqueries | Compare a batch price with the average price |
| Set operators | UNION example |
| Normalization | 1NF, 2NF and 3NF notes |
| Views and indexes | Inventory/low-stock views and SQLite app indexes |
| Transactions | Sale + stock change commits or rolls back together in the web app |
| Basic PL/SQL concepts | Only add Oracle procedures, functions, cursors or triggers if the official lab syllabus requires them; MySQL SQL is not Oracle PL/SQL |
| Concurrency, recovery and security | Explain at theory/viva level if included in the current course syllabus |

## Running the MySQL lab script

1. Download `database/medcare_mysql.sql`.
2. Log in using MySQL Command Line Client.
3. Run `SOURCE C:/full/path/to/medcare_mysql.sql;` with the real file path.
4. Run each commented practice SELECT separately.
5. Confirm output with `USE medcare_pharmacy;`, `SHOW TABLES;`, and `SELECT * FROM medicines;`.

**Warning:** the lab script drops and recreates the named project tables in `medcare_pharmacy`. Do not run it in a database that contains data you need to preserve.

## Data and safety

All suppliers, customers, batches, invoices and medicine rows in the SQL script are fictional classroom examples. The live web app's SQLite database and deployment configuration are not replaced by the MySQL lab script. The Render URL remains the existing service URL.
