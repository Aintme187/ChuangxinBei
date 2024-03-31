<script type="text/javascript">
import axios from "axios";

axios.defaults.withCredentials = true

function get_csrf_token() {
  // console.log(API_URL)
  axios.get(API_URL+"/get_csrf_token/")
  let match = document.cookie.match('(^| )csrftoken=([^;]+)')
  // console.log('cookie_csrf_token=' + match[2])
  return match[2]
}

const API_URL = import.meta.env.VITE_API_URL

export {axios, get_csrf_token, API_URL}
</script>

<template>

</template>

<style scoped>

</style>