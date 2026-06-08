"""
TMDB 电影数据抓取脚本
从 TMDB 抓取 top -rated 电影数据，存入 book_system 数据库
- movie_info 表：存储电影基本信息
- category 表：存储电影类型/分类
"""
import asyncio
import re
import time

import requests
from lxml import html
from tortoise import Tortoise, run_async

from settings import TORTOISE_ORM
from models import Category, MovieInfo

TMDB_TOP_URL1 = "https://www.themoviedb.org/movie/top-rated"
TMDB_TOP_URL2 = "https://www.themoviedb.org/discover/movie/items"
TMDB_BASE_URL = "https://www.themoviedb.org"
PAGE_COUNT = 5  # 抓取页数（每页约 20 部）


def get_movie_years(movie_years):
    movie_year = movie_years[0].strip() if movie_years else ""
    return movie_year.replace("(", "").replace(")", "")


def get_movie_publish_date(movie_release_dates):
    movie_date = movie_release_dates[0].strip() if movie_release_dates else ""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", movie_date)
    return match.group() if match else ""


def get_movie_cost_time(movie_durations):
    movie_cost_time = movie_durations[0].strip() if movie_durations else ""
    h_res = re.search(r"(\d+)h", movie_cost_time)
    m_res = re.search(r"(\d+)m", movie_cost_time)
    h = int(h_res.group(1)) if h_res else 0
    m = int(m_res.group(1)) if m_res else 0
    return f"{h * 60 + m}m"


def get_movie_info(movie_info_url, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            movie_response = requests.get(movie_info_url, timeout=(10, 120))
            print(f"{movie_info_url}, 获取电影详情数据 ...")
            movie_doc = html.fromstring(movie_response.text)

            movie_names = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/a/text()")
            movie_years = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/span/text()")
            movie_release_dates = movie_doc.xpath(
                '//*[@id="original_header"]/div[2]/section/div[1]/div/span[@class="release"]/text()'
            )
            movie_types = movie_doc.xpath(
                '//*[@id="original_header"]/div[2]/section/div[1]/div/span[@class="genres"]/a/text()'
            )
            movie_durations = movie_doc.xpath(
                '//*[@id="original_header"]/div[2]/section/div[1]/div/span[@class="runtime"]/text()'
            )
            movie_ratings = movie_doc.xpath(
                '//*[@id="consensus_pill"]/div/div[1]/div/div/@data-percent'
            )
            movie_languages = movie_doc.xpath(
                '//*[@id="media_v4"]/div/div/div[2]/div/section/div[1]/div/section[1]/p[3]/text()'
            )
            movie_directors = movie_doc.xpath(
                '//*[@id="original_header"]/div[2]/section/div[3]/ol/li/p[1]/a/text()'
            )
            movie_Starrings = movie_doc.xpath(
                '//*[@id="cast_scroller"]/ol/li/p[1]/a/text()'
            )
            movie_slogans = movie_doc.xpath(
                '//*[@id="original_header"]/div[2]/section/div[3]/h3[1]/text()'
            )
            movie_Introductions = movie_doc.xpath(
                '//*[@id="original_header"]/div[2]/section/div[3]/div/p/text()'
            )
            movie_images = movie_doc.xpath(
                '//*[@id="original_header"]/div[1]/div/div[1]/div/img/@src'
            )

            movie_info = {
                "name": movie_names[0].strip() if movie_names else "",
                "img": movie_images[0].strip() if movie_images else "",
                "year": get_movie_years(movie_years),
                "release_date": get_movie_publish_date(movie_release_dates),
                "genres": ",".join(movie_types).strip() if movie_types else "",
                "duration": get_movie_cost_time(movie_durations),
                "rating": movie_ratings[0].strip() if movie_ratings else "",
                "language": movie_languages[0].strip() if movie_languages else "",
                "director": ",".join(movie_directors).strip() if movie_directors else "",
                "actors": ",".join(movie_Starrings).strip() if movie_Starrings else "",
                "tagline": movie_slogans[0].strip() if movie_slogans else "",
                "introduction": movie_Introductions[0].strip() if movie_Introductions else "",
                # 取第一个类型作为主分类
                "primary_genre": movie_types[0].strip() if movie_types else "",
            }
            print(f"[OK] {movie_info['name']}")
            return movie_info
        except Exception as e:
            print(f"[WARN] 请求失败 (尝试 {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
            else:
                print(f"[FAIL] 放弃: {movie_info_url}")
                return None


async def ensure_category(genre_name):
    """确保分类存在，返回 category 对象"""
    if not genre_name:
        return None
    category, _ = await Category.get_or_create(name=genre_name)
    return category


async def save_movie_to_db(movie_data):
    """将单条电影数据写入数据库"""
    # 确保分类存在
    category = await ensure_category(movie_data["primary_genre"])

    # 检查是否已存在（按名称去重）
    existing = await MovieInfo.filter(name=movie_data["name"]).first()
    if existing:
        if not existing.img and movie_data.get("img"):
            # 已有记录但缺封面，补充更新
            existing.img = movie_data["img"]
            await existing.save()
            print(f"  [UPDATE] 更新封面: {movie_data['name']}")
        else:
            print(f"  [SKIP] 已存在: {movie_data['name']}")
        return

    await MovieInfo.create(
        name=movie_data["name"],
        img=movie_data.get("img", ""),
        year=movie_data["year"],
        release_date=movie_data["release_date"],
        genres=movie_data["genres"],
        duration=movie_data["duration"],
        rating=movie_data["rating"],
        language=movie_data["language"],
        director=movie_data["director"],
        actors=movie_data["actors"],
        tagline=movie_data["tagline"],
        introduction=movie_data["introduction"],
        category=category,
    )
    print(f"  [OK] 已入库: {movie_data['name']}{' (有封面)' if movie_data.get('img') else ''}")


async def crawl_and_save():
    """主流程：抓取 TMDB 数据并写入数据库"""
    print("=" * 60)
    print("TMDB 电影数据抓取开始")
    print("=" * 60)

    for page_num in range(1, PAGE_COUNT + 1):
        print(f"\n--- 第 {page_num} 页 ---")

        # 请求列表页
        for attempt in range(1, 4):
            try:
                if page_num == 1:
                    print(f"GET {TMDB_TOP_URL1}")
                    response = requests.get(TMDB_TOP_URL1, timeout=60)
                else:
                    print(f"POST {TMDB_TOP_URL2} (page={page_num})")
                    response = requests.post(
                        TMDB_TOP_URL2,
                        data=f"page={page_num}&sort_by=vote_average.desc&vote_count.gte=300",
                        timeout=20,
                    )
                break
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                print(f"[WARN] 列表页超时 (尝试 {attempt}/3): {e}")
                if attempt < 3:
                    time.sleep(2 ** attempt)
                else:
                    response = None

        if response is None:
            print(f"[SKIP] 第 {page_num} 页")
            continue

        # 解析电影列表
        document = html.fromstring(response.text)
        movie_list = document.xpath(
            f"//*[@id='page_{page_num}']//div[contains(@class, 'comp:poster-card')]"
        )

        for movie in movie_list:
            movie_urls = movie.xpath(
                ".//a[contains(@class, 'hover:text-tmdb-light-blue')]/@href"
            )
            if not movie_urls:
                continue

            movie_info_url = TMDB_BASE_URL + movie_urls[0]
            movie_data = get_movie_info(movie_info_url)
            if movie_data:
                await save_movie_to_db(movie_data)

            # 控制请求频率
            time.sleep(1)

    print("\n" + "=" * 60)
    print("抓取完成！")
    print("=" * 60)


async def main():
    # 初始化 Tortoise ORM
    await Tortoise.init(config=TORTOISE_ORM)
    # 确保表结构存在
    await Tortoise.generate_schemas()
    try:
        await crawl_and_save()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(main())