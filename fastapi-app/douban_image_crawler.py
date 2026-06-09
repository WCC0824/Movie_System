"""
豆瓣电影封面图片抓取脚本
从豆瓣网搜索电影，获取封面图片链接，更新到 movie_info 表的 img 字段
"""
import asyncio

import requests
from lxml import html
from tortoise import Tortoise, run_async

from settings import TORTOISE_ORM
from models import MovieInfo

# 请求头，模拟浏览器
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.douban.com/",
}

DOUBAN_SEARCH_URL = "https://www.douban.com/search"


def _search_douban_sync(movie_name):
    """同步方式搜索豆瓣"""
    search_params = {"q": movie_name, "cat": 1002}
    resp = requests.get(
        DOUBAN_SEARCH_URL,
        params=search_params,
        headers=HEADERS,
        timeout=15,
    )
    resp.encoding = "utf-8"
    return resp


async def get_movie_image(movie_name, max_retries=3):
    """
    通过豆瓣搜索电影名称，从搜索结果中获取封面图片链接
    返回图片 URL，失败返回 None
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"  搜索豆瓣: {movie_name}")

            # 使用 asyncio.to_thread 在线程池中运行同步 requests
            resp = await asyncio.to_thread(_search_douban_sync, movie_name)

            if resp.status_code != 200:
                print(f"  [WARN] 豆瓣搜索返回 {resp.status_code}")
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                continue

            doc = html.fromstring(resp.text)

            # 从搜索结果中直接提取图片链接（豆瓣搜索页面不受反爬限制）
            result_count = len(doc.xpath('//div[@class="result"]'))
            print(f"  result块数: {result_count}, 响应长度: {len(resp.text)}")

            if result_count == 0:
                print(f"  [FAIL] 豆瓣未搜索到结果: {movie_name}")
                return None

            img_srcs = doc.xpath('//div[@class="result"]//img/@src')
            if img_srcs:
                img_url = img_srcs[0].strip()
                print(f"  [OK] 获取封面成功: {movie_name}")
                return img_url

            print(f"  [FAIL] 搜索结果中未找到图片: {movie_name}")
            return None

        except requests.exceptions.Timeout:
            print(f"  [WARN] 超时 (尝试 {attempt}/{max_retries}): {movie_name}")
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
        except Exception as e:
            print(f"  [WARN] 请求失败 (尝试 {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
            else:
                print(f"  [FAIL] 放弃: {movie_name}")
                return None


async def update_all_movie_images(max_count=None):
    """
    遍历 movie_info 表中 img 为空的记录，通过豆瓣获取并更新封面
    max_count: 限制更新条数，None 表示全部
    """
    print("=" * 60)
    print("豆瓣电影封面抓取开始")
    print("=" * 60)

    # 查询所有电影记录（用豆瓣图片覆盖更新）
    from tortoise import connections

    conn = connections.get("default")
    # 获取所有电影，按 id 排序
    results = await conn.execute_query_dict(
        "SELECT id, name, img FROM movie_info ORDER BY id"
    )

    total = len(results)
    print(f"待处理电影总数: {total}")

    if max_count and max_count < total:
        results = results[:max_count]
        print(f"本次限制抓取: {max_count} 部")
    else:
        print(f"本次全部抓取: {total} 部")

    if not results:
        print("所有电影已有封面，无需更新。")
        return

    success_count = 0
    fail_count = 0

    for idx, row in enumerate(results, 1):
        movie_id = row["id"]
        movie_name = row["name"]
        print(f"\n[{idx}/{len(results)}] 处理: {movie_name} (ID={movie_id})")

        img_url = await get_movie_image(movie_name)
        if img_url:
            await conn.execute_query(
                "UPDATE movie_info SET img = %s WHERE id = %s",
                [img_url, movie_id]
            )
            success_count += 1
            print(f"  [UPDATE] 封面已更新: {movie_name}")
        else:
            fail_count += 1
            print(f"  [SKIP] 未能获取封面: {movie_name}")

        # 控制请求频率
        delay = 2 + (idx % 3)
        print(f"  等待 {delay}s ...")
        await asyncio.sleep(delay)

    print("\n" + "=" * 60)
    print(f"抓取完成！成功: {success_count}, 失败: {fail_count}")
    print("=" * 60)


async def main():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    try:
        # 全量更新所有电影的豆瓣封面
        await update_all_movie_images()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(main())