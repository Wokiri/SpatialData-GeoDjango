const path = require('path')
const common = require("./webpack.common")
const { merge } = require("webpack-merge")
var HtmlWebpackPlugin = require("html-webpack-plugin")

module.exports = merge(
    common, {
        
        devServer: {
            compress: true,
            hot: false,
            port: 2021
        },
        devtool: 'inline-source-map',
        output: {
            path: path.resolve(__dirname, 'dev'),
            filename: '[name].js'
        },
        module: {
            rules: [
                {
                    test: /\.css$/i,
                    use: ['style-loader', 'css-loader']
                },

                {
                    //transpiles SCSS to js
                    test: /\.scss$/i,
                    use: [
                        'style-loader', //Injects css into DOM
                        'css-loader', //Turns css into common js
                        'sass-loader' //Turns scss into css
                    ]
                }
            ]
        },

        plugins: [
            new HtmlWebpackPlugin({
                template: './src/map.html'
            })
        ]

    }
)