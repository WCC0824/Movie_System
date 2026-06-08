from typing import List, Optional

from fastapi import APIRouter
from pydantic import create_model
from tortoise.contrib.pydantic import pydantic_model_creator

from common.exception_handler import CustomException
from common.result import Result, PageInfo
from models import Category

router = APIRouter(prefix="/category")
# 创建 pydantic 只读模型
CategoryPydantic = pydantic_model_creator(Category)
# 自动生成所有字段为 Optional 的更新模型
CategoryCreatePydantic = create_model(
    "CategoryPydantic",
    **{
        name: (Optional[field.annotation], None)
        for name, field in CategoryPydantic.model_fields.items()
    }
)


# 新增
@router.post("/add")
async def add(category_create_pydantic : CategoryCreatePydantic):
    
    create_data = category_create_pydantic.model_dump(exclude_unset=True, exclude={'id'})
    create_data['role'] = '管理员'
    await Category.create(**create_data)
    return Result.success()


# 修改
@router.put("/update")
async def update(category_create_pydantic: CategoryCreatePydantic):
    update_data = category_create_pydantic.model_dump(exclude_unset=True, exclude={"id"})
    await Category.filter(id=category_create_pydantic.id).update(**update_data)
    return Result.success()


# 删除
@router.delete("/delete/{category_id}")
async def delete(category_id: int):
    await Category.filter(id=category_id).delete()
    return Result.success()


# 批量删除
@router.delete("/deleteBatch")
async def delete_batch(ids: List[int]):
    await Category.filter(id__in=ids).delete()
    return Result.success()


# 单个查询
@router.get("/selectById/{category_id}")
async def select_one(category_id: int):
    category = await Category.get_or_none(id=category_id)
    return Result.success(category)


# 查询所有
@router.get("/selectAll")
async def select_all(name: str = ""):
    category_list = await Category.filter(name__contains=name)
    return Result.success(category_list)


# 分页查询
@router.get("/selectPage")
async def select_page(name: str = "", pageNum: int = 1, pageSize: int = 10):
    # 同时获取分页数据和总数
    query = Category.filter(name__contains=name)
    # 获取分页数据
    category_list = await query.offset((pageNum - 1) * pageSize).limit(pageSize)
    category_list = [
        CategoryPydantic.model_validate(category).model_dump()
        for category in category_list
    ]
    # 计算总数
    total = await query.count()
    # 封装分页数据
    pageinfo = PageInfo(total=total, list=category_list)
    return Result.success(pageinfo)
