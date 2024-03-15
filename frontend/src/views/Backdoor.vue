<script setup>
import {onMounted, ref} from "vue";
import {axios, get_csrf_token} from "@/views/global.vue";

const myVideo = ref()
const myCanvas = ref()
const fileInput = ref()
const fileTest = ref()
const reader = new FileReader()
const testReader = new FileReader()
const imageUrl = ref()
const test_imageUrl = ref()
const image = ref()
const testImg = ref()
const tar_image = ref()
const flag = ref(-1)

reader.onload = ((event) => {
  imageUrl.value = event.target.result
})

testReader.onload = ((event) => {
  test_imageUrl.value = event.target.result
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

function backdoorAttack() {
  //生成后门攻击图片
  if (image.value) {
    const formData = new FormData()
    formData.append('image', image.value)
    axios({
      method: 'post', //只有post可以传文件
      headers: {'X-CSRFToken': get_csrf_token()},
      data: formData,
      url: 'http://localhost:8000/attack_backdoor/',
    }).then((request) => {
      const dataGet = request.data
      if (dataGet['code'] === -1) {
        alert(dataGet['msg'])
      } else {
        tar_image.value = dataGet['tar_image']
      }
    })
  } else {
    alert('请拍摄或上传图片')
  }
}

function uploadChange() {
  testImg.value = fileTest.value.files[0]
  testReader.readAsDataURL(testImg.value)
}

function backdoorTest() {
  //检测图片是否异常
  if (testImg.value) {
    const formData = new FormData()
    formData.append('image', testImg.value)
    axios({
      method: 'post', //只有post可以传文件
      headers: {'X-CSRFToken': get_csrf_token()},
      data: formData,
      url: 'http://localhost:8000/predict/',
    }).then((request) => {
      const dataGet = request.data
      if (dataGet['code'] === -1) {
        alert(dataGet['msg'])
      } else {
        flag.value = dataGet['status']
      }
    })
  } else {
    alert('请拍摄或上传图片')
  }
}

onMounted(() => {
  getVideo()
})
</script>

<template>
  <el-card class="container">
    摄像头实时显示:
    <video ref="myVideo" autoplay></video>

    <el-card class="body">
      <el-button @click="shootPicture" round>
        拍摄照片
      </el-button>
      <br>

      <el-button class="file-box" text type="primary" round>
        <input type="file" ref="fileInput" multiple class="file-btn" required @change="fileChange"/>上传
      </el-button>

      <!--
        <input type="file" ref="fileInput" @change="fileChange" />
      -->


      <br>
      <!--用隐形的画布来获取一帧画面-->
      <canvas ref="myCanvas" style="display: none"></canvas>
      <img v-if="imageUrl" :src="imageUrl" alt="Image" width="200rpx">
      <br>
      <el-tag type="success" size="small">正常图片</el-tag>
      <br>
      <br>
      <el-button type="danger" icon="" @click="backdoorAttack">进行后门攻击</el-button>
      <br>
      <img v-if="tar_image" :src="tar_image" alt="Image" width="200rpx">
      <br>
      <el-tag type="danger" size="small">异常图片</el-tag>
    </el-card>
    <el-card class="body">
      <h3>后门攻击图片检测</h3>
      <el-button class="file-box" text type="primary" round>
        <input type="file" ref="fileTest" multiple class="file-btn" required @change="uploadChange"/>上传检测图片
      </el-button>
      <br>
      <img v-if="test_imageUrl" :src="test_imageUrl" alt="test Image" width="200rpx">
      <br>
      <el-button type="primary" @click="backdoorTest">检测</el-button>
      <br>
      <div>
        <el-text>检测结果:</el-text>
        <el-tag v-if="flag===-1" type="info" effect="plain">待检测</el-tag>
        <el-tag v-else-if="flag===1" type="success">正常图片</el-tag>
        <el-tag v-else-if="flag===0" type="danger">异常图片</el-tag>
      </div>
      <br>
    </el-card>
  </el-card>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  width: 700px;
  margin-left: 350px;
  height: 1600px;


}

.body {
  display: flex;
  width: 640px;
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
@/api/backdoor.js