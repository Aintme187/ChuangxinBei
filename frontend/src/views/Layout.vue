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
                <el-menu-item index="/attack/noise">
                    <el-icon>
                        <Promotion />
                    </el-icon>
                    <span>噪声检测</span>
                </el-menu-item>
                <el-menu-item index="/attack/backdoor">
                    <el-icon>
                        <Promotion />
                    </el-icon>
                    <span>后门攻击</span>
                </el-menu-item>
                
            </el-menu>
        </el-aside>
        <!-- 右侧主区域 -->
        <el-container class="main-container">
            <!-- 头部区域 -->
            <el-header>
                <div>
                    <strong>创新杯</strong>
                </div>
                <!--注意这个place属性-->
                
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
            <el-footer>
                创新杯
            </el-footer>
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
        .header{
            align-content: center;
            justify-content: center;
            margin-left: 1000px;
            border: 10px solid black;
        }
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