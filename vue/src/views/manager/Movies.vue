<template>
  <div>

    <div class="card" style="margin-bottom: 5px;">
      <el-input v-model="data.name" style="width: 300px; margin-right: 10px" placeholder="请输入名称查询"></el-input>
      <el-button type="primary" @click="load">查询</el-button>
      <el-button type="info" style="margin: 0 10px" @click="reset">重置</el-button>
    </div>

    <div class="card" style="margin-bottom: 5px">
      <div style="margin-bottom: 10px">
        <el-button type="primary" @click="handleAdd">新增</el-button>
      </div>
      <el-table tooltip-effect="dark myEff" :data="data.tableData" stripe>
        <el-table-column label="电影名称" prop="name"></el-table-column>
        <el-table-column label="封面" prop="img">
          <template #default="scope">
            <el-image v-if="scope.row.img" preview-teleported :src="scope.row.img" :preview-src-list="[scope.row.img]" style="width: 40px; height: 40px;"></el-image>
          </template>
        </el-table-column>
        <el-table-column label="导演" prop="director" show-overflow-tooltip>
          <template #default="scope">
            <div class="line-clamp-3">{{ scope.row.director }}</div>
          </template>
        </el-table-column>
        <el-table-column label="演员" prop="actors" show-overflow-tooltip>
          <template #default="scope">
            <div class="line-clamp-3">{{ scope.row.actors }}</div>
          </template>
        </el-table-column>
        <el-table-column label="上映时间" prop="release_date"></el-table-column>
        <el-table-column label="电影年份" prop="year"></el-table-column>
        <el-table-column label="电影时长" prop="duration"></el-table-column>
        <el-table-column label="评分" prop="rating"></el-table-column>
        <el-table-column label="语言" prop="language"></el-table-column>
        <el-table-column label="类型" prop="genres" show-overflow-tooltip>
          <template #default="scope">
            <div class="line-clamp-3">{{ scope.row.genres }}</div>
          </template>
        </el-table-column>
        <el-table-column label="标语" prop="tagline" show-overflow-tooltip>
          <template #default="scope">
            <div class="line-clamp-3">{{ scope.row.tagline }}</div>
          </template>
        </el-table-column>
        <el-table-column label="简介" prop="introduction" show-overflow-tooltip>
          <template #default="scope">
            <div class="line-clamp-3">{{ scope.row.introduction }}</div>
          </template>
        </el-table-column>
        <el-table-column label="分类" prop="categoryName"></el-table-column>
        <el-table-column label="操作" align="center" width="160">
          <template #default="scope">
            <el-button type="primary" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="card">
      <el-pagination @current-change="load" background layout="total, prev, pager, next" v-model:page-size="data.pageSize" v-model:current-page="data.pageNum" :total="data.total"/>
    </div>

    <el-dialog title="电影信息" width="40%" v-model="data.formVisible" :close-on-click-modal="false" destroy-on-close>
      <el-form ref="formRef" :model="data.form" :rules="data.rules" label-width="100px" style="padding-right: 50px">
        <el-form-item label="电影名称" prop="name">
          <el-input v-model="data.form.name" placeholder="请输入电影名称" autocomplete="off" />
        </el-form-item>
        <el-form-item label="封面" prop="img">
          <el-upload :action="uploadUrl" list-type="picture" :on-success="handleImgSuccess">
            <el-button type="primary">上传封面</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="电影年份" prop="year">
          <el-input v-model="data.form.year" placeholder="请输入电影年份" autocomplete="off" />
        </el-form-item>
        <el-form-item label="上映时间" prop="release_date">
          <el-input v-model="data.form.release_date" placeholder="请输入上映时间" autocomplete="off" />
        </el-form-item>
        <el-form-item label="电影类型" prop="categoryId">
          <el-select v-model="data.form.categoryId" placeholder="请选择电影类型">
            <el-option v-for="item in data.categoryList" :label="item.name" :value="item.id" :key="item.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="类型标签" prop="genres">
          <el-input v-model="data.form.genres" placeholder="多个类型用逗号分隔" autocomplete="off" />
        </el-form-item>
        <el-form-item label="电影时长" prop="duration">
          <el-input v-model="data.form.duration" placeholder="例如: 120m" autocomplete="off" />
        </el-form-item>
        <el-form-item label="电影评分" prop="rating">
          <el-input v-model="data.form.rating" placeholder="请输入电影评分" autocomplete="off" />
        </el-form-item>
        <el-form-item label="电影语言" prop="language">
          <el-input v-model="data.form.language" placeholder="请输入电影语言" autocomplete="off" />
        </el-form-item>
        <el-form-item label="导演" prop="director">
          <el-input v-model="data.form.director" placeholder="请输入导演" autocomplete="off" />
        </el-form-item>
        <el-form-item label="演员" prop="actors">
          <el-input v-model="data.form.actors" placeholder="请输入演员，多个用逗号分隔" autocomplete="off" />
        </el-form-item>
        <el-form-item label="标语" prop="tagline">
          <el-input v-model="data.form.tagline" placeholder="请输入标语" autocomplete="off" />
        </el-form-item>
        <el-form-item label="简介" prop="introduction">
          <el-input type="textarea" placeholder="请输入简介" :rows="3" v-model="data.form.introduction" autocomplete="off" />
        </el-form-item>

      </el-form>
      <template #footer>
      <span class="dialog-footer">
        <el-button @click="data.formVisible = false">取 消</el-button>
        <el-button type="primary" @click="save">保 存</el-button>
      </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import request from "@/utils/request";
import {reactive, ref} from "vue";
import {ElMessageBox, ElMessage} from "element-plus";

// 文件上传的接口地址
const uploadUrl = import.meta.env.VITE_BASE_URL + '/files/upload'

const formRef = ref()
const data = reactive({
  user: JSON.parse(localStorage.getItem('system-user') || '{}'),
  pageNum: 1,
  pageSize: 10,
  total: 0,
  formVisible: false,
  form: {},
  tableData: [],
  name: null,
  categoryList: [],
  rules: {
    name: [
      { required: true, message: '请输入电影名称', trigger: 'blur' }
    ],
    img: [
      { required: true, message: '请上传封面', trigger: 'blur' }
    ],
    director: [
      { required: true, message: '请输入导演', trigger: 'blur' }
    ],
    introduction: [
      { required: true, message: '请输入简介', trigger: 'blur' }
    ],
    categoryId: [
      { required: true, message: '请选择分类', trigger: 'change' }
    ]
  }
})

request.get('category/selectAll').then(res => {
  data.categoryList = res.data
})

// 分页查询
const load = () => {
  request.get('/movieInfo/selectPage', {
    params: {
      pageNum: data.pageNum,
      pageSize: data.pageSize,
      name: data.name,
    }
  }).then(res => {
    data.tableData = res.data?.list
    data.total = res.data?.total
  })
}

// 新增
const handleAdd = () => {
  data.form = {}
  data.formVisible = true
}

// 编辑
const handleEdit = (row) => {
  // categoryId 和 categoryName 是 selectPage 返回的额外字段
  data.form = JSON.parse(JSON.stringify(row))
  data.formVisible = true
}

// 新增保存
const add = () => {
  request.post('/movieInfo/add', data.form).then(res => {
    if (res.code === '200') {
      load()
      ElMessage.success('操作成功')
      data.formVisible = false
    } else {
      ElMessage.error(res.msg)
    }
  })
}

// 编辑保存
const update = () => {
  request.put('/movieInfo/update', data.form).then(res => {
    if (res.code === '200') {
      load()
      ElMessage.success('操作成功')
      data.formVisible = false
    } else {
      ElMessage.error(res.msg)
    }
  })
}

// 弹窗保存
const save = () => {
  formRef.value.validate(valid => {
    if (valid) {
      // data.form有id就是更新，没有就是新增
      data.form.id ? update() : add()
    }
  })
}

// 删除
const handleDelete = (id) => {
  ElMessageBox.confirm('删除后数据无法恢复，您确定删除吗?', '删除确认', { type: 'warning' }).then(res => {
    request.delete('/movieInfo/delete/' + id).then(res => {
      if (res.code === '200') {
        load()
        ElMessage.success('操作成功')
      } else {
        ElMessage.error(res.msg)
      }
    })
  }).catch(err => {})
}

// 处理文件上传的钩子
const handleImgSuccess = (res) => {
  data.form.img = res.data
}


// 重置
const reset = () => {
  data.name = null
  load()
}



load()
</script>

<style>
.myEff{
  max-width: 500px;
}
.line-clamp-3 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
  word-break: break-all;
}
</style>