/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
    theme: {
        extend: {
            colors: {
                ink: '#0f131a',
                panel: '#171d27',
                card: '#1d2430',
                line: '#2b3443',
                accent: '#ffc247',
                accentStrong: '#ffad0f',
            },
            fontFamily: {
                display: ['"Source Serif 4"', 'serif'],
                body: ['"Space Grotesk"', 'sans-serif'],
            },
            boxShadow: {
                glow: '0 18px 50px rgba(0, 0, 0, 0.35)',
            },
        },
    },
    plugins: [],
};
