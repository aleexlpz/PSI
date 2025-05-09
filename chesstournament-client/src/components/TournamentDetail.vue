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
                  <th v-if="selectedColumns.includes('WI')">Wins</th>
                  <th>Score</th>
                  <th v-if="selectedColumns.includes('BT')">Black</th>
                  <th v-if="selectedColumns.includes('BU')">BU</th>
                  <th v-if="selectedColumns.includes('BC')">BC</th>
                  <th v-if="selectedColumns.includes('BA')">BA</th>
                  <th v-if="selectedColumns.includes('SB')">SB</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="player in rankings" :key="player.rank">
                  <td>{{ player.rank }}</td>
                  <td>{{ player.name }}</td>
                  <td v-if="selectedColumns.includes('WI')">{{ player.wins }}</td>
                  <td>{{ player.score.toFixed(2) }}</td>
                  <td v-if="selectedColumns.includes('BT')">{{ player.blackGames }}</td>
                  <td v-if="selectedColumns.includes('BU')">{{ player.buchholz !== undefined ?
                    player.buchholz.toFixed(2) : '0.00' }}</td>
                  <td v-if="selectedColumns.includes('BC')">{{ player.buchholzCut1 !== undefined ?
                    player.buchholzCut1.toFixed(2) : '0.00' }}</td>
                  <td v-if="selectedColumns.includes('BA')">{{ player.buchholzAverage !== undefined ?
                    player.buchholzAverage.toFixed(2) : '0.00' }}</td>
                  <td v-if="selectedColumns.includes('SB')">{{ player.sonnebornBerger !== undefined ?
                    player.sonnebornBerger.toFixed(2) : '0.00' }}</td>
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
              Press <span class="result-btn">✅</span> to update the game result. See the <router-link to="/faq"
                class="text-link"><u>FAQ</u></router-link> for more information.
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
                    <th v-if="authStore.isAuthenticated">Choose Result</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(game, index) in round.games" :key="game.id">
                    <td>{{ index + 1 }}</td>
                    <td>{{ game.white_player }}</td>
                    <td>
                      <!-- Si el resultado ya está definido, mostrarlo como texto -->
                      <div v-if="game.result">
                        {{ game.result }}
                      </div>

                      <!-- Si no hay resultado, mostrar el desplegable y el botón de submit -->
                      <div v-else>
                        <select v-model="resultInputs[game.id]" class="result-select">
                          <option value="" disabled>choose result</option>
                          <option value="1-0">White wins (1-0)</option>
                          <option value="0-1">Black wins (0-1)</option>
                          <option value="½-½">Draw (½-½)</option>
                        </select>
                        <button v-if="tournament.board_type === 'LIC'" @click="submitLichessResult(game)"
                          class="result-btn">
                          ✅
                        </button>
                        <button v-else @click="submitOTBResult(game)" class="result-btn">
                          ✅
                        </button>
                      </div>
                    </td>
                    <td>{{ game.black_player }}</td>

                    <!-- Columna "Set Result" para administradores -->
                    <td v-if="authStore.isAuthenticated">
                      <select v-model="game.result" class="result-select">
                        <option value="" disabled>choose result</option>
                        <option value="w">White wins (w)</option>
                        <option value="b">Black wins (b)</option>
                        <option value="=">Draw (=)</option>
                      </select>
                      <button @click="submitOTBResultAdmin(game)" class="result-btn">✅</button>
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
          <input v-model="playerEmail" type="email" class="form-input" placeholder="Enter your registered email"
            data-cy="player-email-input">
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
const rankings = ref([])
const activeAccordion = ref(null)
const showResultModal = ref(false)
const currentGame = ref(null)
const resultInput = ref('')
const playerEmail = ref('')
const API_URL = import.meta.env.VITE_DJANGO_URL
const tournamentId = route.params.tournament_id
const selectedColumns = ref([]);
const resultInputs = ref({});

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

const submitOTBResultAdmin = async (game) => {
  try {
    const result = game.result;
    if (!result) {
      alert('Please select a result.');
      return;
    }
    const token = authStore.token; // O como guardes tu token
    const response = await axios.post(
      `${API_URL}admin_update_game/`,
      {
        game_id: game.id,
        otb_result: result,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    if (response.status === 200) {
      alert('Result updated by admin!');
      refreshData();
    } else {
      alert('Failed to update result: ' + (response.data?.message || 'Unknown error'));
    }
  } catch (error) {
    alert('Error updating result: ' + (error.response?.data?.message || error.message));
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

    // Contadores para las métricas
    const playerScores = {}; // Almacena los puntajes acumulados de cada jugador
    const blackGamesCount = {};
    const winsCount = {};
    const buchholz = {}; // Buchholz
    const buchholzCut1 = {}; // Buchholz Cut 1
    const buchholzAverage = {}; // Buchholz Average
    const sonnebornBerger = {}; // Sonneborn-Berger

    // Valores dinámicos del torneo
    const winPoints = tournament.value.win_points || 1.0;
    const drawPoints = tournament.value.draw_points || 0.5;
    const losePoints = tournament.value.lose_points || 0.0;

    // Procesar cada ronda y partida
    rounds.forEach(round => {
      round.games.forEach(game => {
        const whitePlayer = game.white_player;
        const blackPlayer = game.black_player;

        // Inicializar contadores si no existen
        if (!playerScores[whitePlayer]) playerScores[whitePlayer] = 0;
        if (!playerScores[blackPlayer]) playerScores[blackPlayer] = 0;
        if (!blackGamesCount[blackPlayer]) blackGamesCount[blackPlayer] = 0;
        if (!winsCount[whitePlayer]) winsCount[whitePlayer] = 0;
        if (!winsCount[blackPlayer]) winsCount[blackPlayer] = 0;

        // Contar partidas jugadas con negras
        if (blackPlayer) blackGamesCount[blackPlayer] += 1;

        // Determinar puntajes según el resultado
        let whiteScore = 0;
        let blackScore = 0;

        switch (game.result) {
          case 'w': // White wins
            whiteScore = winPoints;
            blackScore = losePoints;
            winsCount[whitePlayer] += 1;
            break;
          case 'b': // Black wins
            whiteScore = losePoints;
            blackScore = winPoints;
            winsCount[blackPlayer] += 1;
            break;
          case '=': // Draw
            whiteScore = drawPoints;
            blackScore = drawPoints;
            break;
          case 'H': // Bye
            whiteScore = winPoints;
            break;
          case '+': // Forfeit win
            whiteScore = winPoints;
            break;
          case '-': // Forfeit loss
            blackScore = winPoints;
            break;
          case 'U': // Unplayed
          default:
            break;
        }

        // Acumular puntajes de los jugadores
        playerScores[whitePlayer] += whiteScore;
        playerScores[blackPlayer] += blackScore;
      });
    });

    // Calcular Buchholz manualmente
    Object.keys(playerScores).forEach(player => {
      const opponentScores = [];

      rounds.forEach(round => {
        round.games.forEach(game => {
          if (game.white_player === player && game.black_player) {
            opponentScores.push(playerScores[game.black_player]);
          } else if (game.black_player === player && game.white_player) {
            opponentScores.push(playerScores[game.white_player]);
          }
        });
      });

      // Ordenar los puntajes de los oponentes
      opponentScores.sort((a, b) => a - b);

      // Calcular Buchholz (BU)
      buchholz[player] = opponentScores.reduce((sum, score) => sum + score, 0);

      // Calcular Buchholz Cut 1 (BC)
      // Calcular Buchholz Cut 1 (BC)
      if (opponentScores.length > 1) {
        // Excluir solo el puntaje más bajo
        buchholzCut1[player] = opponentScores
          .slice(1) // Excluir el primer elemento (el más bajo, ya que está ordenado)
          .reduce((sum, score) => sum + score, 0);
      } else {
        buchholzCut1[player] = 0; // No se puede calcular si hay menos de 2 oponentes
      }

      // Calcular Buchholz Average (BA)
      buchholzAverage[player] =
        opponentScores.length > 0
          ? opponentScores.reduce((sum, score) => sum + score, 0) /
          opponentScores.length
          : 0;
    });

    // Calcular Sonneborn-Berger manualmente
    rounds.forEach(round => {
      round.games.forEach(game => {
        const whitePlayer = game.white_player;
        const blackPlayer = game.black_player;

        let whiteScore = 0;
        let blackScore = 0;

        switch (game.result) {
          case 'w': // White wins
            whiteScore = winPoints;
            blackScore = losePoints;
            break;
          case 'b': // Black wins
            whiteScore = losePoints;
            blackScore = winPoints;
            break;
          case '=': // Draw
            whiteScore = drawPoints;
            blackScore = drawPoints;
            break;
          default:
            break;
        }

        if (blackPlayer) {
          sonnebornBerger[whitePlayer] =
            (sonnebornBerger[whitePlayer] || 0) + playerScores[blackPlayer] * whiteScore;
          sonnebornBerger[blackPlayer] =
            (sonnebornBerger[blackPlayer] || 0) + playerScores[whitePlayer] * blackScore;
        }
      });
    });

    // Agregar el conteo a los rankings
    rankings.value = rankings.value.map(player => ({
      ...player,
      blackGames: blackGamesCount[player.name] || 0,
      wins: winsCount[player.name] || 0,
      buchholz: buchholz[player.name] || 0,
      buchholzCut1: buchholzCut1[player.name] || 0,
      buchholzAverage: buchholzAverage[player.name] || 0,
      sonnebornBerger: sonnebornBerger[player.name] || 0, // Agregar SB al ranking
    }));
  } catch (error) {
    console.error('Error fetching round results:', error);
  }
};

const submitOTBResult = async (game) => {
  try {
    const result = resultInputs.value[game.id];
    console.log('Result:', result); // Depuración: verifica el resultado seleccionado
    if (!result) {
      alert('Please select a result.');
      return;
    }

    const response = await axios.post(`${API_URL}update_otb_game/`, {
      game_id: game.id,
      otb_result: result,
      email: playerEmail.value, // Verifica el correo del jugador
    });

    if (response.status === 200) {
      alert('OTB result submitted successfully!');
      game.result = result; // Actualiza el resultado en el frontend
      game.resultInput = ''; // Limpia el cuadro de texto
      refreshData(); // Refresca los datos
    } else {
      alert('Failed to submit OTB result.');
    }
  } catch (error) {
    console.error('Error submitting OTB result:', error);
    alert('An error occurred while submitting the result.');
  }
};

const submitLichessResult = async (game) => {
  try {
    const lichessGameId = resultInputs.value[game.id];
    if (!lichessGameId) {
      alert('Please enter a Lichess game ID.');
      return;
    }

    const response = await axios.post(`${API_URL}update_lichess_game/`, {
      game_id: game.id,
      lichess_game_id: lichessGameId,
    });

    if (response.status === 200) {
      alert('Lichess result updated successfully!');
      game.result = response.data.result; // Actualiza el resultado en el frontend
      game.resultInput = ''; // Limpia el cuadro de texto
      refreshData(); // Refresca los datos
    } else {
      alert('Failed to update Lichess result.');
    }
  } catch (error) {
    console.error('Error updating Lichess result:', error);
    alert('An error occurred while updating the result.');
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

    const data = await response.json();
    tournament.value = data;

    // Guardar las columnas seleccionadas en selectedColumns
    selectedColumns.value = data.rankingList || []; // Si no hay rankingList, usa un array vacío
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
      number: index + 1,
      ...round,
      games: round.games.map(game => {
        if (resultInputs.value[game.id] === undefined) {
          resultInputs.value[game.id] = '';
        }
        return { ...game };
      }),
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
.standings-table,
.pairings-table {
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
  background-color: rgba(0, 0, 0, 0.5);
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

.form-select,
.form-input {
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
  gap: 10px;
  /* Espaciado entre el desplegable y el botón */
}
</style>