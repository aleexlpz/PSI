<template>
  <div class="logout-container">
    <h2>Log Out</h2>
    <p>You will be redirected to home in {{ countdown }} seconds</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const countdown = ref(5)

onMounted(() => {
  authStore.logout()
  
  const timer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value === 0) {
      clearInterval(timer)
      router.push('/')
    }
  }, 1000)
})
</script>

<style scoped>
.logout-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
  margin-top: 50px;
}
</style>