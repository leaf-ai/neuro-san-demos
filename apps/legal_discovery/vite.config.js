import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    define: {
      __API_BASE__: JSON.stringify(env.VITE_API_BASE_URL || '')
    },
    build: {
      manifest: true,
      outDir: 'static',
      emptyOutDir: false,
      rollupOptions: {
        input: 'src/main.jsx',
        output: {
          entryFileNames: 'assets/[name]-[hash].js',
          chunkFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash][extname]'
        }
      }
    }
  };
});
