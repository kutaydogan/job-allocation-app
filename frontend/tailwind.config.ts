import type { Config } from 'tailwindcss';
const config: Config = { content: ['./src/**/*.{ts,tsx}'], theme: { extend: { colors: { brand: { DEFAULT: '#ff9900', dark: '#e88a00' } } } }, plugins: [] };
export default config;
