<script type="text/javascript">
import axios from "axios";

axios.defaults.withCredentials = true

/*function get_csrf_token() {
  axios.get("http://localhost:8000/get_csrf_token/")
  let cookie = document.cookie
  //console.log('cookie_csrf_token=' + csrf_token)
  return cookie.split('=')[1]
}*/

export {axios,/*get_csrf_token*/}
</script>

<template>

</template>

<style scoped>

</style>