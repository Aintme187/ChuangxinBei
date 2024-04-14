<script setup>
import {onMounted, ref} from "vue";
import {axios, get_csrf_token} from "@/views/global.vue";

const myVideo = ref()
const myCanvas = ref()
const fileInput = ref()
const reader = new FileReader()
const imageUrl = ref()
const image = ref()
const tar_image = ref()
const attacking = ref(false) //是否需要刷新tar_image的标志位
const random = ref() //为tar_image添加后缀实现更新图像
const count = ref(0)
const openPrompt = ref(false)
const openPrompt1 = ref(false)
const openPrompt2 = ref(false)
const Flag = ref(-1)

reader.onload = ((event) => {
  imageUrl.value = event.target.result
})

function getVideo() {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({video: true}).then((stream) => {
      myVideo.value.srcObject = stream
    }).catch((error) => {
      alert('获取摄像头失败：' + error.toString())
    })
  } else {
    alert('浏览器不支持获取摄像头')
  }
}

function shootPicture() {
  const videoElement = myVideo.value
  const canvasElement = myCanvas.value

  if (videoElement && videoElement.videoWidth) { // 检查视频元素是否存在和是否已加载视频尺寸
    const context = canvasElement.getContext('2d')
    canvasElement.width = videoElement.videoWidth
    canvasElement.height = videoElement.videoHeight
    context.drawImage(videoElement, 0, 0, videoElement.videoWidth, videoElement.videoHeight)
    imageUrl.value = canvasElement.toDataURL()
    canvasElement.toBlob((blob) => {
      image.value = blob
    }, 'image/JPEG')
  } else {
    console.error('视频元素尚未设置或视频尺寸未加载')
  }
}

function fileChange() {
  image.value = fileInput.value.files[0]
  reader.readAsDataURL(image.value)
}

function attack(flag, select) {//改动了参数
  if (flag === 1 && select === 1) {
    Flag.value = 1;
  }else if(flag === 1 && select === 2) {
    Flag.value = 2;
  }else if(flag === 0 && select === 0) {
    Flag.value = 3;
  }
  if (image.value) {
    const formData = new FormData()
    formData.append('image', image.value)
    formData.append('flag', flag)//改动了formData内容
    formData.append('select', select)//改动了formData内容
    axios({
      method: 'post', //只有post可以传文件
      headers: {'X-CSRFToken': get_csrf_token()},
      data: formData,
      url: 'http://localhost:8000/attack/',
    }).then((request) => {
      const dataGet = request.data
      if (dataGet['code'] === -1) {
        alert(dataGet['msg'])
      } else {
        tar_image.value = dataGet['tar_image']
        attacking.value = true
        get_status()
      }
    })
  } else {
    alert('请拍摄或上传图片')
  }
}

//新增参数
function stop(status) {
  console.log(status)
  axios({
    method: 'get',
    url: 'http://localhost:8000/stop/',
  }).then((request) => {
    const dataGet = request.data
    if (dataGet['code'] === -1) {
      alert(dataGet['msg'])
    } else {
      attacking.value = false
      if (status === 0) {//手动停止
        alert('攻击已停止')
      } else if (status === 1) {//攻击成功停止
        alert('攻击成功')
      } else if (status === -1) {//攻击失败停止
        alert('攻击失败')
      }
      status = ref()//清除status
    }
  })
}

// function set_random() {
//   if (attacking.value) {
//     random.value = Math.random()
//     setTimeout(set_random, 1000)
//   }
// }
//修改为get_status，获取攻击状态并处理，解决攻击失败或成功时不给予用户反馈的问题
//{0:攻击中;1:攻击成功;-1:攻击失败}
function get_status() {
  if (attacking.value) {
    axios({
      method: 'get',
      url: 'http://localhost:8000/get_status/',
    }).then((request) => {
      const dataGet = request.data
      if (dataGet['code'] === -1) {
        alert(dataGet['msg'])
      } else {
        if (dataGet['status'] === 0) {//攻击中
          random.value = Math.random()
          setTimeout(get_status, 1000)
        } else {
          stop(dataGet['status'])//调用stop处理停止
        }
      }
    })
  }
}

function openPromptFunc(val){
  console.log("val've been changed");
  if(val == 1) openPrompt.value = true;
  else if(val == 2) openPrompt1.value = true;
  else if(val == 3) openPrompt2.value = true;
  else{
    openPrompt.value = false;
    openPrompt1.value = false;
    openPrompt2.value = false;
  }
}

onMounted(() => {
  getVideo()
})
</script>

<template>
  <div class="container">
    <el-card class="body">
      <h3 style="margin-top: 0; margin-bottom: 0">噪声还原检测与保护</h3>
      <br>
      摄像头实时显示:
      <br>
      <video ref="myVideo" autoplay style="width: 350px"></video>
      <br>
      <br>
      <el-button @click="shootPicture" round>
          拍摄照片
      </el-button>
      <el-button class="file-box" text type="primary" round >
        <input type="file" ref="fileInput" multiple class="file-btn" required @change="fileChange" width="400rpx" />上传
      </el-button>
      <br>
      <br>
      <div class="box">
        <div class="one-third">
          <br>
          <el-button @click="attack(1,1)" @mouseover="openPromptFunc(1)"
                     @mouseout="openPromptFunc(0)" size="large" color="#1eeea7" round plain style="--el-button-text-color: black">
            检测方式1
          </el-button>
          <br>
          <br>
        </div>
        <div class="one-third">
          <br>
          <el-button @click="attack(1,2)" @mouseover="openPromptFunc(2)"
                     @mouseout="openPromptFunc(0)" size="large" color="#5bbaf6" round plain style="--el-button-text-color: black">
            检测方式2
          </el-button>
          <br>
          <br>
        </div>
        <div class="one-third">
          <br>
          <el-button @click="attack(0,0)" @mouseover="openPromptFunc(3)"
                     @mouseout="openPromptFunc(0)" size="large" color="#d3b100" round plain style="--el-button-text-color: black">
            混淆保护
          </el-button>
          <br>
          <br>
        </div>
      </div>
      <br>
      <div class="box">
        <div class="a-half">
          当前正在进行：
          <el-tag v-if="Flag===1" type="success" size="large">检测方式1</el-tag>
          <el-tag v-else-if="Flag===2" type="primary" size="large">检测方式2</el-tag>
          <el-tag v-else-if="Flag===3" type="warning" size="large">混淆保护</el-tag>
        </div>
        <div class="a-half">
          <el-button type="danger" @click="stop(0)">停止</el-button>
        </div>
      </div>
    </el-card>

    <el-card class="body">
      <h3 style="margin-top: 0; margin-bottom: 0">效果对比</h3>
      <br>
      <div class="box">
        <div class="a-half">
          <p>拍摄或上传的原图:</p>
          <br>
          <canvas ref="myCanvas" style="display: none"></canvas>
          <img v-if="imageUrl" :src="imageUrl" alt="Image" width="200px">
        </div>
        <div class="a-half">
          <p>攻击生成的图片:</p>
          <br>
          <img v-if="tar_image" :src="tar_image + '?' + random" alt="正在处理图片">
        </div>
      </div>
    </el-card>

    <el-card class="prompt" v-show="openPrompt" style="background-color: #1eeea7; opacity: 0.4">
      <el-text style="color: black; font-weight: bold">检测攻击1的说明书</el-text>
    </el-card>
    <el-card class="prompt" v-show="openPrompt1" style="background-color: #5bbaf6; opacity: 0.4">
      <el-text style="color: black; font-weight: bold">检测攻击2的说明书</el-text>
    </el-card>
    <el-card class="prompt" v-show="openPrompt2" style="background-color: #d3b100; opacity: 0.4">
      <el-text style="color: black; font-weight: bold">混淆保护的说明书</el-text>
    </el-card>
    
  </div>

</template>

<style scoped>
.container {
  position:relative;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  width: 100%;
  height: 600px;
}

.body{
  position: relative;
  width: 570px;
  height: 630px;
  margin-left: auto;
  margin-right: auto;
  align-content: start;
}

.box {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}
.one-third{
  width: 32%;
}
.a-half {
  width: 49%;
}

.prompt{
  height: 300px;
  width: 570px;
  margin-left: 39%;
  margin-top: 22.5%;
  display: flex;
  position: fixed;
}

.file-box {
    display: inline-block;
    position: relative;
    overflow: hidden;
    background-color: rgb(255, 255, 255);
}
 
.file-btn {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    outline: none;
    filter: alpha(opacity=0);
    -moz-opacity: 0;
    -khtml-opacity: 0;
    opacity: 0;
}

</style>
