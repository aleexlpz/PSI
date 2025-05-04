<template>
  <div class="create-tournament">
    <h1>Create a Tournament</h1>
    <form @submit.prevent="submitForm" class="tournament-form">
      <div class="form-group">
        <label>Tournament name:</label>
        <input 
          v-model="form.name" 
          required
          data-cy="tournament-name-input"
        >
      </div>

      <div class="form-group">
        <label>Board type:</label>
        <select 
          v-model="form.board_type" 
          @change="handleBoardTypeChange"
          data-cy="board-type-select"
        >
          <option value="OTB">Over-the-board (OTB)</option>
          <option value="LIC">Lichess (LIC)</option>
        </select>
      </div>

      <div v-if="form.board_type === 'LIC'" class="form-group">
        <label>Lichess usernames (comma separated):</label>
        <textarea 
          v-model="form.lichess_usernames" 
          placeholder="username1, username2, username3"
          data-cy="lichess-usernames-input"
        ></textarea>
      </div>

      <div v-else class="form-group">
        <label>Upload players CSV:</label>
        <input 
          type="file" 
          @change="handleFileUpload"
          accept=".csv"
          data-cy="players-csv-input"
        >
      </div>

      <div class="form-group">
        <label>Points:</label>
        <div class="points-grid">
          <div>
            <label>Win:</label>
            <input 
              v-model="form.win_points" 
              type="number" 
              step="0.5" 
              min="0"
              data-cy="win-points-input"
            >
          </div>
          <div>
            <label>Draw:</label>
            <input 
              v-model="form.draw_points" 
              type="number" 
              step="0.5" 
              min="0"
              data-cy="draw-points-input"
            >
          </div>
          <div>
            <label>Loss:</label>
            <input 
              v-model="form.loss_points" 
              type="number" 
              step="0.5" 
              min="0"
              data-cy="loss-points-input"
            >
          </div>
        </div>
      </div>

      <button type="submit" data-cy="create-tournament-submit">Create Tournament</button>
    </form>

    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const errorMessage = ref('')

const form = ref({
  name: '',
  board_type: 'OTB',
  lichess_usernames: '',
  players_file: null,
  win_points: 1.0,
  draw_points: 0.5,
  loss_points: 0.0
})

const handleBoardTypeChange = () => {
  // Reset related fields when board type changes
  form.value.lichess_usernames = ''
  form.value.players_file = null
}

const handleFileUpload = (event) => {
  form.value.players_file = event.target.files[0]
}

const submitForm = async () => {
  try {
    const formData = new FormData()
    
    // Append all form fields to FormData
    Object.keys(form.value).forEach(key => {
      if (form.value[key] !== null) {
        formData.append(key, form.value[key])
      }
    })

    const response = await axios.post('/api/tournaments/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    router.push(`/tournamentdetail/${response.data.id}`)
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Error creating tournament'
    console.error('Error creating tournament:', error)
  }
}
</script>

<style scoped>
.create-tournament {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.tournament-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

input, select, textarea {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.points-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.points-grid > div {
  display: flex;
  flex-direction: column;
}

button {
  padding: 10px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

button:hover {
  background-color: #218838;
}

.error-message {
  color: red;
  margin-top: 15px;
}
</style>