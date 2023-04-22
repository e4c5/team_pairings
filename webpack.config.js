const webpack = require('webpack');
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const fs = require('fs')

const port = process.env.PORT || 3000;

class HtmlUpdater {
    apply(compiler) {
      compiler.hooks.emit.tapAsync("HtmlUpdater", (compilation, callback) => {

        let html = fs.readFileSync('tournament/templates/index.html','utf-8')
        const regex = /<script[^>]*src="\/static\/js\/(.*?)"[^>]*>/; // regular expression that matches the src attribute in script tags
        const mode = compiler.options.mode;

        html = html.replace(regex, function(match, group1) {
            if(mode === 'production') {
                let f = "";
                Object.keys(compilation.assets).forEach(
                    fileName => { 
                        if(fileName.endsWith('js')) {
                            f = match.replace(group1, fileName);
                        }
                    }
                )
                return f
            }
            else {
                return match.replace(group1, 'bundle.js');
            }
        });

        fs.writeFileSync('tournament/templates/index.html', html);
        callback();
      });
    }
}


/**
 * 
 * @returns name of the bundle file for production that will be a
 *    hashed file name and for development it will be just bundle.js
 */
function generateName() {
   
    const idx = process.argv.indexOf('--mode')
    if( idx !== -1 && process.argv[idx + 1] === 'production') {
        const name = 'bundle[contenthash].js'
        return name
    }
    else {
        return 'bundle.js'
    }
}

module.exports = {
  mode: 'development',  
  entry: './jsx/main.jsx',

  output: {
    filename: generateName(),
    path: path.resolve(__dirname, 'tournament/static/js'),
  },
  devtool: 'inline-source-map',
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: ['babel-loader']
      },
      {
        test: /\.css$/,
        use: [
          {
            loader: 'style-loader'
          },
          {
            loader: 'css-loader',
            options: {
              modules: true,
              localsConvention: 'camelCase',
              sourceMap: true
            }
          }
        ]
      }
    ]
  },
  plugins: [
    new HtmlUpdater()
  ],
  devServer: {
    host: 'localhost',
    port: port,
    historyApiFallback: true,
    open: true
  }
};
