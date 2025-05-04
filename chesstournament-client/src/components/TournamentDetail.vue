<template>
  <div class="tournament-detail">
    <h1>Tournament: {{ tournament.name }}</h1>
    
    <button @click="refreshData" data-cy="refresh-button">Refresh Page</button>

    <div class="tabs">
      <button 
        @click="activeTab = 'standings'" 
        :class="{ active: activeTab === 'standings' }"
        data-cy="standings-tab"
      >
        Standing
      </button>
      <button 
        @click="activeTab = 'pairings'" 
        :class="{ active: activeTab === 'pairings' }"
        data-cy="pairings-tab"
      >
        Pairings/Results
      </button>
    </div>

    <div v-if="activeTab === 'standings'" class="standings">
      <h2>Current Standings</h2>
      <table>
        <thead>
          <tr>
            <th>Position</th>
            <th>Player</th>
            <th>Points</th>
            <th v-for="tiebreak in tournament.tiebreak_methods" :key="tiebreak">
              {{ tiebreak }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(player, index) in standings" :key="player.id">
            <td>{{ index + 1 }}</td>
            <td>{{ player.name }}</td>
            <td>{{ player.points }}</td>
            <td v-for="tiebreak in tournament.tiebreak_methods" :key="tiebreak">
              {{ player[tiebreak.toLowerCase()] || '-' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="pairings">
      <h2>{{ tournament.board_type === 'LIC' ? 'LICHESS' : 'OTB' }}</h2>
      <p>The abbreviations used in the "result" column are explained at the end of the page.</p>
      
      <div v-for="round in tournament.rounds" :key="round.number" class="round">
        <h3>Round {{ round.number }}</h3>
        <table>
          <thead>
            <tr>
              <th>Table</th>
              <th>White</th>
              <th>Result</th>
              <th>Black</th>
              <th v-if="authStore.isAdmin">Result (Admin)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="game in round.games" :key="game.id">
              <td>{{ game.table_number }}</td>
              <td>{{ game.white_player.name }}</td>
              <td>
                <span v-if="game.result">{{ game.result }}</span>
                <button 
                  v-else 
                  @click="openResultModal(game)"
                  data-cy="update-result-btn"
                >
                  Enter Result
                </button>
              </td>
              <td>{{ game.black_player.name }}</td>
              <td v-if="authStore.isAdmin">
                <select 
                  v-model="game.result" 
                  @change="updateGameResult(game)"
                  data-cy="admin-result-select"
                >
                  <option value="">-</option>
                  <option value="1-0">1-0 (White wins)</option>
                  <option value="0-1">0-1 (Black wins)</option>
                  <option value="½-½">½-½ (Draw)</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Result Modal -->
    <div v-if="showResultModal" class="modal">
      <div class="modal-content">
        <h3>Enter Game Result</h3>
        <p>Game: {{ currentGame.white_player.name }} vs {{ currentGame.black_player.name }}</p>
        
        <div class="form-group">
          <label>Result:</label>
          <select v-model="resultInput" data-cy="result-select">
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
            data-cy="player-email-input"
          >
        </div>

        <div class="modal-actions">
          <button @click="submitResult" data-cy="submit-result-btn">Submit</button>
          <button @click="closeModal">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const route = useRoute()
const authStore = useAuthStore()

const tournament = ref({ rounds: [], players: [] })
const standings = ref([])
const activeTab = ref('standings')
const showResultModal = ref(false)
const currentGame = ref(null)
const resultInput = ref('')
const playerEmail = ref('')

const fetchTournamentData = async () => {
  try {
    const [tournamentRes, standingsRes] = await Promise.all([
      axios.get(`/api/tournaments/${route.params.tournament_id}/`),
      axios.get(`/api/tournaments/${route.params.tournament_id}/standings/`)
    ])
    
    tournament.value = tournamentRes.data
    standings.value = standingsRes.data
  } catch (error) {
    console.error('Error fetching tournament data:', error)
  }
}

const refreshData = () => {
  fetchTournamentData()
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

const updateGameResult = async (game) => {
  try {
    await axios.patch(`/api/games/${game.id}/`, {
      result: game.result
    })
    refreshData()
  } catch (error) {
    console.error('Error updating game result:', error)
    alert(error.response?.data?.message || 'Error updating result')
  }
}

onMounted(() => {
  fetchTournamentData()
})
</script>

<style scoped>
.tournament-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.tabs button {
  padding: 8px 16px;
  background: none;
  border: 1px solid #ddd;
  cursor: pointer;
}

.tabs button.active {
  background-color: #007bff;
  color: white;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
}

.round {
  margin-bottom: 30px;
}

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
  padding: 20px;
  border-radius: 5px;
  width: 400px;
  max-width: 90%;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
</style>