const axios = require('axios');

// Configuration de test
const API_BASE_URL = 'http://localhost:8000';
const TEST_ENDPOINTS = [
  '/',
  '/auth/login',
  '/auth/me',
  '/api/home',
  '/admin/roles',
  '/docs'
];

async function testConnectivity() {
  console.log('🔍 Test de connectivité Frontend-Backend\n');
  
  for (const endpoint of TEST_ENDPOINTS) {
    try {
      const response = await axios.get(`${API_BASE_URL}${endpoint}`, {
        timeout: 5000,
        validateStatus: (status) => status < 500 // Accepte les 401, 403, etc.
      });
      
      console.log(`✅ ${endpoint} - Status: ${response.status}`);
      
      if (endpoint === '/') {
        console.log('   📋 Endpoints disponibles:', Object.keys(response.data.endpoints || {}));
      }
      
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        console.log(`❌ ${endpoint} - Connexion refusée (Backend non démarré)`);
      } else if (error.response) {
        console.log(`⚠️  ${endpoint} - Status: ${error.response.status} (${error.response.statusText})`);
      } else {
        console.log(`❌ ${endpoint} - Erreur: ${error.message}`);
      }
    }
  }
  
  console.log('\n📊 Résumé:');
  console.log('- Si vous voyez des ✅ : Backend accessible');
  console.log('- Si vous voyez des ❌ : Backend non accessible');
  console.log('- Si vous voyez des ⚠️  : Endpoint accessible mais nécessite authentification');
}

// Test des variables d'environnement
function testEnvironmentVariables() {
  console.log('\n🔧 Test des variables d\'environnement:');
  
  const requiredVars = [
    'REACT_APP_API_URL',
    'REACT_APP_JWT_STORAGE_KEY'
  ];
  
  for (const varName of requiredVars) {
    const value = process.env[varName];
    if (value) {
      console.log(`✅ ${varName} = ${value}`);
    } else {
      console.log(`❌ ${varName} = Non définie`);
    }
  }
}

// Test de configuration JWT
function testJWTConfiguration() {
  console.log('\n🔐 Test de configuration JWT:');
  
  const jwtSecret = process.env.JWT_SECRET;
  if (jwtSecret) {
    console.log(`✅ JWT_SECRET = ${jwtSecret.substring(0, 10)}...`);
  } else {
    console.log('❌ JWT_SECRET = Non définie (utilise la valeur par défaut)');
  }
}

// Exécuter les tests
async function runTests() {
  console.log('🚀 Démarrage des tests de connectivité...\n');
  
  testEnvironmentVariables();
  testJWTConfiguration();
  await testConnectivity();
  
  console.log('\n✨ Tests terminés !');
}

// Exécuter si le script est appelé directement
if (require.main === module) {
  runTests().catch(console.error);
}

module.exports = { testConnectivity, testEnvironmentVariables, testJWTConfiguration }; 