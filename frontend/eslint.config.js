import react from "eslint-plugin-react";

const browserGlobals = {
  Blob: "readonly",
  File: "readonly",
  FormData: "readonly",
  URL: "readonly",
  clearTimeout: "readonly",
  console: "readonly",
  document: "readonly",
  event: "readonly",
  localStorage: "readonly",
  setTimeout: "readonly",
  window: "readonly"
};

export default [
  {
    ignores: ["dist/**", "node_modules/**"]
  },
  {
    files: ["src/**/*.{js,jsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: browserGlobals,
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        }
      }
    },
    plugins: {
      react
    },
    settings: {
      react: {
        version: "detect"
      }
    },
    rules: {
      "no-unused-vars": ["error", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
      "react/jsx-key": "error",
      "react/jsx-no-undef": "error",
      "react/jsx-uses-vars": "error",
      "react/no-unescaped-entities": "error",
      "react/react-in-jsx-scope": "off"
    }
  }
];
