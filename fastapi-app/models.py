from tortoise.models import Model
from tortoise import fields


class Admin(Model):
    """管理员"""
    id = fields.IntField(pk=True, null=False)
    username = fields.CharField(max_length=255, null=True)
    password = fields.CharField(max_length=255, null=True)
    name = fields.CharField(max_length=255, null=True)
    avatar = fields.CharField(max_length=255, null=True)
    role = fields.CharField(max_length=255, null=True)

    class Meta:
        table = 'admin'


class Category(Model):
    """图书分类"""
    id = fields.IntField(pk=True, null=False)
    name = fields.CharField(max_length=255, null=True)

    class Meta:
        table = 'category'

class Movies(Model):
    """图书信息"""
    id = fields.IntField(pk=True, null=False)
    name = fields.CharField(max_length=255, null=True)
    img = fields.CharField(max_length=255, null=True)
    author = fields.CharField(max_length=255, null=True)
    publisher = fields.CharField(max_length=255, null=True)
    year = fields.CharField(max_length=255, null=True)
    price = fields.FloatField(max_length=255, null=True)
    isbn = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    category = fields.ForeignKeyField("models.Category", null=True)

    class Meta:
        table = 'movies'


class MovieInfo(Model):
    """电影信息"""
    id = fields.IntField(pk=True, null=False)
    name = fields.CharField(max_length=255, null=True)          # 电影名称
    img = fields.CharField(max_length=255, null=True)           # 电影封面
    year = fields.CharField(max_length=50, null=True)           # 电影年份
    release_date = fields.CharField(max_length=50, null=True)   # 上映时间
    genres = fields.CharField(max_length=255, null=True)        # 电影类型（逗号分隔）
    duration = fields.CharField(max_length=50, null=True)       # 电影时长
    rating = fields.CharField(max_length=50, null=True)         # 电影评分
    language = fields.CharField(max_length=50, null=True)       # 电影语言
    director = fields.CharField(max_length=255, null=True)      # 导演
    actors = fields.TextField(null=True)                        # 演员
    tagline = fields.CharField(max_length=255, null=True)       # 标语
    introduction = fields.TextField(null=True)                  # 简介
    category = fields.ForeignKeyField("models.Category", null=True)  # 关联分类

    class Meta:
        table = 'movie_info'
    