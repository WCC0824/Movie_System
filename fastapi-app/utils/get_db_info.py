import asyncio

import aiomysql


def get_table_info(database: str = "", table_name: str = ""):
    async def async_get_table_info():
        # 1. 创建连接
        conn = await aiomysql.connect(host="localhost", port=3306, user="root",
                                      password="123456", db=database, charset='utf8mb4')

        # 2. 获取表注释
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 查询表注释
            await cursor.execute("""
                    SELECT TABLE_COMMENT FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """, (database, table_name))
            table_comment = (await cursor.fetchone() or {}).get('TABLE_COMMENT', '')

            # 获取字段信息
            await cursor.execute("""
                    SELECT COLUMN_NAME, COLUMN_COMMENT, DATA_TYPE, COLUMN_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION
                """, (database, table_name))

            columns = await cursor.fetchall()

            # 4. 整理返回结果
            return {
                'table_name': table_name,
                'table_comment': table_comment,
                'columns': [
                    {
                        'column_name': col['COLUMN_NAME'],
                        'column_comment': col['COLUMN_COMMENT'] or '',
                        'data_type': col['DATA_TYPE'],
                        'column_type': col['COLUMN_TYPE']
                    }
                    for col in columns
                ]
            }

    return asyncio.run(async_get_table_info())

