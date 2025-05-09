<template>
  <div class="tournament-form">
    <form @submit.prevent="submitForm" data-cy="tournament-form">
      <h1>Create a Tournament</h1>

      <div class="form-section">
        <label for="tournament-name" data-cy="name-cypress-test">Tournament name</label>
        <input id="tournament-name" v-model="tournament.name" placeholder="“My tournament name”" class="form-input">
        <small class="hint">tournament full name</small>
        <small class="error-message" v-if="errors.name">Tournament name is required.</small>
      </div>

      <div class="form-section checkbox-section">
        <input type="checkbox" id="admin-update" v-model="tournament.onlyAdminCanUpdate"
          data-cy="only_administrative-cypress-test">
        <label for="admin-update">Only administrator can update games</label>
        <small class="hint">Set to false if user can update names. Otherwise only administrator can input the game
          results.</small>
      </div>

      <div class="form-section">
        <label for="pairing-system">Pairing system</label>
        <select id="pairing-system" v-model="tournament.pairingSystem" class="form-input"
          data-cy="single_round_robin-cypress-test">
          <option value="SR">Single Round Robin</option>
          <option value="DR">Double Round Robin</option>
          <option value="DD">Double Round Robin (same day)</option>
          <option value="SW">Swiss</option>
        </select>
        <small class="hint">Select the pairing system used in the tournament</small>
        <small class="error-message" v-if="errors.pairingSystem">Pairing system is required.</small>
      </div>

      <div class="form-section">
        <label for="board-type">Board type</label>
        <select id="board-type" v-model="tournament.boardType" class="form-input" data-cy="boardtype-cypress-test">
          <option value="LIC">Lichess</option>
          <option value="OTB">On The Board</option>
        </select>
        <small class="hint">Select the board type used in the tournament</small>
        <small class="error-message" v-if="errors.boardType">Board type is required.</small>
      </div>

      <div class="form-section points-section">
        <h3>Provide points awarded to player if:</h3>
        <div class="points-grid">
          <div class="points-row">
            <label>wins</label>
            <input type="number" v-model="tournament.points.win" step="0.1" class="points-input">
          </div>
          <div class="points-row">
            <label>draws</label>
            <input type="number" v-model="tournament.points.draw" step="0.1" class="points-input">
          </div>
          <div class="points-row">
            <label>loses</label>
            <input type="number" v-model="tournament.points.lose" step="0.1" class="points-input">
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3>Ranking method used in the tournament</h3>
        <small>Select ranking methods in the order in which should be applied</small>

        <div class="ranking-methods">
          <div class="ranking-method" v-for="method in rankingMethods" :key="method.value"
            data-cy="ranking-method-cypress-test">
            <input type="checkbox" :id="`method-option-${method.value.toLowerCase()}`" v-model="selectedRankingMethods"
              :value="method.value">
            <label :for="method.value">{{ method.label }} ({{ method.value }})</label>
          </div>
        </div>

        <div class="ranking-order">
          <h4>Order in which ranking methods are applied</h4>
          <div class="order-list">
            <span v-for="(method, index) in orderedRankingMethods" :key="method" class="order-item">
              {{ index + 1 }}. {{ getMethodLabel(method) }}
            </span>
            <span v-if="orderedRankingMethods.length === 0" class="empty-order">[]</span>
          </div>
        </div>
      </div>

      <div class="form-section">
        <label for="tournament-category">Tournament category (rapid, classical, etc)</label>
        <select id="tournament-category" v-model="tournament.category" class="form-input"
          data-cy="tournament_speed-cypress-test">
          <option value="CL">Classical</option>
          <option value="RA">Rapid</option>
          <option value="BL">Blitz</option>
          <option value="BU">Bullet</option>
        </select>
        <small class="hint">Games played on lichess, OTB, etc.</small>
        <small class="error-message" v-if="errors.category">Category is required.</small>
      </div>

      <div class="form-section">
        <h3>Players</h3>
        <p>Introduce players using the CSV format (see FAQ for details). Do NOT add trailing spaces</p>


        <textarea id="input_9" v-model="tournament.playersCSV" data-cy="players-input"
          class="players-textarea"></textarea>
        <small>List of players participating in the tournament</small><br>
      </div>
      <div>
        <small>Examples of CSV format are available in the <router-link to="/faq" class="text-link"><u>faq how can I add
              players to a tournament</u></router-link></small>
      </div>
      <small class="error-message" v-if="errors.tournament">Sorry, not all fields are filled out correctly.</small>
      <button class="register-button" @click="submitForm">Register</button>
    </form>
    <div v-if="errorMessage" class="error-message" data-cy="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

const API_URL = import.meta.env.VITE_DJANGO_URL;
const errorMessage = ref('')
export default {
  data() {
    return {
      tournament: {
        name: '',
        onlyAdminCanUpdate: true,
        pairingSystem: '',
        boardType: '',
        points: {
          win: 1.0,
          draw: 0.5,
          lose: 0.0
        },
        rankingMethods: [],
        category: '',
        playersCSV: ''
      },
      rankingMethods: [
        { value: 'BU', label: 'Buchholz' },
        { value: 'BC', label: 'Buchholz cut 1' },
        { value: 'BA', label: 'Buchholz average' },
        { value: 'SB', label: 'Sonneborn-Berger' },
        { value: 'WI', label: 'Number of wins' },
        { value: 'BT', label: 'Number of times played as Black' }
      ],
      selectedRankingMethods: [],
      orderedRankingMethods: [],
      errors: {
        name: false
      }
    };
  },
  methods: {
    getMethodLabel(value) {
      const method = this.rankingMethods.find(m => m.value === value);
      return method ? method.label : value;
    },
    transformTournamentData() {
      // Parse players CSV
      const playerRows = this.tournament.playersCSV.trim().split('\n');
      const headers = playerRows[0].split(',').map(header => header.trim());
      const players = [];

      for (let i = 1; i < playerRows.length; i++) {
        const values = playerRows[i].split(',').map(value => value.trim());
        const player = {};

        headers.forEach((header, index) => {
          player[header] = values[index] || '';
        });

        players.push(player);
      }

      return {
        name: this.tournament.name,
        only_administrative: this.tournament.onlyAdminCanUpdate,
        tournament_type: this.tournament.pairingSystem,
        tournament_speed: this.tournament.category,
        board_type: this.tournament.boardType,
        win_points: this.tournament.points.win,
        draw_points: this.tournament.points.draw,
        lose_points: this.tournament.points.lose,
        rankingList: this.selectedRankingMethods,
        players: players // Send the properly parsed player objects
      };
    },
    validatePlayersCSV() {
      const rows = this.tournament.playersCSV.trim().split('\n');

      if (rows.length < 2) {
        return 'Error: can not add players to tournament';
      }

      const headers = rows[0].split(',').map(header => header.trim());

      // Validate headers based on tournament type
      if (this.tournament.boardType === 'LIC') {
        if (!headers.includes('lichess_username')) {
          errorMessage.value = 'Error: can not add players to tournament';
          return 'Error: can not add players to tournament';
        }
      } else if (this.tournament.boardType === 'OTB') {
        if (!headers.includes('name') || !headers.includes('email')) {
          errorMessage.value = 'Error: can not add players to tournament';
          return 'Error: can not add players to tournament';
        }
      }

      // Validate each row
      for (let i = 1; i < rows.length; i++) {
        const values = rows[i].split(',').map(value => value.trim());

        if (this.tournament.boardType === 'LIC') {
          if (!values[headers.indexOf('lichess_username')]) {
            errorMessage.value = 'Error: can not add players to tournament';
            return 'Error: can not add players to tournament';
          }
        } else if (this.tournament.boardType === 'OTB') {
          if (!values[headers.indexOf('name')] || !values[headers.indexOf('email')]) {
            errorMessage.value = 'Error: can not add players to tournament';
            return 'Error: can not add players to tournament';
          }

          // Basic email validation
          const email = values[headers.indexOf('email')];
          if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            errorMessage.value = 'Error: can not add players to tournament';
            return 'Error: can not add players to tournament';
          }
        }
      }

      return null; // Valid CSV
    },
    async submitForm() {
      // Validar el CSV
      const csvError = this.validatePlayersCSV();
      if (csvError) {
        this.errors.playersCSV = csvError;
        return;
      }
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No token found');
        return;
      }

      // Validación básica
      this.errors.name = !this.tournament.name;
      this.errors.pairingSystem = !this.tournament.pairingSystem;
      this.errors.boardType = !this.tournament.boardType;
      this.errors.category = !this.tournament.category;

      if (!this.errors.name && !this.errors.pairingSystem && !this.errors.boardType && !this.errors.category) {
        const tournamentData = this.transformTournamentData();

        try {
          // Crear el torneo
          const response = await fetch(API_URL + 'tournament_create/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Token ${token}`
            },
            body: JSON.stringify(tournamentData)
          });

          if (response.ok) {
            const data = await response.json();

            // Crear las rondas usando el ID del torneo recién creado
            const roundResponse = await fetch(API_URL + 'create_round/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`
              },
              body: JSON.stringify({ tournament_id: data.tournament_id })
            });

            if (roundResponse.ok) {
              // Redirigir al detalle del torneo
              this.$router.push(`/tournamentdetail/${data.tournament_id}`);
            } else {
              console.error('Error creating rounds:', await roundResponse.text());
            }
          } else {
            console.error('Error creating tournament:', response.statusText);
          }
        } catch (error) {
          console.error('Error creating tournament or rounds:', error);
        }

      } else {
        this.errors.tournament = true;
      }
    }

  },
  watch: {
    selectedRankingMethods(newVal) {
      // Actualizamos los métodos ordenados cuando cambia la selección
      this.orderedRankingMethods = [...newVal];
      this.tournament.rankingMethods = [...newVal];
    }
  }
};

</script>

<style scoped>
.tournament-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  overflow: visible;
  min-height: 100vh;
}

h1 {
  font-size: 24px;
  margin-bottom: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  font-size: 24px;
  margin-bottom: 20px;
}

.form-section {
  margin-bottom: 25px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-section {
  margin-bottom: 25px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}

.error-message {
  color: #ff0000;
  display: block;
  margin-top: 5px;
}

.checkbox-section {
  display: flex;
  align-items: center;

}

.checkbox-section input[type="checkbox"] {
  margin-right: 10px;
}

.hint {
  display: block;
  color: #666;
  font-size: 12px;
  margin-top: 5px;
}

.points-section h3 {
  margin-bottom: 10px;
}

.points-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  max-width: 400px;
  max-width: 400px;
}

.points-row {
  display: flex;
  flex-direction: column;
}

.points-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.ranking-methods {
  margin: 15px 0;
  border: #0a002c solid 1px;
  padding: 10px;
}

.ranking-method {
  margin-bottom: 8px;
  display: flex;
  align-items: center;

}

.ranking-method input[type="checkbox"] {
  margin-right: 8px;
}

.ranking-order {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.order-list {
  margin-top: 10px;
  width: 100%;
}

.order-item {
  display: block;
  margin-bottom: 5px;
  align-items: center;
}

.empty-order {
  color: #999;
}

.players-textarea {
  width: 100%;
  height: 150px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: monospace;
  margin-top: 10px;
}

.register-button {
  background-color: #003de4;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: monospace;
  margin-top: 10px;
}

.register-button {
  background-color: #003de4;
  color: white;
  padding: 12px 20px;
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 20px;
  margin-bottom: 40px;
}

.register-button:hover {
  background-color: #0300a5;
}

.register-button:hover {
  background-color: #0300a5;
}
</style>