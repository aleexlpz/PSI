<template>
  <div class="chess-app">
    <!-- Contenido principal -->
    <main class="main-content">
      <!-- Texto de bienvenida -->
      <div class="welcome-section">
        <p>Welcome to the Chess Tournament Database. This database features the unique ability for players to update the results of their games. To create tournaments, an administrative account is required. However, any player can enter the result of a game.</p>
        <p>You can use the search button to find tournaments by name. For further information, please refer to the<router-link to="/faq" class="text-link"><u>FAQ</u></router-link>section.</p>
      </div>

      <section class="tournaments-and-search">
        <!-- Listado de torneos -->
        <div class="tournaments-section">
          <h2>Tournaments</h2>
          <table class="tournaments-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tournament in torneos" :key="tournament.id">
                <td>{{ tournament.name }}</td>
                <td>{{ tournament.start_date }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Paginación -->
          <div class="pagination">
            <button 
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="pagination-button"
            >
              Previous
            </button>
            <span class="page-indicator">Page {{ currentPage }} of {{ totalPages }}</span>
            <button 
              @click="goToPage(currentPage + 1)" 
              :disabled="currentPage === totalPages"
              class="pagination-button"
            >
              Next
            </button>
          </div>
        </div>

        <!-- Barra de búsqueda -->
        <div class="search-section">
          <h3>Search</h3>
          <div class="search-box">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search..."
              class="search-input"
            >
            <button @click="searchTournaments" class="search-button">Search</button>
          </div>
        </div>
      </section>
    </main>

    <!-- Pie de página -->
  </div>
</template>

<script setup>

  import { inject } from 'vue'
  const torneos = inject('torneos')
</script>

<style scoped>

.chess-app {
  display: flex; /* Activa el modelo de caja flexible */
  justify-content: center; /* Centra horizontalmente el contenido */
  align-items: flex-start; /* Alinea el contenido al inicio verticalmente */
  min-height: 100vh; /* Asegura que ocupe al menos toda la altura de la pantalla */
  padding: 20px; /* Espaciado interno opcional */
  box-sizing: border-box; /* Incluye el padding en el tamaño total */
}

.main-content {
  max-width: 1300px; /* Define el ancho máximo del contenido */
  width: 100%; 
  margin: 0;
}

.text-link {
  color: #3498db;
  text-decoration: none;
  padding: 2px 8px;
}

.text-link:hover {
  color: #2c0083;
  text-decoration: underline;
}

.welcome-section {
  text-align:justify;
  margin-bottom: 40px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  font-size: 1.7rem; 
}

.tournaments-and-search {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 30px; /* Espaciado entre las dos secciones */
}

.tournaments-section {
  margin: 2rem 0;
  width: 100%;
  max-width: 800px;
}

.tournaments-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9rem;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

.tournaments-table th,
.tournaments-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.tournaments-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.tournaments-table tr:hover {
  background-color: #f5f5f5;
}

/* Paginación */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.pagination-button {
  padding: 8px 16px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-button:hover:not(:disabled) {
  background-color: #e9ecef;
  border-color: #adb5bd;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-indicator {
  font-size: 0.9rem;
  color: #666;
}

.search-section {
  flex: 2; 
  display: flex;
  flex-direction: column;
  align-items: flex-start; /* Alinea el contenido al inicio horizontalmente */
}


</style>