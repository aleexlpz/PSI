<template>
  <div class="tournament-detail">
    <h1>Tournament: <em>{{ tournament.name }}</em></h1>
    
    
    <button @click="refreshData" class="refresh-btn" data-cy="refresh-button">
      Refresh Page
    </button>

    <p class="instructions">Click the accordions below to expand/collapse the content.</p>

    <hr class="divider">

    <div class="accordion-container">
      <!-- Standing Accordion -->
      <div class="accordion-item" :class="{ active: activeAccordion === 'standing' }">
        <div class="accordion-header" @click="toggleAccordion('standing')">
          <h2>Standing</h2>
          <span class="accordion-icon">{{ activeAccordion === 'standing' ? '−' : '+' }}</span>
        </div>
        <transition name="slide">
          <div class="accordion-content" v-show="activeAccordion === 'standing'">
            <table class="standings-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Name</th>
                  <th>Score</th>
                  <th>Buchholz</th>
                  <th>No. games played with Black</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>{{ tournament.name }}</td>
                  <td>{{ tournament.name }}</td>
                  <td>{{ tournament.name }}</td>
                  <td>{{ tournament.name }}</td>
                  <td>{{ tournament.name }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </transition>
      </div>

      <!-- Pairings/Results Accordion -->
      <div class="accordion-item" :class="{ active: activeAccordion === 'pairings' }">
        <div class="accordion-header" @click="toggleAccordion('pairings')">
          <h2>Pairings/Results</h2>
          <span class="accordion-icon">{{ activeAccordion === 'pairings' ? '−' : '+' }}</span>
        </div>
        <transition name="slide">
          <div class="accordion-content" v-show="activeAccordion === 'pairings'">
            <div class="board-type-indicator">
              {{ tournament.board_type === 'LIC' ? 'LICHESS' : 'OTB' }}
            </div>
            
            <p class="instructions">
              The abbreviations used in the "result" column are explained at the end of the page.<br>
              Press <span class="result-btn">✅</span> to update the game result. See the FAQ for more information.
            </p>

            <div v-for="round in tournament.rounds" :key="round.number" class="round-section">
              <h3>round_{{ String(round.number).padStart(3, '0') }}</h3>
              <table class="pairings-table">
                <thead>
                  <tr>
                    <th>Table</th>
                    <th>White</th>
                    <th>Result</th>
                    <th>Black</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="game in round.games" :key="game.id">
                    <td>{{ game.table_number || '-' }}</td>
                    <td>{{ game.white_player.name }}</td>
                    <td>
                      <span v-if="game.result">{{ game.result }}</span>
                      <button v-else @click="openResultModal(game)" class="result-btn">
                        choose result
                      </button>
                    </td>
                    <td>{{ game.black_player.name }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Result Modal -->
    <div v-if="showResultModal" class="modal">
      <div class="modal-content">
        <h3>Enter Game Result</h3>
        <p>Game: {{ currentGame.white_player.name }} vs {{ currentGame.black_player.name }}</p>
        
        <div class="form-group">
          <label>Result:</label>
          <select v-model="resultInput" class="form-select" data-cy="result-select">
            <option value="">Select result</option>
            <option value="1-0">1-0 (White wins)</option>
            <option value="0-1">0-1 (Black wins)</option>
            <option value="½-½">½-½ (Draw)</option>
          </select>
        </div>

        <div v-if="tournament.board_type === 'OTB'" class="form-group">
          <label>Your Email (for verification):</label>
          <input 
            v-model="playerEmail" 
            type="email" 
            class="form-input"
            placeholder="Enter your registered email"
            data-cy="player-email-input"
          >
        </div>

        <div class="modal-actions">
          <button @click="submitResult" class="modal-btn submit-btn" data-cy="submit-result-btn">
            Submit
          </button>
          <button @click="closeModal" class="modal-btn cancel-btn">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()

const tournament = ref([])
const standings = ref([])
const players = ref([])
const activeAccordion = ref(null)
const showResultModal = ref(false)
const currentGame = ref(null)
const resultInput = ref('')
const playerEmail = ref('')
const API_URL = import.meta.env.VITE_DJANGO_URL


const fetchTournamentData = async () => {
  try {
    const tournamentId = route.params.tournament_id
    const response = await fetch(API_URL + `tournaments/${tournamentId}/`, {
      headers: {
        'Accept': 'application/json',
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    tournament.value = await response.json()

    const players = tournament.value.players
  } catch (error) {
    console.error('Error fetching tournament data:', error)
  }
}

const refreshData = () => {
  fetchTournamentData()
}

const toggleAccordion = (section) => {
  activeAccordion.value = activeAccordion.value === section ? null : section
}

const openResultModal = (game) => {
  currentGame.value = game
  resultInput.value = ''
  playerEmail.value = ''
  showResultModal.value = true
}

const closeModal = () => {
  showResultModal.value = false
}

const submitResult = async () => {
  try {
    const payload = {
      result: resultInput.value
    }
    
    if (tournament.value.board_type === 'OTB') {
      payload.email = playerEmail.value
    }

    await axios.patch(`/api/games/${currentGame.value.id}/`, payload)
    closeModal()
    refreshData()
  } catch (error) {
    console.error('Error submitting result:', error)
    alert(error.response?.data?.message || 'Error submitting result')
  }
}

onMounted(() => {
  fetchTournamentData()
})
</script>

<style scoped>
.tournament-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 10px;
}

h1 em {
  font-style: italic;
  color: #007bff;
}

.refresh-btn {
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.refresh-btn:hover {
  background-color: #e0e0e0;
}

.instructions {
  color: #666;
  margin-bottom: 20px;
  font-size: 0.95rem;
}

.divider {
  border: 0;
  height: 1px;
  background-color: #eee;
  margin: 20px 0;
}

/* Accordion Styles */
.accordion-container {
  margin-top: 20px;
}

.accordion-item {
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
  overflow: hidden;
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background-color: #f8f9fa;
  cursor: pointer;
  user-select: none;
}

.accordion-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.accordion-icon {
  font-size: 1.3rem;
  font-weight: bold;
}

.accordion-content {
  padding: 15px 20px;
  background-color: white;
}

/* Table Styles */
.standings-table, .pairings-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
  font-size: 0.9rem;
}

.standings-table th, 
.pairings-table th {
  background-color: #f8f9fa;
  padding: 10px;
  text-align: left;
  border-bottom: 2px solid #ddd;
}

.standings-table td, 
.pairings-table td {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.standings-table tr:hover, 
.pairings-table tr:hover {
  background-color: #f5f5f5;
}

/* Round Section */
.round-section {
  margin-bottom: 25px;
}

.round-section h3 {
  font-size: 1rem;
  color: #555;
  margin: 15px 0 10px 0;
  font-family: monospace;
}

/* Result Button */
.result-btn {
  background: none;
  border: none;
  color: #28a745;
  cursor: pointer;
  padding: 2px 5px;
  font-size: 0.9rem;
}

.result-btn:hover {
  text-decoration: underline;
}

.board-type-indicator {
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

/* Modal Styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 5px;
  width: 450px;
  max-width: 95%;
}

.modal-content h3 {
  margin-top: 0;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-select, .form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.modal-btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.submit-btn {
  background-color: #28a745;
  color: white;
  border: none;
}

.submit-btn:hover {
  background-color: #218838;
}

.cancel-btn {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
}

.cancel-btn:hover {
  background-color: #e2e6ea;
}

/* Animations */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 1000px;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
}
</style>