module.exports = {
  chainWebpack: (config) => {
    const svgRule = config.module.rule("svg");

    svgRule.uses.clear();

    svgRule
      .use("babel-loader")
      .loader("babel-loader")
      .end()
      .use("vue-svg-loader")
      .loader("vue-svg-loader");
  },

  devServer: {
    allowedHosts: [
      'all',              // acepta todos los hosts (formato correcto en array)
      '.ngrok-free.app',  // dominio de ngrok (por si acaso)
      'localhost'         // el local
    ],
    disableHostCheck: true,
    host: '0.0.0.0',
    port: 8080
  },
};
