<template>
  <div class="app-container">
    <nav class="navbar">
      <div class="navbar-content">
        <router-link to="/" class="navbar-title">Chess-T-DB</router-link>
        <div class="navbar-links">
          <router-link to="/" class="nav-link">Home</router-link>
          <router-link to="/login" class="nav-link">Admin Log-In</router-link>
          <router-link to="/logout" class="nav-link">Log-Out</router-link>
          <router-link to="/faq" class="nav-link">FAQ</router-link>
        </div>
      </div>
    </nav>
    <main class="main-content">
      <router-view></router-view>
      
    </main>
    <footer class="footer">
      © 2025 Copyright: Alejandro López & Ernesto Piñón
    </footer>
  </div>
</template>

<script setup>
import { provide, ref, onMounted } from 'vue'


const torneos = ref([])
const isLoading = ref(false)
const error = ref(null)
const API_URL = import.meta.env.VITE_DJANGO_URL

provide('torneos', torneos)

const listadoTorneos = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await fetch(API_URL + 'tournaments/', {
      headers: {
        'Accept': 'application/json',
      }
    })    

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    torneos.value = (await response.json()).results
    
  } catch (error) {
    error.value = `Error al cargar torneos: ${error.message}`
    torneos.value = []
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  listadoTorneos()
})



</script>

<style>
.app-container {
  font-family: Arial, sans-serif; 
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: #000000;
    padding: 1rem 0;
    border-bottom: 1px solid #e0e0e0;
    z-index: 1000;
  }
  
  .navbar-content {
    display: flex;
    align-items: center;
    max-width: 1200;
    margin: 0 auto;
    padding: 0 1rem;
  }
  
  .navbar-title {
    font-size: 1.5rem;
    margin: 0;
    padding: 0.5rem 0;
    color: #ffffff;
    text-decoration: none;
  }
  
  .navbar-links {
    display: flex;
    align-items: center;
    margin-left: 1rem;
  }
  
  .nav-link {
    text-decoration: none;
    color: #999999;
    padding: 0.5rem;
    margin: 0 0.25rem;
    font-size: 1rem;
    line-height: 1.5;
  }
  
  .nav-link:hover {
    color: #ffffff;
  }
  
  @media (max-width: 768px) {
    .navbar-content {
      flex-direction: column;
    }
    
    .navbar-links {
      margin-left: 0;
      margin-top: 0.5rem;
    }
  }

.main-content {
  flex: 1;
  margin-top: 60px; /* Compensa el navbar fixed */
  padding: 20px;
}

.footer {
  position: fixed;
  bottom: 0;
  left: 0; 
  width: 100%;
  text-align: center; 
  padding: 1rem; 
  background-color: #f5f5f5; 
  border-top: 1px solid #e0e0e0; 
  box-sizing: border-box; 
  z-index: 1000; 
}

</style>