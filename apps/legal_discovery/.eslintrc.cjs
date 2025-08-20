module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: ['eslint:recommended'],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  globals: {
    __API_BASE__: 'readonly',
    vis: 'readonly',
  },
  rules: {
    'no-unused-vars': 'off',
  },
};
