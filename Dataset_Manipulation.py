import sqlite3
from sqlite3 import Error
import tkinter
from tkinter import messagebox
import re
import csv
import os

# Test the connection to SQLLITE database
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def check_invaild_codes(conn,dte_table_name,listOfRestrictedCodes):
    cur = conn.cursor()
    db_codes=cur.execute('Select distinct att_absence_type from ' + dte_table_name)
    lstDbCodes=[]
    for indx1 in db_codes:
        lstDbCodes.append(indx1[0])
    lstUserIp=[]
    for indx2 in listOfRestrictedCodes:
        lstUserIp.append(indx2.replace('"','').upper())
    check=all(item in lstDbCodes for item in lstUserIp)
    return check

#Generate the query required to create new tables Staffit
def prepare_query_for_staffit_data(dfs,staffit_tbl_nm,calender_tbl_nm,staffit_tbl_name_mod):
    lstCols=list(dfs.columns)
    lstColsSelected=[]
    chkPattern = '[_]'
    for indxNo in lstCols:
        if str(re.sub(chkPattern, '', indxNo)).isdigit():
            lstColsSelected.append(indxNo)
    staffitSqlQry=''
    for indx in lstColsSelected:
        if lstColsSelected[0] == indx:
            staffitSqlQry = staffitSqlQry + 'CREATE TABLE ' + staffit_tbl_name_mod + ' AS SELECT EMAIL_ID,NAME,Request_Name, Updated_Billing_Status,HOURS,Yearly_Week FROM ( SELECT EMAIL_ID,NAME,Request_Name,Updated_Billing_Status,case when UPPER("' + indx + '") LIKE \'%CS%\' then SUBSTR("' + indx + '",INSTR("' + indx + '",\'(\')+1,INSTR("' + indx + '",\'CS\')-INSTR("' + indx + '",\'(\')-1) else \'0\' end AS Hours,\'' + indx + '\' AS WEEK_START_DATE FROM ' + staffit_tbl_nm + ' UNION '
        if lstColsSelected[-1] == indx:
            staffitSqlQry = staffitSqlQry + ' SELECT EMAIL_ID,NAME,Request_Name,Updated_Billing_Status,case when UPPER("' + indx + '") LIKE \'%CS%\' then SUBSTR("' + indx + '",INSTR("' + indx + '",\'(\')+1,INSTR("' + indx + '",\'CS\')-INSTR("' + indx + '",\'(\')-1) else \'0\' end AS Hours,\'' + indx + '\' AS WEEK_START_DATE FROM ' + staffit_tbl_nm + ' ) TAB1 INNER JOIN ' + calender_tbl_nm + ' on REPLACE(Week_starting_Sunday,\'_0\',\'_\')=WEEK_START_DATE ORDER BY EMAIL_ID,Yearly_Week'
        else:
            staffitSqlQry = staffitSqlQry + ' SELECT EMAIL_ID,NAME,Request_Name,Updated_Billing_Status,case when UPPER("' + indx + '") LIKE \'%CS%\' then SUBSTR("' + indx + '",INSTR("' + indx + '",\'(\')+1,INSTR("' + indx + '",\'CS\')-INSTR("' + indx + '",\'(\')-1)  else \'0\' end AS Hours,\'' + indx + '\' AS WEEK_START_DATE FROM ' + staffit_tbl_nm + ' UNION '
    return staffitSqlQry

# Create modified tables with new data format for Staffit and DTE
def create_table_staffit(conn,staffitSqlQry):
    cur = conn.cursor()
    cur.execute(staffitSqlQry)

def create_table_dte(conn,modified_dte_table,dte_table_name):
    cur = conn.cursor()
    sqlDTE = 'create table ' + modified_dte_table + ' as select Name_of_employee,Email_Address ,Week,'
    cur.execute('Select distinct att_absence_type from ' + dte_table_name)
    for indx in cur:
        sqlDTE = sqlDTE + 'max(case when trim(upper(Att_Absence_type))=\'' + indx[0].upper() + '\' then total_dte_hours end) as "' + indx[0] + '",'
    sqlDTE = sqlDTE.rstrip(",") + ' from  ( select Name_of_employee ,Email_Address ,Week,Att_Absence_type,sum(Number_unit) as total_dte_hours from ' + dte_table_name + ' group by Name_of_employee ,Email_Address ,Week,Att_Absence_type) tab1 group by Name_of_employee ,Email_Address ,Week'
    cur.execute(sqlDTE)

def create_join_dte_staffit_table(conn,modified_dte_table,staffit_tbl_name_mod,join_tab_name,dte_table_name):
    cur = conn.cursor()
    sqlJoin = 'create table ' + join_tab_name + ' as SELECT * FROM (SELECT coalesce(dte.name_of_employee,staffit.name,\'NA\') AS Emp_Name,upper(coalesce(dte.email_address,staffit.email_id,\'NA\')) AS Email_Id,staffit.request_name AS Request_Name,staffit.Updated_Billing_Status,coalesce(staffit.yearly_week,dte.week,\'NA\') AS Week,'
    cur.execute('Select distinct att_absence_type from ' + dte_table_name)
    for indx in cur:
        sqlJoin = sqlJoin + 'dte."' + indx[0] + '",'
    sqlJoin = sqlJoin + 'staffit.hours CS_STAFFIT FROM ' + modified_dte_table + ' dte LEFT OUTER JOIN ' + staffit_tbl_name_mod + ' staffit ON upper(trim(dte.email_address)) = upper(trim(staffit.email_id)) AND dte.week = staffit.yearly_week UNION SELECT coalesce(dte.name_of_employee,staffit.name,\'NA\') AS Emp_Name,upper(coalesce(dte.email_address,staffit.email_id,\'NA\')) AS Email_Id,staffit.request_name AS Request_Name,staffit.Updated_Billing_Status,coalesce(staffit.yearly_week,dte.week,\'NA\') AS Week,'
    cur.execute('Select distinct att_absence_type from ' + dte_table_name)
    for indx1 in cur:
        sqlJoin = sqlJoin + 'dte."' + indx1[0] + '",'
    sqlJoin = sqlJoin + 'staffit.hours cs_staffit FROM ' + staffit_tbl_name_mod + ' staffit LEFT OUTER JOIN ' + modified_dte_table + ' dte ON upper(trim(dte.email_address)) = upper(trim(staffit.email_id)) AND dte.week = staffit.yearly_week)'

    cur.execute(sqlJoin)

def create_variance_table(conn,variance_tab_name,join_tab_name,dte_table_name,lorc_billable,lorc_bench,lorc_int_billable,lorc_int,lorc_leave,lorc_JV,thresh):
    cur = conn.cursor()
    sqlVariance = 'create table ' + variance_tab_name + ' as SELECT tab1.*, CASE WHEN (upper(updated_billing_status) = \'FULL TIME BILLABLE\' AND ( '
    for resIndx in lorc_billable:
        sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal) > 0 or '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ')) OR  (upper(updated_billing_status) = \'BENCH\' AND ( '
    for resIndx in lorc_bench:
        sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal) > 0 or '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ')) OR (upper(updated_billing_status) = \'INTERNAL PROJ - BILLABLE\' AND ( '
    for resIndx in lorc_int_billable:
        sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal) > 0 or '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ')) OR (upper(updated_billing_status) = \'INTERNAL PROJ\' AND ( '
    for resIndx in lorc_int:
        sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal) > 0 or '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ')) OR (upper(updated_billing_status) = \'LONG LEAVE\' AND ( '
    for resIndx in lorc_leave:
        sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal) > 0 or '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ')) OR (upper(updated_billing_status) = \'JV\' AND ( '
    for resIndx in lorc_JV:
        sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal) > 0 or '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ')) THEN \'Yes\' ELSE \'No\' END AS Variance, CASE WHEN (upper(updated_billing_status) = \'FULL TIME BILLABLE\' AND (( '
# ====================================
    for resIndx in lorc_billable:
        sqlVariance = sqlVariance + 'IFNULL(cast( ' + resIndx + ' as DECIMAL), 0)  + '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ') >= ' + thresh + ')) OR  (upper(updated_billing_status) = \'BENCH\' AND (( '
    for resIndx in lorc_bench:
        sqlVariance = sqlVariance + 'IFNULL(cast( ' + resIndx + ' as DECIMAL), 0)  + '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ') >= ' + thresh + ')) OR  (upper(updated_billing_status) = \'INTERNAL PROJ - BILLABLE\' AND (( '
    for resIndx in lorc_int_billable:
        sqlVariance = sqlVariance + 'IFNULL(cast( ' + resIndx + ' as DECIMAL), 0)  + '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ') >= ' + thresh + ')) OR  (upper(updated_billing_status) = \'INTERNAL PROJ\' AND (( '
    for resIndx in lorc_int:
        sqlVariance = sqlVariance + 'IFNULL(cast( ' + resIndx + ' as DECIMAL), 0)  + '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ') >= ' + thresh + ')) OR  (upper(updated_billing_status) = \'LONG LEAVE\' AND (( '
    for resIndx in lorc_leave:
        sqlVariance = sqlVariance + 'IFNULL(cast( ' + resIndx + ' as DECIMAL), 0)  + '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ') >= ' + thresh + ')) OR  (upper(updated_billing_status) = \'JV\' AND (( '
    for resIndx in lorc_JV:
        sqlVariance = sqlVariance + 'IFNULL(cast( ' + resIndx + ' as DECIMAL), 0)  + '
    sqlVariance = sqlVariance.rsplit(' ', 2)[
                      0] + ') >= ' + thresh + ')) THEN \'Yes\' ELSE \'No\' END as Send_Email ,\'Compliant\'   AS Reason_For_Variance, CASE WHEN upper(Updated_Billing_Status) = \'Management\' THEN \'Management\' WHEN gaa IS NOT NULL AND "Holding Tank" IS NULL AND upper(Updated_Billing_Status) <> \'FPX\' THEN \'GAA\' WHEN "Holding Tank" IS NOT NULL AND gaa IS NULL AND upper(Updated_Billing_Status) <> \'FPX\' THEN \'Holding Tank\' WHEN upper(Updated_Billing_Status) = \'FPX\' AND "Holding Tank" IS NULL AND gaa IS NULL THEN \'FPX\' WHEN gaa IS NOT NULL AND "Holding Tank" IS NOT NULL AND upper(Updated_Billing_Status) <> \'FPX\' THEN \'GAA,Holding Tank\' WHEN gaa IS NOT NULL AND "Holding Tank" IS NULL AND upper(Updated_Billing_Status) = \'FPX\' THEN \'GAA,FPX\' WHEN gaa IS NULL AND "Holding Tank" IS NOT NULL AND upper(Updated_Billing_Status) = \'FPX\' THEN \'Holding Tank,FPX\' WHEN gaa IS NOT NULL AND "Holding Tank" IS NOT NULL AND upper(Updated_Billing_Status) = \'FPX\' THEN \'GAA,Holding Tank,FPX\' ELSE NULL END AS Category FROM ' + join_tab_name + ' tab1 ORDER BY email_id,week'

    print("sqlVariance: " + sqlVariance)
    cur.execute(sqlVariance)
    updQry = 'update ' + variance_tab_name + ' set reason_for_variance=\'Not Available(DTE)\' where upper(Updated_Billing_Status)=\'FULL TIME BILLABLE\' and '
    cur.execute('Select distinct att_absence_type from ' + dte_table_name)
    for indx in cur:
        updQry = updQry + '"' + indx[0] + '" is null and '
    updQry = updQry.rsplit(' ', 2)[0]
    print("updQry: " + updQry)
    cur.execute(updQry)
    # print("UPDATE2: ")
    # print('update ' + variance_tab_name + ' set Send_Email=\'No\',variance=\'No\' where upper(Updated_Billing_Status)=\'FULL TIME BILLABLE\' and reason_for_variance=\'Not Available(DTE)\'')
    cur.execute(
        'update ' + variance_tab_name + ' set Send_Email=\'No\',variance=\'No\' where upper(Updated_Billing_Status)=\'FULL TIME BILLABLE\' and reason_for_variance=\'Not Available(DTE)\'')

    conn.commit()

def export_variance_data_in_csv(conn,variance_tab_name,WKIP,dte_table_name):
    # ================
    cur = conn.cursor()
    exptabqry = "CREATE TABLE CSV_EXPORT AS SELECT Emp_Name,Email_Id,Request_Name,Updated_Billing_Status,Week,"
    cur.execute('Select distinct att_absence_type from ' + dte_table_name)
    for indx in cur:
        exptabqry = exptabqry + '"' + indx[0] + '",'
    addColumns = ''
    cur.execute('Select distinct att_absence_type from ' + dte_table_name)
    for indx1 in cur:
        addColumns = addColumns + 'IFNULL("' + indx1[0] + '",0)+'
    addColumns = addColumns[:-1]
    exptabqry = exptabqry + addColumns + " as Grand_Total,Cs_Staffit,Variance, Send_Email,Reason_For_Variance,Category FROM " + variance_tab_name + " WHERE Week=\'" + WKIP + "\'"
    # print("exptabqry===========================")
    # print(exptabqry)
    cur.execute(exptabqry)
    conn.commit()
    print("CSV_EXPORT Table Created...")
    # updCSVDATA0 = 'UPDATE CSV_EXPORT SET Send_Email = \'Yes\' WHERE Variance = \'Yes\' '
    # cur.execute(updCSVDATA0)
    # conn.commit()
    updCSVDATA1 = 'UPDATE CSV_EXPORT SET reason_for_variance = \'Not Available(DTE)\' WHERE upper(Updated_Billing_Status) = \'FULL TIME BILLABLE\' AND Grand_Total = 0'
    cur.execute(updCSVDATA1)
    conn.commit()
    updCSVDATA2 = 'UPDATE CSV_EXPORT SET reason_for_variance = Updated_Billing_Status WHERE Variance = \'Yes\' '
    # print('updCSVDATA2: ' + updCSVDATA2)
    cur.execute(updCSVDATA2)
    conn.commit()
    # ===========================
    csvdata= 'Select * from CSV_EXPORT'
    # ========================
    cur.execute(csvdata)
    print("Exporting Variance data....")
    with open("Op_Variance_Data.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",", lineterminator='\n')
        csv_writer.writerow([i[0] for i in cur.description])
        csv_writer.writerows(cur)

    dirpath = os.getcwd() + "\Op_Variance_Data.csv"
    print("Data exported Successfully into {}".format(dirpath))

def create_count_stat_from_variance(conn,stat_tab,variance_tab_name,WKIP):
    cur = conn.cursor()
    sqlstatraw = 'create table statistics_tab AS Select (select count(*) from  ' + variance_tab_name + '  where reason_for_variance =\'Compliant\' and Week=\'' + WKIP + '\' ) as count_novar,\
         (select count(*) from  ' + variance_tab_name + '  where reason_for_variance not in (\'Compliant\', \'Not Available(DTE)\') and Week=\'' + WKIP + '\') as count_var,\
         (select count(*) from  ' + variance_tab_name + '  where reason_for_variance = \'Not Available(DTE)\' and Week=\'' + WKIP + '\' ) as count_nadte,\
         (SELECT Count(*) FROM  ' + variance_tab_name + ' WHERE  week =\'' + WKIP + '\') AS count_tot'

    sqlSTAT = 'CREATE TABLE ' + stat_tab + ' AS\
     Select round(count_novar*100.0/count_tot,2) as No_Variance, round(count_var*100.0/count_tot,2) As Variance, round(count_nadte*100.0/count_tot,2) As Not_Available_DTE,\
     count_novar AS NoVar_Count, count_var AS Var_Count, count_nadte AS NA_Count\
     from statistics_tab'
    # print('sqlstatraw:  '+sqlstatraw)
    # print('sqlSTAT:  '+sqlSTAT)
    cur.execute(sqlstatraw)
    cur.execute(sqlSTAT)

def select_stat_data(conn,stat_tab):
    cur = conn.cursor()
    sqlSelectStat = 'select * from ' + stat_tab
    cur.execute(sqlSelectStat)
    print("Exporting Statistics data....")
    with open("Statistics_Data_Extract.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",", lineterminator='\n')
        csv_writer.writerow([i[0] for i in cur.description])
        csv_writer.writerows(cur)
    dirpath = os.getcwd() + "\Statistics_Data_Extract.csv"
    print("Data exported Successfully into {}".format(dirpath))

# Main Function
def main(dte_table_name,staffit_tbl_nm,calender_tbl_nm,dataStaffit,listOfRestrictedCodes,week,th):
    database = "SampleData.db"
    WKIP=week
    modified_staffit_table="STAFFIT_TAB_MODIFIED"
    modified_dte_table="DTE_TAB_MODIFIED"
    join_tab_name="Join_DTE_STAFFIT"
    variance_tab_name="DTE_STAFFIT_VARIANCE_TAB"
    stat_tab="Count_Statistics_Tab"
    print("Restricted Code Details (Please Verify)")
    lorc_billable = ['"PRD-PX"', 'PRD', 'LPX', 'FPX', 'ORT', 'GAA', 'INT']
    lorc_bench = ['"PRD-PX"', 'PRD', 'LPX', 'FPX', 'ORT', '"CS Hours"', 'INT']
    lorc_int_billable = ['"PRD-PX"', 'PRD', 'LPX', 'FPX', 'ORT', 'GAA', 'INT']
    lorc_int = ['"CS Hours"', 'GAA']
    lorc_leave = ['"PRD-PX"', 'PRD', 'LPX', 'FPX', 'ORT', '"CS Hours"', 'INT']
    lorc_JV = ['"PRD-PX"', 'PRD', 'LPX', 'FPX', 'ORT', '"CS Hours"', 'INT', 'GAA']
    print("FULL TIME Billable: ")
    print(lorc_billable)
    print("Bench: ")
    print(lorc_bench)
    print("Internal Billable Projects: ")
    print(lorc_int_billable)
    print("Internal Projects: ")
    print(lorc_int)
    print("Long Leave: ")
    print(lorc_leave)
    print("Joint Venture: ")
    print(lorc_JV)
    thresh = str(th)
    newStaffitQry=prepare_query_for_staffit_data(dataStaffit,staffit_tbl_nm,calender_tbl_nm,modified_staffit_table)
    # create a database connection
    conn = create_connection(database)
    with conn:
        chkcode=check_invaild_codes(conn,dte_table_name,listOfRestrictedCodes)
        if chkcode:
            create_table_staffit(conn,newStaffitQry)
            print('Modified STAFFIT table created...')
            create_table_dte(conn, modified_dte_table, dte_table_name)
            print('Modified DTE Table created...')
            create_join_dte_staffit_table(conn, modified_dte_table, modified_staffit_table, join_tab_name,dte_table_name)
            create_variance_table(conn,variance_tab_name,join_tab_name,dte_table_name,lorc_billable,lorc_bench,lorc_int_billable,lorc_int,lorc_leave,lorc_JV,thresh)
            print('DTE and STAFFIT Variance Table created...')
            export_variance_data_in_csv(conn, variance_tab_name, WKIP,dte_table_name)
            create_count_stat_from_variance(conn, stat_tab, "CSV_EXPORT", WKIP)
            print("Statistics table created...")
            select_stat_data(conn, stat_tab)
            return True
        else:
            return False

if __name__ == '__main__':
    root = tkinter.Tk()
    root.withdraw()  # use to hide tkinter window
    messagebox.showerror("Error", "Not to be executed as standalone file....")