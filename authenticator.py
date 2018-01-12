from sql import *
db = SQL("sqlite:///watchdog.db")

def createMaster():
    db.execute("""CREATE TABLE 'master' ('id' INTEGER  PRIMARY KEY AUTOINCREMENT NOT NULL,
        'name' TEXT, 'dealer' TEXT, 'gstin' TEXT NOT NULL, 'turnover_pfy' TEXT,
         'turnover_q1' TEXT)""")

def createCompany(request):
    master_id = db.execute("""INSERT INTO :table
                    (name, dealer, gstin, turnover_pfy, turnover_q1) VALUES
                    (:name, :dealer, :gstin, :turnover_pfy, :turnover_q1)
                    """,table="master",name=request.get('name'),dealer=request.get('dealer'),
                        gstin=request.get('gstin'),
                        turnover_pfy=request.get('turnover_pfy'),
                        turnover_q1=request.get('turnover_q1'))
    # Create Ledgers
    ledgers = str(master_id) +'_ledgers'
    db.execute("""CREATE TABLE :table
        ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'name' TEXT, 'gstin' TEXT,
        'place_of_supply' TEXT,
        'unregistered' TEXT,
        'composition' TEXT, 'sez' TEXT)
        """,table=ledgers)
    # master purchase
    master_purchase = str(master_id) + '_master_purchase'
    db.execute("""CREATE TABLE :table
        ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'ledger_id' INTEGER,
        'day' TEXT, 'month' TEXT, 'year' TEXT, 'inv_no' TEXT, 'pos' TEXT,
        'comp' TEXT, 'un_reg' TEXT, 'sez' TEXT, 'roundoff' REAL)""",table=master_purchase)

    # secondary purchase
    secondary_purchase = str(master_id) + '_secondary_purchase'
    db.execute("""CREATE TABLE :table ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'master_id' INTEGER NOT NULL, 'rate' REAL NOT NULL, 'amount' REAL NOT NULL)
        """, table=secondary_purchase)
    # master sales
    master_sales = str(master_id) + '_master_sales'
    db.execute("""CREATE TABLE :table
        ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'ledger_id' INTEGER,
        'day' TEXT, 'month' TEXT, 'year' TEXT, 'inv_no' TEXT, 'pos' TEXT,
        'comp' TEXT, 'un_reg' TEXT, 'sez' TEXT, 'roundoff' REAL)""",table=master_sales)
    # secondary sales
    secondary_sales = str(master_id) + '_secondary_sales'
    db.execute("""CREATE TABLE :table ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'master_id' INTEGER NOT NULL, 'rate' REAL NOT NULL, 'amount' REAL NOT NULL)
        """,table=secondary_sales)
    # purchase_view
    purchase_view = str(master_id) + '_purchase_view'
    db.execute("""CREATE VIEW :purchase_view AS SELECT master_id,rate,
        SUM(amount) AS rate_amount, ledger_id, day, month, year,
        inv_no, pos, comp,un_reg,sez, roundoff, invoice_value,
        invoice_tax,invoice_taxable_value FROM :secondary_purchase
        INNER JOIN :master_purchase ON :master_purchase.id = master_id
        INNER JOIN ( SELECT master_id AS invoice_id,
        SUM(amount + amount*rate + roundoff) AS invoice_value,
        SUM(amount*rate) AS invoice_tax, SUM(amount)
        AS invoice_taxable_value FROM :secondary_purchase
        INNER JOIN :master_purchase ON :master_purchase.id = master_id
        GROUP BY master_id ) ON invoice_id = master_id GROUP BY master_id, rate
        """,purchase_view=purchase_view, master_purchase=master_purchase,
        secondary_purchase=secondary_purchase)
    # sales view
    sales_view = str(master_id) + '_sales_view'
    db.execute("""CREATE VIEW :sales_view AS SELECT master_id,rate,
        SUM(amount) AS rate_amount, ledger_id, day, month, year,
        inv_no, pos, comp,un_reg,sez, roundoff, invoice_value,
        invoice_tax,invoice_taxable_value FROM :secondary_sales
        INNER JOIN :master_sales ON :master_sales.id = master_id
        INNER JOIN ( SELECT master_id AS invoice_id,
        SUM(amount + amount*rate + roundoff) AS invoice_value,
        SUM(amount*rate) AS invoice_tax,
        SUM(amount) AS invoice_taxable_value FROM :secondary_sales
        INNER JOIN :master_sales ON :master_sales.id = master_id
        GROUP BY master_id ) ON invoice_id = master_id
        GROUP BY master_id, rate
        """, sales_view=sales_view, master_sales=master_sales,
        secondary_sales=secondary_sales)
    return

def authenticationList():
    authList = db.execute("SELECT * FROM 'master'");
    return authList

def getDetails(gstin):
    authList = db.execute("SELECT * FROM 'master' WHERE gstin=:gstin",
                        gstin=gstin);
    if len(authList) > 0:
        return authList

    return None

def setSessionData(request, session):
    data = getDetails(request.form.get('gstin'))
    if data is None:
        return False
    else:
        session['company_id'] = data[0]['id']
        session['company_name'] = data[0]['name']
        return True
