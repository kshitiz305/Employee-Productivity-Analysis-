#####For Input and Flask API######################
import os, os.path
import win32com.client
import pythoncom
import csv
from os import scandir, listdir
import datetime
from datetime import datetime as dt
from flask import Flask, render_template, redirect, request, flash
import easygui
import shutil
from Main_Program_Wrapper import main_function
import pathlib
from Compare_response import compare_var_resp
import webbrowser
from openpyxl import Workbook
import re
import plotly as py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def get_prac_num_snd_eml():
    variance_file_path = 'Op_Variance_Data.csv'

    A = pd.read_csv(variance_file_path, engine='python', encoding = "cp1252")
    Send_email = A['Send_Email'].tolist()

    emails_num = Send_email.count('Yes')
    print('Number of Practitioners to be emailed: ' + str(emails_num))
    return emails_num


def listtofile():
    with open("rstcodes.txt", "w") as outfile:
        outfile.write("\n".join(str(item) for item in listOfRestrictedCodes))


def filetolist():  # read from file to list
    global listOfRestrictedCodes
    with open('rstcodes.txt', 'r') as f:
        x = f.readlines()

    list1 = list(x)
    listOfRestrictedCodes = [x.replace('\n', '') for x in list1]

    print(listOfRestrictedCodes)


def launch():
    webbrowser.open("http://localhost:5000/home")


def run_macro(mcname):
    try:
        print("Macro started: " + mcname)
        if os.path.exists("macro.xlsm"):
            pythoncom.CoInitialize()
            xl = win32com.client.Dispatch("Excel.Application")
            wb = xl.Workbooks.Open(os.path.abspath("macro.xlsm"), ReadOnly=1)
            xl.Application.Run("macro.xlsm!Module1." + mcname)
            wb.Close(False)
            # xl.Application.Quit()  # Comment this out if your excel script closes
            print("Macro completed: " + mcname)
        else:
            print("Macro failed: " + mcname)
    except:
        print("Macro Completed with Warnings : " + mcname + " : Ignored")
        return "A previous file is opened. Please Save your work and close it."


def copyxl():
    try:
        run_macro('MainWrap')
    except IOError:
        print("A previous report is open. Please save and close it then try again.")


def prev_reps():  # print last 5 reports####
    def convert_date(timestamp):
        d = dt.utcfromtimestamp(timestamp)
        formated_date = d.strftime('%d %b %Y')
        return formated_date

    def get_files():
        file_name = []
        Modified_date = []
        dir_entries = scandir('./Previous_Reports')  # Path for results folder

        for entry in dir_entries:
            if entry.is_file():
                info = entry.stat()
                file_name.append(entry.name)
                Modified_date.append(convert_date(info.st_mtime))

        r_name = sorted(file_name, reverse=True)
        r_date = sorted(Modified_date, reverse=False)
        global matrixArr
        matrixArr = [r_name, r_date]

        # global sortedArr
        # ascArr = numpy.sort(matrixArr)  # sorting based on date
        # sortedArr = matrixArr[:, matrixArr[-1].argsort()]

    get_files()

    global Report_1, Report_2, Report_3, Report_4, Report_5, time_1, time_2, time_3, time_4, time_5
    try:
        print(matrixArr)
        Report_1 = matrixArr[0][0]
        time_1 = matrixArr[1][0]
        try:
            Report_2 = matrixArr[0][1]
            time_2 = matrixArr[1][1]
            try:
                Report_3 = matrixArr[0][2]
                time_3 = matrixArr[1][2]
                try:
                    Report_4 = matrixArr[0][3]
                    time_4 = matrixArr[1][3]
                    try:
                        Report_5 = matrixArr[0][4]
                        time_5 = matrixArr[1][4]
                    except:
                        Report_5 = ""
                        time_5 = ""
                except:
                    Report_4 = ""
                    time_4 = ""
                    Report_5 = ""
                    time_5 = ""
            except:
                Report_3 = ""
                time_3 = ""
                Report_4 = ""
                time_4 = ""
                Report_5 = ""
                time_5 = ""
        except:
            Report_2 = ""
            time_2 = ""
            Report_3 = ""
            time_3 = ""
            Report_4 = ""
            time_4 = ""
            Report_5 = ""
            time_5 = ""
    except:
        Report_1 = "No Previous Reports found"
        time_1 = ""
        Report_2 = ""
        time_2 = ""
        Report_3 = ""
        time_3 = ""
        Report_4 = ""
        time_4 = ""
        Report_5 = ""
        time_5 = ""


# Get stats after db operation #######

# def backup_start():
#     try:
#         # Before db operations Copy latest report into previous_reports folder
#         shutil.copyfile('Latest_Report\\A&C_Variance_Report.xlsx', 'Previous_Reports\Report_' + datetime.datetime.now().strftime(
#             "%Y%m%d-%H%M%S") + "_" + week + ".xlsx")
#         print("Last Report moved to Previous_Reports")
#
#     except IOError:
#         return render_template("report.html")


def backup_end():
    # After dboperations Copy DTE Input file into historical_raw_files
    shutil.copyfile('current_files\dte_input.xlsx',
                    'historical_raw_files\DTE_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".xlsx")
    # After dboperations Copy STAFFIT Input file into historical_raw_files
    shutil.copyfile('current_files\stf_input.xlsx',
                    'historical_raw_files\STF_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".xlsx")
    # After dboperations Copy Op_Variance_Data Report file into Latest Report folder
    # run macros
    copyxl()
    # Copy the latest file in to the Previous Report folder
    shutil.copyfile('Latest_Report\\A&C_Variance_Report.xlsx',
                    'Previous_Reports\Report_' + datetime.datetime.now().strftime(
                        "%Y%m%d-%H%M%S") + "_" + week + ".xlsx")
    print("Report copied to Previous_Reports")


def get_stats():
    global zero_var, pos_var, neg_var, NoVar_Count, Var_Count, NA_Count
    with open('Statistics_Data_Extract.csv', 'r') as f:

        reader = csv.reader(f)
        for i, l in enumerate(reader):
            if i == 1:
                zero_var = l[0] + "%"
                neg_var = l[1] + "%"
                pos_var = l[2] + "%"
                NoVar_Count = l[3]
                Var_Count = l[4]
                NA_Count = l[5]


app = Flask(__name__)
app.config['SECRET_KEY'] = 'stiler'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/home/', methods=['POST', 'GET'])
def home():
    return render_template("temp.html")


@app.route('/support', methods=['POST', 'GET'])
def support():
    return render_template("support.html")


@app.route('/userguide', methods=['POST', 'GET'])
def userguide():
    os.startfile(".\\Help&Support\\STILER_Tool_User_Guide_v1.docx")
    return redirect("/home/")


@app.route('/settings', methods=['POST', 'GET'])
def settings():
    return render_template("settings.html")


# @app.route('/get_tags', methods=['POST', 'GET'])
# def get_tags():
#   global hidden,listOfRestrictedCodes
#  hidden = request.form.get("hidden-tags")

# return render_template("settings.html")

@app.route('/trend', methods=['POST', 'GET'])
def trend():
    return render_template("trend.html")


@app.route('/UpResponseVariance', methods=['POST', 'GET'])
def UpResponseVariance():
    try:
        global variance_data_file_path_by_project
        variance_data_file_path_by_project = easygui.fileopenbox(
            title="Please browse the Response Variance Data file generated by Survey")
        print(variance_data_file_path_by_project)
        oldext = os.path.splitext(variance_data_file_path_by_project)[1]
        shutil.copyfile(variance_data_file_path_by_project,
                        'ResponseAnalysis\Response' + oldext)
        return redirect("/trend")
    except:
        return redirect("/trend")


@app.route('/UpGraph', methods=['POST', 'GET'])
def UpGraph():
    # code to browse the excel file
    response_data_file_path_by_wk = './ResponseAnalysis/Response.xlsx'

    variance_file_path = './Latest_Report/A&C_Variance_Report.xlsx'

    variance_indicator_proj = pd.read_excel(response_data_file_path_by_wk)
    report_data = pd.read_excel(variance_file_path, sheet_name='Op_Variance_Data')
    report_data['Email_Id'] = report_data['Email_Id'].str.upper()
    variance_indicator_proj['2. Email ID:'] = variance_indicator_proj['2. Email ID:'].str.upper()
    jnData = variance_indicator_proj
    lst_col = list(jnData)
    pattern = '[(|)|.|:|0-9]'
    cleaned_list_cols_1 = [re.sub(pattern, '', i) for i in lst_col]
    cleaned_list_cols_2 = [x.strip(' ') for x in cleaned_list_cols_1]
    cleaned_list_cols_3 = [x.replace(' ', '_') for x in cleaned_list_cols_2]
    jnData.columns = cleaned_list_cols_3

    dfFinal = jnData.join(report_data.set_index('Email_Id')[['Request_Name']], on='Email_ID')
    dfFinal['Request_Name'] = dfFinal['Request_Name'].str.replace(r"\(.*\)", "")
    countProjectWise = dfFinal.groupby(by='Request_Name', as_index=False).agg({'Personnel_Number': 'count'})
    sortedcountProjectWise = countProjectWise.sort_values('Personnel_Number', ascending=False)
    chartProject = sortedcountProjectWise.head(20)

    countWeekWise = variance_indicator_proj.groupby(by='Week_number', as_index=False).agg(
        {'Personnel_Number': pd.Series.nunique})
    countResponseWise = variance_indicator_proj.groupby(by='Please_select_Response_Type_below', as_index=False).agg(
        {'Personnel_Number': pd.Series.nunique})
    countWeekWise.columns = ['Week', 'Varinace_Count']
    countResponseWise.columns = ['Response', 'Varinace_Count']
    chartProject.columns = ['Project', 'Varinace_Count']
    chartProject['Indexes'] = chartProject['Project'].str.find('_')
    chartProject1 = chartProject.apply(lambda x: x['Project'][0:x['Indexes']], axis=1)
    chartProject['Project'] = chartProject1
    countResponseWise.loc[countResponseWise.Response == "PTO - If you were on PTO, please specify", "Response"] = "PTO"
    countResponseWise.loc[
        countResponseWise.Response == "Roll Off – Mention the project name and roll-off date", "Response"] = "Roll Off From Project"
    countResponseWise.loc[
        countResponseWise.Response == "FPX Project – Mention FPX and the project name", "Response"] = "FPX Project"
    countResponseWise.loc[
        countResponseWise.Response == "Project Shutdown - Mention the project name with shutdown details", "Response"] = "Project Shutdown"
    countResponseWise.loc[countResponseWise.Response == "Other - Please specify below", "Response"] = "Other Reason"
    countResponseWise.loc[countResponseWise.Response == "On Bench – Not staffed", "Response"] = "On Bench"
    countResponseWise.loc[
        countResponseWise.Response == "No WBS – If you have not received the WBS, please mention this", "Response"] = "No WBS"
    countResponseWise.loc[countResponseWise.Response == "Travelling Week", "Response"] = "Travelling Week"
    x_column_wk = 'Week'
    y_column_wk = 'Varinace_Count'
    random_x_wk = countWeekWise[x_column_wk]
    random_y_wk = countWeekWise[y_column_wk]

    x_column_proj = 'Response'
    y_column_proj = 'Varinace_Count'
    random_x_proj = countResponseWise[x_column_proj]
    random_y_proj = countResponseWise[y_column_proj]

    x_column_new = 'Project'
    y_column_new = 'Varinace_Count'
    random_x_new = chartProject[x_column_new]
    random_y_new = chartProject[y_column_new]

    fig = make_subplots(rows=2, cols=2, column_widths=[0.6, 0.4],
                        specs=[[{"type": "xy"}, {"type": "domain"}], [{"colspan": 2}, None]], subplot_titles=(
        '<b>'"Projects With Most Variance(6 Weeks)"'</b>', '<b>'"Response Wise Trend(6 Weeks)"'</b>',
        '<b>'"Week Wise Trend(6 Weeks)"'</b>'), print_grid=True)
    blue_colors = ['rgb(139,0,0)', 'rgb(178,34,34)', 'rgb(220,20,60)', 'rgb(205,92,92)', 'rgb(240,128,128)',
                   'rgb(233,150,122)', 'rgb(250,128,114)', 'rgb(255,160,122)']
    fig.add_trace(go.Bar(x=random_x_new, y=random_y_new, marker_color='olivedrab', name='Trend By Project'), row=1,
                  col=1)
    fig.add_trace(
        go.Pie(labels=random_x_proj, values=random_y_proj, name='Trend By Response', marker_colors=blue_colors,
               textposition='inside', textinfo='percent+label'), row=1, col=2)
    fig.add_trace(go.Scatter(x=random_x_wk, y=random_y_wk, line=dict(color='steelblue', width=2), name="Trend By Week"),
                  row=2, col=1)
    # Update xaxis properties
    fig.update_xaxes(title_text="Project", mirror=True, linewidth=1, linecolor='black', showline=False, showgrid=False,
                     row=1, col=1)
    fig.update_xaxes(title_text="Response", mirror=True, linewidth=1, linecolor='black', showline=False, showgrid=False,
                     row=1, col=2)
    fig.update_xaxes(title_text="Week", mirror=True, linewidth=1, linecolor='black', showline=False, showgrid=False,
                     row=2, col=1)
    # Update yaxis properties
    fig.update_yaxes(title_text="Number Of Variance", mirror=True, linewidth=1, linecolor='black', showline=False,
                     showgrid=False, row=1, col=1)
    fig.update_yaxes(title_text="Number Of Variance", mirror=True, linewidth=1, linecolor='black', showline=False,
                     showgrid=False, row=1, col=2)
    fig.update_yaxes(title_text="Number Of Variance", mirror=True, linewidth=1, linecolor='black', showline=False,
                     showgrid=False, row=2, col=1)
    fig.update_layout(title={
        'text': '<b></b><b>'"Trend Charts By Operational Metrics"'</b>',
        'y': 1.0,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'}, bargap=0.1, showlegend=False, margin=dict(t=60, b=0, l=0, r=0),
        plot_bgcolor='rgba(0,0,0,.20)',
        images=[dict(
            source="./static/images/stilerlogo_trans.png",
            xref="paper", yref="paper",
            x=0, y=1.03,
            sizex=0.1, sizey=0.1,
            xanchor="center", yanchor="bottom")]
    )
    py.offline.plot(fig, filename='./templates/plot-wk-project.html')

    return redirect("/trend")


@app.route('/save', methods=['POST', 'GET'])
def save():
    global hidden, listOfRestrictedCodes
    hidden = request.form.get("hidden-tags")
    tags = hidden.split(',')
    print(tags)
    print(len(tags))

    x = set(tags)
    y = set(['lpx', 'prd', 'gaa', 'ort', 'fpx'])

    z = x.difference(y)
    z1 = y.difference(x)
    z2 = x & y
    z3 = z.union(z1, z2)
    listOfRestrictedCodes = list(z3)
    print(z3)
    print(listOfRestrictedCodes)

    print("Difference of first and second String: " + str(z))
    print("Difference of first and second String: " + str(z1))
    print("common items of first and second String: " + str(z2))
    print("listOfRestrictedCodes: " + str(z3))

    quote = "\'"
    comma = ','
    prefilled = ""
    replace_string = ""
    # Copy list to rstcodes files to save the tags
    listtofile()

    for i in listOfRestrictedCodes:
        replace_string = quote + i + quote + comma + replace_string

        #   print(replace_string)

    replace_string = replace_string[:-1]  # to remove the last comma in the replace string
    code = replace_string
    # print(code)

    f = open(".\\static\\js\\tags.js", "r")
    js = f.read()
    # print(js)

    start = js.find("prefilled: [") + len("prefilled: [")
    # print(start)
    end = js.find("],")
    prefilled = js[start:end]
    prefilled = prefilled.strip()
    # print(prefilled)
    removed = js.replace(prefilled, '')
    # print(removed)

    res = removed[: start] + code + removed[start:]
    # print(res)

    f = open(".\\static\\js\\tags.js", "w+")
    f.write(res)
    f.close()
    print("Updated JS successfully")

    return redirect("/settings")


@app.route("/Staffit_template", methods=['GET', 'POST'])
def Staffit_template():
    os.startfile(".\\DTE&Staffit_templates\\Staffit_template.xlsx")
    return render_template("settings.html")


@app.route("/DTE_template", methods=['GET', 'POST'])
def DTE_template():
    os.startfile(".\\DTE&Staffit_templates\\DTE_template.xlsx")
    return render_template("settings.html")


@app.route("/Manager_details", methods=['GET', 'POST'])
def Manager_details():
    os.startfile(".\\DTE&Staffit_templates\\Manager&Counselor_details.xlsx")
    return render_template("settings.html")


@app.route('/reports', methods=['POST', 'GET'])
def reports():
    today = datetime.datetime.today()
    datem = datetime.datetime(today.year, today.month, today.day)
    datem = str(datem)
    datem = datem.split('-')  # Splits at '-'

    global year
    year = int(datem[0])
    month = int(datem[1])

    if month > 5:
        year = year
        print("current year is taken")

    else:
        year = year - 1
        print("Previous year is taken")
    print(year)
    # fyear = str((year+1)%100)

    fyear = ["FY-" + str(year) for year in (year - 1, year, year + 1)]
    return render_template("report.html", year=fyear)


@app.route("/UpDTE", methods=['POST'])
def UpDTE():
    # open file dialog to select a file
    try:
        dte_file_path = easygui.fileopenbox(title='Select the DTE Extract')
        print(dte_file_path)
        # Copy the file to root/DTE_Raw_History and rename it with current Time Stamp
        oldext = os.path.splitext(dte_file_path)[1]
        shutil.copyfile(dte_file_path,
                        'current_files\dte_input' + oldext)
        return redirect("/reports")
    except:
        return redirect("/reports")


@app.route("/UpSTF", methods=['POST'])
def UpSTF():
    # open file dialog to select a file
    try:
        stf_file_path = easygui.fileopenbox(title='Select the Staffit Extract')
        print(stf_file_path)
        # Copy the file to root/DTE_Raw_History and rename it with current Time Stamp
        oldext = os.path.splitext(stf_file_path)[1]
        shutil.copyfile(stf_file_path,
                        'current_files\stf_input' + oldext)
        return redirect("/reports")

    except:
        return redirect("/reports")


@app.route("/UpReport", methods=['GET', 'POST'])
def UpReport():
    # try:
    global week
    global th
    filetolist()
    week = "W" + request.form.get("week")
    th = request.form.get("thresh")
    print("Week Captured: " + week)
    print("Threshold for Mails: " + th)
    year_r = request.form.get("dropdown")
    year_f = int(year_r.split('-')[1]) - 1
    # backup_start()
    main_func_stat = main_function(listOfRestrictedCodes, week, year_f, th)
    if main_func_stat:
        print("main_function completed successfully")
        get_stats()
        prev_reps()
        get_stats()
        backup_end()
        return render_template("dashboard.html", positive_variance=pos_var,
                               negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                               Var_Count=Var_Count, NA_Count=NA_Count,
                               Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                               Report_5=Report_5,
                               time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)

    else:
        flash("An error occurred while processing the data")
        return redirect("/reports")


@app.route("/View_Excel_Report", methods=['GET', 'POST'])
def View_Excel_Report():
    try:
        os.startfile(".\\Latest_Report\\A&C_Variance_Report.xlsx")
        return render_template("dashboard.html", positive_variance=pos_var,
                               negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                               Var_Count=Var_Count, NA_Count=NA_Count,
                               Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                               Report_5=Report_5,
                               time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)
    except IOError:
        flash(msg)
        return render_template("dashboard.html", positive_variance=pos_var,
                               negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                               Var_Count=Var_Count, NA_Count=NA_Count,
                               Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                               Report_5=Report_5,
                               time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)


@app.route("/Latest_Report", methods=['GET', 'POST'])
def Latest_Report():
    try:
        os.startfile(".\\Latest_Report\\A&C_Variance_Report.xlsx")
        return render_template("report.html")
    except IOError:
        flash(msg)
        return render_template("report.html")


@app.route('/Send_Emails', methods=['POST', 'GET'])
def Send_Emails():
    try:
        run_macro("MailusingOutlook")
        return render_template("dashboard.html", positive_variance=pos_var,
                               negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                               Var_Count=Var_Count, NA_Count=NA_Count,
                               Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                               Report_5=Report_5,
                               time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)

    except:
        flash("Function is currently blocked for demo")
        return render_template("dashboard.html", positive_variance=pos_var,
                               negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                               Var_Count=Var_Count, NA_Count=NA_Count,
                               Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                               Report_5=Report_5,
                               time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)


@app.route('/Get_Prac_num', methods=['POST', 'GET'])
def Get_Prac_num():
    try:
        emails_num = get_prac_num_snd_eml()
        num_emp = str(emails_num)
        flash("You are going to send Variance Emails to " + num_emp + " Practitioners.")
        return render_template("dashboard.html", positive_variance=pos_var,
                               negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                               Var_Count=Var_Count, NA_Count=NA_Count,
                               Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                               Report_5=Report_5,
                               time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)
    except:
        print("Error in Method: Get_Prac_num")
        return render_template("dashboard.html", positive_variance=pos_var,
                               negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                               Var_Count=Var_Count, NA_Count=NA_Count,
                               Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                               Report_5=Report_5,
                               time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)


@app.route('/Get_Resp_file', methods=['POST', 'GET'])
def Get_Resp_file():
    try:
        emails_num = compare_var_resp()
        num_emp = str(emails_num)
        flash("You are going to send Reminder Emails to " + num_emp + " Practitioners.")
        return redirect("/reports")
    except:
        return redirect("/reports")


@app.route('/Send_Reminder', methods=['POST', 'GET'])
def Send_Reminder():
    try:
        run_macro("RemindusingOutlook")
        print("Reminder Mail Sent.")
        return redirect("/reports")
    except:
        return redirect("/reports")


@app.route("/Op_Variance", methods=['GET', 'POST'])
def Op_Variance():
    try:
        os.startfile(".\\Op_Variance_Data.csv")
        return render_template("dashboard.html", positive_variance=pos_var,
                               negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                               Var_Count=Var_Count, NA_Count=NA_Count,
                               Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                               Report_5=Report_5,
                               time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)
    except IOError:
        flash(msg)
        return render_template("dashboard.html", positive_variance=pos_var,
                               negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                               Var_Count=Var_Count, NA_Count=NA_Count,
                               Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                               Report_5=Report_5,
                               time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)


@app.route("/Op_Variance_Report", methods=['GET', 'POST'])
def Op_Variance_Report():
    try:
        os.startfile(".\\Op_Variance_Data.csv")
        return redirect("/reports")
    except IOError:
        flash(msg)
        return redirect("/reports")


@app.route("/Directory_file1", methods=['GET', 'POST'])
def View_Report_1():
    d = pathlib.Path().absolute()
    report_1_path = str(d) + "/Previous_Reports/" + Report_1
    os.startfile(report_1_path)
    return render_template("dashboard.html", positive_variance=pos_var,
                           negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                           Var_Count=Var_Count, NA_Count=NA_Count,
                           Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                           Report_5=Report_5,
                           time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)


@app.route("/Directory_file2", methods=['GET', 'POST'])
def View_Report_2():
    d = pathlib.Path().absolute()
    report_path = str(d) + "/Previous_Reports/" + Report_2
    os.startfile(report_path)
    return render_template("dashboard.html", positive_variance=pos_var,
                           negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                           Var_Count=Var_Count, NA_Count=NA_Count,
                           Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                           Report_5=Report_5,
                           time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)


@app.route("/Directory_file3", methods=['GET', 'POST'])
def View_Report_3():
    d = pathlib.Path().absolute()
    report_path = str(d) + "/Previous_Reports/" + Report_3
    os.startfile(report_path)
    return render_template("dashboard.html", positive_variance=pos_var,
                           negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                           Var_Count=Var_Count, NA_Count=NA_Count,
                           Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                           Report_5=Report_5,
                           time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)


@app.route("/Directory_file4", methods=['GET', 'POST'])
def View_Report_4():
    d = pathlib.Path().absolute()
    report_path = str(d) + "/Previous_Reports/" + Report_4
    os.startfile(report_path)
    return render_template("dashboard.html", positive_variance=pos_var,
                           negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                           Var_Count=Var_Count, NA_Count=NA_Count,
                           Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                           Report_5=Report_5,
                           time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)


@app.route("/Directory_file5", methods=['GET', 'POST'])
def View_Report_5():
    d = pathlib.Path().absolute()
    report_path = str(d) + "/Previous_Reports/" + Report_5
    os.startfile(report_path)
    return render_template("dashboard.html", positive_variance=pos_var,
                           negative_variance=neg_var, zero_variance=zero_var, NoVar_Count=NoVar_Count,
                           Var_Count=Var_Count, NA_Count=NA_Count,
                           Report_1=Report_1, Report_2=Report_2, Report_3=Report_3, Report_4=Report_4,
                           Report_5=Report_5,
                           time_1=time_1, time_2=time_2, time_3=time_3, time_4=time_4, time_5=time_5)


webbrowser.open("http://localhost:5000/home")

if __name__ == '__main__':
    app.secret_key = "stiler"
    app.run(debug=False)
