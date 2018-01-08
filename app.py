from flask import Flask, flash, redirect, render_template, request, session, url_for, Response, make_response
from flask_session import Session
from tempfile import gettempdir
import json
from helper import *
from sql import *
import authenticator
import ledgers
import vouchers

app = Flask(__name__)
app.config["SESSION_FILE_DIR"] = gettempdir()
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
@app.route('/purchase/add', methods=['GET','POST'])
@login_required
def addpurchase():
    if request.method == 'POST':
        vouchers.createSalesVoucher((request.form), session['company_id'])
        return str(dict(request.form))
    return render_template('add_voucher.html',voucher_type='Purchase',
            taxrates=vouchers.getTaxrates())
@app.route('/sales/data/<inv_no>')
@login_required
def getsalesvoucherdata(inv_no):
    return json.dumps(vouchers.getSalesVoucherByInvNo(inv_no, session['company_id']))

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

@app.route('/gstr3b/<m>')
@login_required
def gstr3b(m):
    return render_template('gstr3b.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
