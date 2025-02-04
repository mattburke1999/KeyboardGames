from flask import render_template
from app.views import json_result
from app.models import Func_Result

# page
def skins_view(skins_page: Func_Result):
    if not skins_page.success:
        return render_template('505.html'), 505
    return render_template('skins.html', skins_page=skins_page.result)

# endpoint
def get_skin_view(data: dict):
    return json_result(Func_Result(True, {'html': render_template('skin_macros/skin_render.html', page=data['page'], skin=data['skin'])}))

# page 
def create_skin_view(create_skin: Func_Result):
    if not create_skin.success:
        return render_template('505.html'), 505
    return render_template('create_skin.html', new_skin_page = create_skin.result)

    