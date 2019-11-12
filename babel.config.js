module.exports = function(api) {
  api.cache.using(() => process.env.NODE_ENV === 'development');

  return {
    presets: ['@babel/preset-env', '@babel/preset-react'],
    plugins: [
      '@babel/plugin-transform-runtime',
      '@babel/plugin-proposal-class-properties',
      '@babel/plugin-transform-runtime',
      'babel-plugin-idx'
    ]
  };
};
