import aiomysql, asyncio

async def run():
    conn = await aiomysql.connect(host='localhost', port=3306, user='root', password='123456', db='book_system', charset='utf8mb4')
    async with conn.cursor() as cursor:
        await cursor.execute("ALTER TABLE movie_info ADD COLUMN img VARCHAR(500) NULL COMMENT '封面图片链接'")
        print('img 字段添加成功')
    conn.close()
asyncio.run(run())