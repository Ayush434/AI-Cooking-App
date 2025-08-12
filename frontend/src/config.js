// Frontend configuration
const config = {
    // API Base URL - change this for production
    // Change this line:
    API_BASE_URL: 'https://insertion-pain-surprising-contemporary.trycloudflare.com',
    
    // App settings
    APP_NAME: 'AI Cooking App',
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
      SEARCH_INGREDIENTS: '/api/recipes/search-ingredients'
    }
  };
  
  export default config;