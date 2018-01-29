from flask import Flask, flash, redirect, render_template, request, session, url_for, Response, make_response
from flask_session import Session
from tempfile import gettempdir
import json
from helper import *
from sql import *
import authenticator
import ledgers
import vouchers
import gstr
import download
import drive
import data

app = Flask(__name__)
app.config["SESSION_FILE_DIR"] = "./session/"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///watchdog.db")

@app.route('/statecodes')
def dumpstatecodes():
    return json.dumps(state_codes)

@app.route('/ledger/add', methods=['GET','POST'])
@login_required
def addledger():
    if request.method == "GET":
        return render_template('add_ledger.html')
    else:
        ledgers.create(request.form, session['company_id'])
        return render_template('add_ledger.html')

@app.route('/ledger/search/<s>')
@login_required
def searchledger(s):
    return json.dumps(ledgers.search(s, session['company_id']))

@app.route('/ledger/data/<ledger_id>')
@login_required
def getledgerdata(ledger_id):
    return json.dumps(ledgers.getLedgerById(ledger_id, session['company_id'])[0])

@app.route('/ledger/edit/<name>', methods=['GET','POST'])
@login_required
def editledger(name):
    if request.method == "GET":
        return render_template('add_ledger.html',
            data=ledgers.search(s, session['company_id'])[0])
    else:
        ledgers.create(request.form, session['company_id'])
        return render_template('add_ledger.html')

@app.route('/sales/add', methods=['GET','POST'])
@login_required
def addsales():
    if request.method == 'POST':
        vouchers.createSalesVoucher((request.form), session['company_id'])
        #return str(dict(request.form))
    return render_template('add_voucher.html',voucher_type='Sales',
            taxrates=vouchers.getTaxrates())

@app.route('/sales/view')
@login_required
def viewsales():
    return render_template('search_voucher.html',view_type='sales')

@app.route('/sales/search/bymonth/<year>/<month>')
@login_required
def searchsalesbymonth(month,year):
    return json.dumps(vouchers.getSalesVoucherByMonth(month, year, session['company_id']))

@app.route('/sales/search/byinv/',methods=['GET','POST'])
@login_required
def getsalesvoucherdata():
    return json.dumps(
            vouchers.getSalesVoucherByInvNo(request.form.get('inv_no'),
                                            session['company_id'])
        )

@app.route('/sales/delete/<id>')
@login_required
def deletesales(id):
    vouchers.deleteSalesVoucher(id,  session['company_id'])
    return json.dumps({'status':'ok'})

@app.route('/purchase/add', methods=['GET','POST'])
@login_required
def addpurchase():
    if request.method == 'POST':
        vouchers.createPurchaseVoucher((request.form), session['company_id'])
        #return str(dict(request.form))
    return render_template('add_voucher.html',voucher_type='Purchase',
            taxrates=vouchers.getTaxrates())

@app.route('/purchase/view')
@login_required
def viewpurchase():
    return render_template('search_voucher.html',view_type='purchase')

@app.route('/purchase/search/bymonth/<year>/<month>')
@login_required
def searchpurchasebymonth(month,year):
    return json.dumps(vouchers.getPurchaseVoucherByMonth(month, year, session['company_id']))

@app.route('/purchase/search/byinv/',methods=['GET','POST'])
@login_required
def getpurchasevoucherdata():
    return json.dumps(
                vouchers.getPurchaseVoucherByInvNo(request.form.get('inv_no'),
                                                    session['company_id'])
        )

@app.route('/purchase/delete/<id>')
@login_required
def deletepurchase(id):
    vouchers.deletePurchaseVoucher(id,  session['company_id'])
    return json.dumps({'status':'ok'})


@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET','POST'])
def login():
    session.clear()
    if request.method == 'GET':
        return render_template('validate.html',
                authList=authenticator.authenticationList())
    else:
        if authenticator.setSessionData(request, session):
            return redirect(url_for('index'))

        return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        authenticator.createCompany(request.form)
        return 'Success'
    return render_template('register.html')

@app.route('/gstr/')
@login_required
def gstr_main():
    return render_template('gstr.html')

@app.route('/gstr1/<y>/<m>')
@login_required
def gstr3b(m,y):
    form_1 = gstr.GSTR1(m, y, session['company_id'])
    data = form_1.getData()
    #return json.dumps(data)
    return render_template('gstr1.html',data=data,year=y,month=m)

@app.route('/gstr3b/<y>/<m>')
@login_required
def gstr1(m,y):
    form_3b = gstr.GSTR3b(m,y,session['company_id'])
    data = form_3b.getData()
    #return json.dumps(data)
    return render_template('gstr3b.html',data=data,year=y,month=m)

@app.route('/download/gstr1/<y>/<m>')
@login_required
def downloadGSTR1(m,y):
    filename = session["company_name"].strip()

    gstr1 = download.GSTR1(m,y,session['company_id'])
    b2b = gstr1.downloadB2b()
        # We need to modify the response, so the first thing we
    # need to do is create a response out of the CSV string
    response = make_response(b2b)
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment;filename="+filename+" "+m+"_b2b"+".csv"
    return response

@app.route('/backup/',methods=["GET","POST"])
def backup_gdrive():
    backup = drive.GoogleDrive()
    if request.method == "GET":
        url = backup.OauthURL()
        return render_template('backup.html',url=url)
    else:
        backup.upload(request.form.get('key'))
        return "Success"

@app.route('/chart/<type>/<dur>')
@login_required
def chart_data(type,dur):
    chartdata = data.ChartData(session["company_id"])

    if dur == "monthlytotal":
        return json.dumps(chartdata.getMonthlyTotalData(type))
    if dur == "dailytotal":
        return json.dumps(chartdata.getDailyTotalData(type))
    if dur == "partytotal":
        return json.dumps(chartdata.getPartyTotalData(type))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
