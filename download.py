from flask import redirect, render_template, request, url_for, flash
from sql import *
import ledgers
import vouchers
from helper import state_codes

db = SQL("sqlite:///watchdog.db")

def encode(value):
    if value is None:
        return 0.00
    if isinstance(value, dict):
        for key in value.keys():
            value[key] = encode(value[key])
    return value

class GSTR1():
    def __init__(self, month, year, company_id):
        self.company_id = company_id
        self.month = month
        self.year = year
        self.sales_view = str(company_id) + '_sales_view'
        self.sales_master = str(company_id) + '_master_sales'
        self.sales_secondary = str(company_id) + '_secondary_sales'
        self.ledger_table = str(company_id) + '_ledgers'

    def getB2BVouchers(self):
        rows = db.execute("""SELECT name, inv_no, day, month, year, gstin,
            invoice_value, pos, rate, SUM(rate_amount) AS amount, comp, sez, un_reg
            FROM :table
            INNER JOIN
                (SELECT id AS l_id,name,gstin FROM :ledger_table)
            ON l_id=ledger_id
            WHERE un_reg='False' AND month=:month AND year=:year
            GROUP BY master_id, rate
            ORDER BY inv_no ASC""",table=self.sales_view, ledger_table=self.ledger_table,
            month=self.month, year=self.year)
        return rows

    def downloadB2b(self):
        csv = "GSTIN/UIN of Recipient,Invoice Number,Invoice date,Invoice Value,Place Of Supply,Reverse Charge,Invoice Type,E-Commerce GSTIN,Rate,Taxable Value,Cess Amount"
        rows = self.getB2BVouchers()
        for row in rows:
            if row["sez"] == "True":
                continue

            csv += "\n"
            if len(str(row["day"])) == 1:
                row["day"] = "0"+str(row["day"])
            csv += row["gstin"]+","
            csv += row["inv_no"]+","
            csv += str(row["day"]) + "-" + row["month"] + "-" + str(row["year"])+","
            csv += str("%0.2f"%round(row["invoice_value"]))+","
            csv += state_codes[row["pos"]]+","
            csv += "N," #Reverse Charge
            csv += "Regular," #Invoice Type
            csv += "," #E-Commerce
            csv += str("%0.1f"%(row["rate"]*100))+","
            csv += str("%0.2f"%row["amount"])+","

        return csv
