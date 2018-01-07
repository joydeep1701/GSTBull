from flask import redirect, render_template, request, session, url_for
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("company_id") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

state_codes = {"35":"35-Andaman and Nicobar Islands","37":"37-Andhra Pradesh",
"12":"12-Arunachal Pradesh","18":"18-Assam","10":"10-Bihar","04":"04-Chandigarh",
"22":"22-Chhattisgarh","26":"26-Dadra and Nagar Haveli","25":"25-Daman and Diu",
"07":"07-Delhi","30":"30-Goa","24":"24-Gujarat","06":"06-Haryana",
"02":"02-Himachal Pradesh","01":"01-Jammu and Kashmir","20":"20-Jharkhand",
"29":"29-Karnataka","32":"32-Kerala","31":"31-Lakshadweep","23":"23-Madhya Pradesh",
"27":"27-Maharashtra","14":"14-Manipur","17":"17-Meghalaya","15":"15-Mizoram",
"13":"13-Nagaland","21":"21-Odisha","34":"34-Puducherry","03":"03-Punjab",
"08":"08-Rajasthan","11":"11-Sikkim","33":"33-Tamil Nadu","36":"36-Telangana",
"16":"16-Tripura","09":"09-Uttar Pradesh","05":"05-Uttarakhand",
"97":"97-Other Territory","19":"19-West Bengal"}
