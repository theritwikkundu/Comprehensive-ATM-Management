create Table Customer_Ad(
c_adr varchar(25) PRIMARY KEY,
c_apc numeric(6) NOT NULL
);

create table Customer(
cust_id char(5) PRIMARY KEY,
cust_pw varchar(10) NOT NULL,
name_f varchar(15) NOT NULL,
name_l varchar(15) NOT NULL,
c_adr varchar(25) REFERENCES Customer_Ad(c_adr),
dob date NOT NULL,
sex char(1) NOT NULL
);

create table Customer_ph(
cust_id char(5) REFERENCES Customer(cust_id),
c_ph numeric(10) NOT NULL,
CONSTRAINT cp_pk PRIMARY KEY(cust_id,c_ph)
);

create table Admin(
ad_id char(5) PRIMARY KEY,
ad_pw varchar(10) NOT NULL
);

create table Branch_Ad(
br_adr varchar(25) PRIMARY KEY,
br_apc numeric(6) NOT NULL
);

create table Branch(
ifsc char(10) PRIMARY KEY,
br_bal numeric(9) NOT NULL,
br_adr varchar(25) REFERENCES Branch_Ad(br_adr)
);

create table Branch_ph(
ifsc char(10) REFERENCES Branch(ifsc),
br_ph numeric(10) NOT NULL,
CONSTRAINT bp_pk PRIMARY KEY(ifsc,br_ph)
);

create table Account(
ac_no numeric(16) PRIMARY KEY,
ac_typ numeric(1) NOT NULL,
ac_bal numeric(9) NOT NULL,
cust_id char(5) REFERENCES Customer(cust_id),
ifsc char(10) REFERENCES Branch(ifsc)
);

create table Card(
cd_no numeric(16) PRIMARY KEY,
cd_typ numeric(1) NOT NULL,
pin numeric(4) NOT NULL,
cd_exp date NOT NULL,
ac_no numeric(16) REFERENCES Account(ac_no)
);

create table ATM_Ad(
atm_adr varchar(25) PRIMARY KEY,
atm_apc numeric(6) NOT NULL
);

create table ATM(
atm_id char(10) PRIMARY KEY,
atm_tp varchar(15) NOT NULL,
atm_bl numeric(9) NOT NULL,
atm_adr varchar(25) REFERENCES ATM_Ad(atm_adr),
avg_w numeric(4) NOT NULL,
avg_d numeric(4) NOT NULL,
avg_t numeric(4) NOT NULL,
ifsc char(10) REFERENCES Branch(ifsc)
);

create table Deposit(
tr_id char(10) PRIMARY KEY,
tr_tp numeric(1) NOT NULL,
tr_dt datetime NOT NULL,
td_amt numeric(6) NOT NULL,
atm_id char(10) REFERENCES ATM(atm_id),
ac_no numeric(16) REFERENCES Account(ac_no)
);

create table Withdraw(
tr_id char(10) PRIMARY KEY,
tr_tp numeric(1) NOT NULL,
tr_dt datetime NOT NULL,
tw_amt numeric(6) NOT NULL,
atm_id char(10) REFERENCES ATM(atm_id),
ac_no numeric(16) REFERENCES Account(ac_no)
);

create table Security(
atm_id char(10) REFERENCES ATM(atm_id),
s_dt datetime NOT NULL,
frd varchar(50) NOT NULL,
res varchar(200) NULL,
CONSTRAINT se_pk PRIMARY KEY(atm_id,s_dt)
);

create table Complaint(
cl_id char(10) PRIMARY KEY,
descr varchar(200) NOT NULL,
cl_stat varchar(15) NULL,
cust_id char(5) REFERENCES Customer(cust_id),
atm_id char(10) REFERENCES ATM(atm_id)
);

create table Vendor(
comp varchar(20) PRIMARY KEY,
rvw numeric(2) NOT NULL,
no_ct numeric(5) NOT NULL 
);

create table Contract(
ct_id char(10) PRIMARY KEY,
ct_yr year NOT NULL,
amc numeric(7) NOT NULL,
warr numeric(2) NOT NULL,
atm_id char(10) REFERENCES ATM(atm_id),
comp varchar(20) REFERENCES Vendor(comp)
);

create table refill(
ifsc char(10) REFERENCES Branch(ifsc),
atm_id char(10) REFERENCES ATM(atm_id),
r_dt datetime NOT NULL,
r_amt numeric(9) NOT NULL,
CONSTRAINT re_pk PRIMARY KEY(ifsc,atm_id,r_dt)
);

create table monitor(
ad_id char(5) REFERENCES Admin(ad_id),
atm_id char(10) REFERENCES ATM(atm_id),
CONSTRAINT mo_pk PRIMARY KEY(ad_id,atm_id)
);

create table sign(
ad_id char(5) REFERENCES Admin(ad_id),
comp varchar(20) REFERENCES Vendor(comp),
CONSTRAINT si_pk PRIMARY KEY(ad_id,comp)
);