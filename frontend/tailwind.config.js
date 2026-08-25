export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        grid: {
          ink: "#14213d",
          teal: "#0f766e",
          amber: "#f59e0b",
          line: "#d7dee8",
          surface: "#f8fafc"
        }
      },
      boxShadow: {
        panel: "0 12px 30px rgba(20, 33, 61, 0.08)"
      }
    }
  },
  plugins: []
};
