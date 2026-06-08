<template>
  <div>

    <div class="card" style="margin-bottom: 10px">
      <div>欢迎您，<b>{{ data.user.name }}</b> 祝您今天过得开心！</div>
    </div>
    <div class="card" style="line-height:30px">
      <div><a href="https://github.com/WCC0824">https://github.com/WCC0824</a>作品,感谢大家的支持~</div>
      
      
        </div>
    </div>

</template>

<script setup>
import { reactive } from "vue";
import request from "@/utils/request";

const data = reactive({
  user: JSON.parse(localStorage.getItem('system-user') || '{}'),
})
</script>