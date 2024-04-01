<template>
  <div class="container">
    <div class="inner-container">
      <div>1号div</div>
      <div>2号div</div>
    </div>
    <div class="outer-div">3号div（容器）</div>
  </div>
</template>

<script>
export default {
  name: 'DivLayout',
}
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center; /* 居中对齐 */
}
.inner-container {
  display: flex;
}
.inner-container div {
  width: 100px; /* 设置1号和2号div的宽度 */
  background-color: #f0f0f0;
  padding: 10px;
  box-sizing: border-box;
}
.outer-div {
  background-color: lightblue;
  padding: 20px;
}
</style>
