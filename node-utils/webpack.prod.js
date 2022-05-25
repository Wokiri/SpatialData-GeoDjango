const path = require('path')
const common = require("./webpack.common")
const { merge } = require("webpack-merge")
const { CleanWebpackPlugin } = require('clean-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const MinimizeCssAssetsPlugin = require('css-minimizer-webpack-plugin')
const TerserPlugin = require('terser-webpack-plugin')
var HtmlWebpackPlugin = require("html-webpack-plugin")

module.exports = merge(
    common, {
        
        output: {
            path: path.resolve(__dirname, 'production'),
            filename: '[name].js'
        },

        optimization: {
            minimizer: [
                new MinimizeCssAssetsPlugin(),
                new TerserPlugin()
            ]
        },

        module: {
        rules: [{
                test: /\.css$/i,
                use: [
                    MiniCssExtractPlugin.loader, //Extracts css into files
                    'css-loader' //Tuns css into common js
                ]
            },
            {
                //transpiles SCSS to js
                test: /\.scss$/i,
                use: [
                    MiniCssExtractPlugin.loader, //Extract css into files
                    'css-loader', //Turns css into common js
                    'sass-loader' //Turns scss into css
                ]
            }
        ]
    },

        plugins: [
            new CleanWebpackPlugin(),
            new CleanWebpackPlugin({ cleanStaleWebpackAssets: false }),
            new MiniCssExtractPlugin({ filename: '[name].css' }),
            new HtmlWebpackPlugin({
                template: './src/map.html',
                minify: {
                    collapseWhitespace: true,
                    removeComments: true, // false for Vue SSR to find app placeholder
                    removeEmptyAttributes: true,
                }
            })
        ]

    }
)