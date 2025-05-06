<template>
  <div class="faq-container">
    <h1>FAQ</h1>
    
    <div class="faq-item" v-for="(item, index) in faqItems" :key="index">
      <div class="faq-question" @click="toggleItem(index)">
        <h2>{{ item.question }}</h2>
        <span class="toggle-icon">{{ activeIndex === index ? '−' : '+' }}</span>
      </div>
      
      <transition name="slide">
        <div class="faq-answer" v-show="activeIndex === index">
          <div class="answer-content">
            <p>{{ item.answer }}</p>
            
            <div v-if="item.details">
              <h3>{{ item.details.title }}</h3>
              <ul v-if="item.details.list">
                <li v-for="(point, i) in item.details.list" :key="i">{{ point }}</li>
              </ul>
              
              <h3 v-if="item.details.example1">{{ item.details.example1.title }}</h3>
              <pre v-if="item.details.example1">{{ item.details.example1.content }}</pre>
              
              <h3 v-if="item.details.example2">{{ item.details.example2.title }}</h3>
              <pre v-if="item.details.example2">{{ item.details.example2.content }}</pre>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeIndex = ref(null)

const faqItems = ref([
  {
    question: "How can players update the result of a game?",
    answer: "Players can update game results by navigating to the tournament detail page, finding their game, and clicking the 'Enter Result' button. For OTB tournaments, they will need to provide their email for verification."
  },
  {
    question: "How can administrators add players to a tournament?",
    answer: "Players are added using the CSV file format. Comma-separated values (CSV) is a text format that uses commas to separate values, and newlines to separate records.",
    details: {
      title: "CSV Format Requirements:",
      list: [
        "The first row must contain column names",
        "Columns must match player fields (name, email, lichess_username, etc.)",
        "For Lichess tournaments: lichess_username is required",
        "For OTB tournaments: name and email are required"
      ],
      example1: {
        title: "Example CSV for Lichess:",
        content: "lichess_username\nusername1\nusername2\nusername3"
      },
      example2: {
        title: "Example CSV for OTB:",
        content: "name, email, fide_rating_rapid\nname1 familyname1, name1@gmail.com, 1234\nname2 familyname2, name2@gmail.com, 1233\nname3 familyname3, name3@gmail.com, 1239"
      }
    }
  }
])

const toggleItem = (index) => {
  activeIndex.value = activeIndex.value === index ? null : index
}
</script>

<style scoped>
.faq-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.faq-item {
  margin-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
}

.faq-question:hover {
  background-color: #f8f8f8;
}

.toggle-icon {
  font-size: 1.5rem;
  font-weight: bold;
  transition: transform 0.3s ease;
}

.faq-answer {
  overflow: hidden;
}

.answer-content {
  padding: 0 0 20px 0;
}

/* Animaciones */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.75s ease;
  max-height: 1000px; /* Ajusta según tu contenido máximo */
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

h2 {
  color: #333;
  margin: 0;
  font-size: 1.2rem;
}

h3 {
  margin: 15px 0 10px 0;
  color: #921d00;
  font-size: 1rem;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.9rem;
}

ul {
  margin: 10px 0;
  padding-left: 20px;
}

li {
  margin-bottom: 5px;
  font-size: 0.95rem;
}

p {
  margin-bottom: 15px;
  line-height: 1.5;
  font-size: 0.95rem;
}
</style>