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
  else openPrompt.value = false;
}

onMounted(() => {
  getVideo()
})
</script>

<template>
  <el-card class="prompt" v-show="openPrompt">
    
  </el-card>
  <el-card class="container">
    摄像头实时显示:
    
    <video ref="myVideo" autoplay></video>
    

    <el-card class="body">
      <el-button @click="shootPicture" round >
        拍摄照片
      </el-button>
      <br>

      <el-button class="file-box" text type="primary" round >
        <input type="file" ref="fileInput" multiple class="file-btn" required @change="fileChange" width="400rpx" />上传
      </el-button>

      <!--
        <input type="file" ref="fileInput" @change="fileChange" />
      -->


      <br>
      <!--用隐形的画布来获取一帧画面-->
      <canvas ref="myCanvas" style="display: none"></canvas>
      <img v-if="imageUrl" :src="imageUrl" alt="Image">
      <br>
      <el-button @click="attack(1,1)" @mouseover="openPromptFunc(1)" @mouseout="openPromptFunc(0)">检测方式1</el-button>
      <br>
      <el-button @click="attack(1,2)">检测方式2</el-button>
      <br>
      <el-button @click="attack(0,0)">混淆保护</el-button>
      <br>
      <el-button @click="stop(0)" round>停止</el-button>
      <br>
      <p>攻击生成图片:</p>
      <br>
      <img v-if="tar_image" :src="tar_image + '?' + random" alt="正在处理图片">
    </el-card>
  </el-card>

</template>

<style scoped>

.container {
  
  display: flex;
  flex-direction: column;
  width: 700px;
  margin-left: 350px;
  height: 1900px;

  
}
.body{
  .el-button:hover{
    background: black;
  }
  display: flex;
  position: relative;
  width: 640px;
  height: 1300px;
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
.prompt{
  height: 400px;
  width: 400px;
  margin-top: 200px;
  margin-left: 500px;
  top: 0px;
  display: flex;
  position:absolute;
  z-index: 9999;
}


</style>
