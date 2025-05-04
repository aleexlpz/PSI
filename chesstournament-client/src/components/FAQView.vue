<template>
  <div class="faq-container">
    <h1>FAQ</h1>
    
    <div class="faq-item">
      <h2>How can players update the result of a game?</h2>
      <p>Players can update game results by navigating to the tournament detail page, finding their game, and clicking the "Enter Result" button. For OTB tournaments, they will need to provide their email for verification.</p>
    </div>

    <div class="faq-item">
      <h2>How can administrators add players to a tournament?</h2>
      <p>Players are added using the CSV file format. Comma-separated values (CSV) is a text format that uses commas to separate values, and newlines to separate records.</p>
      
      <h3>CSV Format Requirements:</h3>
      <ul>
        <li>The first row must contain column names</li>
        <li>Columns must match player fields (name, email, lichess_username, etc.)</li>
        <li>For Lichess tournaments: <code>lichess_username</code> is required</li>
        <li>For OTB tournaments: <code>name</code> and <code>email</code> are required</li>
      </ul>
      
      <h3>Example CSV for Lichess:</h3>
      <pre>lichess_username
username1
username2
username3</pre>
      
      <h3>Example CSV for OTB:</h3>
      <pre>name, email, fide_rating_rapid
name1 familyname1, name1@gmail.com, 1234
name2 familyname2, name2@gmail.com, 1233
name3 familyname3, name3@gmail.com, 1239</pre>
    </div>
  </div>
</template>

<script setup>
// No se necesita lógica específica para esta vista
</script>

<style scoped>
.faq-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.faq-item {
  margin-bottom: 40px;
  border-bottom: 1px solid #eee;
  padding-bottom: 20px;
}

h2 {
  color: #333;
  margin-bottom: 10px;
}

h3 {
  margin-top: 15px;
  color: #555;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

ul {
  margin: 10px 0;
  padding-left: 20px;
}

code {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
}
</style>