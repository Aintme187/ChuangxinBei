<script setup>
import {
  Management,
  Promotion,
  UserFilled,
  User,
  Crop,
  EditPen,
  SwitchButton,
  CaretBottom
} from '@element-plus/icons-vue'

</script>
<template>
  <el-container class="layout-container">
    <!-- 左侧菜单 -->
    <el-aside width="250px" style="background-color: #2c3951">
      <div class="el-aside__logo"></div>
      <el-menu default-active="/attack/noise" active-text-color="#296bf2" text-color="#fff"
               style="background-color: #2c3951;" router>
        <el-menu-item index="/attack/noise" style="align-content: center">
          <el-icon>
            <Promotion/>
          </el-icon>
          <span>噪声还原</span>
        </el-menu-item>
        <el-menu-item index="/attack/backdoor">
          <el-icon>
            <Promotion/>
          </el-icon>
          <span>后门攻击</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <!-- 右侧主区域 -->
    <el-container class="main-container">
      <!-- 头部区域 -->
      <el-header>
        <el-text class="mx-1" size="large">
          人工智能应用安全检测和保护平台
        </el-text>
        <!--注意这个place属性-->

      </el-header>
      <!-- 中间区域 -->
      <el-main style="padding: 8px">
        <!--替换掉前端这个样式style="width: 1290px; height: 570px;border: 1px solid red;"-->
        <div>
          <!--内容展示区-->
          <router-view></router-view>
        </div>
      </el-main>
      <!-- 底部区域 -->

    </el-container>
  </el-container>
</template>
<style lang="scss" scoped>

.layout-container {
  height: 98vh;

  .el-aside {
    //&是占位符，替代父样式的标签名
    &__logo {
      height: 60px;
      background: url('@/assets/Union.png') no-repeat center / 30px auto;
      background-color: white;
    }

    //el-组件可以直接用名字当作css标签直接引用修改css样式
    .el-menu {
      border-right: none;

      .el-menu-item {
        align-items: center;
        justify-content: center;
      }

    }
  }

  .el-header {
    background-color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: space-between;

    .el-dropdown__box {
      display: flex;
      align-items: center;

      .el-icon {
        color: #999;
        margin-left: 20px;
      }

      &:active,
      &:focus {
        outline: none;
      }
    }
  }

  .main-container {
    .header {
      align-content: center;
      justify-content: center;
      margin-left: 1000px;
    }

    .el-main {
      display: flex;
      //设置以下两个属性会将container中的内容居中
      /*align-items: center;
      justify-content: center;*/

    }

  }

  .el-footer {
    //最基础的弹性居中布局，display align-items justify-content
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    color: #666;
  }
}
</style>