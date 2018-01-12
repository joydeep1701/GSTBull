from flask import redirect, render_template, request, url_for, flash
from sql import *
import ledgers
import vouchers

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
    def table_b2b(self):
        data = {}
        summary_count = db.execute("""SELECT count(inv_no) AS no_records,
                            sum(invoice_value) AS invoice_value,
                            sum(invoice_taxable_value) AS taxable_value
                            FROM
                                (SELECT inv_no,invoice_value,invoice_taxable_value
                                FROM :table WHERE
                                un_reg='False'
                                AND month=:month AND year=:year
                                GROUP BY inv_no)
                            """, table=self.sales_view,
                            month=self.month, year=self.year)
        summary_tax_os = db.execute("""SELECT sum(rate*rate_amount) AS igst
                            FROM :table WHERE
                            un_reg='False'
                            AND pos != :hs
                            AND month=:month AND year=:year""",
                            table=self.sales_view, month=self.month, year=self.year, hs=19)
        summary_tax_hs = db.execute("""SELECT sum(rate*rate_amount/2) AS cgst,
                            sum(rate*rate_amount/2) AS sgst
                            FROM :table WHERE
                            un_reg='False'
                            AND pos = :hs
                            AND month=:month AND year=:year""",
                            table=self.sales_view, month=self.month, year=self.year, hs=19)

        reciever_wise = db.execute("""SELECT
                            name,gstin,sum(invoice_taxable_value) as taxable_value,
                            sum(invoice_tax) as tax,pos,count(inv_no) AS no_records
                            FROM
                                (SELECT name,gstin,inv_no,invoice_taxable_value,
                                invoice_tax,pos FROM :table
                                INNER JOIN
                                    (SELECT id AS l_id, name, gstin
                                    FROM :ledgers)
                                ON l_id=ledger_id
                                WHERE un_reg='False' AND month=:month AND year=:year
                                GROUP BY master_id)
                            GROUP BY gstin""",table=self.sales_view, ledgers=self.ledger_table,
                            month=self.month, year=self.year)
        #print(summary_count)
        data['summary'] = summary_count[0]
        data['summary']['igst'] = summary_tax_os[0]['igst']
        data['summary']['sgst'] = summary_tax_hs[0]['sgst']
        data['summary']['cgst'] = summary_tax_hs[0]['cgst']
        data['reciever_wise'] = reciever_wise
        #print(data)
        return encode(data)
    def table_b2cs(self):
        data = {}
        summary_count = db.execute("""SELECT count(inv_no) AS no_records,
                            sum(invoice_value) AS invoice_value,
                            sum(invoice_taxable_value) AS taxable_value
                            FROM
                                (SELECT inv_no,invoice_value,invoice_taxable_value
                                FROM :table WHERE
                                un_reg='True'
                                AND month=:month AND year=:year
                                GROUP BY inv_no)
                            """, table=self.sales_view,
                            month=self.month, year=self.year)
        summary_tax_os = db.execute("""SELECT sum(rate*rate_amount) AS igst
                            FROM :table WHERE
                            un_reg='True'
                            AND pos != :hs
                            AND month=:month AND year=:year""",
                            table=self.sales_view, month=self.month, year=self.year, hs=19)
        summary_tax_hs = db.execute("""SELECT sum(rate*rate_amount/2) AS cgst,
                            sum(rate*rate_amount/2) AS sgst
                            FROM :table WHERE
                            un_reg='True'
                            AND pos = :hs
                            AND month=:month AND year=:year""",
                            table=self.sales_view, month=self.month, year=self.year, hs=19)
        details = db.execute("""SELECT rate, sum(rate_amount) AS taxable_value,
                        sum(rate_amount*rate) AS tax, pos FROM :table
                        WHERE un_reg='True'
                        AND month=:month AND year=:year
                        GROUP BY pos,rate""",
                        table=self.sales_view, month=self.month, year=self.year)

        data['summary'] = summary_count[0]
        data['summary']['igst'] = summary_tax_os[0]['igst']
        data['summary']['sgst'] = summary_tax_hs[0]['sgst']
        data['summary']['cgst'] = summary_tax_hs[0]['cgst']
        data['details'] = details

        return encode(data)

    def table_8(self):
        data = {}
        summary = db.execute("""SELECT count(rate_amount) AS no_records,
                    sum(rate_amount) AS taxable_value FROM :table
                    WHERE rate='0.00'
                    AND month=:month AND year=:year""",
                    table=self.sales_view, month=self.month, year=self.year)

        hs_reg = db.execute("""SELECT sum(rate_amount) AS taxable_value
                    FROM :table WHERE rate='0.00'
                    AND pos=:hs AND un_reg='False'
                    AND month=:month AND year=:year""",
                    table=self.sales_view, month=self.month, year=self.year, hs=19)
        os_reg = db.execute("""SELECT sum(rate_amount) AS taxable_value
                    FROM :table WHERE rate='0.00'
                    AND pos!=:hs AND un_reg='False'
                    AND month=:month AND year=:year""",
                    table=self.sales_view, month=self.month, year=self.year, hs=19)
        hs_unreg = db.execute("""SELECT sum(rate_amount) AS taxable_value
                    FROM :table WHERE rate='0.00'
                    AND pos=:hs AND un_reg='True'
                    AND month=:month AND year=:year""",
                    table=self.sales_view, month=self.month, year=self.year, hs=19)
        os_unreg = db.execute("""SELECT sum(rate_amount) AS taxable_value
                    FROM :table WHERE rate='0.00'
                    AND pos!=:hs AND un_reg='True'
                    AND month=:month AND year=:year""",
                    table=self.sales_view, month=self.month, year=self.year, hs=19)


        data['summary'] = summary[0]
        data['details'] = {}
        data['details']['nil_rated'] = {'hs_reg':hs_reg[0]['taxable_value'],
                                        'os_reg':os_reg[0]['taxable_value'],
                                        'hs_unreg':hs_unreg[0]['taxable_value'],
                                        'os_unreg':os_unreg[0]['taxable_value'],
                                        }


        return encode(data)
    def getData(self):
        data = {'b2b':self.table_b2b(),
                'b2cs':self.table_b2cs(),
                'table_8':self.table_8()}
        return data

class GSTR3b():
    def __init__(self, month, year, company_id):
        self.company_id = company_id
        self.month = month
        self.year = year
        self.sales_view = str(company_id) + '_sales_view'
        self.sales_master = str(company_id) + '_master_sales'
        self.sales_secondary = str(company_id) + '_secondary_sales'
        self.purchase_view = str(company_id) + '_purchase_view'
        self.purchase_master = str(company_id) + '_master_purchase'
        self.purchase_secondary = str(company_id) + '_secondary_purchase'
        self.ledger_table = str(company_id) + '_ledgers'


    def table3_1(self):
        data = {}
        rowa_hs = db.execute("""SELECT sum(rate_amount) AS taxable_value,
                    sum(rate_amount*rate/2) AS cgst, sum(rate_amount*rate/2) AS sgst
                    FROM :table
                    WHERE sez='False' AND rate !='0.0'
                    AND pos = :hs
                    AND month=:month AND year=:year""",
                    table=self.sales_view, month=self.month, year=self.year, hs=19)

        rowa_os = db.execute("""SELECT sum(rate_amount) AS taxable_value,
                    sum(rate_amount*rate) AS igst
                    FROM :table
                    WHERE sez='False' AND rate !='0.0'
                    AND pos != :hs
                    AND month=:month AND year=:year""",
                    table=self.sales_view, month=self.month, year=self.year, hs=19)
        #print(rowa_hs,rowa_os)

        data['row_a'] = {'taxable_value':
                            encode(rowa_os[0]['taxable_value'])
                            +
                            encode(rowa_hs[0]['taxable_value']) ,
                        'igst':rowa_os[0]['igst'],
                        'cgst':rowa_hs[0]['cgst'] ,
                        'sgst':rowa_hs[0]['sgst'] ,
                        }



        rowb = db.execute("""SELECT sum(rate_amount) AS taxable_value,
                    sum(rate_amount*rate) AS igst FROM :table WHERE sez='True'
                    AND month=:month AND year=:year""",
                    table=self.sales_view, month=self.month, year=self.year)
        data['row_b'] = {
                'taxable_value':
                    rowb[0]['taxable_value'] ,
                 'igst': rowb[0]['igst']}
        rowc = db.execute("""SELECT sum(rate_amount) AS taxable_value
                        FROM :table WHERE sez='False' AND rate='0.0'
                        AND month=:month AND year=:year""",
                        table=self.sales_view, month=self.month, year=self.year)
        data['row_c'] = {'taxable_value': rowc[0]['taxable_value']}

        return encode(data)

    def table3_2(self):
        data = {}
        row_ur = db.execute("""SELECT
                    pos, sum(rate_amount) AS taxable_value,
                    sum(rate_amount*rate) AS igst FROM :table
                    WHERE pos != :hs
                    AND un_reg='True' AND comp='False' AND sez='False'
                    AND rate !='0.0'
                    AND month=:month AND year=:year
                    GROUP BY pos
                    """,
                    table=self.sales_view, month=self.month, year=self.year, hs=19)
        data['row_ur'] = row_ur
        row_cmp = db.execute("""SELECT
                    pos, sum(rate_amount) AS taxable_value,
                    sum(rate_amount*rate) AS igst FROM :table
                    WHERE pos != :hs
                    AND un_reg='False' AND comp='True' AND sez='False'
                    AND rate !='0.0'
                    AND month=:month AND year=:year
                    GROUP BY pos
                    """,
                    table=self.sales_view, month=self.month, year=self.year, hs=19)
        data['row_cmp'] = row_cmp
        return encode(data)

    def table4(self):
        data = {}
        row_5_os = db.execute("""SELECT sum(rate_amount*rate) AS igst
                    FROM :table WHERE
                    sez='False' AND comp='False' AND rate != '0.00' AND pos != :hs
                    AND month=:month AND year=:year""",
                    table=self.purchase_view, month=self.month, year=self.year, hs=19)
        row_5_hs = db.execute("""SELECT sum(rate_amount*rate/2) AS cgst,
                    sum(rate_amount*rate/2) AS sgst
                    FROM :table WHERE
                    sez='False' AND comp='False' AND rate != '0.00' AND pos = :hs
                    AND month=:month AND year=:year""",
                    table=self.purchase_view, month=self.month, year=self.year, hs=19)
        data.update(row_5_os[0])
        data.update(row_5_hs[0])
        return encode(data)
    def table5(self):
        data = {}
        row_hs = db.execute("""SELECT sum(rate_amount) AS intra_state_value
                    FROM :table WHERE sez='False' AND pos=:hs
                    AND (rate = '0.00' OR comp='True' )
                    AND month=:month AND year=:year""",
                    table=self.purchase_view, month=self.month, year=self.year, hs=19)
        row_os = db.execute("""SELECT sum(rate_amount) AS inter_state_value
                    FROM :table WHERE sez='False' AND pos!=:hs
                    AND (rate = '0.00' OR comp='True' )
                    AND month=:month AND year=:year""",
                    table=self.purchase_view, month=self.month, year=self.year, hs=19)
        data.update(row_os[0])
        data.update(row_hs[0])
        return encode(data)
    def getData(self):
        data = {'table3_1':self.table3_1(),
                'table3_2':self.table3_2(),
                'table4'  :self.table4(),
                'table5'  :self.table5(),}
        return encode(data)
