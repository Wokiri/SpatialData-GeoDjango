module.exports = {
  entry: {
    // surveyor_location_js: './src/js/surveyor_location_js.js',
    // surveyor_location_js: './src/js/surveyor_location_js.js',
    // parcels_map_js: './src/js/parcels_map.js',
    // parcels_map_css: './src/js/parcels_map_css.js',
    // parcel_detail_map: './src/js/parcel_detail_map.js',
    // controls_map_js: './src/js/controls_map_js.js',
    shp_preview_map: './src/js/shapefile_preview_map.js',
    open_layers_css: './src/js/open_layers_css.js',
    bootstrap_css: './src/js/bootstrap_css.js',
  },

  module: {
    rules: [
      {
        //Babel loader transpiles the latest version of JS to old js
        // Babel loader compiles ES2015 into ES5 for complete cross-browser support
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
            plugins: ['@babel/plugin-transform-runtime']
          }
        }
      },

      {
        //HTML loader Exports HTML as string, hence it can capture file extention names
        test: /\.html$/,
        use: ["html-loader"]
      },

    ]
  }

};
