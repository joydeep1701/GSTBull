from flask import redirect, render_template, request, url_for, flash
from sql import *
import ledgers
db = SQL("sqlite:///watchdog.db")

def getTaxrates():
    rates = db.execute("""SELECT * FROM taxrates""")
    return rates

def getSalesVoucherByInvNo(inv_no, company_id):
    master_table = str(company_id) + '_master_sales'
    rows = db.execute("""SELECT * FROM :table WHERE inv_no = :inv_no""",
                table=master_table,inv_no=inv_no)
    return rows

def createSalesVoucher(request, company_id):
    master_table = str(company_id) + '_master_sales'
    secondary_table = str(company_id) + '_secondary_sales'

    ledger_id = request.get('ledger_id')
    ledger_data = ledgers.getLedgerById(ledger_id, company_id)

    inv_no = request.get('inv_no')

    date = request.get('date').split('-')
    if len(date[0]) < 2:
        day = '0' + date[0]
    else:
        day = date[0]
    month = date[1]
    year = date[2]

    pos = ledger_data[0]['place_of_supply']
    un_reg = ledger_data[0]['unregistered']
    comp = ledger_data[0]['composition']
    sez = ledger_data[0]['sez']
    roundoff = request.get('roundoff')

    request = dict(request)

    # Check for duplicates
    if len(getSalesVoucherByInvNo(inv_no, company_id)) > 0:
        flash('Invoice Number must be unique','red')
        return

    # insert in master table
    row_id = db.execute("""INSERT INTO :table
            (ledger_id, day, month, year, inv_no, pos, comp, un_reg, sez, roundoff)
            VALUES
            (:ledger_id, :day, :month, :year, :inv_no, :pos, :comp, :un_reg, :sez, :roundoff)""",
            table=master_table, ledger_id=ledger_id, day=day, month=month,year=year,
            inv_no=inv_no, pos=pos, comp=comp, un_reg=un_reg, sez=sez, roundoff=roundoff)
    if row_id is None:
        flash('Server Error','red')
        return

    for rate,amount in zip(request.get('rate'),request.get('amount')):
        db.execute("""INSERT INTO :table
            (master_id, rate, amount) VALUES (:master_id, :rate, :amount)
        """,table=secondary_table,master_id=row_id,rate=rate,amount=amount)
    flash('Invoice Added','yellow')
