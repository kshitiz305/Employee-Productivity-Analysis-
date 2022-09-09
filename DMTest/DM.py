import sqlite3
from sqlite3 import Error
thresh = str(18)
variance_tab_name = "dte_staffit_variance_tab"
join_tab_name = "join_dte_staffit"
dte_table_name = "DTE_DATA"
lorc_billable = ['"PRD-PX"', 'PRD', 'LPX', 'FPX', 'ORT', 'GAA', 'INT']
lorc_bench = ['"PRD-PX"', 'PRD', 'LPX', 'FPX', 'ORT', '"CS Hours"', 'INT']
lorc_int_billable = ['"PRD-PX"', 'PRD', 'LPX', 'FPX', 'ORT', 'GAA', 'INT']
lorc_int = ['"CS Hours"', 'GAA']
lorc_leave = ['"PRD-PX"', 'PRD', 'LPX', 'FPX', 'ORT', '"CS Hours"', 'INT']
lorc_JV = ['"PRD-PX"', 'PRD', 'LPX', 'FPX', 'ORT', '"CS Hours"', 'INT', 'GAA']
db_path = r'SampleData.db'
conn = sqlite3.connect(db_path)


cur = conn.cursor()
sqlVariance = 'create table ' + variance_tab_name + ' as SELECT tab1.*,CASE WHEN (upper(updated_billing_status) = \'FULL TIME BILLABLE\' AND ( '
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
                  0] + ')) THEN \'Yes\' ELSE \'No\' END as Variance, CASE WHEN (upper(updated_billing_status) = \'FULL TIME BILLABLE\' AND (( '
# ====================================
for resIndx in lorc_billable:
    sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal)  + '
sqlVariance = sqlVariance.rsplit(' ', 2)[
                  0] + ') >= ' + thresh + ')) OR  (upper(updated_billing_status) = \'BENCH\' AND (( '
for resIndx in lorc_bench:
    sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal)  + '
sqlVariance = sqlVariance.rsplit(' ', 2)[
                  0] + ') >= ' + thresh + ')) OR  (upper(updated_billing_status) = \'INTERNAL PROJ - BILLABLE\' AND (( '
for resIndx in lorc_int_billable:
    sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal) + '
sqlVariance = sqlVariance.rsplit(' ', 2)[
                  0] + ') >= ' + thresh + ')) OR  (upper(updated_billing_status) = \'INTERNAL PROJ\' AND (( '
for resIndx in lorc_int:
    sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal) + '
sqlVariance = sqlVariance.rsplit(' ', 2)[
                  0] + ') >= ' + thresh + ')) OR  (upper(updated_billing_status) = \'LONG LEAVE\' AND (( '
for resIndx in lorc_leave:
    sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal) + '
sqlVariance = sqlVariance.rsplit(' ', 2)[
                  0] + ') >= ' + thresh + ')) OR  (upper(updated_billing_status) = \'JV\' AND (( '
for resIndx in lorc_JV:
    sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal) + '
sqlVariance = sqlVariance.rsplit(' ', 2)[
                  0] + ') >= ' + thresh + ')) THEN \'Yes\' ELSE \'No\' END as Send_Email,CASE WHEN upper(Updated_Billing_Status) = \'Management\'THEN \'Not Applicable\' WHEN upper(updated_billing_status) = \'BILLABLE\' AND ('
for resIndx in lorc_billable:
    sqlVariance = sqlVariance + 'cast (' + resIndx + ' as decimal) > 0 or '
sqlVariance = sqlVariance.rsplit(' ', 2)[0] + ') THEN \'Variance\' WHEN '
cur.execute('Select distinct att_absence_type from ' + dte_table_name)
for indx in cur:
    sqlVariance = sqlVariance + '"' + indx[0] + '" is null and '
sqlVariance = sqlVariance.rsplit(' ', 2)[
                  0] + ' AND cs_staffit IS NOT NULL AND cs_staffit <> \'0\' AND upper(Updated_Billing_Status) = \'JV\' THEN \'JV\' WHEN'
cur.execute('Select distinct att_absence_type from ' + dte_table_name)
for indx in cur:
    sqlVariance = sqlVariance + '"' + indx[0] + '" is null and '
sqlVariance = sqlVariance.rsplit(' ', 2)[
                  0] + ' AND cs_staffit IS NOT NULL AND cs_staffit <> \'0\' AND upper(Updated_Billing_Status) <> \'JV\' THEN \'Not Available(DTE)\' ELSE \'Not Applicable\' END  AS Reason_For_Variance, CASE WHEN upper(Updated_Billing_Status) = \'Management\' THEN \'Management\' WHEN gaa IS NOT NULL AND "Holding Tank" IS NULL AND upper(Updated_Billing_Status) <> \'FPX\' THEN \'GAA\' WHEN "Holding Tank" IS NOT NULL AND gaa IS NULL AND upper(Updated_Billing_Status) <> \'FPX\' THEN \'Holding Tank\' WHEN upper(Updated_Billing_Status) = \'FPX\' AND "Holding Tank" IS NULL AND gaa IS NULL THEN \'FPX\' WHEN gaa IS NOT NULL AND "Holding Tank" IS NOT NULL AND upper(Updated_Billing_Status) <> \'FPX\' THEN \'GAA,Holding Tank\' WHEN gaa IS NOT NULL AND "Holding Tank" IS NULL AND upper(Updated_Billing_Status) = \'FPX\' THEN \'GAA,FPX\' WHEN gaa IS NULL AND "Holding Tank" IS NOT NULL AND upper(Updated_Billing_Status) = \'FPX\' THEN \'Holding Tank,FPX\' WHEN gaa IS NOT NULL AND "Holding Tank" IS NOT NULL AND upper(Updated_Billing_Status) = \'FPX\' THEN \'GAA,Holding Tank,FPX\' ELSE NULL END AS Category FROM ' + join_tab_name + ' tab1 ORDER BY email_id,week'


print("sqlVariance: " + sqlVariance)
# cur.execute(sqlVariance)
cur.execute('update '+ variance_tab_name + ' set send_email=\'No\',variance=\'No\' where upper(Updated_Billing_Status)=\'BILLABLE\' and reason_for_variance=\'Not Available(DTE)\'')
updQry = 'update ' + variance_tab_name + ' set reason_for_variance=\'Not Available(DTE)\' where upper(Updated_Billing_Status)=\'BILLABLE\' and '
cur.execute('Select distinct att_absence_type from ' + dte_table_name)
for indx in cur:
    updQry = updQry + '"' + indx[0] + '" is null and '
updQry = updQry.rsplit(' ', 2)[0]
print("updQry: " + updQry)