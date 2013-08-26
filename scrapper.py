from BeautifulSoup import BeautifulSoup
from config import *
import mechanize
import getpass
import time
import smtplib  

def email(to, subj, msg):
    #http://www.pythonforbeginners.com/code-snippets-source-code/using-python-to-send-email/
    header  = 'From: %s\n' % gmail[0]
    header += 'To: %s\n' % ','.join(to)
    header += 'Cc: %s\n' % ','.join([])
    header += 'Subject: '+subj+'\n\n'
    message = header +  msg
  
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(gmail[0],gmail[1])
    problems = server.sendmail(gmail[0], email_to, message)
    server.quit()

def course_email(subj_code, subj_no, crn_no):
    subject = "Course Registration!!!"
    message = "REGISTER FAST!!! "+subj_code+" "+str(subj_no)+" "+str(crn_no)+" is available!"
    to = email_to
    email(to, subject, message)

def test_email():
    to = email_to
    subj = "Test Course Check"
    message = "This is just a test email. Script to check the following courses has started. It will run every "+str(time_interval/60)+" mins"
    for each in courses:
        message += "\n"+each[0]+str(each[1])+" crn:"+str(each[2])
    email(to, subj, message)

def login(br):
    #go past the login page
    br.set_handle_robots(False)
    url = "https://eas.admin.uillinois.edu/eas/servlet/EasLogin?redirect=https://webprod.admin.uillinois.edu/ssa/servlet/SelfServiceLogin?appName=edu.uillinois.aits.SelfServiceLogin&dad=BANPROD1"
    br.open(url)
    br.select_form(name="easForm")
    br["inputEnterpriseId"] = enterprise[0]
    br["password"] = enterprise[1]
    resp = br.submit()


def get_course_table(br, subj_code, subj_no):
    #go to the registration page
    url = "https://ui2web1.apps.uillinois.edu/BANPROD1/twbkwbis.P_GenMenu?name=bmenu.P_StuMainMnu"
    br.open(url)
    url = "https://ui2web1.apps.uillinois.edu/BANPROD1/twbkwbis.P_GenMenu?name=bmenu.P_RegMnu"
    br.open(url)
    url = "https://ui2web1.apps.uillinois.edu/BANPROD1/twbkwbis.P_GenMenu?name=bmenu.P_RegAgreementAdd"
    br.open(url)
    url = "https://ui2web1.apps.uillinois.edu/BANPROD1/bwskfreg.P_AltPin" #fall 2013 selection page
    br.open(url)
    br.select_form(nr=1)
    br.submit()

    #on the reg page
    br.select_form(nr=1)
    resp = br.submit(name='REG_BTN', label='Class Search')

    br.select_form(nr=1)
    resp = br.submit(name='SUB_BTN', label = 'Advanced Search')

    br.select_form(nr=1)
    br.find_control(name="sel_subj", nr=1).value = [subj_code]
    br["sel_crse"] = R_COURSE = str(subj_no)
    resp = br.submit().read()

    # f_name = str(subj_code)+"_"+str(subj_no)+".txt"
    # f2 = open("raw_"+f_name, "w")
    # f2.write(resp)
    # f2.close()

    return resp

def parse_page(resp, crn_no):
    soup = BeautifulSoup(resp)
    table = soup.findAll("table",{"class":"datadisplaytable"})
    if(len(table) == 0):
        append_to_log("Can't find the course table")
        return False
    table = table[0]

    crn_nav_txt = table.find(text=str(crn_no))
    if crn_nav_txt is None:
        append_to_log("Can't find the CRN "+str(crn_no))
        return False

    crn_td = crn_nav_txt.parent.parent
    avail_td = crn_td.findPreviousSibling("td")

    if(avail_td.find("input") is not None):
        return True
    return False

def check_course(br, subj_code, subj_no, crn_no):
    resp = get_course_table(br, subj_code, subj_no)
    if parse_page(resp, crn_no):
        text = subj_code+" "+str(subj_no)+" is available"
        append_to_log(text)
        course_email(subj_code, subj_no, crn_no) #email the user
    else:
        text = subj_code+" "+str(subj_no)+" is un-available"
        append_to_log(text)

def run_routine():
    br = mechanize.Browser()
    login(br)
    for each in courses:
        check_course(br, each[0], each[1], each[2])
    br.close()

def append_to_log(text):
    f = open(log_file, 'a')
    text = time.ctime()+":"+text+"\n"
    f.write(text)
    f.close()

def check_log_file():
    try:
       with open(log_file): pass
    except IOError:
       f = open(log_file, 'w')
       f.write("created on:"+time.ctime()+"\n")
       f.close()

check_log_file()
test_email()
while(1):
    append_to_log("running check")
    try:
        run_routine()
    except:
        append_to_log("ERROR")
    time.sleep(time_interval)
    