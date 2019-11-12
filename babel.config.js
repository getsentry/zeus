module.exports = function(api) {
  api.cache.using(() => process.env.NODE_ENV === 'development');

  return {
    presets: ['@babel/preset-env', '@babel/react'],
    plugins: [
      '@babel/plugin-proposal-class-properties',
      '@babel/plugin-transform-runtime',
      'babel-plugin-idx'
    ]
  };
};
