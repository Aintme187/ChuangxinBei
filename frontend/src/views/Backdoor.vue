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
const openPrompt = ref(false)
const openPrompt1 = ref(false)
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

function openPromptFunc(val){
  console.log("val've been changed");
  if(val === 1) openPrompt.value = true;
  else if(val === 2) openPrompt1.value = true;
  else{
    openPrompt.value = false;
    openPrompt1.value = false;
  }
}

onMounted(() => {
  getVideo()
})
</script>

<template>
  <div class="container" style="margin-left: auto;margin-right: auto">
    <el-card class="body">
      <h3 style="margin-top: 0; margin-bottom: 0">生成后门攻击图片</h3>
      <br>
      摄像头实时显示:
      <br>
      <video ref="myVideo" autoplay style="width: 350px"></video>
      <br>
      <br>
      <div class="box">
        <div class="oneSide">
          <el-button @click="shootPicture" round>
            拍摄照片
          </el-button>
          <el-button class="file-box" text type="primary" round>
            <input type="file" ref="fileInput" multiple class="file-btn" required @change="fileChange"/>上传
          </el-button>
          <!-- <input type="file" ref="fileInput" @change="fileChange" /> -->
          <br>
          <!--用隐形的画布来获取一帧画面-->
          <canvas ref="myCanvas" style="display: none"></canvas>
          <br>
          <el-tag type="success" size="small">正常图片</el-tag>
          <br>
          <img v-if="imageUrl" :src="imageUrl" alt="Image" width="200px">
        </div>
        <div class="oneSide">
          <el-button type="danger" @click="backdoorAttack" @mouseover="openPromptFunc(1)"
                     @mouseout="openPromptFunc(0)" round plain>进行后门攻击</el-button>
          <br>
          <br>
          <el-tag type="danger" size="small">异常图片</el-tag>
          <img v-if="tar_image" :src="tar_image" alt="Image" width="200rpx">
        </div>
      </div>
    </el-card>

    <el-card class="body">
      <h3>后门攻击图片检测</h3>
      <el-button class="file-box" text type="primary" round>
        <input type="file" ref="fileTest" multiple class="file-btn" required @change="uploadChange"/>上传检测图片
      </el-button>
      <br>
      <img v-if="test_imageUrl" :src="test_imageUrl" alt="test Image" width="200rpx">
      <br>
      <el-button type="primary" @click="backdoorTest" @mouseover="openPromptFunc(2)"
                     @mouseout="openPromptFunc(0)" >检测</el-button>
      <br>
      <div>
        <el-text>检测结果:</el-text>
        <el-tag v-if="flag===-1" type="info" effect="plain">待检测</el-tag>
        <el-tag v-else-if="flag===1" type="success">正常图片</el-tag>
        <el-tag v-else-if="flag===0" type="danger">异常图片</el-tag>
      </div>
      <br>
    </el-card>

    <el-card class="prompt" v-show="openPrompt" style="background-color: lightcoral; opacity: 0.4">
      <el-text style="color: black; font-weight: bold">
        后门攻击 的说明书:
        <br>
        从摄像头拍摄图片或上传图片，点击“后门攻击”进行攻击，在左侧下方区域对比观察原图与生成图片。
        <br>
        若生成的图片在原图基础上戴上了墨镜，即攻击成功。
        <br>
        <br>
        模型训练中，后门攻击者往往会采取向训练数据中植入不易被察觉的后门，让训练数据异常化，以达到获取未授权的权限，干扰正常用户识别等目的。后门攻击不需要知道训练集和模型结构即可攻击，对人脸识别终端的安全构成了严重的威胁。
      </el-text>
    </el-card>
    <el-card class="prompt" v-show="openPrompt1" style="background-color: #5bbaf6; opacity: 0.4">
      <el-text style="color: black; font-weight: bold">
        后门检测 的说明书:
        <br>
        上传待检测图片，点击“检测”进行检测，在按钮下方得到检测结果。
        <br>
        <br>
        后门攻击训练数据异常检测方法：通过二分类器筛选新增样本，对于已知分布样本预测与标注结果一致率，对未知分布样本利用少样本抽检，从而评估样本可用性.
        <br>
        对于已知分布样本，我们所采用的二分类器是支持向量机（Support Vector Machine，SVM),对于未知分布样本，我们利用少样本抽检来评估样本可用性，根据评估指标更新优化模型，在这里我们采用准确率作为评估指标。
      </el-text>
    </el-card>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  width: 100%;
  height: 600px;

}
.body {
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
.oneSide {
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
