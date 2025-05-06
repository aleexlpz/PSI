<template>
  <div class="login-container">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin" class="login-form">
      <div class="form-group">
        <label for="username">Username:</label>
        <input 
          id="username" 
          v-model="username" 
          type="text"
          required
          data-cy="username-input"
        >
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input 
          id="password" 
          v-model="password" 
          type="password" 
          required
          data-cy="password-input"
        >
      </div>
      <button type="submit" data-cy="login-button">LOG IN</button>
    </form>
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = import.meta.env.VITE_DJANGO_URL

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const authStore = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
  errorMessage.value = ''
  try {
    const response = await axios.post(API_URL + 'auth_token/login/', {
      username: username.value,
      password: password.value
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.data && response.data.token) {
      authStore.login(response.data.token)
      router.push('/')
    } else {
      errorMessage.value = 'Invalid response from server'
    }
  } catch (error) {
    if (error.response) {
      if (error.response.status === 401) {
        errorMessage.value = 'Invalid username or password' + error.response.status
      } else {
        errorMessage.value = 'Server error' + username.value + password.value + '    ' + error.response.status
      }
    } else if (error.request) {
      errorMessage.value = 'No response from server' + error.response.status
    } else {
      errorMessage.value = 'Request error occurred' + error.response.status
    }
    console.error('Login error:', error)
  }
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-top: 50px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

.error-message {
  color: red;
  margin-top: 15px;
}
</style>