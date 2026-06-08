from typing import List, Optional

from fastapi import APIRouter
from pydantic import create_model
from tortoise.contrib.pydantic import pydantic_model_creator

from common.exception_handler import CustomException
from common.result import Result, PageInfo
from models import Movies

router = APIRouter(prefix="/movies")
# 创建 pydantic 只读模型
MoviesPydantic = pydantic_model_creator(Movies)
# 自动生成所有字段为 Optional 的更新模型
MoviesCreatePydantic = create_model(
    "MoviesPydantic",
    **{
        name: (Optional[field.annotation], None)
        for name, field in MoviesPydantic.model_fields.items()
    }
)


# 新增
@router.post("/add")
async def add(movies_create_pydantic : MoviesCreatePydantic):
    
    create_data = movies_create_pydantic.model_dump(exclude_unset=True, exclude={'id'})
    create_data['role'] = '管理员'
    await Movies.create(**create_data)
    return Result.success()


# 修改
@router.put("/update")
async def update(movies_create_pydantic: MoviesCreatePydantic):
    update_data = movies_create_pydantic.model_dump(exclude_unset=True, exclude={"id"})
    await Movies.filter(id=movies_create_pydantic.id).update(**update_data)
    return Result.success()


# 删除
@router.delete("/delete/{movies_id}")
async def delete(movies_id: int):
    await Movies.filter(id=movies_id).delete()
    return Result.success()


# 批量删除
@router.delete("/deleteBatch")
async def delete_batch(ids: List[int]):
    await Movies.filter(id__in=ids).delete()
    return Result.success()


# 单个查询
@router.get("/selectById/{movies_id}")
async def select_one(movies_id: int):
    movies = await Movies.get_or_none(id=movies_id)
    return Result.success(movies)


# 查询所有
@router.get("/selectAll")
async def select_all(name: str = ""):
    movies_list = await Movies.filter(name__contains=name)
    return Result.success(movies_list)


# 分页查询
@router.get("/selectPage")
async def select_page(name: str = "", pageNum: int = 1, pageSize: int = 10):
    # 同时获取分页数据和总数
    query = Movies.filter(name__contains=name).prefetch_related('category')
    # 获取分页数据
    movies_list = await query.offset((pageNum - 1) * pageSize).limit(pageSize)
    movies_list = [
        {
            **MoviesPydantic.model_validate(movies).model_dump(),
            "categoryId": movies.category.id if movies.category else None,
            "categoryName": movies.category.name if movies.category else None,
        }
        
        for movies in movies_list
    ]
    # 计算总数
    total = await query.count()
    # 封装分页数据
    pageinfo = PageInfo(total=total, list=movies_list)
    return Result.success(pageinfo)
