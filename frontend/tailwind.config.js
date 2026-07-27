/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#F3F6F7",
        panel: "#FFFFFF",
        ink: "#10241F",
        inksoft: "#4B5D59",
        border: "#D8E0DF",
        accent: "#0F6E5C",
        accentsoft: "#E4F0EC",
        resistant: "#C4432B",
        resistantsoft: "#FBEAE6",
        intermediate: "#C98A1F",
        intermediatesoft: "#FBF2E0",
        susceptible: "#1C7A4D",
        susceptiblesoft: "#E7F5EC",
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        body: ["Inter", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
