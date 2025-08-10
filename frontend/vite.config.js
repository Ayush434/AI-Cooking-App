import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow external connections
    port: 3000,
    allowedHosts: [
      '0.0.0.0',
      // Cloudflare tunnel hosts
      'hill-substantial-solaris-tie.trycloudflare.com',
      'vendors-starsmerchant-friend-pda.trycloudflare.com',
      // Allow all trycloudflare.com subdomains
      '.trycloudflare.com'
    ]
  }
})