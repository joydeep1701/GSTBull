from sql import *
db = SQL("sqlite:///watchdog.db")


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
