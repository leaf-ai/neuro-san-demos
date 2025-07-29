import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'static',
    emptyOutDir: false,
    rollupOptions: {
      input: 'src/main.jsx',
      output: {
        entryFileNames: 'bundle.js',
        assetFileNames: '[name][extname]'
      }
    }
  }
});
