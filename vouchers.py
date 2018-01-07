from sql import *
db = SQL("sqlite:///watchdog.db")

def getTaxrates():
    rates = db.execute("""SELECT * FROM taxrates""")
    return rates
