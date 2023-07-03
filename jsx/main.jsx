//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';
import * as ReactDOM from 'react-dom';
import App from './app'
import { BrowserRouter } from "react-router-dom";
import { TournamentProvider} from './context.jsx';
import { ThemeProvider } from './theme.jsx';

const div = document.getElementById('root')
const root = ReactDOM.createRoot(div) 
root.render(<BrowserRouter>
                <ThemeProvider>
                    <TournamentProvider><App/></TournamentProvider>
                </ThemeProvider>
            </BrowserRouter>)

console.log('main.js 0.03')



 