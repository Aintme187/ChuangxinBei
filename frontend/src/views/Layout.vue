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
        <el-aside width="250px">
            <div class="el-aside__logo"></div>
            <el-menu active-text-color="#ffd04b" background-color="#232323" text-color="#fff" router>
                <el-menu-item index="/article/category">
                    <el-icon>
                        <Management />
                    </el-icon>
                    <span>文章分类/前端element测试</span>
                </el-menu-item>
                <el-menu-item index="/article/manage">
                    <el-icon>
                        <Promotion />
                    </el-icon>
                    <span>文章管理</span>
                </el-menu-item>
                <el-sub-menu>
                    <template #title>
                        <el-icon>
                            <UserFilled />
                        </el-icon>
                        <span>个人中心</span>
                    </template>
                    <el-menu-item index="/user/info">
                        <el-icon>
                            <User />
                        </el-icon>
                        <span>基本资料</span>
                    </el-menu-item>
                    <el-menu-item index="/user/changeavatar">
                        <el-icon>
                            <Crop />
                        </el-icon>
                        <span>更换头像</span>
                    </el-menu-item>
                    <el-menu-item index="/user/changepassword">
                        <el-icon>
                            <EditPen />
                        </el-icon>
                        <span>重置密码</span>
                    </el-menu-item>
                </el-sub-menu>
            </el-menu>
        </el-aside>
        <!-- 右侧主区域 -->
        <el-container class="main-container">
            <!-- 头部区域 -->
            <el-header>
                <div>当前登陆用户：<strong>123456</strong></div>
                <!--注意这个place属性-->
                <el-dropdown placement="bottom-end">
                    <span class="el-dropdown__box">
                        <!--el可以用avatar来声明头像的位置-->
                        <el-avatar :src="avatar" />
                        <el-icon>
                            <CaretBottom />
                        </el-icon>
                    </span>
                    <!--el-dropdown 用template #dropdown来声明下拉菜单， 下面的command有什么用？-->
                    <template #dropdown>
                        <el-dropdown-menu>
                            <el-dropdown-item command="profile" :icon="User">基本
                                资料</el-dropdown-item>
                            <el-dropdown-item command="avatar" :icon="Crop">更换头
                                像</el-dropdown-item>
                            <el-dropdown-item command="password" :icon="EditPen">
                                重置密码</el-dropdown-item>
                            <el-dropdown-item command="logout" :icon="SwitchButton">退出登录</el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </el-header>
            <!-- 中间区域 -->
            <el-main>
                <!--替换掉前端这个样式style="width: 1290px; height: 570px;border: 1px solid red;"-->
                <div >
                    <!--内容展示区-->
                    <router-view></router-view>
                </div>
            </el-main>
            <!-- 底部区域 -->
            <el-footer>软工大二下作业</el-footer>
        </el-container>
    </el-container>
</template>
<style lang="scss" scoped>
.layout-container {
    height: 98vh;

    .el-aside {
        background-color: #232323;

        //&是占位符，替代父样式的标签名
        &__logo {
            height: 120px;
            background: url('@/assets/DogHead.jpg') no-repeat center / 120px auto;
        }
        //el-组件可以直接用名字当作css标签直接引用修改css样式
        .el-menu {
            border-right: none;
        }
    }

    .el-header {
        background-color: #fff;
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
        .el-main{
            display: flex;
            //设置以下两个属性会将container中的内容居中
            /*align-items: center;
            justify-content: center;*/
            border: 1px solid blue;
        }
        border: 1px solid red;
    }

    .el-footer {
        //最基础的弹性居中布局，display align-items justify-content
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        color: #666;
    }
}</style>