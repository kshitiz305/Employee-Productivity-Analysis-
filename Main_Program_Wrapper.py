import forDB as Fdb
import Dataset_Manipulation as DM
import datetime
import pandas as pd
import os
import re
def main_function(listOfRestrictedCodes,week,year,th):

    # database path
    db_path = r'SampleData.db'
    if os.path.isfile(db_path):
        os.remove(db_path)
        print("Deleted previous database files ...")


    # Process DTE input file
    xlsDTE = pd.ExcelFile("current_files\dte_input.xlsx")
    dfsDTE = pd.read_excel(xlsDTE, 'DTE Report')
    lst_col = list(dfsDTE)
    pattern = '[(|)|.]'
    cleaned_list_cols_1 = [re.sub(pattern, '', i) for i in lst_col]
    cleaned_list_cols_2 = [x.strip(' ') for x in cleaned_list_cols_1]
    cleaned_list_cols_3 = [x.replace(' ', '_') for x in cleaned_list_cols_2]
    cleaned_list_cols_4 = [x.replace('/', '_') for x in cleaned_list_cols_3]
    dfsDTE.columns = cleaned_list_cols_4

    # Process STAFFIT input file
    xls = pd.ExcelFile("current_files\stf_input.xlsx")
    dfs = pd.read_excel(xls, 'Availability Base')
    lst_col = list(dfs)
    pattern = '[(|)|.]'
    cleaned_list_cols_1 = [re.sub(pattern, '', i) for i in lst_col]
    cleaned_list_cols_2 = [x.strip(' ') for x in cleaned_list_cols_1]
    cleaned_list_cols_3 = [x.replace(' ', '_') for x in cleaned_list_cols_2]
    cleaned_list_cols_4 = [x.replace('/', '_') for x in cleaned_list_cols_3]
    dfs.columns = cleaned_list_cols_4
    lstSelectedCols = ['Email_Id', 'Name','Location']
    chkPattern = '[_]'
    for indx in cleaned_list_cols_4:
        if str(re.sub(chkPattern, '', indx)).isdigit():
            lstSelectedCols.append(indx)
    lstSelectedColsEnd = ['Request_Name','Updated_Billing_Status']
    for trailIndx in lstSelectedColsEnd:
        lstSelectedCols.append(trailIndx)
    dataStaffit = dfs[dfs.columns.intersection(lstSelectedCols)]
    lstModCols = dataStaffit.columns
    lstAppendCols = ['Email_Id', 'Name']
    for indx_1 in lstModCols:
        if str(re.sub(chkPattern, '', indx_1)).isdigit():
            if len(indx_1[0:indx_1.find('_')]) == 1:
                lstAppendCols.append('0' + indx_1)
            else:
                lstAppendCols.append(indx_1)
    for trailIndx in lstSelectedColsEnd:
        lstAppendCols.append(trailIndx)
    dataStaffit.columns = lstAppendCols

    # Create Weekly Calender to map the week start date to Staffit date
    print('Creating Calender for the given fiscal year')
    start_year = year
    start_month = 5
    start_date = 30
    periodSuffix = 0
    startFlag = True
    allRows = []

    def next_weekday(d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return d + datetime.timedelta(days_ahead)

    d = datetime.date(start_year, start_month, start_date)
    next_sunday = next_weekday(d, 6)

    def genWeeklyCalender(date_str, indx, periodSuffix):
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        start_of_week = date_obj
        end_of_week = start_of_week + datetime.timedelta(days=6)
        getFY = 'FY' + str(start_year + 1)[2:]
        getWeekInPeriod = (indx - 1) % 4 + 1
        getPeriod = 'P' + str(periodSuffix)
        getYearlyWk = 'W' + str(indx)
        getListOfPeriods = getFY + '-' + getPeriod
        listRows = [start_of_week.strftime("%m_%d_%Y"), end_of_week.strftime("%m_%d_%Y"), getFY, getPeriod,
                    getWeekInPeriod, getYearlyWk, getListOfPeriods]
        return listRows

    for indx in range(52):
        if ((indx + 1) % 4 == 1 and startFlag):
            periodSuffix = periodSuffix + 1
            startFlag = False
        elif ((indx + 1) % 4 == 1 and not startFlag):
            periodSuffix = periodSuffix + 1
        else:
            periodSuffix = periodSuffix
        calc = genWeeklyCalender(next_sunday.strftime("%Y-%m-%d"), indx + 1, periodSuffix)
        allRows.append(calc)
        next_sunday = datetime.datetime.strptime(calc[1], '%m_%d_%Y') + datetime.timedelta(days=1)
    dfCalender = pd.DataFrame(allRows,
                              columns=['Week_starting_Sunday', 'Week_ending_Saturday', 'FY', 'Period', 'Week_in_Period',
                                       'Yearly_Week', 'List_of_Periods'])
    print(dfCalender)
    # Insert Records into database tables
    dte_tbl_nm = Fdb.insert_record(dfsDTE, "DTE_DATA")
    print('DTE Records Inserted into table')
    staffit_tbl_nm = Fdb.insert_record(dataStaffit, "STAFFIT_DATA")
    print('STAFFIT Records Inserted into table')
    calender_tbl_nm = Fdb.insert_record(dfCalender, "CALENDER_DATA")
    print('Calender Records Inserted into table')

    # calling Main Function for dataset manipulation
    mainProgStat = DM.main(dte_tbl_nm, staffit_tbl_nm, calender_tbl_nm, dataStaffit, listOfRestrictedCodes,week,th)
    return mainProgStat


