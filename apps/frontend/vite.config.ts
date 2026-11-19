import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit()
	],
	resolve: {
		alias: {
			'$lib': path.resolve(__dirname, 'src/lib'),
			'#lib': path.resolve(__dirname, 'src/lib')
		}
	},
	server: {
		port: 3000,
		strictPort: false,
		proxy: {
			'/api/v1': {
				target: 'http://localhost:8080',
				changeOrigin: true
			},
			'/api-opt': {
				target: 'http://localhost:8001',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api-opt/, '')
			},
			'/api-ai': {
				target: 'http://localhost:8000',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api-ai/, '')
			}
		}
	},
	preview: {
		port: 3000,
		strictPort: false
	}
});
