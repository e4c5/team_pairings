//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';
import * as ReactDOM from 'react-dom';
import App from './app'


const div = document.getElementById('root')
const root = ReactDOM.createRoot(div) 
root.render(<App/>)
console.log('main.js 0.02.1')



 