from flask import render_template
from flask import redirect
from flask import jsonify
from services import get_home_page_data
from models import Func_Result

def json_result(result: Func_Result):
    if result.success:
        return (jsonify(result.result), 200) 
    else:
        if result.result and 'logged_in' in result.result and not result.result['logged_in']:
            return (jsonify(result.result), 401)
        return (jsonify(result.result), 500)

# page
def home_view():
    home_page = get_home_page_data()
    if not home_page.success or not home_page.result:
        return render_template('505.html'), 505
    return render_template('index.html', home_page=home_page.result)