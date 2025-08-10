import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow external connections
    port: 3000,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '0.0.0.0',
      // Add your cloudflared hosts
      'hill-substantial-solaris-tie.trycloudflare.com',
      'vendors-starsmerchant-friend-pda.trycloudflare.com',
      // Allow all trycloudflare.com subdomains
      '.trycloudflare.com'
    ]
  }
})