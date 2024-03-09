<script setup>
import { User, Lock } from '@element-plus/icons-vue'
import { ref } from 'vue'
import { registerService,loginService } from '@/api/user.js'
import { ElMessage } from 'element-plus'
//使用router
import { useRouter } from 'vue-router'
import { useTokenStore } from '@/stores/token'


const router = useRouter();
const tokenStore = useTokenStore();
//控制注册与登录表单的显示， 默认显示注册
const isRegister = ref(false);

const registerData = ref({
  username: '',
  password: '',
  rePassword: ''
})

//自定义确认密码的校验函数
const rePasswordValid = (rule, value, callback) => {
 if (value == null || value === '') {
  return callback(new Error('请再次确认密码'))
 }
 if (registerData.value.password !== value) {
  return callback(new Error('两次输入密码不一致'))
 }
}
//用于注册的表单校验模型
const rules = ref({
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 5, max: 16, message: '用户名的长度必须为5~16位', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 5, max: 16, message: '密码长度必须为5~16位', trigger: 'blur' }
    ],
    rePassword: [
        { validator: rePasswordValid, trigger: 'blur' }
    ]
})
//完成注册接口函数及其调用
const register = async() => {
  //一定不要忘了ref声明的数据的内置属性.value
  await registerService(registerData.value);
  ElMessage.success('注册成功');
}

//完成登陆接口函数及其调用
const login = async() => {
  await loginService(registerData.value);

  //保存token
  tokenStore.setToken(result.data);

  ElMessage.success('登陆成功');
  router.push('/')
}

//切换登陆注册页面时清空数据
const clearData = () => {
  // json格式数据需要用花括号{}包裹
  registerData.value = {
    username: '',
    password: '',
    rePassword: ''
  }
}

</script>

<template>
  <el-row class="login-page">
    <el-col :span="12" class="bg"></el-col>
    <el-col :span="6" :offset="3" class="form">
      <!-- 注册表单 -->
      <el-form 
        ref="form" 
        size="large" 
        autocomplete="off" 
        v-if="isRegister"
        :rules="rules"
        :model="registerData"
      >
        <el-form-item>
          <h1>注册</h1>
        </el-form-item>
        <el-form-item prop="username">
          <el-input :prefix-icon="User" placeholder="请输入用户名" v-model="registerData.username"></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input :prefix-icon="Lock" type="password" placeholder="请输入密码" v-model="registerData.password"></el-input>
        </el-form-item>
        <el-form-item prop="rePassword">
          <el-input :prefix-icon="Lock" type="password" placeholder="请输入再次密码" v-model="registerData.rePassword"></el-input>
        </el-form-item>
        <!-- 注册按钮 -->
        <el-form-item>
          <el-button class="button" type="primary" auto-insert-space @click="register()">
            注册
          </el-button>
        </el-form-item>
        <el-form-item class="flex">
          <el-link type="info" :underline="false" @click="isRegister = false, clearData()">
            ← 返回
          </el-link>
        </el-form-item>
      </el-form>
      <!-- 登录表单 -->
      <el-form
      ref="form" 
      size="large" 
      autocomplete="off" 
      :rules="rules"
      :model="registerData"
      v-else 
      >
        <el-form-item>
          <h1>登录</h1>
        </el-form-item>
        <el-form-item prop="username">
          <el-input :prefix-icon="User" placeholder="请输入用户名" v-model="registerData.username"></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input name="password" :prefix-icon="Lock" type="password" placeholder="请输入密码" v-model="registerData.password"></el-input>
        </el-form-item>
        <el-form-item class="flex">
          <div class="flex">
            <el-checkbox>记住我</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码？</el-link>
          </div>
        </el-form-item>
        <!-- 登录按钮 -->
        <el-form-item>
          <el-button class="button" type="primary" auto-insert-space @click="login()">登录</el-button>
        </el-form-item>
        <el-form-item class="flex">
          <el-link type="info" :underline="false" @click="isRegister = true, clearData()">
            注册 →
          </el-link>
        </el-form-item>
      </el-form>
    </el-col>
  </el-row>
</template>

<style lang="scss" scoped>
/* 样式 */
.login-page {
  height: 100vh;
  background-color: #fff;

  .bg {
    /*background: url('@/assets/DogHead.jpg') no-repeat 60% center / 240px auto,*/
    background: url('@/assets/DogHead.jpg') no-repeat center / cover;
    border-radius: 0 20px 20px 0;
  }

  .form {
    display: flex;
    flex-direction: column;
    justify-content: center;
    user-select: none;

    .title {
      margin: 0 auto;
    }

    .button {
      width: 100%;
    }

    .flex {
      width: 100%;
      display: flex;
      justify-content: space-between;
    }
  }
}
</style>