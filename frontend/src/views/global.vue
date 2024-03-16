<script type="text/javascript">
import axios from "axios";

axios.defaults.withCredentials = true

function get_csrf_token() {
  axios.get("http://localhost:8000/get_csrf_token/")
  let match = document.cookie.match('(^| )csrftoken=([^;]+)')
  console.log('cookie_csrf_token=' + match[2])
  return match[2]
}

export {axios, get_csrf_token}
</script>

<template>

</template>

<style scoped>

</style>