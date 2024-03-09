<script setup>
import {onMounted, ref} from "vue";
import {axios, get_csrf_token} from "@/global.vue";

const myVideo = ref()
const myCanvas = ref()
const fileInput = ref()
const reader = new FileReader()
const imageUrl = ref()
const image = ref()
const tar_image = ref()
const attacking = ref(false) //是否需要刷新tar_image的标志位
const random = ref() //为tar_image添加后缀实现更新图像
/*reader.onload = ((event) => {
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

function attack(attack_type) {
  if (image.value) {
    const formData = new FormData()
    formData.append('image', image.value)
    formData.append('attack_type', attack_type)
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
        set_random()
      }
    })
  } else {
    alert('请拍摄或上传图片')
  }
}

function stop() {
  axios({
    method: 'get',
    url: 'http://localhost:8000/stop/',
  }).then((request) => {
    const dataGet = request.data
    if (dataGet['code'] === -1) {
      alert(dataGet['msg'])
    } else {
      alert('攻击已停止')
      attacking.value = false
    }
  })
}

function set_random() {
  if (attacking.value) {
    random.value = Math.random()
    setTimeout(set_random, 1000)
  }
}

onMounted(() => {
  getVideo()
})*/
</script>

<template>
  <div class="container">
    摄像头实时显示:
    <video ref="myVideo" autoplay></video>
    <button @click="shootPicture">拍摄照片</button>
    <input type="file" ref="fileInput" @change="fileChange">
    <!--用隐形的画布来获取一帧画面-->
    <canvas ref="myCanvas" style="display: none"></canvas>
    <img v-if="imageUrl" :src="imageUrl" alt="Image">
    <button @click="attack(1)">检测方式1</button>
    <button @click="attack(2)">检测方式2</button>
    <button @click="stop">停止</button>
    攻击生成图片:
    <img v-if="tar_image" :src="tar_image+'?'+random" alt="正在处理图片">
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  width: 500px;
  margin: auto;
}
</style>
