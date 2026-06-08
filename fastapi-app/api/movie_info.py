from typing import List, Optional

from fastapi import APIRouter
from pydantic import create_model
from tortoise.contrib.pydantic import pydantic_model_creator

from common.result import Result, PageInfo
from models import MovieInfo

router = APIRouter(prefix="/movieInfo")
# 创建 pydantic 只读模型
MovieInfoPydantic = pydantic_model_creator(MovieInfo)
# 自动生成所有字段为 Optional 的更新模型
MovieInfoCreatePydantic = create_model(
    "MovieInfoPydantic",
    **{
        name: (Optional[field.annotation], None)
        for name, field in MovieInfoPydantic.model_fields.items()
    }
)


# 新增
@router.post("/add")
async def add(movie_info_pydantic: MovieInfoCreatePydantic):
    create_data = movie_info_pydantic.model_dump(exclude_unset=True, exclude={'id'})
    await MovieInfo.create(**create_data)
    return Result.success()


# 修改
@router.put("/update")
async def update(movie_info_pydantic: MovieInfoCreatePydantic):
    update_data = movie_info_pydantic.model_dump(exclude_unset=True, exclude={"id"})
    await MovieInfo.filter(id=movie_info_pydantic.id).update(**update_data)
    return Result.success()


# 删除
@router.delete("/delete/{movie_info_id}")
async def delete(movie_info_id: int):
    await MovieInfo.filter(id=movie_info_id).delete()
    return Result.success()


# 批量删除
@router.delete("/deleteBatch")
async def delete_batch(ids: List[int]):
    await MovieInfo.filter(id__in=ids).delete()
    return Result.success()


# 单个查询
@router.get("/selectById/{movie_info_id}")
async def select_one(movie_info_id: int):
    movie_info = await MovieInfo.get_or_none(id=movie_info_id)
    return Result.success(movie_info)


# 查询所有
@router.get("/selectAll")
async def select_all(name: str = ""):
    movie_info_list = await MovieInfo.filter(name__contains=name)
    return Result.success(movie_info_list)


# 分页查询
@router.get("/selectPage")
async def select_page(name: str = "", pageNum: int = 1, pageSize: int = 10):
    # 同时获取分页数据和总数
    query = MovieInfo.filter(name__contains=name).prefetch_related('category')
    # 获取分页数据
    movie_info_list = await query.offset((pageNum - 1) * pageSize).limit(pageSize)
    movie_info_list = [
        {
            **MovieInfoPydantic.model_validate(movie_info).model_dump(),
            "categoryId": movie_info.category.id if movie_info.category else None,
            "categoryName": movie_info.category.name if movie_info.category else None,
        }

        for movie_info in movie_info_list
    ]
    # 计算总数
    total = await query.count()
    # 封装分页数据
    pageinfo = PageInfo(total=total, list=movie_info_list)
    return Result.success(pageinfo)