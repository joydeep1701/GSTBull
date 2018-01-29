from sql import *
import ledgers
import vouchers

db = SQL("sqlite:///watchdog.db")

class ChartData():
    def __init__(self, company_id):
        self.company_id = company_id
        self.sales_view = str(company_id) + '_sales_view'
        self.sales_master = str(company_id) + '_master_sales'
        self.sales_secondary = str(company_id) + '_secondary_sales'
        self.purchase_view = str(company_id) + '_purchase_view'
        self.purchase_master = str(company_id) + '_master_purchase'
        self.purchase_secondary = str(company_id) + '_secondary_purchase'
        self.ledger_table = str(company_id) + '_ledgers'

    def getMonthlyTotalData(self, type):
        if type == "Pur":
            rows = db.execute("""
                SELECT month, sum(amount) AS amount FROM
                    (SELECT month, sum(invoice_value) AS amount
                    FROM :table GROUP BY inv_no)
                GROUP BY month
            """,table=self.purchase_view)
            return rows
        if type == "Sale":
            rows = db.execute("""
                SELECT month, sum(amount) AS amount FROM
                    (SELECT month, sum(invoice_value) AS amount
                    FROM :table GROUP BY inv_no)
                GROUP BY month
            """,table=self.sales_view)
            return rows
    def getDailyTotalData(self, type):
        if type == "Pur":
            rows = db.execute("""
                SELECT day,month, sum(amount) AS amount FROM
                    (SELECT day,month, sum(invoice_value) AS amount
                    FROM :table GROUP BY inv_no)
                GROUP BY day,month
            """,table=self.purchase_view)
            return rows
        if type == "Sale":
            rows = db.execute("""
                SELECT day,month, sum(amount) AS amount FROM
                    (SELECT day,month, sum(invoice_value) AS amount
                    FROM :table GROUP BY inv_no)
                GROUP BY day,month
            """,table=self.sales_view)
            return rows

    def getPartyTotalData(self, type):
        if type == "Pur":
            rows = db.execute("""
                SELECT name,ledger_id, sum(amount) AS amount FROM
                    (SELECT ledger_id,sum(invoice_value) AS amount
                    FROM :table GROUP BY inv_no)
                INNER JOIN
                    (SELECT id AS l_id, name, gstin FROM :ledgers)
                ON l_id=ledger_id
                GROUP BY ledger_id ORDER BY amount DESC
            """,table=self.purchase_view,ledgers=self.ledger_table)
        if type == "Sale":
            rows = db.execute("""
                SELECT name,ledger_id, sum(amount) AS amount FROM
                    (SELECT ledger_id,sum(invoice_value) AS amount
                    FROM :table GROUP BY inv_no)
                INNER JOIN
                    (SELECT id AS l_id, name, gstin FROM :ledgers)
                ON l_id=ledger_id
                GROUP BY ledger_id ORDER BY amount DESC
            """,table=self.sales_view,ledgers=self.ledger_table)

        return rows
