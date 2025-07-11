from flask import render_template
from flask import jsonify
from app.data_access.models import Func_Result

def json_result(result: Func_Result):
    if result.success:
        return (jsonify(result.result), 200) 
    else:
        if 'invalid_request' in result.result and result.result['invalid_request']:
            return (jsonify(result.result), 400)
        elif result.result and 'logged_in' in result.result and not result.result['logged_in']:
            return (jsonify(result.result), 401)
        return (jsonify(result.result), 500)

# page
def home_view(home_page: Func_Result):
    if not home_page.success or not home_page.result:
        return render_template('500.html'), 500
    return render_template('index.html', home_page=home_page.result)

def invalid_request_format_view():
    return json_result(Func_Result(False, {'error': 'Invalid request format.', 'invalid_request': True}))