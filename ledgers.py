from flask import redirect, render_template, request, url_for, flash
from sql import *
db = SQL("sqlite:///watchdog.db")


def create(request, company_id):
    issez = str(request.get('sez') is not None)
    isur = str(request.get('ur') is not None)
    iscmp = str(request.get('cmp') is not None)

    table_name = str(company_id) + '_ledgers'
    similar_named_co = db.execute("""SELECT * FROM :table WHERE
                        name = :ledger_name""",
                        table=table_name,ledger_name=request.get('ledger_name'))
    if len(similar_named_co) > 0:
        flash('Duplicate Entry! ' + request.get('ledger_name'), 'red')
        return
    else:
        row = db.execute("""INSERT INTO :table
                    (name, gstin, place_of_supply, unregistered, composition, sez)
                    VALUES (:name, :gstin, :pos, :ur, :comp, :sez)
                    """, table=table_name,name=request.get('ledger_name'),
                        gstin=request.get('gstin'), pos=request.get('pos'),
                        ur=isur,comp=iscmp,sez=issez)
        if row:
            flash('Ledger Created: ' + request.get('ledger_name'),'green')
            return
        flash('Internal Server Error','red')

    return str(dict(request))

def search(s, company_id):
    table_name = str(company_id) + '_ledgers'
    search = '%'+s+'%'
    rows = db.execute("""SELECT * FROM :table WHERE name LIKE :search""",
                    table=table_name,search=search)
    return rows
