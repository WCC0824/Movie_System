import re
from pathlib import Path

from get_db_info import get_table_info

model_content_template = """
class {}(Model):
    id = fields.IntField(pk=True, null=False)
"""


def snake_to_pascal(snake_str: str) -> str:
    """下划线转大驼峰（首字母大写）"""
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)


def snake_to_camel(s: str) -> str:
    """下划线转小驼峰（首字母小写）"""
    parts = s.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


def covert_sql_tortoise(data_type):
    if data_type == 'int':
        return "IntField"
    elif data_type == 'bigint':
        return "BigIntField"
    elif data_type == 'float' or data_type == 'double':
        return "FloatField"
    elif data_type == 'boolean' or data_type == 'tinyint':
        return "BooleanField"
    elif data_type == 'varchar':
        return "CharField"
    elif data_type == 'datetime' or data_type == 'date' or data_type == 'timestamp':
        return "DateTimeField"


# 定义orm模型
def write_model_file(database_name: str, table_name: str):
    model_pascal_name = snake_to_pascal(table_name)
    model_camel_name = snake_to_camel(table_name)
    # 查询数据库表信息和字段信息
    table_info = get_table_info(database_name, table_name)
    table_columns = table_info['columns']
    column_str = ""
    for column in table_columns:
        column_name = column['column_name']
        if column_name == "id":
            continue
        column_comment = column['column_comment']
        tortoise_type = covert_sql_tortoise(column['data_type'])
        max_length_str = ""
        if tortoise_type == 'CharField':
            max_length_str = "max_length=255, "
        column_str += f"""    {column_name} = fields.{tortoise_type}({max_length_str}null=True)\n"""
    # 追加内容
    with open("../models.py", "a", encoding="utf-8") as f:
        model_content = model_content_template.format(model_pascal_name)
        model_content += column_str
        model_content += f"""\n    class Meta:\n""" + f"        table = '{table_name}'\n\n"
        f.writelines(model_content)

    print(f"追加生成Model<{model_pascal_name}>成功")


# 生成api接口
def write_api_file(table_name):
    model_pascal_name = snake_to_pascal(table_name)
    project_dir = Path(__file__).parent.parent
    admin_api_path = project_dir / 'api' / 'admin.py'
    current_api_path = project_dir / 'api' / f'{table_name}.py'
    content = admin_api_path.read_text(encoding="utf-8")
    api_content = (content.replace("Admin", model_pascal_name)
                   .replace("admin", table_name))
    # 生成api文件
    with open(current_api_path, "w", encoding="utf-8") as f:
        f.writelines(api_content)

    print(f"生成API接口<api/{table_name}.py>成功")


# 生成vue文件
def copy_vue_file(table_name: str):
    model_pascal_name = snake_to_pascal(table_name)
    model_camel_name = snake_to_camel(table_name)
    # 获取当前脚本所在目录: fastapi/utils/
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    vue_manager_path = project_root / "vue" / "src" / "views" / "manager"
    src_file = vue_manager_path / "Admin.vue"
    dist_file = vue_manager_path / (model_pascal_name + ".vue")
    # 检查源目录是否存在
    if not src_file.exists():
        raise FileNotFoundError(f"Admin文件不存在: {src_file}")
    # 读取文件内容
    content = src_file.read_text(encoding="utf-8")
    # 替换单词边界上的 "Admin"
    content = re.sub(r'\bAdmin\b', model_pascal_name, content)
    # 替换单词边界上的 "admin"
    content = re.sub(r'\badmin\b', model_camel_name, content)
    dist_file.write_text(content, encoding="utf-8")
    print(f"{model_pascal_name}.vue生成成功")


if __name__ == "__main__":
    # 修改下方的数据库和表
    database = "student_system"
    table = "clazz"

    write_model_file(database, table)
    write_api_file(table)
    copy_vue_file(table)
