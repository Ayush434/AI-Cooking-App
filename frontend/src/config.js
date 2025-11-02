// Frontend configuration
const config = {
    // API Base URL - change this for production
    // Change this line:
    // API_BASE_URL: 'https://ai-cooking-app.onrender.com/',
    API_BASE_URL: 'http://127.0.0.1:5000',
    
    // App settings
    APP_NAME: 'SnackHack',
    VERSION: '1.0.0',
    
    // Feature flags
    ENABLE_VALIDATION: true,
    ENABLE_AUTOCOMPLETE: true,
    ENABLE_IMAGE_DETECTION: true,
    
    // API endpoints
    ENDPOINTS: {
      HEALTH: '/health',
      DETECT_INGREDIENTS: '/api/recipes/detect-ingredients',
      GET_RECIPES: '/api/recipes/get-recipes',
      VALIDATE_INGREDIENT: '/api/recipes/validate-ingredient',
      VALIDATE_INGREDIENTS: '/api/recipes/validate-ingredients',
      AUTOCOMPLETE: '/api/recipes/autocomplete',
      SEARCH_INGREDIENTS: '/api/recipes/search-ingredients',
      NUTRITION_FACTS: '/api/recipes/nutrition-facts',
      TOGGLE_FAVOURITE: '/api/recipes/toggle-favourite',
      FAVOURITE_RECIPES: '/api/recipes/favourite-recipes',
      SAVED_RECIPE: '/api/recipes/saved-recipe',
      MY_RECIPES: '/api/recipes/my-recipes',
      // Auth endpoints
      LOGIN: '/api/auth/login',
      REGISTER: '/api/auth/register',
      PROFILE: '/api/auth/profile',
      REFRESH: '/api/auth/refresh',
      VALIDATE: '/api/auth/validate'
    }
  };
  
  export default config;