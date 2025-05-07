<template>
  <div class="tournament-form">
    <h1>Create a Tournament</h1>
    
    <div class="form-section">
      <label for="tournament-name">Tournament name</label>
      <input 
        id="tournament-name" 
        v-model="tournament.name" 
        placeholder="“My tournament name”" 
        class="form-input"
      >
      <small class="hint">tournament full name</small>
      <small class="error-message" v-if="errors.name">Tournament name is required.</small>
    </div>
    
    <div class="form-section checkbox-section">
      <input 
        type="checkbox" 
        id="admin-update" 
        v-model="tournament.onlyAdminCanUpdate"
      >
      <label for="admin-update">Only administrator can update games</label>
      <small class="hint">Set to false if user can update names. Otherwise only administrator can input the game results.</small>
    </div>
    
    <div class="form-section">
      <label for="pairing-system">Pairing system</label>
      <select 
        id="pairing-system" 
        v-model="tournament.pairingSystem" 
        class="form-input"
      >
        <option value="Single-round-robin">Single Round Robin</option>
        <option value="Double-round-robin">Double Round Robin</option>
        <option value="Double-round-robin">Double Round Robin (same day)</option>
        <option value="swiss">Swiss</option>
      </select>
      <small class="hint">Select the pairing system used in the tournament</small>
      <small class="error-message" v-if="errors.pairingSystem">Pairing system is required.</small>
    </div>
    
    <div class="form-section">
      <label for="board-type">Board type</label>
      <select 
        id="board-type" 
        v-model="tournament.boardType" 
        class="form-input"
      >
        <option value="lichess">Lichess</option>
        <option value="otb">On The Board</option>
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
        <div class="ranking-method" v-for="method in rankingMethods" :key="method.value">
          <input 
            type="checkbox" 
            :id="method.value" 
            v-model="selectedRankingMethods" 
            :value="method.value"
          >
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
      <select 
        id="tournament-category" 
        v-model="tournament.category" 
        class="form-input"
      >
        <option value="classical">Classical</option>
        <option value="rapid">Rapid</option>
        <option value="blitz">Blitz</option>
        <option value="bullet">Bullet</option>
      </select>
      <small class="hint">Games played on lichess, OTB, etc.</small>
      <small class="error-message" v-if="errors.category">Category is required.</small>
    </div>
    
    <div class="form-section">
      <h3>Players</h3>
      <p>Introduce players using the CSV format (see FAQ for details). Do NOT add trailing spaces</p>
      
      
      <textarea 
        v-model="tournament.playersCSV" 
        class="players-textarea" 
        placeholder="Ejemplo: username,rating,title&#10;player1,1500,GM&#10;player2,1400,IM"
      ></textarea>
      <small>List of players participating in the tournament</small><br>
    </div>
    <div>
      <small>Examples of CSV format are available in the <router-link to="/faq" class="text-link"><u>faq how can I add players to a tournament</u></router-link></small>
    </div>
    <small class="error-message" v-if="errors.tournament">Sorry, not all fields are filled out correctly.</small>
    <button class="register-button" @click="submitForm">Register</button>
  </div>
</template>

<script>
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
  computed: {
    selectedRankingMethods() {
      return this.rankingMethods.filter(
        method => this.selectedRankingMethods.includes(method.value)
      );
    }
  },
  methods: {
    getMethodLabel(value) {
      const method = this.rankingMethods.find(m => m.value === value);
      return method ? method.label : value;
    },
    submitForm() {
      // Validación básica
      this.errors.name = !this.tournament.name;
      this.errors.pairingSystem = !this.tournament.pairingSystem;
      this.errors.boardType = !this.tournament.boardType;
      this.errors.playersCSV = !this.tournament.playersCSV;
      this.errors.category = !this.tournament.category;

      if (!this.errors.name && !this.errors.pairingSystem && !this.errors.boardType && !this.errors.category && !this.errors.playersCSV) {
        // Simula la creación del torneo (puedes reemplazar esto con una llamada al backend)
        const tournamentId = Math.random().toString(36).substr(2, 9); // Generar un ID único simulado

        // Guardar las columnas seleccionadas en localStorage
        localStorage.setItem(
          `tournament_columns_${tournamentId}`,
          JSON.stringify(this.selectedRankingMethods)
        );

        console.log('Formulario enviado:', this.tournament);
        console.log('Columnas seleccionadas:', this.selectedRankingMethods);

        // Redirigir al detalle del torneo (simulado)
        this.$router.push(`/tournament/${tournamentId}`);
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

.form-input {
  width: 100%;
  padding: 8px;
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
  border: #0a002c  solid 1px;
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
  align-items:flex-start;
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
  color: white;
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
</style>