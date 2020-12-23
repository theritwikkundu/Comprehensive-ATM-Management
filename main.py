from tkinter import *
from tkinter import messagebox
from datetime import *
from tkinter import ttk


# sql-connector

import mysql.connector as sql
db = sql.connect(
    host="localhost",
    user="root",
    password="",
    database="ATM"
)
if db.is_connected():
    print("Successfully connected to", db.connection_id)


#global variables
minBalance=100
minAtmBalance=10000
atmNumber=0
cardNo=0
cardPin=0
acNumber=0
acBalance=0
custNumber=''
custPassword=''
adminNumber=''
adminPassword=''

def chkAcCred(cardNo, cardPin):
    cursor = db.cursor()
    selQuery = "select cd_no, pin, cd_exp from Card"
    cursor.execute(selQuery)
    flag = 0
    records = cursor.fetchall()
    dt = date.today()
    for row in records:
        if(str(row[0]) == cardNo and str(row[1]) == cardPin and row[2] > dt):
            flag = 1
            break
    cursor.close()
    return flag

def chkWithd(amount):
    flag=0
    if((acBalance-amount) > minBalance):
        flag=1
    return flag

def perfTransact(amount,ch,ch1,acNum):
    if (ch == 1):
        amount = amount * (-1)

    #update Account
    cursor = db.cursor()
    upQuery = "update Account set ac_bal = ac_bal + %s where ac_no = %s;"
    data = (amount, acNum, )
    cursor.execute(upQuery, data)
    db.commit()
    cursor.close()

    #update ATM
    cursor = db.cursor()
    upQuery = "update ATM set atm_bl = atm_bl + %s where atm_id = %s;"
    data = (amount, atmNumber,)
    cursor.execute(upQuery, data)
    db.commit()
    cursor.close()
    cursor=db.cursor()
    if(ch == 1 and ch1 == 1):
        upQuery = "update ATM set avg_w = avg_w + 1 where atm_id = %s;"
    elif(ch == 2 and ch1 == 2):
        upQuery = "update ATM set avg_d = avg_d + 1 where atm_id = %s;"
    elif(ch == 1 and ch1 == 3):
        upQuery = "update ATM set avg_t = avg_t + 1 where atm_id = %s;"
    elif (ch == 2 and ch1 == 3):
        upQuery = "update ATM set avg_t = avg_t where atm_id = %s;"
    data = (atmNumber,)
    cursor.execute(upQuery, data)
    db.commit()
    cursor.close()

    #add Transaction
    cursor = db.cursor()
    selQuery = "select tr_id from Withdraw order by tr_dt asc;"
    cursor.execute(selQuery)
    records = cursor.fetchall()
    for row in records:
        Tid = row[0]
    cursor.close()
    partid1 = int(Tid[5:])
    cursor=db.cursor()
    selQuery = "select tr_id from Deposit order by tr_dt asc;"
    cursor.execute(selQuery)
    records = cursor.fetchall()
    for row in records:
        Tid=row[0]
    cursor.close()
    partid2 = int(Tid[5:])

    partid=max(partid1,partid2)
    if(ch==1 and ch1 == 1):
        Tid='TWSNT'+str(partid+1)
    elif(ch==2 and ch1 == 2):
        Tid='TDSNT'+str(partid+1)
    elif(ch==1 and ch1 == 3):
        Tid='TTSNT'+str(partid+1)
    elif (ch == 2 and ch1 == 3):
        Tid='TTSNT'+str(partid)
    now = datetime.now()
    dt_str = now.strftime("%Y-%m-%d %H:%M:%S")
    cursor=db.cursor()
    if(ch==1):
        inQuery = "insert into Withdraw values(%s,%s,%s,%s,%s,%s);"
    elif(ch==2):
        inQuery = "insert into Deposit values(%s,%s,%s,%s,%s,%s);"
    data=(Tid,ch,dt_str,amount,atmNumber,acNum,)
    cursor.execute(inQuery, data)
    db.commit()
    cursor.close()

    return Tid

def chkCCred(custNum, custPass):
    cursor = db.cursor()
    selQuery = "select cust_id, cust_pw from Customer"
    cursor.execute(selQuery)
    flag = 0
    records = cursor.fetchall()
    for row in records:
        if (row[0] == custNum and row[1] == custPass):
            flag = 1
            break
    cursor.close()
    return flag

def chkAdCred(adminNum, adminPass):
    cursor = db.cursor()
    selQuery = "select ad_id, ad_pw from Admin"
    cursor.execute(selQuery)
    flag = 0
    records = cursor.fetchall()
    for row in records:
        if (row[0] == adminNum and row[1] == adminPass):
            flag = 1
            break
    cursor.close()
    return flag

def chkAtCred(atmNum):
    cursor = db.cursor()
    selQuery = "select atm_id from ATM"
    cursor.execute(selQuery)
    flag = 0
    records = cursor.fetchall()
    for row in records:
        if (row[0] == atmNum):
            flag = 1
            break
    cursor.close()
    return flag

def isRecycler(atmNum):
    cursor = db.cursor()
    selQuery = "select atm_tp from ATM where atm_id=%s"
    data=(atmNum,)
    cursor.execute(selQuery,data)
    flag = 0
    records = cursor.fetchone()
    if (records[0] == 'Recycler'):
        flag = 1
    cursor.close()
    return flag

def RflIsValid(atmNum, amt):
    cursor = db.cursor()
    selQuery = "select br_bal from ATM inner join Branch on Branch.ifsc=ATM.ifsc where atm_id=%s;"
    data = (atmNum,)
    cursor.execute(selQuery, data)
    flag = 0
    records = cursor.fetchone()
    if (records[0]-amt > minAtmBalance):
        flag = 1
    cursor.close()
    return flag

def perfRefill(atmNum, amt):
    #get ifsc
    cursor = db.cursor()
    selQuery = "select ifsc from ATM where atm_id=%s;"
    data = (atmNumber,)
    cursor.execute(selQuery,data)
    records=cursor.fetchone()
    ifsctemp=records[0]
    cursor.close()

    #update ATM
    cursor = db.cursor()
    upQuery = "update ATM set atm_bl = atm_bl + %s where atm_id = %s;"
    data = (amt, atmNum,)
    cursor.execute(upQuery, data)
    db.commit()
    cursor.close()

    #update Branch
    cursor = db.cursor()
    upQuery = "update Branch set br_bal = br_bal - %s where ifsc = %s;"
    data = (amt, ifsctemp,)
    cursor.execute(upQuery, data)
    db.commit()
    cursor.close()

    #add refill entry
    now=datetime.now()
    dt_str=now.strftime("%Y-%m-%d %H:%M:%S")
    cursor = db.cursor()
    inQuery = "insert into refill values(%s,%s,%s,%s);"
    data = (ifsctemp, atmNumber, dt_str, amt)
    cursor.execute(inQuery, data)
    db.commit()
    cursor.close()

def secIsValid(atmNum,dt):
    cursor = db.cursor()
    selQuery = "select atm_id,s_dt from Security"
    cursor.execute(selQuery)
    flag = 0
    records = cursor.fetchall()
    for row in records:
        # print(type(row[1]))
        if (row[0] == atmNum and str(row[1]) == dt):
            flag = 1
            break
    cursor.close()
    return flag

def perfSec(atmNum,resolution):
    cursor = db.cursor()
    upQuery = "update Security set res = %s where atm_id = %s;"
    data = (resolution, atmNum,)
    cursor.execute(upQuery, data)
    db.commit()
    cursor.close()

def compIsValid(compNum):
    cursor = db.cursor()
    selQuery = "select cl_id from Complaint"
    cursor.execute(selQuery)
    flag = 0
    records = cursor.fetchall()
    for row in records:
        if (row[0] == compNum):
            flag = 1
            break
    cursor.close()
    return flag

def perfComp(compNum,status):
    cursor = db.cursor()
    upQuery = "update Complaint set cl_stat = %s where cl_id = %s;"
    data = (status,compNum,)
    cursor.execute(upQuery, data)
    db.commit()
    cursor.close()

def vendIsValid(compName,compReview):
    flag=1
    if(compName=='' or compReview==''):
        flag=0
        return flag
    if(int(compReview)<1 or int(compReview)>10):
        flag=0
        return flag
    cursor = db.cursor()
    selQuery = "select comp from Vendor"
    cursor.execute(selQuery)
    records = cursor.fetchall()
    for row in records:
        if (row[0] == compName):
            flag = 0
            break
    cursor.close()
    return flag

def perfVend(compName,compReview):
    cursor = db.cursor()
    inQuery = "insert into Vendor values(%s,%s,0);"
    data = (compName, compReview,)
    cursor.execute(inQuery, data)
    db.commit()
    cursor.close()

    cursor = db.cursor()
    inQuery = "insert into sign values(%s,%s);"
    data = (adminNumber,compName,)
    cursor.execute(inQuery, data)
    db.commit()
    cursor.close()

def perfBlock(cardNo):
    cursor = db.cursor()
    upQuery = "update Card set cd_exp = '2000-01-01' where cd_no=%s;"
    data=(cardNo,)
    cursor.execute(upQuery,data)
    db.commit()
    cursor.close()

def perfCompC(atmNum,descrip):
    cursor = db.cursor()
    selQuery = "select cl_id from Complaint order by cl_id asc;"
    cursor.execute(selQuery)
    records = cursor.fetchall()
    for row in records:
        Clid = row[0]
    cursor.close()
    partid = int(Clid[5:])
    Clid = 'CLSNT' + str(partid + 1)

    cursor = db.cursor()
    inQuery = "insert into Complaint values(%s,%s,%s,%s,%s);"
    data = (Clid, descrip, '', custNumber, atmNum)
    cursor.execute(inQuery, data)
    db.commit()
    cursor.close()
    return Clid

def atmChkIsValid(ifscNumber, amount):
    cursor = db.cursor()
    selQuery = "select ifsc from Branch"
    cursor.execute(selQuery)
    flag = 0
    records = cursor.fetchall()
    for row in records:
        if (row[0] == ifscNumber and amount <=10000):
            flag = 1
            break
    cursor.close()
    return flag

def cntIsValid(atmNum,company):
    flag1 = flag2 = flag3 = 0
    cursor = db.cursor()
    selQuery = "select atm_id from ATM"
    cursor.execute(selQuery)
    records = cursor.fetchall()
    for row in records:
        if (row[0] == atmNum):
            flag1 = 1
            break
    cursor.close()

    cursor = db.cursor()
    selQuery = "select comp from Vendor"
    cursor.execute(selQuery)
    records = cursor.fetchall()
    for row in records:
        if (row[0] == company):
            flag2 = 1
            break
    cursor.close()

    if(flag1==1):
        cursor = db.cursor()
        selQuery = "select ct_yr, warr from Contract where atm_id=%s order by ct_yr desc;"
        data=(atmNum,)
        cursor.execute(selQuery, data)
        records = cursor.fetchone()
        yeartemp=records[0]
        warrtemp=records[1]
        yr= datetime.now().year
        if (int(yeartemp)+int(warrtemp) < int(yr)):
            flag3 = 1

    cursor.close()

    flag=flag1*flag2*flag3
    return flag

def perfCnt(atmNum, company, amctemp, warrtemp):
    #update Vendor table
    cursor = db.cursor()
    upQuery = "update Vendor set no_ct = no_ct + 1 where comp=%s;"
    data = (company,)
    cursor.execute(upQuery, data)
    db.commit()
    cursor.close()

    #add Contract table
    cursor = db.cursor()
    selQuery = "select ct_id from Contract order by ct_id asc;"
    cursor.execute(selQuery)
    records = cursor.fetchall()
    for row in records:
        Cntid = row[0]
    cursor.close()
    partid = int(Cntid[5:])
    Cntid = 'CTSNT' + str(partid + 1)

    yr = datetime.now().year
    cursor = db.cursor()
    inQuery = "insert into Contract values(%s,%s,%s,%s,%s,%s);"
    data = (Cntid, yr, amctemp, warrtemp, atmNum, company,)
    cursor.execute(inQuery, data)
    db.commit()
    cursor.close()

    return Cntid

# sql-connector


root = Tk()
root.title("Sanatan Bank")
root.wm_iconbitmap("SB_icon1.ico")
root.geometry("700x420")

def openATM():
    try:
        global atmNumber
        atmNumber = AtmNo.get()
        CredF = chkAtCred(atmNumber)
        if (CredF != 1):
            messagebox.showwarning("Error", "This ATM does not exist!")
            return
    except Exception:
        pass
    try:
        root.destroy()
    except Exception:
        pass
    AtmRt = Tk()
    AtmRt.title("Sanatan Bank / ATM")
    AtmRt.wm_iconbitmap("SB_icon1.ico")
    AtmRt.geometry("700x420")

    def openCAc():
        try:
            global cardNo, cardPin
            cardNo = CdNo.get()
            cardPin = pin.get()
            CredF = chkAcCred(cardNo,cardPin)
            if(CredF!=1):
                messagebox.showwarning("Error", "Card is invalid!")
                return
        except Exception:
            pass
        try:
            AtmRt.destroy()
        except Exception:
            pass
        CAcW = Tk()
        CAcW.title("Sanatan Bank / ATM / Account")
        CAcW.wm_iconbitmap("SB_icon1.ico")
        CAcW.geometry("700x420")

        cursor = db.cursor()            #sql
        selQuery = "select ac_bal,Account.ac_no from Account inner join Card on Card.ac_no=Account.ac_no where cd_no = %s"
        data = (cardNo,)
        cursor.execute(selQuery, data)
        record = cursor.fetchone()
        global acBalance, acNumber
        acBalance = record[0]
        acNumber = record[1]
        cursor.close()

        def openWithdW():
            try:
                CAcW.destroy()
            except Exception:
                pass
            WithdW = Tk()
            WithdW.title("Sanatan Bank / ATM / Account / Withdraw")
            WithdW.wm_iconbitmap("SB_icon1.ico")
            WithdW.geometry("700x420")

            def exeWithd():
                WithdStat=chkWithd(int(WithdAmtT.get()))         #sql
                if(WithdStat==1):
                    messagebox.showinfo("Withdraw Status", "Withdraw successful!\nTransaction ID: "+perfTransact(int(WithdAmtT.get()),1,1,acNumber))
                    WithdW.destroy()
                    openCAc()
                else:
                    messagebox.showerror("Withdraw Status", "Withdraw failed!")


            SpcLabel1 = Label(WithdW, text=SpcText)
            SpcLabel2 = Label(WithdW, text=SpcText)
            SpcLabel3 = Label(WithdW, text=SpcText)
            WithdLbl = Label(WithdW, text="Withdraw", fg="green")
            WithdLbl.config(font=("Magneto Bold", 36))
            WithdAmtT = Entry(WithdW, width="32", bg="green", fg="white")
            WithdAmtT.insert(1, "Amount")
            ConfWithdB = Button(WithdW, text="Confirm", padx=26, command=exeWithd)

            SpcLabel1.grid(row=0, column=0)
            WithdLbl.grid(row=1, column=1, padx=120, pady=75)
            WithdAmtT.grid(row=2, column=1, pady=10)
            ConfWithdB.grid(row=3, column=1, pady=10)

        def openDeposW():
            try:
                CAcW.destroy()
            except Exception:
                pass
            DeposW = Tk()
            DeposW.title("Sanatan Bank / ATM / Account / Deposit")
            DeposW.wm_iconbitmap("SB_icon1.ico")
            DeposW.geometry("700x420")

            def exeDepos():
                DeposStat = 0
                if(int(DeposAmtT.get()) >= minBalance):         #sql
                    DeposStat=1
                if(DeposStat==1):
                    messagebox.showinfo("Deposit Status", "Deposit successful!\nTransaction ID: "+perfTransact(int(DeposAmtT.get()),2,2,acNumber))
                else:
                    messagebox.showerror("Deposit Status", "Deposit failed!")
                DeposW.destroy()
                openCAc()


            SpcLabel1 = Label(DeposW, text=SpcText)
            SpcLabel2 = Label(DeposW, text=SpcText)
            SpcLabel3 = Label(DeposW, text=SpcText)
            DeposLbl = Label(DeposW, text="Deposit", fg="green")
            DeposLbl.config(font=("Magneto Bold", 36))
            DeposAmtT = Entry(DeposW, width="32", bg="green", fg="white")
            DeposAmtT.insert(1, "Amount")
            ConfDeposB = Button(DeposW, text="Confirm", padx=26, command=exeDepos)

            SpcLabel1.grid(row=0, column=0)
            DeposLbl.grid(row=1, column=1, padx=120, pady=75)
            DeposAmtT.grid(row=2, column=1, pady=10)
            ConfDeposB.grid(row=3, column=1, pady=10)

        def openTrnsfW():
            try:
                CAcW.destroy()
            except Exception:
                pass
            TrnsfW = Tk()
            TrnsfW.title("Sanatan Bank / ATM / Account / Transfer")
            TrnsfW.wm_iconbitmap("SB_icon1.ico")
            TrnsfW.geometry("700x420")

            def exeTrnsf():
                tgtAcNo=TrnsfAccT.get()
                amttemp=TrnsfAmtT.get()
                TrnsfStat = chkWithd(int(TrnsfAmtT.get()))
                if(TrnsfStat==1):
                    temp1=perfTransact(int(amttemp),1,3,acNumber)
                    temp2=perfTransact(int(amttemp),2,3,tgtAcNo)
                    messagebox.showinfo("Transfer Status","Transfer successful!\nTransaction ID: "+temp1)
                else:
                    messagebox.showerror("Transfer Status","Transfer failed!")
                TrnsfW.destroy()
                openCAc()


            SpcLabel1 = Label(TrnsfW, text=SpcText)
            SpcLabel2 = Label(TrnsfW, text=SpcText)
            SpcLabel3 = Label(TrnsfW, text=SpcText)
            TrnsfLbl = Label(TrnsfW, text="Transfer", fg="green")
            TrnsfLbl.config(font=("Magneto Bold", 36))
            TrnsfAccT = Entry(TrnsfW, width="32", bg="green", fg="white")
            TrnsfAccT.insert(1, "Recipient's account no.")
            TrnsfAmtT = Entry(TrnsfW, width="32", bg="green", fg="white")
            TrnsfAmtT.insert(1, "Amount")
            ConfTrnsfB = Button(TrnsfW, text="Confirm", padx=26, command=exeTrnsf)

            SpcLabel1.grid(row=0, column=0)
            TrnsfLbl.grid(row=1, column=1, padx=120, pady=75)
            TrnsfAccT.grid(row=2, column=1, pady=10)
            TrnsfAmtT.grid(row=3, column=1, pady=10)
            ConfTrnsfB.grid(row=4, column=1, pady=10)

        def doLogout():
            try:
                CAcW.destroy()
            except Exception:
                pass
            try:
                openATM()
            except Exception:
                pass


        SpcLabel1 = Label(CAcW, text=SpcText)
        SpcLabel2 = Label(CAcW, text=SpcText)
        SpcLabel3 = Label(CAcW, text=SpcText)
        BalLbl = Label(CAcW, text="Balance:\t" + str(acBalance), fg="green")      #sql
        BalLbl.config(font=("Cambria", 20, "bold"))
        WithdB = Button(CAcW, text="Withdraw", padx=26, command=openWithdW)
        DeposB = Button(CAcW, text="Deposit", padx=31, command=openDeposW)
        TrnsfB = Button(CAcW, text="Transfer", padx=31, command=openTrnsfW)
        LgoutB = Button(CAcW, text="Logout", padx=20, command=doLogout)

        LgoutB.grid(row=0, column=2, padx=20, pady=10)
        SpcLabel2.grid(row=1, column=0)
        BalLbl.grid(row=1, column=1, padx=32, pady=75)
        SpcLabel1.grid(row=2, column=0)
        WithdB.grid(row=2, column=1, padx=180, pady=5)
        isRecyclerF = isRecycler(atmNumber)         #sql
        if(isRecyclerF == 1):
            DeposB.grid(row=3, column=1, pady=5)
        TrnsfB.grid(row=4, column=1, pady=5)

    ATMlbl1 = Label(AtmRt, text="Login to ATM", fg="green")
    ATMlbl1.config(font=("Magneto Bold", 36))
    CdNo = Entry(AtmRt, width="32", bg="green", fg="white")
    CdNo.insert(0, "Card no.")
    pin = Entry(AtmRt, width="32", bg="green", fg="white")
    pin.insert(0, "ATM pin")
    ATMloginB = Button(AtmRt, text="Login", padx=20, command=openCAc)
    SpcLabel1 = Label(AtmRt, text=SpcText)
    SpcLabel2 = Label(AtmRt, text=SpcText)
    SpcLabel3 = Label(AtmRt, text=SpcText)

    SpcLabel2.grid(row=1, column=0)
    ATMlbl1.grid(row=1, column=1, padx=32, pady=75)
    SpcLabel1.grid(row=2, column=0)
    CdNo.grid(row=2, column=1, pady=10)
    #SpcLabel2.grid(row=3, column=0)
    pin.grid(row=3, column=1, pady=10)
    ATMloginB.grid(row=4, column=1, pady=10)


def openAdmin():
    try:
        root.destroy()
    except Exception:
        pass
    AdLginW = Tk()
    AdLginW.title("Sanatan Bank / Admin login")
    AdLginW.wm_iconbitmap("SB_icon1.ico")
    AdLginW.geometry("700x420")

    def openAdRt():
        try:
            global adminNumber, adminPassword
            adminNumber=AdId.get()
            adminPassword=Adpw.get()
            CredF=chkAdCred(adminNumber,adminPassword)
            if(CredF!=1):
                messagebox.showwarning("Error","Invalid credentials!")
                return
        except Exception:
            pass
        try:
            AdLginW.destroy()
        except Exception:
            pass
        AdRtW = Tk()
        AdRtW.title("Sanatan Bank / Admin login / Dashboard")
        AdRtW.wm_iconbitmap("SB_icon1.ico")
        AdRtW.geometry("700x420")

        def doLogout():
            try:
                AdRtW.destroy()
            except Exception:
                pass
            try:
                openAdmin()
            except Exception:
                pass

        def openRfl():
            try:
                AdRtW.destroy()
            except Exception:
                pass
            AdRfW = Tk()
            AdRfW.title("Sanatan Bank / Admin login / Dashboard / Refill")
            AdRfW.wm_iconbitmap("SB_icon1.ico")
            AdRfW.geometry("700x420")

            def doBack():
                try:
                    AdRfW.destroy()
                except Exception:
                    pass
                try:
                    openAdRt()
                except Exception:
                    pass
            def doRfl():
                global atmNumber
                atmNumber=Rfl_AtT.get()
                amt=int(Rfl_AmT.get())
                RflIsValidF = RflIsValid(atmNumber, amt)
                if (RflIsValidF!=1):
                    messagebox.showerror("ATM Refiller", "Refill failed!")
                    return

                perfRefill(atmNumber, amt)
                messagebox.showinfo("ATM Refiller", "Refill Successful!")
                doBack()

            def showBalLst():
                BalLstW = Tk()
                BalLstW.title("Sanatan Bank - ATM Balance List")
                BalLstW.wm_iconbitmap("SB_icon1.ico")

                BalChart = ttk.Treeview(BalLstW)
                BalChart['columns'] = ("c1", "c2", "c3")

                BalChart.column("#0", width=0, stretch=NO)
                BalChart.column("c1", anchor=W, width=100)
                BalChart.column("c2", anchor=E, width=100)
                BalChart.column("c3", anchor=W, width=100)

                BalChart.heading("#0", text="", anchor=W)
                BalChart.heading("c1", text="ATM ID", anchor=CENTER)
                BalChart.heading("c2", text="Balance", anchor=CENTER)
                BalChart.heading("c3", text="Address", anchor=CENTER)

                cursor = db.cursor()
                selQuery = "select atm_id, atm_bl, atm_adr from ATM order by atm_bl asc;"
                cursor.execute(selQuery)
                records = cursor.fetchall()
                cursor.close()

                for rowNum in records:
                    BalChart.insert(parent='', index='end', iid=rowNum, text="",
                                    values=(rowNum[0], str(rowNum[1]), rowNum[2]))

                BalChart.grid(row=4, columnspan=4, sticky='nsew')

            # ACk_frm = LabelFrame(AtmCkW, "Check cash availability at ATM", padx=16, pady=16)
            Rfl_backB = Button(AdRfW, text="←Back", padx=5, pady=5, command=doBack)
            Rfl_Lbl = Label(AdRfW, text="Refill", fg="green")
            Rfl_Lbl.config(font=("Magneto Bold", 36))
            Rfl_AtT = Entry(AdRfW, width="32", bg="green", fg="white")
            Rfl_AtT.insert(0, "Enter ATM no.")
            Rfl_AmT = Entry(AdRfW, width="32", bg="green", fg="white")
            Rfl_AmT.insert(0, "Enter refill amount")
            RflDoB = Button(AdRfW, text="Refill", padx=16, command=doRfl)
            BalLstB = Button(AdRfW, text="View ATM balances", padx=16, command=showBalLst)
            # ACk_frm.grid(row=2, column=0, rowspan=4, padx=20, pady=30)

            Rfl_backB.grid(row=0, column=0, sticky=W, padx=60, pady=5)
            Rfl_Lbl.grid(row=1, column=0, columnspan=3, padx=60, pady=20)
            Rfl_AtT.grid(row=2, column=0, padx=60, pady=0)
            Rfl_AmT.grid(row=2, column=1, padx=0, pady=0)
            RflDoB.grid(row=2, column=2, padx=60, pady=20)
            BalLstB.grid(row=3, column=0, columnspan=3, padx=60, pady=20)

        def openVnd():
            try:
                AdRtW.destroy()
            except Exception:
                pass
            AVndW = Tk()
            AVndW.title("Sanatan Bank / Admin login / Dashboard / Vendors")
            AVndW.wm_iconbitmap("SB_icon1.ico")
            AVndW.geometry("700x420")

            def doBack():
                try:
                    AVndW.destroy()
                except Exception:
                    pass
                try:
                    openAdRt()
                except Exception:
                    pass

            def openNewVnd():
                try:
                    AVndW.destroy()
                except Exception:
                    pass
                NewVndW = Tk()
                NewVndW.title("Sanatan Bank / Admin login / Dashboard / Vendors / New Vendor")
                NewVndW.wm_iconbitmap("SB_icon1.ico")
                NewVndW.geometry("700x420")

                def doBack():
                    try:
                        NewVndW.destroy()
                    except Exception:
                        pass
                    try:
                        openVnd()
                    except Exception:
                        pass

                def addVnd():
                    compName=NwVndCmT.get()
                    compReview=NwVndRvT.get()
                    CredF = vendIsValid(compName,compReview)
                    if (CredF != 1):
                        messagebox.showerror("New Vendor", "Addition failed!")
                        return

                    perfVend(compName,int(compReview))

                    messagebox.showinfo("New Vendor", "New vendor successfully added!")
                    doBack()

                SpcLabel1 = Label(NewVndW, text=SpcText)
                SpcLabel2 = Label(NewVndW, text=SpcText)
                SpcLabel3 = Label(NewVndW, text=SpcText)
                BackB = Button(NewVndW, text="←Back", padx=5, pady=5, command=doBack)
                NwVndLbl = Label(NewVndW, text="Vendor Details", fg="green")
                NwVndLbl.config(font=("Magneto Bold", 24))
                # C_DtlFrm = LabelFrame(CdtlW, text="*-*-*-*-*", padx=10, pady=10)
                NwVndCmL = Label(NewVndW, text="Company name: ")
                NwVndRvL = Label(NewVndW, text="Review: ")
                NwVndCmT = Entry(NewVndW, width="32", bg="green", fg="white")
                # NwVndCmT.insert(0, "YYYY")
                NwVndRvT = Entry(NewVndW, width="32", bg="green", fg="white")
                NwVndRvT.insert(0, "0 to 10")
                NwVndOkB = Button(NewVndW, text="Add", padx=16, command=addVnd)

                # .grid(row=9, column=1, rowspan=2, sticky=E, pady=30)
                # SpcLabel1.grid(row=1, column=1, rowspan=2, pady=50)
                BackB.grid(row=0, column=0, padx=10, pady=10)
                NwVndLbl.grid(row=1, column=1, columnspan=2, padx=145, pady=50)
                NwVndCmL.grid(row=4, column=1, sticky=E)
                NwVndRvL.grid(row=6, column=1, sticky=E)
                NwVndCmT.grid(row=4, column=2, sticky=W)
                NwVndRvT.grid(row=6, column=2, sticky=W)
                NwVndOkB.grid(row=10, column=1, columnspan=2, pady=32)

            def showVndLst():
                VndLstW = Tk()
                VndLstW.title("Sanatan Bank - Vendors List")
                VndLstW.wm_iconbitmap("SB_icon1.ico")

                VndChart = ttk.Treeview(VndLstW)
                VndChart['columns'] = ("c1", "c2", "c3")

                VndChart.column("#0", width=0, stretch=NO)
                VndChart.column("c1", anchor=W, width=100)
                VndChart.column("c2", anchor=E, width=100)
                VndChart.column("c3", anchor=E, width=100)

                VndChart.heading("#0", text="", anchor=W)
                VndChart.heading("c1", text="Company", anchor=CENTER)
                VndChart.heading("c2", text="Review score", anchor=CENTER)
                VndChart.heading("c3", text="No. of contracts", anchor=CENTER)

                cursor=db.cursor()
                selQuery="select comp, rvw, no_ct from Vendor order by comp asc;"
                cursor.execute(selQuery)
                records = cursor.fetchall()
                cursor.close()

                for rowNum in records:
                    VndChart.insert(parent='', index='end', iid=rowNum, text="",
                                    values=(rowNum[0], str(rowNum[1]), str(rowNum[2])))  # change

                VndChart.grid(row=4, columnspan=4, sticky='nsew')

            # ACk_frm = LabelFrame(AtmCkW, "Check cash availability at ATM", padx=16, pady=16)
            Cnt_backB = Button(AVndW, text="←Back", padx=5, pady=5, command=doBack)
            CntLbl = Label(AVndW, text="Vendors", fg="green")
            CntLbl.config(font=("Magneto Bold", 36))
            # Cnt_AtT = Entry(ACntW, width="32", bg="green", fg="white")
            # Cnt_AtT.insert(0, "Enter ATM no.")
            # Cnt_VdT = Entry(ACntW, width="32", bg="green", fg="white")
            # Cnt_VdT.insert(0, "Enter vendor name")
            CntAddB = Button(AVndW, text="New Vendor", padx=27, command=openNewVnd)
            VndLstB = Button(AVndW, text="View Vendor List", padx=16, command=showVndLst)
            # ACk_frm.grid(row=2, column=0, rowspan=4, padx=20, pady=30)

            Cnt_backB.grid(row=0, column=0, sticky=W, padx=32, pady=5)
            CntLbl.grid(row=1, column=0, columnspan=3, padx=250, pady=40)
            # Cnt_AtT.grid(row=2, column=0, padx=60, pady=0)
            # Cnt_VdT.grid(row=2, column=1, padx=0, pady=0)
            CntAddB.grid(row=2, column=0, columnspan=3, padx=32, pady=8)
            VndLstB.grid(row=3, column=0, columnspan=3, padx=32, pady=8)

        def openACnt():
            try:
                AdRtW.destroy()
            except Exception:
                pass
            ACntW = Tk()
            ACntW.title("Sanatan Bank / Admin login / Dashboard / Contracts")
            ACntW.wm_iconbitmap("SB_icon1.ico")
            ACntW.geometry("700x420")

            def doBack():
                try:
                    ACntW.destroy()
                except Exception:
                    pass
                try:
                    openAdRt()
                except Exception:
                    pass

            def openNewCnt():
                try:
                    ACntW.destroy()
                except Exception:
                    pass
                NewCntW = Tk()
                NewCntW.title("Sanatan Bank / Admin login / Dashboard / Contracts / New Contract")
                NewCntW.wm_iconbitmap("SB_icon1.ico")
                NewCntW.geometry("700x420")

                def doBack():
                    try:
                        NewCntW.destroy()
                    except Exception:
                        pass
                    try:
                        openACnt()
                    except Exception:
                        pass

                def addNewCnt():
                    atmNum=NwCntAtT.get()
                    company=NwCntCoT.get()
                    CredF = cntIsValid(atmNum,company)
                    if (CredF != 1):
                        messagebox.showerror("New Contract", "Assignment failed!")
                        return
                    amctemp=NwCntAmcT.get()
                    warrtemp=NwCntWarT.get()

                    messagebox.showinfo("New Contract", "New contract successfully assigned!\nContract ID: "+perfCnt(atmNum, company, amctemp, warrtemp))
                    doBack()

                SpcLabel1 = Label(NewCntW, text=SpcText)
                SpcLabel2 = Label(NewCntW, text=SpcText)
                SpcLabel3 = Label(NewCntW, text=SpcText)
                BackB = Button(NewCntW, text="←Back", padx=5, pady=5, command=doBack)
                NwCntLbl = Label(NewCntW, text="Contract Details", fg="green")
                NwCntLbl.config(font=("Magneto Bold", 24))
                #C_DtlFrm = LabelFrame(CdtlW, text="*-*-*-*-*", padx=10, pady=10)
                #NwCntIdL = Label(NewCntW, text="Contract ID: ")
                NwCntAtL = Label(NewCntW, text="Atm ID: ")
                NwCntCoL = Label(NewCntW, text="Company: ")
                NwCntAmcL = Label(NewCntW, text="AMC: ")
                NwCntWarL  = Label(NewCntW, text="Warranty: ")
                #NwCntYrL = Label(NewCntW, text="Contract year: ")
                #NwCntIdT = Entry(NewCntW, width="32", bg="green", fg="white")
                NwCntAtT = Entry(NewCntW, width="32", bg="green", fg="white")
                NwCntCoT = Entry(NewCntW, width="32", bg="green", fg="white")
                NwCntAmcT = Entry(NewCntW, width="32", bg="green", fg="white")
                NwCntWarT  = Entry(NewCntW, width="32", bg="green", fg="white")
                NwCntWarT.insert(0, "No. of years")
                #NwCntYrT = Entry(NewCntW, width="32", bg="green", fg="white")
                #NwCntYrT.insert(0, "YYYY")
                NwCntOkB = Button(NewCntW, text="Assign", padx=16, command=addNewCnt)

                #.grid(row=9, column=1, rowspan=2, sticky=E, pady=30)
                #SpcLabel1.grid(row=1, column=1, rowspan=2, pady=50)
                BackB.grid(row=0, column=0, padx=10, pady=10)
                NwCntLbl.grid(row=1, column=1, columnspan=2, padx=135, pady=36)
                #NwCntIdL.grid(row=2, column=1, sticky=E)
                NwCntAtL.grid(row=3, column=1, sticky=E)
                NwCntCoL.grid(row=4, column=1, sticky=E)
                NwCntAmcL.grid(row=5, column=1, sticky=E)
                NwCntWarL.grid(row=6, column=1, sticky=E)
                #NwCntYrL.grid(row=7, column=1, sticky=E)
                #NwCntIdT.grid(row=2, column=2, sticky=W)
                NwCntAtT.grid(row=3, column=2, sticky=W)
                NwCntCoT.grid(row=4, column=2, sticky=W)
                NwCntAmcT.grid(row=5, column=2, sticky=W)
                NwCntWarT.grid(row=6, column=2, sticky=W)
                #NwCntYrT.grid(row=7, column=2, sticky=W)
                NwCntOkB.grid(row=10, column=1, columnspan=2, pady=32)

            def showCntrLst():
                CntrLstW = Tk()
                CntrLstW.title("Sanatan Bank - Contracts List")
                CntrLstW.wm_iconbitmap("SB_icon1.ico")

                VndChart = ttk.Treeview(CntrLstW)
                VndChart['columns'] = ("c1", "c2", "c3", "c4", "c5")

                VndChart.column("#0", width=0, stretch=NO)
                VndChart.column("c1", anchor=W, width=100)
                VndChart.column("c2", anchor=W, width=100)
                VndChart.column("c3", anchor=CENTER, width=100)
                VndChart.column("c4", anchor=E, width=100)
                VndChart.column("c5", anchor=E, width=120)

                VndChart.heading("#0", text="", anchor=W)
                VndChart.heading("c1", text="Contract ID", anchor=CENTER)
                VndChart.heading("c2", text="ATM ID", anchor=CENTER)
                VndChart.heading("c3", text="Signing year", anchor=CENTER)
                VndChart.heading("c4", text="Years of warranty", anchor=CENTER)
                VndChart.heading("c5", text="AMC amount", anchor=CENTER)

                cursor = db.cursor()
                selQuery = "select ct_id, atm_id, ct_yr, warr, amc from Contract order by ct_yr desc;"
                cursor.execute(selQuery)
                records = cursor.fetchall()
                cursor.close()

                for rowNum in records:
                    VndChart.insert(parent='', index='end', iid=rowNum, text="",
                                    values=(rowNum[0], rowNum[1], str(rowNum[2]), str(rowNum[3]), str(rowNum[4])))

                VndChart.grid(row=4, columnspan=4, sticky='nsew')

            # ACk_frm = LabelFrame(AtmCkW, "Check cash availability at ATM", padx=16, pady=16)
            Cnt_backB = Button(ACntW, text="←Back", padx=5, pady=5, command=doBack)
            CntLbl = Label(ACntW, text="Contracts", fg="green")
            CntLbl.config(font=("Magneto Bold", 36))
            CntAddB = Button(ACntW, text="New Contract", padx=26, command=openNewCnt)
            CntrLstB = Button(ACntW, text="View Contract List", padx=16, command=showCntrLst)
            # ACk_frm.grid(row=2, column=0, rowspan=4, padx=20, pady=30)

            Cnt_backB.grid(row=0, column=0, sticky=W, padx=32, pady=5)
            CntLbl.grid(row=1, column=0, columnspan=3, padx=220, pady=36)
            # Cnt_AtT.grid(row=2, column=0, padx=60, pady=0)
            # Cnt_VdT.grid(row=2, column=1, padx=0, pady=0)
            CntAddB.grid(row=2, column=0, columnspan=3, padx=220, pady=5)
            CntrLstB.grid(row=3, column=0, columnspan=3, padx=220, pady=5)


        def openASec():
            try:
                AdRtW.destroy()
            except Exception:
                pass
            ASecW = Tk()
            ASecW.title("Sanatan Bank / Admin login / Dashboard / Security")
            ASecW.wm_iconbitmap("SB_icon1.ico")
            ASecW.geometry("700x420")

            def doBack():
                try:
                    ASecW.destroy()
                except Exception:
                    pass
                try:
                    openAdRt()
                except Exception:
                    pass

            def openSecRespond():
                global atmNumber
                atmNumber=ASecAtNoT.get()
                dt=ASecDtTmT.get()
                CredF = secIsValid(atmNumber,dt)
                if (CredF!=1):
                    messagebox.showerror("Resolve Fraud", "Described fraud not found!")
                    return

                try:
                    ASecW.destroy()
                except Exception:
                    pass
                SecRespW = Tk()
                SecRespW.title("Sanatan Bank / Admin login / Dashboard / Security / New Response")
                SecRespW.wm_iconbitmap("SB_icon1.ico")
                SecRespW.geometry("700x420")

                def doBack():
                    try:
                        SecRespW.destroy()
                    except Exception:
                        pass
                    try:
                        openASec()
                    except Exception:
                        pass

                cursor = db.cursor()            #sql
                selQuery = "select frd from Security where atm_id=%s and s_dt=%s;"
                data = (atmNumber,dt)
                cursor.execute(selQuery, data)
                records = cursor.fetchone()
                frd = records[0]
                cursor.close()

                def doResp():
                    resolution=SRsp_ResT.get("1.0",'end-1c')
                    FrdHasTextF = 0
                    if(resolution!=''):
                        FrdHasTextF = 1
                    if(FrdHasTextF!=1):
                        messagebox.showwarning("Fraud Resolution",
                                            "Fraud resolution cannot be empty!")
                        return

                    perfSec(atmNumber,resolution)

                    messagebox.showinfo("Fraud Resolution",
                                        "Fraud resolution has been\nsuccessfully registered.")
                    doBack()

                SRsp_BackB = Button(SecRespW, text="←Back", padx=5, pady=5, command=doBack)
                SRspLbl = Label(SecRespW, text="Respond to fraud", fg="green")
                SRspLbl.config(font=("Magneto Bold", 36))
                SRsp_frdL = Label(SecRespW, text="Fraud: ")
                SRsp_frdV = Label(SecRespW, text=frd, fg="green")
                SRsp_ResL = Label(SecRespW, text="Resolution: ")
                SRsp_ResT = Text(SecRespW, height="6", width="50", bg="green", fg="white")
                RspB = Button(SecRespW, text="Submit", padx=16, command=doResp)

                SRsp_BackB.grid(row=0, column=0, sticky=W, padx=10, pady=8)
                SRspLbl.grid(row=1, column=0, columnspan=3, sticky=E, padx=120, pady=20)
                SRsp_frdL.grid(row=2, column=1, sticky=NE, padx=6, pady=5)
                SRsp_frdV.grid(row=2, column=2, sticky=W, padx=6, pady=5)
                SRsp_ResL.grid(row=3, column=1, sticky=NE, padx=6, pady=5)
                SRsp_ResT.grid(row=3, column=2, sticky=NW, padx=6, pady=8)
                RspB.grid(row=5, column=0, columnspan=3, padx=60, pady=32)

            def showSecLst():
                SecLstW = Tk()
                SecLstW.title("Sanatan Bank - List of Security Threats")
                SecLstW.wm_iconbitmap("SB_icon1.ico")

                SecChart = ttk.Treeview(SecLstW)
                SecChart['columns'] = ("c1", "c2", "c3")

                SecChart.column("#0", width=0, stretch=NO)
                SecChart.column("c1", anchor=W, width=100)
                SecChart.column("c2", anchor=CENTER, width=140)
                SecChart.column("c3", anchor=W, width=220)

                SecChart.heading("#0", text="", anchor=W)
                SecChart.heading("c1", text="ATM ID", anchor=CENTER)
                SecChart.heading("c2", text="Date & time", anchor=CENTER)
                SecChart.heading("c3", text="Security Threats", anchor=CENTER)

                cursor = db.cursor()
                selQuery = "select atm_id, s_dt, frd from Security where res = '' order by s_dt asc;"
                cursor.execute(selQuery)
                records = cursor.fetchall()
                cursor.close()

                # rowTot = 10  # change
                for rowNum in records:
                    SecChart.insert(parent='', index='end', iid=rowNum, text="",
                                    values=(rowNum[0], str(rowNum[1]), rowNum[2]))

                SecChart.grid(row=4, columnspan=4, sticky='nsew')

            ASec_backB = Button(ASecW, text="←Back", padx=5, pady=5, command=doBack)
            ASecLbl = Label(ASecW, text="Security", fg="green")
            ASecLbl.config(font=("Magneto Bold", 36))
            ASecAtNoT = Entry(ASecW, width="32", bg="green", fg="white")
            ASecAtNoT.insert(0, "ATM no.")
            ASecDtTmT = Entry(ASecW, width="32", bg="green", fg="white")
            ASecDtTmT.insert(0, "YYYY-MM-DD hh:mm:ss")
            ReslvB = Button(ASecW, text="Respond", padx=20, command=openSecRespond)
            SecLstB = Button(ASecW, text="View Security Threats", padx=20, command=showSecLst)

            ASec_backB.grid(row=0, column=0, sticky=W, padx=10, pady=10)
            ASecLbl.grid(row=1, column=1, columnspan=4, sticky=W, padx=160, pady=32)
            ASecAtNoT.grid(row=2, column=1, sticky=W, padx=10, pady=5)
            ASecDtTmT.grid(row=2, column=2, sticky=W, padx=10, pady=5)
            ReslvB.grid(row=2, column=3, sticky=W, padx=10, pady=5)
            SecLstB.grid(row=5, column=1, columnspan=5, padx=160, pady=20)


        def openACmp():
            try:
                AdRtW.destroy()
            except Exception:
                pass
            ACmpW = Tk()
            ACmpW.title("Sanatan Bank / Admin login / Dashboard / Complaints")
            ACmpW.wm_iconbitmap("SB_icon1.ico")
            ACmpW.geometry("700x420")

            def doBack():
                try:
                    ACmpW.destroy()
                except Exception:
                    pass
                try:
                    openAdRt()
                except Exception:
                    pass

            def openACmpAtnd():
                # CredF = 1
                compNum=ACmpNoT.get()
                CredF = compIsValid(compNum)
                if (CredF != 1):
                    messagebox.showwarning("Attend Complaint", "Invalid Complaint no.!")
                    return
                try:
                    ACmpW.destroy()
                except Exception:
                    pass
                CmpAtndW = Tk()
                CmpAtndW.title("Sanatan Bank / Admin login / Dashboard / Complaints / Attend Complaint")
                CmpAtndW.wm_iconbitmap("SB_icon1.ico")
                CmpAtndW.geometry("700x420")

                def doBack():
                    try:
                        CmpAtndW.destroy()
                    except Exception:
                        pass
                    try:
                        openACmp()
                    except Exception:
                        pass

                cursor = db.cursor()  #sql
                selQuery = "select descr from Complaint where cl_id=%s;"
                data = (compNum,)
                cursor.execute(selQuery, data)
                records = cursor.fetchone()
                descr = records[0]
                cursor.close()

                def doUpdate():
                    status = CmpAtnd_StsT.get()
                    StsHasTextF = 0
                    if (status != ''):
                        StsHasTextF = 1
                    if (StsHasTextF != 1):
                        messagebox.showwarning("Update Complaint Status",
                                               "Complaint status cannot be empty!")
                        return

                    perfComp(compNum,status)

                    messagebox.showinfo("Update Complaint Status",
                                        "Complaint status has been\nsuccessfully updated!")
                    doBack()

                CmpAtnd_BackB = Button(CmpAtndW, text="←Back", padx=5, pady=5, command=doBack)
                CmpAtndLbl = Label(CmpAtndW, text="Attend Complaint", fg="green")
                CmpAtndLbl.config(font=("Magneto Bold", 36))
                CmpAtnd_descL = Label(CmpAtndW, text="Complaint: ")
                CmpAtnd_descV = Label(CmpAtndW, text=descr, fg="green")
                CmpAtnd_StsL = Label(CmpAtndW, text="Complaint status: ")
                CmpAtnd_StsT = Entry(CmpAtndW, width="32", bg="green", fg="white")
                UpdateB = Button(CmpAtndW, text="Update", padx=16, command=doUpdate)

                CmpAtnd_BackB.grid(row=0, column=0, sticky=W, padx=10, pady=8)
                CmpAtndLbl.grid(row=1, column=0, columnspan=4, sticky=E, padx=120, pady=40)
                CmpAtnd_descL.grid(row=2, column=1, sticky=NE, padx=6, pady=5)
                CmpAtnd_descV.grid(row=2, column=2, sticky=W, padx=6, pady=5)
                CmpAtnd_StsL.grid(row=3, column=1, sticky=NE, padx=6, pady=5)
                CmpAtnd_StsT.grid(row=3, column=2, sticky=W, padx=10, pady=0)
                UpdateB.grid(row=5, column=0, columnspan=4, padx=60, pady=32)

            def showACmpLst():
                ACmpLstW = Tk()
                ACmpLstW.title("Sanatan Bank - Complaint List")
                ACmpLstW.wm_iconbitmap("SB_icon1.ico")

                ACmpChart = ttk.Treeview(ACmpLstW)
                ACmpChart['columns'] = ("c1", "c2", "c3")

                ACmpChart.column("#0", width=0, stretch=NO)
                ACmpChart.column("c1", anchor=W, width=100)
                ACmpChart.column("c2", anchor=W, width=100)
                ACmpChart.column("c3", anchor=W, width=250)

                ACmpChart.heading("#0", text="", anchor=W)
                ACmpChart.heading("c1", text="Complaint ID", anchor=CENTER)
                ACmpChart.heading("c2", text="ATM ID", anchor=CENTER)
                ACmpChart.heading("c3", text="Description", anchor=CENTER)

                cursor = db.cursor()
                selQuery = "select cl_id, atm_id, descr from Complaint where cl_stat ='' order by cl_id asc;"
                cursor.execute(selQuery)
                records = cursor.fetchall()
                cursor.close()

                # rowTot = 10  # change
                for rowNum in records:
                    ACmpChart.insert(parent='', index='end', iid=rowNum, text="",
                                     values=(rowNum[0], rowNum[1], rowNum[2]))

                ACmpChart.grid(row=4, columnspan=4, sticky='nsew')

            ACmp_backB = Button(ACmpW, text="←Back", padx=5, pady=5, command=doBack)
            ACmpLbl = Label(ACmpW, text="Complaints", fg="green")
            ACmpLbl.config(font=("Magneto Bold", 36))
            ACmpNoT = Entry(ACmpW, width="32", bg="green", fg="white")
            ACmpNoT.insert(0, "Complaint no.")
            ReslvB = Button(ACmpW, text="Attend", padx=10, command=openACmpAtnd)
            ACmpLstB = Button(ACmpW, text="View Complaint List", padx=10, command=showACmpLst)

            ACmp_backB.grid(row=0, column=0, sticky=W, padx=10, pady=10)
            ACmpLbl.grid(row=1, column=1, columnspan=2, sticky=W, padx=136, pady=25)
            ACmpNoT.grid(row=2, column=1, sticky=E, padx=20, pady=5)
            ReslvB.grid(row=2, column=2, sticky=W, padx=20, pady=5)
            ACmpLstB.grid(row=5, column=1, columnspan=2, padx=100, pady=25)

        def openAtmRcd():
            try:
                AdRtW.destroy()
            except Exception:
                pass
            AtmRcdW = Tk()
            AtmRcdW.title("Sanatan Bank / Admin login / Dashboard / ATM Records")
            AtmRcdW.wm_iconbitmap("SB_icon1.ico")
            AtmRcdW.geometry("700x420")

            def doBack():
                try:
                    AtmRcdW.destroy()
                except Exception:
                    pass
                try:
                    openAdRt()
                except Exception:
                    pass

            def showTrHist():
                try:
                    global atmNumber
                    atmNumber = AtRcNoT.get()  #sql
                    CredF = chkAtCred(atmNumber)
                    if (CredF != 1):
                        messagebox.showwarning("Error", "This ATM does not exist!")
                        return
                except Exception:
                    pass

                TrHistW = Tk()
                TrHistW.title("Sanatan Bank - Transaction History")
                TrHistW.wm_iconbitmap("SB_icon1.ico")

                TrHistChart = ttk.Treeview(TrHistW)
                TrHistChart['columns'] = ("c1", "c2", "c3", "c4", "c5", "c6")

                TrHistChart.column("#0", width=0, stretch=NO)
                TrHistChart.column("c1", anchor=W, width=100)
                TrHistChart.column("c2", anchor=W, width=120)
                TrHistChart.column("c3", anchor=W, width=150)
                TrHistChart.column("c4", anchor=W, width=80)
                TrHistChart.column("c5", anchor=E, width=80)
                TrHistChart.column("c6", anchor=CENTER, width=150)

                TrHistChart.heading("#0", text="", anchor=W)
                TrHistChart.heading("c1", text="Transaction ID", anchor=CENTER)
                TrHistChart.heading("c2", text="Transaction type", anchor=CENTER)
                TrHistChart.heading("c3", text="Account No.", anchor=CENTER)
                TrHistChart.heading("c4", text="ATM Id", anchor=CENTER)
                TrHistChart.heading("c5", text="Amount", anchor=CENTER)
                TrHistChart.heading("c6", text="Date & time", anchor=CENTER)

                cursor = db.cursor()
                selQuery = "select tr_id, ac_no, atm_id, tw_amt, tr_dt from Withdraw \
                            where atm_id=%s order by tr_dt desc;"
                data = (atmNumber,)
                cursor.execute(selQuery, data)
                records = cursor.fetchall()
                cursor.close()
                for rowNum in records:
                    temptype=rowNum[0][1:2]
                    if(temptype=='W'):
                        trtype='Withdraw'
                    elif(temptype=='T'):
                        trtype='Transfer'
                    TrHistChart.insert(parent='', index='end', iid=rowNum, text="",
                                       values=(rowNum[0], trtype, str(rowNum[1]), rowNum[2], str(rowNum[3]), str(rowNum[4])))

                cursor = db.cursor()
                selQuery = "select tr_id, ac_no, atm_id, td_amt, tr_dt from Deposit \
                                            where atm_id=%s order by tr_dt desc;"
                data = (atmNumber,)
                cursor.execute(selQuery, data)
                records = cursor.fetchall()
                cursor.close()
                for rowNum in records:
                    temptype = rowNum[0][1:2]
                    if (temptype == 'D'):
                        trtype = 'Deposit'
                    elif (temptype == 'T'):
                        trtype = 'Transfer'
                    TrHistChart.insert(parent='', index='end', iid=rowNum, text="",
                                       values=(
                                       rowNum[0], trtype, str(rowNum[1]), rowNum[2], str(rowNum[3]), str(rowNum[4])))

                TrHistChart.grid(row=4, columnspan=4, sticky='nsew')

            def showRfHist():
                try:
                    global atmNumber
                    atmNumber = AtRcNoT.get()  #sql
                    CredF = chkAtCred(atmNumber)
                    if (CredF != 1):
                        messagebox.showwarning("Error", "This ATM does not exist!")
                        return
                except Exception:
                    pass

                RflHistW = Tk()
                RflHistW.title("Sanatan Bank - Refill History")
                RflHistW.wm_iconbitmap("SB_icon1.ico")

                RflHistChart = ttk.Treeview(RflHistW)
                RflHistChart['columns'] = ("c1", "c2", "c3")

                RflHistChart.column("#0", width=0, stretch=NO)
                RflHistChart.column("c1", anchor=W, width=100)
                RflHistChart.column("c2", anchor=W, width=160)
                RflHistChart.column("c3", anchor=E, width=100)

                RflHistChart.heading("#0", text="", anchor=W)
                RflHistChart.heading("c1", text="ATM ID", anchor=CENTER)
                RflHistChart.heading("c2", text="Date & time", anchor=CENTER)
                RflHistChart.heading("c3", text="Amount", anchor=CENTER)

                cursor = db.cursor()
                selQuery = "select atm_id, r_dt, r_amt from refill where atm_id=%s order by r_dt desc;"
                data=(atmNumber,)
                cursor.execute(selQuery,data)
                records = cursor.fetchall()
                cursor.close()

                # rowTot = 10  # change
                for rowNum in records:
                    RflHistChart.insert(parent='', index='end', iid=rowNum, text="",
                                        values=(rowNum[0], rowNum[1], rowNum[2]))  #change

                RflHistChart.grid(row=4, columnspan=4, sticky='nsew')

            AtRcBackB = Button(AtmRcdW, text="←Back", padx=5, pady=5, command=doBack)
            AtRcLbl = Label(AtmRcdW, text="ATM Records", fg="green")
            AtRcLbl.config(font=("Magneto Bold", 36))
            AtRcNoT = Entry(AtmRcdW, width="32", bg="green", fg="white")
            AtRcNoT.insert(0, "ATM no.")
            AtRcTrB = Button(AtmRcdW, text="Transactions", padx=8, command=showTrHist)
            AtRcHtB = Button(AtmRcdW, text="Refill History", padx=8, command=showRfHist)

            AtRcBackB.grid(row=0, column=0, sticky=W, padx=10, pady=10)
            AtRcLbl.grid(row=1, column=1, columnspan=2, sticky=W, padx=96, pady=55)
            AtRcNoT.grid(row=2, column=1, columnspan=2, padx=2, pady=5)
            AtRcTrB.grid(row=3, column=1, sticky=E, padx=6, pady=20)
            AtRcHtB.grid(row=3, column=2, sticky=W, padx=6, pady=5)


        SpcLabel1 = Label(AdRtW, text=SpcText)
        SpcLabel2 = Label(AdRtW, text=SpcText)
        SpcLabel3 = Label(AdRtW, text=SpcText)
        AR_Lbl = Label(AdRtW, text="Admin options", fg="green")
        AR_Lbl.config(font=("Magneto Bold", 36))
        AR_RflB = Button(AdRtW, text="Refill ATM", padx=62, command=openRfl)
        AR_VndB = Button(AdRtW, text="Vendors", padx=68, command=openVnd)
        AR_CntB = Button(AdRtW, text="Contracts", padx=64, command=openACnt)
        AR_SecB = Button(AdRtW, text="Monitor Security", padx=46, command=openASec)
        AR_CmpB = Button(AdRtW, text="Attend Complaints", padx=40, command=openACmp)
        AR_RcdB = Button(AdRtW, text="ATM Records", padx=55, command=openAtmRcd)
        LgoutB = Button(AdRtW, text="Logout", padx=12, command=doLogout)

        LgoutB.grid(row=0, column=3, sticky=S, padx=0, pady=10)
        SpcLabel2.grid(row=1, column=0)
        AR_Lbl.grid(row=1, column=1, columnspan=2, padx=60, pady=50)
        SpcLabel1.grid(row=2, column=0)
        AR_RflB.grid(row=2, column=1, sticky=SE, padx=5, pady=5)
        AR_VndB.grid(row=3, column=1, sticky=E, padx=5, pady=5)
        AR_CntB.grid(row=4, column=1, sticky=E, padx=5, pady=5)
        AR_SecB.grid(row=2, column=2, sticky=SW, padx=5, pady=5)
        AR_CmpB.grid(row=3, column=2, sticky=W, padx=5, pady=5)
        AR_RcdB.grid(row=4, column=2, sticky=W, padx=5, pady=5)

    AdLlbl1 = Label(AdLginW, text="Admin Login", fg="green")
    AdLlbl1.config(font=("Magneto Bold", 36))
    AdId = Entry(AdLginW, width="32", bg="green", fg="white")
    AdId.insert(0, "Admin ID")
    Adpw = Entry(AdLginW, width="32", bg="green", fg="white")
    Adpw.insert(0, "Password")
    AdLloginB = Button(AdLginW, text="Login", padx=20, command=openAdRt)
    SpcLabel1 = Label(AdLginW, text=SpcText)
    SpcLabel2 = Label(AdLginW, text=SpcText)
    SpcLabel3 = Label(AdLginW, text=SpcText)

    SpcLabel2.grid(row=1, column=0)
    AdLlbl1.grid(row=1, column=1, padx=60, pady=75)
    SpcLabel1.grid(row=2, column=0)
    AdId.grid(row=2, column=1, pady=10)
    # SpcLabel2.grid(row=3, column=0)
    Adpw.grid(row=3, column=1, pady=10)
    AdLloginB.grid(row=4, column=1, pady=10)


def openCLgin():
    try:
        root.destroy()
    except Exception:
        pass

    CLginW = Tk()
    CLginW.title("Sanatan Bank / Customer login")
    CLginW.wm_iconbitmap("SB_icon1.ico")
    CLginW.geometry("700x420")

    def openCRt():
        try:
            global custNumber, custPassword         #sql
            custNumber=CId.get()
            custPassword=pw.get()
            CredF=chkCCred(custNumber,custPassword)
            if(CredF!=1):
                messagebox.showwarning("Error","Invalid credentials!")
                return
        except Exception:
            pass
        try:
            CLginW.destroy()
        except Exception:
            pass

        CRtW = Tk()
        CRtW.title("Sanatan Bank / Customer login / Dashboard")
        CRtW.wm_iconbitmap("SB_icon1.ico")
        CRtW.geometry("700x420")

        def openCDtl():
            try:
                CRtW.destroy()
            except Exception:
                pass

            CdtlW = Tk()
            CdtlW.title("Sanatan Bank / Customer login / Dashboard / Details")
            CdtlW.wm_iconbitmap("SB_icon1.ico")
            CdtlW.geometry("700x420")

            def C_OK():
                try:
                    CdtlW.destroy()
                except Exception:
                    pass
                openCRt()

            cursor = db.cursor()
            selQuery = "select name_f, name_l, Customer.c_adr, dob, sex, c_apc, Customer_ph.c_ph  \
                       from Customer inner join Customer_Ad  \
                       on Customer.c_adr=Customer_Ad.c_adr  \
                       inner join Customer_ph on Customer.cust_id=Customer_ph.cust_id   \
                       where Customer.cust_id=%s;"
            data=(custNumber,)
            cursor.execute(selQuery,data)
            records = cursor.fetchone()
            cursor.close()

            SpcLabel1 = Label(CdtlW, text=SpcText)
            SpcLabel2 = Label(CdtlW, text=SpcText)
            SpcLabel3 = Label(CdtlW, text=SpcText)
            HeadLbl = Label(CdtlW, text="My Details", fg="green")
            HeadLbl.config(font=("Magneto Bold", 24))
            #C_DtlFrm = LabelFrame(CdtlW, text="*-*-*-*-*", padx=10, pady=10)
            C_fnmL = Label(CdtlW, text="First name: ")
            C_lnmL = Label(CdtlW, text="Last name: ")
            C_idL  = Label(CdtlW, text="Customer ID: ")
            C_dobL = Label(CdtlW, text="DOB: ")
            C_sexL = Label(CdtlW, text="Sex: ")
            C_pphL = Label(CdtlW, text="Primary phone: ")
            C_addL = Label(CdtlW, text="Address: ")
            C_apcL = Label(CdtlW, text="Pincode: ")
            C_fnmV = Label(CdtlW, text=records[0])
            C_lnmV = Label(CdtlW, text=records[1])
            C_idV  = Label(CdtlW, text=custNumber)
            C_dobV = Label(CdtlW, text=records[3])
            C_sexV = Label(CdtlW, text=records[4])
            C_pphV = Label(CdtlW, text=records[6])
            C_addV = Label(CdtlW, text=records[2])
            C_apcV = Label(CdtlW, text=records[5])
            CDtlOKB = Button(CdtlW, text="OK", padx=16, command=C_OK)

            #.grid(row=9, column=1, rowspan=2, sticky=E, pady=30)
            #SpcLabel1.grid(row=1, column=1, rowspan=2, pady=50)
            HeadLbl.grid(row=1, column=1, columnspan=2, padx=250, pady=36)
            C_fnmL.grid(row=2, column=1, sticky=E)
            C_lnmL.grid(row=3, column=1, sticky=E)
            C_idL.grid(row=4, column=1, sticky=E)
            C_dobL.grid(row=5, column=1, sticky=E)
            C_sexL.grid(row=6, column=1, sticky=E)
            C_pphL.grid(row=7, column=1, sticky=E)
            C_addL.grid(row=8, column=1, sticky=NE)
            C_apcL.grid(row=9, column=1, sticky=E)
            C_fnmV.grid(row=2, column=2, sticky=W)
            C_lnmV.grid(row=3, column=2, sticky=W)
            C_idV.grid(row=4, column=2, sticky=W)
            C_dobV.grid(row=5, column=2, sticky=W)
            C_sexV.grid(row=6, column=2, sticky=W)
            C_pphV.grid(row=7, column=2, sticky=W)
            C_addV.grid(row=8, column=2, sticky=W)
            C_apcV.grid(row=9, column=2, sticky=W)
            CDtlOKB.grid(row=10, column=1, columnspan=2, pady=32)

        def openAtmCk():
            try:
                CRtW.destroy()
            except Exception:
                pass
            AtmCkW = Tk()
            AtmCkW.title("Sanatan Bank / Customer login / Dashboard / ATM Check")
            AtmCkW.wm_iconbitmap("SB_icon1.ico")
            AtmCkW.geometry("700x420")

            def doBack():
                try:
                    AtmCkW.destroy()
                except Exception:
                    pass
                try:
                    openCRt()
                except Exception:
                    pass

            def showAtmLst():
                ifscNumber = ACk_BrT.get()
                amount = ACk_AmT.get()
                CredF = atmChkIsValid(ifscNumber, int(amount))
                if (CredF != 1):
                    messagebox.showerror("ATM Locator",
                                         "Invalid credentials!")
                    return

                AtmLstW = Tk()
                AtmLstW.title("Sanatan Bank - Available ATMs")
                AtmLstW.wm_iconbitmap("SB_icon1.ico")

                AtmChart = ttk.Treeview(AtmLstW)
                AtmChart['columns'] = ("c1", "c2", "c3", "c4", "c5")

                AtmChart.column("#0", width=0, stretch=NO)
                AtmChart.column("c1", anchor=W, width=100)
                AtmChart.column("c2", anchor=W, width=100)
                AtmChart.column("c3", anchor=W, width=100)
                AtmChart.column("c4", anchor=W, width=100)
                AtmChart.column("c5", anchor=W, width=100)

                AtmChart.heading("#0", text="", anchor=W)
                AtmChart.heading("c1", text="ATM ID", anchor=CENTER)
                AtmChart.heading("c2", text="ATM Address", anchor=CENTER)
                AtmChart.heading("c3", text="ATM Pin", anchor=CENTER)
                AtmChart.heading("c4", text="Machine type", anchor=CENTER)
                AtmChart.heading("c5", text="Availability", anchor=CENTER)

                ifscNumber = ACk_BrT.get()
                amount = ACk_AmT.get()
                CredF = atmChkIsValid(ifscNumber, int(amount))
                if (CredF != 1):
                    messagebox.showerror("ATM Locator",
                                         "Invalid credentials!")
                    return

                cursor = db.cursor()
                selQuery = "select atm_id, ATM.atm_adr, atm_apc, atm_tp, atm_bl \
                            from ATM inner join ATM_Ad on ATM.atm_adr=ATM_Ad.atm_adr    \
                            where ifsc=%s and atm_bl > %s order by atm_id asc;"
                data=(ifscNumber, amount,)
                cursor.execute(selQuery,data)
                records = cursor.fetchall()
                cursor.close()

                for rowNum in records:
                    AtmChart.insert(parent='', index='end', iid=rowNum, text="",
                                    values=(rowNum[0], rowNum[1], str(rowNum[2]), rowNum[3], 'Yes'))

                AtmChart.grid(row=4, columnspan=4, sticky='nsew')

            def showBrLst():
                BrLstW = Tk()
                BrLstW.title("Sanatan Bank - Branch List")
                BrLstW.wm_iconbitmap("SB_icon1.ico")

                BrChart = ttk.Treeview(BrLstW)
                BrChart['columns'] = ("c1", "c2", "c3")

                BrChart.column("#0", width=0, stretch=NO)
                BrChart.column("c1", anchor=W, width=100)
                BrChart.column("c2", anchor=W, width=100)
                BrChart.column("c3", anchor=W, width=100)

                BrChart.heading("#0", text="", anchor=W)
                BrChart.heading("c1", text="IFSC", anchor=CENTER)
                BrChart.heading("c2", text="Branch Address", anchor=CENTER)
                BrChart.heading("c3", text="Branch PIN", anchor=CENTER)

                cursor = db.cursor()
                selQuery = "select ifsc, Branch.br_adr, br_apc from Branch inner join Branch_Ad on Branch.br_adr=Branch_Ad.br_adr order by ifsc asc;"
                cursor.execute(selQuery)
                records = cursor.fetchall()
                cursor.close()

                for rowNum in records:
                    BrChart.insert(parent='', index='end', iid=rowNum, text="",
                                   values=(rowNum[0], rowNum[1], str(rowNum[2])))  # change

                BrChart.grid(row=4, columnspan=4, sticky='nsew')

            # ACk_frm = LabelFrame(AtmCkW, "Check cash availability at ATM", padx=16, pady=16)
            ACk_backB = Button(AtmCkW, text="←Back", padx=5, pady=5, command=doBack)
            ACk_BrT = Entry(AtmCkW, width="32", bg="green", fg="white")
            ACk_BrT.insert(0, "Enter IFSC")
            ACk_AmT = Entry(AtmCkW, width="32", bg="green", fg="white")
            ACk_AmT.insert(0, "Enter Amount")
            ChkB = Button(AtmCkW, text="Check", padx=16, command=showAtmLst)
            LmtLbl1 = Label(AtmCkW, text="[Amount upto Rs.10000 can be checked]", fg="grey")
            BrLstB = Button(AtmCkW, text="Show Branch List", padx=16, command=showBrLst)
            # ACk_frm.grid(row=2, column=0, rowspan=4, padx=20, pady=30)

            ACk_backB.grid(row=0, column=0, sticky=W, padx=60, pady=5)
            ACk_BrT.grid(row=2, column=0, padx=60, pady=0)
            ACk_AmT.grid(row=2, column=1, padx=0, pady=0)
            ChkB.grid(row=2, column=2, padx=60, pady=20)
            LmtLbl1.grid(row=4, column=1, sticky=W, columnspan=1, padx=0, pady=0)
            BrLstB.grid(row=5, column=0, columnspan=3, padx=60, pady=20)

        def openCmp():
            try:
                CRtW.destroy()
            except Exception:
                pass
            CCompW = Tk()
            CCompW.title("Sanatan Bank / Customer login / Dashboard / Complaints")
            CCompW.wm_iconbitmap("SB_icon1.ico")
            CCompW.geometry("700x420")

            def doBack():
                try:
                    CCompW.destroy()
                except Exception:
                    pass
                try:
                    openCRt()
                except Exception:
                    pass

            def doNewCmp():
                try:
                    CCompW.destroy()
                except Exception:
                    pass
                NCmpW = Tk()
                NCmpW.title("Sanatan Bank / Customer login / Dashboard / Complaints / New Complaint")
                NCmpW.wm_iconbitmap("SB_icon1.ico")
                NCmpW.geometry("700x420")

                def doBack():
                    try:
                        NCmpW.destroy()
                    except Exception:
                        pass
                    try:
                        openCmp()
                    except Exception:
                        pass

                def doReg():
                    global atmNumber
                    atmNumber=NCmp_AtNoT.get()
                    descrip = NCmp_descT.get("1.0", 'end-1c')
                    CmpIsValidF = chkAtCred(atmNumber)
                    if (CmpIsValidF != 1):
                        messagebox.showwarning("New Complaint Registration", "Invalid ATM No.!")
                        return
                    CmpIsValidF =0
                    if (descrip != ''):
                        CmpIsValidF = 1
                    if (CmpIsValidF != 1):
                        messagebox.showwarning("New Complaint Registration", "Description cannot be blank!")
                        return

                    messagebox.showinfo("New Complaint Registration",
                                        "New complaint successfully registered.\nSorry for the inconvenience.\nComplaint ID: "+perfCompC(atmNumber,descrip))
                    doBack()

                NCmp_BackB = Button(NCmpW, text="←Back", padx=5, pady=5, command=doBack)
                NCmpLbl = Label(NCmpW, text="Register complaint", fg="green")
                NCmpLbl.config(font=("Magneto Bold", 36))
                NCmp_AtNoL = Label(NCmpW, text="ATM no:")
                NCmp_AtNoT = Entry(NCmpW, width="32", bg="green", fg="white")
                NCmp_descL = Label(NCmpW, text="Description:")
                NCmp_descT = Text(NCmpW, height="6", width="42", bg="green", fg="white")
                RegB = Button(NCmpW, text="Submit", padx=16, command=doReg)

                NCmp_BackB.grid(row=0, column=0, sticky=W, padx=10, pady=8)
                NCmpLbl.grid(row=1, column=0, columnspan=4, sticky=E, padx=100, pady=20)
                NCmp_AtNoL.grid(row=2, column=1, sticky=NE, padx=6, pady=5)
                NCmp_AtNoT.grid(row=2, column=2, sticky=NW, padx=10, pady=7)
                NCmp_descL.grid(row=5, column=1, sticky=NE, padx=6, pady=5)
                NCmp_descT.grid(row=5, column=2, sticky=NW, padx=10, pady=7)
                RegB.grid(row=6, column=0, columnspan=4, padx=60, pady=32)

            def showCCmpLst():
                CCmpLstW = Tk()
                CCmpLstW.title("Sanatan Bank - Complaint List")
                CCmpLstW.wm_iconbitmap("SB_icon1.ico")

                CCmpChart = ttk.Treeview(CCmpLstW)
                CCmpChart['columns'] = ("c1", "c2", "c3", "c4")

                CCmpChart.column("#0", width=0, stretch=NO)
                CCmpChart.column("c1", anchor=W, width=100)
                CCmpChart.column("c2", anchor=W, width=100)
                CCmpChart.column("c3", anchor=W, width=200)
                CCmpChart.column("c4", anchor=W, width=120)

                CCmpChart.heading("#0", text="", anchor=W)
                CCmpChart.heading("c1", text="Complaint ID", anchor=CENTER)
                CCmpChart.heading("c2", text="ATM ID", anchor=CENTER)
                CCmpChart.heading("c3", text="Description", anchor=CENTER)
                CCmpChart.heading("c4", text="Resolution", anchor=CENTER)

                cursor = db.cursor()
                selQuery = "select cl_id, atm_id, descr, cl_stat from Complaint where cust_id=%s order by cl_id asc;"
                data=(custNumber,)
                cursor.execute(selQuery,data)
                records = cursor.fetchall()
                cursor.close()

                for rowNum in records:
                    CCmpChart.insert(parent='', index='end', iid=rowNum, text="",
                                     values=(rowNum[0], rowNum[1], rowNum[2], rowNum[3]))

                CCmpChart.grid(row=4, columnspan=4, sticky='nsew')

            Cmp_backB = Button(CCompW, text="←Back", padx=5, pady=5, command=doBack)
            CmpLbl = Label(CCompW, text="Complaints", fg="green")
            CmpLbl.config(font=("Magneto Bold", 36))
            CmpNewB = Button(CCompW, text="New complaint", padx=30, command=doNewCmp)
            CmpLstB = Button(CCompW, text="Show Complaint List", padx=16, command=showCCmpLst)

            Cmp_backB.grid(row=0, column=0, sticky=W, padx=18, pady=10)
            CmpLbl.grid(row=1, column=0, columnspan=3, padx=200, pady=40)
            CmpNewB.grid(row=2, column=0, columnspan=3, padx=0, pady=7)
            CmpLstB.grid(row=5, column=0, columnspan=3, padx=0, pady=7)

        def openCdBlock():
            try:
                CRtW.destroy()
            except Exception:
                pass
            CCdBlkW = Tk()
            CCdBlkW.title("Sanatan Bank / Customer login / Dashboard / Block Card")
            CCdBlkW.wm_iconbitmap("SB_icon1.ico")
            CCdBlkW.geometry("700x420")

            def doBack():
                try:
                    CCdBlkW.destroy()
                except Exception:
                    pass
                try:
                    openCRt()
                except Exception:
                    pass

            def doBlock():
                # CredF = 1
                global cardNo,cardPin
                cardNo=BlkCdT.get()
                cardPin=BlkPnT.get()
                CredF = chkAcCred(cardNo,cardPin)
                if(CredF!=1):
                    messagebox.showerror("Card blocker",
                                         "Invalid credentials!")
                    return

                perfBlock(cardNo)
                messagebox.showinfo("Card blocker",
                                    "Card blocked successfully!")
                doBack()

            def showCrdLst():
                CrdLstW = Tk()
                CrdLstW.title("Sanatan Bank - Card List")
                CrdLstW.wm_iconbitmap("SB_icon1.ico")

                CrdChart = ttk.Treeview(CrdLstW)
                CrdChart['columns'] = ("c1", "c2", "c3", "c4")

                CrdChart.column("#0", width=0, stretch=NO)
                CrdChart.column("c1", anchor=W, width=180)
                CrdChart.column("c2", anchor=W, width=100)
                CrdChart.column("c3", anchor=CENTER, width=100)
                CrdChart.column("c4", anchor=W, width=100)

                CrdChart.heading("#0", text="", anchor=W)
                CrdChart.heading("c1", text="Card no.", anchor=CENTER)
                CrdChart.heading("c2", text="Card type", anchor=CENTER)
                CrdChart.heading("c3", text="Expiry Date", anchor=CENTER)
                CrdChart.heading("c4", text="Validity", anchor=CENTER)

                cursor = db.cursor()
                selQuery = "select cd_no, cd_typ, cd_exp from Card inner join Account   \
                            on Card.ac_no=Account.ac_no inner join Customer \
                            on Account.cust_id=Customer.cust_id where Account.cust_id=%s   \
                            order by cd_exp asc;"
                data=(custNumber, )
                cursor.execute(selQuery, data)
                records = cursor.fetchall()
                cursor.close()

                dt = date.today()
                for rowNum in records:
                    mrkCdTyp=''
                    if(rowNum[1]==1):
                        mrkCdTyp='MasterCard'
                    elif(rowNum[1]==2):
                        mrkCdTyp = 'VISA'
                    elif (rowNum[1] == 3):
                        mrkCdTyp = 'RuPay'
                    elif (rowNum[1] == 4):
                        mrkCdTyp = 'Others'
                    else:
                        mrkCdTyp = 'Unknown'

                    rkExpDt=str(rowNum[2])
                    if(rkExpDt=='2000-01-01'):
                        rkExpDt='Blocked'

                    skValid='Valid'
                    if (rowNum[2] < dt):
                        skValid='Invalid'
                    CrdChart.insert(parent='', index='end', iid=rowNum, text="",
                                    values=(str(rowNum[0]), mrkCdTyp, rkExpDt, skValid))

                CrdChart.grid(row=4, columnspan=4, sticky='nsew')

            Blk_backB = Button(CCdBlkW, text="←Back", padx=5, pady=5, command=doBack)
            BlkLbl = Label(CCdBlkW, text="Block Card", fg="green")
            BlkLbl.config(font=("Magneto Bold", 36))
            BlkCdT = Entry(CCdBlkW, width="32", bg="green", fg="white")
            BlkCdT.insert(0, "Card no.")
            BlkPnT = Entry(CCdBlkW, width="32", bg="green", fg="white")
            BlkPnT.insert(0, "Pin")
            BlockB = Button(CCdBlkW, text="Block", padx=20, command=doBlock)
            CrdLstB = Button(CCdBlkW, text="Show Cards", padx=10, command=showCrdLst)

            Blk_backB.grid(row=0, column=0, sticky=W, padx=10, pady=10)
            BlkLbl.grid(row=1, column=1, columnspan=1, sticky=W, padx=100, pady=25)
            BlkCdT.grid(row=4, column=1, padx=5, pady=8)
            BlkPnT.grid(row=5, column=1, padx=5, pady=8)
            BlockB.grid(row=6, column=1, columnspan=1, padx=20, pady=20)
            CrdLstB.grid(row=8, column=0, columnspan=1, sticky=W, padx=10, pady=10)


        def doLogout():
            try:
                CRtW.destroy()
            except Exception:
                pass
            try:
                openCLgin()
            except Exception:
                pass

        SpcLabel1 = Label(CRtW, text=SpcText)
        SpcLabel2 = Label(CRtW, text=SpcText)
        SpcLabel3 = Label(CRtW, text=SpcText)
        CDshLbl = Label(CRtW, text="Dashboard", fg="green")
        CDshLbl.config(font=("Magneto Bold", 36))
        CDtlB = Button(CRtW, text="My details", padx=44, command=openCDtl)
        CAtmCkB = Button(CRtW, text="Check ATM", padx=40, command=openAtmCk)
        CCmpB = Button(CRtW, text="Complaints", padx=40, command=openCmp)
        CCdBlkB = Button(CRtW, text="Block Card", padx=42, command=openCdBlock)
        LgoutB = Button(CRtW, text="Logout", padx=12, command=doLogout)

        LgoutB.grid(row=0, column=2, padx=0, pady=10)
        SpcLabel2.grid(row=1, column=0)
        CDshLbl.grid(row=1, column=1, padx=32, pady=50)
        SpcLabel1.grid(row=2, column=0)
        CDtlB.grid(row=2, column=1, padx=180, pady=5)
        CAtmCkB.grid(row=3, column=1, pady=5)
        CCmpB.grid(row=4, column=1, pady=5)
        CCdBlkB.grid(row=5, column=1, pady=5)

    CLlbl1 = Label(CLginW, text="Customer Login", fg="green")
    CLlbl1.config(font=("Magneto Bold", 36))
    CId = Entry(CLginW, width="32", bg="green", fg="white")
    CId.insert(0, "Customer ID")
    pw = Entry(CLginW, width="32", bg="green", fg="white")
    pw.insert(0, "Password")
    CLloginB = Button(CLginW, text="Login", padx=20, command=openCRt)
    SpcLabel1 = Label(CLginW, text=SpcText)
    SpcLabel2 = Label(CLginW, text=SpcText)
    SpcLabel3 = Label(CLginW, text=SpcText)

    SpcLabel2.grid(row=1, column=0)
    CLlbl1.grid(row=1, column=1, padx=32, pady=75)
    SpcLabel1.grid(row=2, column=0)
    CId.grid(row=2, column=1, pady=10)
    # SpcLabel2.grid(row=3, column=0)
    pw.grid(row=3, column=1, pady=10)
    CLloginB.grid(row=4, column=1, pady=10)


SpcText = "                                  "

MrkLabel1 = Label(root, text="Welcome to ATM!", fg="green")
MrkLabel1.config(font=("Magneto Bold", 36))
SpcLabel1 = Label(root, text=SpcText)
SpcLabel2 = Label(root, text=SpcText)
SpcLabel3 = Label(root, text=SpcText)
SpcLabel4 = Label(root, text=SpcText)
SpcLabel5 = Label(root, text=SpcText)
SpcLabel6 = Label(root, text=SpcText)
SpcLabel7 = Label(root, text=SpcText)
SpcLabel8 = Label(root, text=SpcText)
SpcLabel9 = Label(root, text=SpcText)
SpcLabel10 = Label(root, text=SpcText)
SpcLabel11 = Label(root, text=SpcText)
SpcLabel12 = Label(root, text=SpcText)
MrkButton1 = Button(root, text="Enter", padx=20, command=openATM)
MrkButton2 = Button(root, text="Customer login", command=openCLgin)
MrkButton3 = Button(root, text="Admin login", padx=9, command=openAdmin)
AtmNo = Entry(root, width="32", bg="green", fg="white")
AtmNo.insert(0, "ATM no.")
#WelcImg = ImageTk.PhotoImage(Image.open("d:/All that matters/All Adobe/Ai/MRK misc/Sanatan Bank/1x/SB_Welcome.png"))


#.grid(row=9, column=1, rowspan=2, sticky=S, pady=30)
SpcLabel1.grid(row=0, column=0)
SpcLabel2.grid(row=0, column=1)
MrkButton2.grid(row=0, column=2)

SpcLabel3.grid(row=1, column=0)
SpcLabel4.grid(row=1, column=1)
MrkButton3.grid(row=1, column=2)

SpcLabel11.grid(row=2, column=0)

SpcLabel5.grid(row=4, column=0)
MrkLabel1.grid(row=4, column=1, pady=50)
SpcLabel6.grid(row=3, column=2)

#SpcLabel12.grid(row=5, column=0)

SpcLabel7.grid(row=6, column=0)
AtmNo.grid(row=6, column=1)
SpcLabel8.grid(row=6, column=2)

SpcLabel9.grid(row=7, column=0)
MrkButton1.grid(row=7, column=1, pady=10)

SpcLabel10.grid(row=8, column=0, pady=32)


#root mainloop
mainloop()

#diconnect database
db.close()