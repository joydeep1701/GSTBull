from flask import redirect, render_template, request, url_for, flash
from sql import *
import ledgers
db = SQL("sqlite:///watchdog.db")

def getTaxrates():
    rates = db.execute("""SELECT * FROM taxrates""")
    return rates

def getSalesVoucherByInvNo(inv_no, company_id):
    master_table = str(company_id) + '_master_sales'
    secondary_table = str(company_id) + '_secondary_sales'
    ledger_table = str(company_id) + '_ledgers'

    rows = db.execute("""SELECT * FROM :table
            INNER JOIN (SELECT id AS l_id,name,gstin FROM :ledger_table) ON l_id=ledger_id
            WHERE inv_no = :inv_no""",
            table=master_table,ledger_table=ledger_table,inv_no=inv_no)

    if rows:
        master_id = rows[0]['id']
        secondary_data = db.execute("""SELECT * FROM :table WHERE master_id=:master_id""",
                        table=secondary_table, master_id=master_id)

        voucher_data = dict(rows[0])
        voucher_data['tax_data'] = secondary_data

        return voucher_data
    return []

def getSalesVoucherByMonth(month, year, company_id):
    view_table = str(company_id) + '_sales_view'
    ledger_table = str(company_id) + '_ledgers'
    rows = db.execute("""SELECT * FROM :table
            INNER JOIN (SELECT id AS l_id,name FROM :ledger_table) ON l_id=ledger_id
            WHERE month=:month AND year=:year GROUP BY master_id
            ORDER BY inv_no ASC""", table=view_table,ledger_table=ledger_table,
            month=month, year=year)
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
def deleteSalesVoucher(voucher_id, company_id):
    master_table = str(company_id) + '_master_sales'
    secondary_table = str(company_id) + '_secondary_sales'

    db.execute("""DELETE FROM :table WHERE id=:id""",table=master_table,
        id=voucher_id)
    db.execute("""DELETE FROM :table WHERE master_id=:id""",table= secondary_table,
        id=voucher_id)
