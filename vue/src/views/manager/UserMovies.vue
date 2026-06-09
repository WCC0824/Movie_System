<template>
  <div>
    <div style="margin-bottom: 30px; display: flex; align-items: center">
      <div style="flex: 1">
        <div style="display: flex; align-items: center; flex-wrap: wrap;">
          <div @click="changeCategory(null)" style="padding-bottom: 5px; margin-right: 20px; cursor: pointer" :class="{'category-active' : data.activeCategoryId === null }">全部电影</div>
          <div @click="changeCategory(item.id)" style="padding-bottom: 5px; margin-right: 20px; cursor: pointer" :class="{'category-active' : data.activeCategoryId === item.id }" v-for="item in data.categoryList" :key="item.id">{{ item.name }}</div>
        </div>
      </div>
      <div>
        <el-input clearable @clear="load" style="width: 300px; height: 40px" v-model="data.name" placeholder="请输入电影名称搜索"></el-input>
        <el-button type="primary" style="height: 40px; margin-left: 10px" @click="load">搜 索</el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="6" style="margin-bottom: 20px" v-for="item in data.tableData" :key="item.id">
        <div class="card item" style="padding: 0">
          <img
            style="width: 100%; height: 400px; border-radius: 5px 5px 0 0; object-fit: cover;"
            :src="item.img || 'https://via.placeholder.com/300x450?text=No+Image'"
            alt=""
          >
          <div style="padding: 12px">
            <div style="font-size: 18px; margin-bottom: 8px; font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" :title="item.name">
              {{ item.name }}
            </div>
            <div style="color: #666; font-size: 13px; margin-bottom: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              <el-tag size="small" type="warning" v-if="item.rating" style="margin-right: 6px">{{ item.rating }} 分</el-tag>
              <span v-if="item.duration">{{ item.duration }}</span>
            </div>
            <div style="color: #666; font-size: 13px; margin-bottom: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" :title="'导演：' + item.director">
              导演：{{ item.director }}
            </div>
            <div style="color: #666; font-size: 13px; margin-bottom: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" :title="'主演：' + item.actors">
              主演：{{ item.actors }}
            </div>
            <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 4px; margin-top: 8px">
              <el-tag size="small" v-if="item.language">{{ item.language }}</el-tag>
              <el-tag size="small" type="success" v-if="item.release_date">{{ item.release_date }}</el-tag>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <div v-if="data.total" style="margin-top: 20px; margin-bottom: 50px">
      <el-pagination @current-change="load" layout="total, prev, pager, next" :page-size="data.pageSize" v-model:current-page="data.pageNum" :total="data.total"/>
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import request from "@/utils/request.js";
import { ElMessage } from "element-plus";

const data = reactive({
  user: JSON.parse(localStorage.getItem('system-user') || '{}'),
  tableData: [],
  total: 0,
  pageNum: 1,
  pageSize: 8,
  name: null,
  activeCategoryId: null,
  categoryList: []
})

// 加载分类列表
request.get('/category/selectAll').then(res => {
  if (res.code === '200') {
    data.categoryList = res.data
  }
})

// 切换分类
const changeCategory = (categoryId) => {
  data.activeCategoryId = categoryId
  data.pageNum = 1
  load()
}

// 加载电影分页数据
const load = () => {
  request.get('/movieInfo/selectPage', {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
      name: data.name,
      categoryId: data.activeCategoryId
    }
  }).then(res => {
    if (res.code === '200') {
      data.tableData = res.data?.list || []
      data.total = res.data?.total
    } else {
      ElMessage.error(res.msg)
    }
  })
}
load()
</script>

<style scoped>
.item {
  transition: all 0.5s;
  background-color: white;
  border-radius: 5px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}
.item:hover {
  transform: translateY(-5px);
}
.category-active {
  color: #006cff;
  border-bottom: 2px solid #006cff;
}
</style>