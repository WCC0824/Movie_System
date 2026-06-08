import aiomysql
import asyncio


async def verify():
    conn = await aiomysql.connect(
        host='localhost', port=3306, user='root',
        password='123456', db='book_system', charset='utf8mb4'
    )
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # category 表
        await cursor.execute('SELECT COUNT(*) as cnt FROM category')
        row = await cursor.fetchone()
        print('category 表总记录数:', row['cnt'])

        await cursor.execute('SELECT * FROM category ORDER BY id')
        rows = await cursor.fetchall()
        print('category 数据:')
        for r in rows:
            print('  id=%d, name=%s' % (r['id'], r['name']))

        print()

        # movie_info 表
        await cursor.execute('SELECT COUNT(*) as cnt FROM movie_info')
        row = await cursor.fetchone()
        print('movie_info 表总记录数:', row['cnt'])

        await cursor.execute(
            'SELECT id, name, year, genres, rating, category_id '
            'FROM movie_info ORDER BY id LIMIT 10'
        )
        rows = await cursor.fetchall()
        print('前 10 条电影数据:')
        for r in rows:
            print('  id=%d, name=%s, year=%s, genres=%s, rating=%s, category_id=%s' % (
                r['id'], r['name'], r['year'], r['genres'], r['rating'], r['category_id']
            ))

    conn.close()


asyncio.run(verify())