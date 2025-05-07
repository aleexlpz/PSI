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
                  <th>Wins</th>
                  <th>Score</th>
                  <th>No. games played with Black</th>
                  <th>BU</th>
                  <th>BC</th>
                  <th>BA</th>
                  <th>SB</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="player in rankings" :key="player.rank">
                  <td>{{ player.rank }}</td>
                  <td>{{ player.name }}</td>
                  <td>{{ player.wins }}</td>
                  <td>{{ player.score }}</td>
                  <td>{{ player.blackGames }}</td>
                  <td>{{ player.buchholz }}</td>
                  <td>{{ player.buchholzCut1 }}</td>
                  <td>{{ player.buchholzAverage }}</td>
                  <td>{{ player.sonnebornBerger }}</td>
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
          <!-- Tipo de torneo -->
          <div class="board-type-indicator">
            {{ tournament.board_type === 'LIC' ? 'LICHESS' : 'OTB' }}
          </div>

          <!-- Instrucciones -->
          <p class="instructions">
            Press <span class="result-btn">✅</span> to update the game result. See the FAQ for more information.
          </p>

          <!-- Rondas -->
          <div v-for="round in tournament.rounds" :key="round.id" class="round-section">
            <h3>{{ round.name }}</h3>
            <table class="pairings-table">
              <thead>
                <tr>
                  <th>Table</th>
                  <th>White</th>
                  <th>Result</th>
                  <th>Black</th>
                  <th v-if="authStore.isAuthenticated">Choose Result</th> <!-- Nueva columna combinada -->
                </tr>
              </thead>
              <tbody>
                <tr v-for="(game, index) in round.games" :key="game.id">
                  <td>{{ index + 1 }}</td>
                  <td>{{ game.white_player }}</td>
                  <td>{{ game.result || 'type gameID' }}</td> <!-- Muestra el resultado o un marcador de posición -->
                  <td>{{ game.black_player }}</td>
                  <td v-if="authStore.isAuthenticated"> <!-- Columna combinada -->
                    <div class="choose-result">
                      <select
                        v-model="game.result"
                        class="result-select"
                      >
                        <option value="" disabled>choose result</option>
                        <option value="1-0">White wins (1-0)</option>
                        <option value="0-1">Black wins (0-1)</option>
                        <option value="½-½">Draw (½-½)</option>
                        <option value="">Unknown result</option>
                      </select>
                      <button @click="submitGameResult(game)" class="result-btn">✅</button>
                    </div>
                  </td>
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
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const tournament = ref([])
const standings = ref([])
const rankings = ref([])
const activeAccordion = ref(null)
const showResultModal = ref(false)
const currentGame = ref(null)
const resultInput = ref('')
const playerEmail = ref('')
const API_URL = import.meta.env.VITE_DJANGO_URL
const tournamentId = route.params.tournament_id

const fetchRankings = async () => {
  try {
    const response = await fetch(API_URL + `get_ranking/${tournamentId}/`, {
      headers: {
        'Accept': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    rankings.value = Object.values(data).sort((a, b) => a.rank - b.rank);
  } catch (error) {
    console.error('Error fetching players:', error);
    rankings.value = [];
  }
};

const fetchRoundResults = async () => {
  try {
    const response = await fetch(API_URL + `get_round_results/${tournamentId}/`, {
      headers: {
        'Accept': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const rounds = await response.json();

    // Contar partidas jugadas con negras y victorias
    const blackGamesCount = {};
    const winsCount = {};
    const buchholz = {}; // Buchholz
    const buchholzCut1 = {}; // Buchholz cut 1
    const buchholzAverage = {}; // Buchholz average
    const sonnebornBerger = {}; // Sonneborn-Berger

    rounds.forEach(round => {
      round.games.forEach(game => {
        // Contar partidas jugadas con negras
        if (game.black_player) {
          blackGamesCount[game.black_player] = (blackGamesCount[game.black_player] || 0) + 1;
        }

        // Contar victorias
        if (game.result === 'w') {
          winsCount[game.white_player] = (winsCount[game.white_player] || 0) + 1;
        } else if (game.result === 'b') {
          winsCount[game.black_player] = (winsCount[game.black_player] || 0) + 1;
        }

        // Calcular Buchholz y Sonneborn-Berger
        const whitePlayer = game.white_player;
        const blackPlayer = game.black_player;

        if (game.result) {
          const whiteScore = game.result === 'w' ? 1 : game.result === '½' ? 0.5 : 0;
          const blackScore = game.result === 'b' ? 1 : game.result === '½' ? 0.5 : 0;

          // Buchholz: suma de los puntajes de los oponentes
          buchholz[whitePlayer] = (buchholz[whitePlayer] || 0) + (game.black_score || 0);
          buchholz[blackPlayer] = (buchholz[blackPlayer] || 0) + (game.white_score || 0);

          // Sonneborn-Berger: suma de los puntajes de los oponentes multiplicados por el resultado
          sonnebornBerger[whitePlayer] = (sonnebornBerger[whitePlayer] || 0) + (game.black_score || 0) * whiteScore;
          sonnebornBerger[blackPlayer] = (sonnebornBerger[blackPlayer] || 0) + (game.white_score || 0) * blackScore;
        }
      });
    });

    // Calcular Buchholz cut 1 y Buchholz average
    Object.keys(buchholz).forEach(player => {
      const scores = rounds
        .flatMap(round => round.games)
        .filter(game => game.white_player === player || game.black_player === player)
        .map(game => game.white_player === player ? game.black_score : game.white_score)
        .sort((a, b) => a - b);

      buchholzCut1[player] = scores.slice(1, -1).reduce((sum, score) => sum + score, 0); // Excluye el más alto y el más bajo
      buchholzAverage[player] = scores.length > 0 ? scores.reduce((sum, score) => sum + score, 0) / scores.length : 0;
    });

    // Agregar el conteo a los rankings
    rankings.value = rankings.value.map(player => ({
      ...player,
      blackGames: blackGamesCount[player.name] || 0,
      wins: winsCount[player.name] || 0,
      buchholz: buchholz[player.name] || 0,
      buchholzCut1: buchholzCut1[player.name] || 0,
      buchholzAverage: buchholzAverage[player.name] || 0,
      sonnebornBerger: sonnebornBerger[player.name] || 0,
    }));
  } catch (error) {
    console.error('Error fetching round results:', error);
  }
};

const submitGameResult = async (game) => {
  try {
    const response = await axios.post(`${API_URL}submit_game_result/`, {
      game_id: game.id,
      result: game.result,
    });

    if (response.status === 200) {
      alert('Result submitted successfully!');
    } else {
      alert('Failed to submit result.');
    }
  } catch (error) {
    console.error('Error submitting game result:', error);
    alert('An error occurred while submitting the result.');
  }
};

const toggleAccordion = (accordionName) => {
  activeAccordion.value = activeAccordion.value === accordionName ? null : accordionName;
};

const fetchTournamentData = async () => {
  try {
    const response = await fetch(API_URL + `tournaments/${tournamentId}/`, {
      headers: {
        'Accept': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    tournament.value = await response.json();
  } catch (error) {
    console.error('Error fetching tournament data:', error);
  }
};

const fetchGamesByRounds = async () => {
  try {
    const response = await fetch(`${API_URL}get_round_results/${tournamentId}/`, {
      headers: {
        'Accept': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const rounds = await response.json();
    console.log('Fetched games by rounds:', rounds); // Depuración: verifica los datos obtenidos

    // Actualiza las rondas en el estado del torneo
    tournament.value.rounds = rounds.map((round, index) => ({
      number: index + 1, // Asigna un número de ronda basado en el índice
      ...round
    }));
  } catch (error) {
    console.error('Error fetching games by rounds:', error);
  }
};

const refreshData = () => {
  fetchTournamentData();
  fetchRankings();
  fetchRoundResults();
  fetchGamesByRounds();
};

onMounted(() => {
  fetchTournamentData();
  fetchRankings();
  fetchRoundResults();
  fetchGamesByRounds();
});
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
  color: #aa8406;
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

.round-section {
  margin-bottom: 25px;
}

.round-section h3 {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 10px;
}

.pairings-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

.pairings-table th,
.pairings-table td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: left;
}

.pairings-table th {
  background-color: #f8f9fa;
}

.pairings-table tr:hover {
  background-color: #f5f5f5;
}

.result-input {
  width: 100px;
  padding: 5px;
  margin-right: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}


.result-btn {
  background: none;
  border: none;
  color: #28a745;
  cursor: pointer;
  font-size: 1rem;
}

.result-btn:hover {
  text-decoration: underline;
}

.result-select {
  width: 150px;
  padding: 5px;
  border: 1px solid #ffffff;
  border-radius: 4px;
  font-size: 0.9rem;
  margin-right: 5px;
}
.choose-result {
  display: flex;
  align-items: center;
  gap: 10px; /* Espaciado entre el desplegable y el botón */
}
</style>