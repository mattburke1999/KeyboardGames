
from flask import session
import psycopg2 as pg
from app.data_access.models import Func_Result
from app.skins.data_access.models import Skin_Input
from app.skins.data_access.models import Skin_Type_With_Inputs
from app.skins.data_access.models import Create_Skin_Page
from app.skins.data_access.models import New_Skin_Type
from app.skins.data_access.models import New_Skin_Input
from app.skins.data_access.db import SkinDB

db = SkinDB()

def get_user_skin() -> Func_Result:
    user_id = session['user_id']
    try:
        user_skin = db.get_user_skin(user_id)
        return Func_Result(True, user_skin)
    except Exception as e:
        return Func_Result(False, {'error': str(e)})

def get_default_skin() -> Func_Result:
    try:
        default_skin = db.get_default_skin()
        return Func_Result(True, default_skin)
    except Exception as e:
        return Func_Result(False, {'error': str(e)})

def get_all_skins() -> Func_Result:
    user_id = session['user_id']
    try:
        all_skins = db.get_all_skins(user_id)
        return Func_Result(True, all_skins)
    except Exception as e:
        return Func_Result(False, {'error': str(e)})
    
def set_user_skin(data: dict[str, int]) -> Func_Result:
    user_id = session['user_id']
    skin_id = data['skin_id']
    set_skin = db.set_user_skin(user_id, skin_id)
    if not set_skin.success:
        return Func_Result(False, set_skin.result)
    return Func_Result(True, {'success': True})

def purchase_skin(data: dict[str, int]) -> Func_Result:
    user_id = session['user_id']
    skin_id = data['skin_id']
    skin_purchaseable = db.check_skin_purchaseable(user_id, skin_id)
    if not skin_purchaseable.success:
        return Func_Result(False, skin_purchaseable.result)
    if not skin_purchaseable.result:
        return Func_Result(False, {'error': 'Not enought points.'})
    purchase_skin = db.purchase_skin(user_id, skin_id)
    if not purchase_skin.success:
        return Func_Result(False, purchase_skin.result)
    return Func_Result(True, {'success': True})

def get_skin_types_with_inputs() -> Func_Result:
    skin_types = db.get_skin_type_with_inputs()
    if not skin_types.success:
        return Func_Result(False, skin_types.result)
    return Func_Result(True, [Skin_Type_With_Inputs(skin[0], skin[1], [skin[2]]) for skin in skin_types.result])

def get_skin_inputs() -> Func_Result:
    skin_inputs = db.get_skin_inputs()
    if not skin_inputs.success:
        return Func_Result(False, skin_inputs.result)
    return Func_Result(True, [Skin_Input(skin[0], skin[1]) for skin in skin_inputs.result])

def create_skin_page() -> Func_Result:
    skin_types = get_skin_types_with_inputs()
    if not skin_types.success: 
        return Func_Result(False, skin_types.result)
    skin_inputs = get_skin_inputs()
    if not skin_inputs.success:
        return Func_Result(False, skin_inputs.result)
    return Func_Result(True, Create_Skin_Page(skin_inputs.result, skin_types.result))

def add_new_skin_inputs(conn, new_skin: New_Skin_Type) -> Func_Result:
    for new_input in new_skin.new_inputs:
        input_id = db.get_skin_input_id_by_name(new_input)
        if not input_id.success:
            return Func_Result(False, input_id.result)
        if input_id.result:
            new_skin.inputs.append(input_id.result)
        else:
            new_input_result = db.new_skin_input(conn, new_input)
            if not new_input_result.success:
                conn.rollback()
                return Func_Result(False, new_input_result.result)
            new_skin.inputs.append(new_input_result.result)
    return Func_Result(True, {'success': True})

def add_new_skin_html(new_skin: New_Skin_Type) -> Func_Result:
    # later we will add some validation checking:
    # - if new_skin.inputs is empty, then skin.data is not in the html
    # - if new_skin.inputs is not empty, then find all skin.data.{input} and make sure any in html are in new_skin.inputs
    macro_name = new_skin.type.replace('-', '_')
    skin_html = "{% macro " + macro_name + "(page, skin) %}\n"
    skin_html += "\t" + new_skin.html + "\n" # type: ignore
    skin_html += "{% endmacro %}"
    # add to /templates/skin_macros/{macro_name}.html
    try:
        with open(f'flask_app/templates/skin_macros/skins/{macro_name}.html', 'w') as f:
            f.write(skin_html)
        return add_new_html_to_mapper(new_skin.type, macro_name)
    except:
        return Func_Result(False, {'error': 'Error writing skin html'})
    
def add_new_html_to_mapper(type, macro_name) -> Func_Result:
    try:
        with open('flask_app/templates/skin_macros/skin-mapper.html', 'r') as f:
            skin_mapper = f.read()
    except:
        return Func_Result(False, {'error': 'Error reading skin mapper'})
    macro_index = skin_mapper.find(macro_name)
    if macro_index == -1:
        end_if = skin_mapper.index('{% endif %}')
        if end_if == -1:
            return Func_Result(False, {'error': 'Error parsing skin mapper'})
        skin_mapper_pre = skin_mapper[:end_if]
        new_macro_mapper = "{% elif skin.type == '" + type + "' %}\n"
        new_macro_mapper += "\t\t{% from 'skin_macros/skins/" + macro_name + ".html' import " + macro_name + " %}\n"
        new_macro_mapper += "\t\t{{ " + macro_name + "(page, skin) }}\n"
        new_skin_mapper = skin_mapper_pre + new_macro_mapper + "    " + skin_mapper[end_if:]
        try:
            with open('flask_app/templates/skin_macros/skin-mapper.html', 'w') as f:
                f.write(new_skin_mapper)
            return Func_Result(True, {'success': True})
        except:
            return Func_Result(False, {'error': 'Error writing skin mapper'})
    return Func_Result(True, {'success': True})
    
def create_new_skin_type(data: dict) -> Func_Result:
    inputs = [int(x) for x in data['inputs']]
    new_skin = New_Skin_Type(data['skinType'], inputs, data['newInputs'], data['skinHtml'])
    skin_type_exists = db.check_skin_type_exists(new_skin.type)
    if not skin_type_exists.success:
        return Func_Result(False, skin_type_exists.result)
    if skin_type_exists.result:
        return Func_Result(False, {'error': 'Skin type already exists'})
    with db.connect_db() as conn:
        if len(new_skin.new_inputs) > 0:
            add_skin_inputs = add_new_skin_inputs(conn, new_skin)
            if not add_skin_inputs.success:
                return add_skin_inputs
        create_skin_result = db.create_skin_type(conn, new_skin)
        if not create_skin_result.success:
            conn.rollback()
            return Func_Result(False, create_skin_result.result)
    if new_skin.html:
        add_html = add_new_skin_html(new_skin)
        if not add_html.success:
            return add_html
    return Func_Result(True, {'success': True})

def add_skin(conn: pg.extensions.connection, name: str, new_skin_input: New_Skin_Input, i: int) -> Func_Result:
    skin_id_result = db.new_skin(conn, name, new_skin_input.points, new_skin_input.type_id)
    if not skin_id_result.success:
        conn.rollback()
        return Func_Result(False, skin_id_result.result)
    for input_name in new_skin_input.inputs:
        input_id = int(new_skin_input.inputs[input_name]['id'])  # type: ignore
        value = new_skin_input.inputs[input_name]['values'][i].strip() # type: ignore
        new_skin_values_result = db.new_skin_values(conn, skin_id_result.result, input_id, value)
        if not new_skin_values_result.success:
            conn.rollback()
            return Func_Result(False, new_skin_values_result.result)
    return Func_Result(True, None)
    
def add_skin_input_name_list(new_skin_input: New_Skin_Input) -> Func_Result:
    names = new_skin_input.names.split(',') # type: ignore
    with db.connect_db() as conn:
        for i in range(len(names)):
            name = names[i].strip()
            added_skin = add_skin(conn, name, new_skin_input, i)
            if not added_skin.success:
                return added_skin
        conn.commit()
    return Func_Result(True, {'success': True})

def add_skin_input_mapper_json(new_skin_input: New_Skin_Input) -> Func_Result:
    mapper_dict = json.loads(new_skin_input.mapper_json) # type: ignore
    values_dict = mapper_dict['ValuesMap']
    with db.connect_db() as conn:
        first_key = list(new_skin_input.inputs.keys())[0]
        for i in range(len(new_skin_input.inputs[first_key]['values'])): # type: ignore
            name = mapper_dict['NameFormatter']
            for input_name in new_skin_input.inputs:
                replace_str = '{' + input_name + '}'
                value = new_skin_input.inputs[input_name]['values'][i].strip() # type: ignore
                value_name = values_dict[value]
                name = name.replace(replace_str, value_name)
            added_skin = add_skin(conn, name, new_skin_input, i)
            if not added_skin.success:
                return added_skin
        conn.commit()
    return Func_Result(True, {'success': True})

def create_new_skin_input(data: dict) -> Func_Result:
    new_skin_input = New_Skin_Input(data['skinTypeId'], data['inputs'], data['points'], data.get('skinName', None), data.get('mapperJson',  None))
    input_names = list(new_skin_input.inputs.keys())
    if len(input_names) > 0:
        input_id_names = db.get_skin_input_list(input_names)
        if not input_id_names.success:
            return Func_Result(False, input_id_names.result)
        input_id_names = {input_id_name[1]: input_id_name[0] for input_id_name in input_id_names.result}
        new_skin_input.inputs = {input_name: {'values': new_skin_input.inputs[input_name].split(','), "id": input_id_names[input_name]} for input_name in input_names} # type: ignore
        if new_skin_input.names:
            return add_skin_input_name_list(new_skin_input)
        else:
            return add_skin_input_mapper_json(new_skin_input)
    return Func_Result(False, {'error': 'No inputs found'})