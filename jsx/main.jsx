//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';
import * as ReactDOM from 'react-dom';

import { Button, ButtonGroup, TextField }  from '@mui/material';
import { ListItem, List } from '@mui/material';
import { Table, TableBody, TableCell,
         TableContainer, TableHead, TableRow } from '@mui/material';
import {Paper, Tooltip} from '@mui/material';

import {
    createBrowserRouter,
    createRoutesFromElements,
    RouterProvider,
    useParams,
    Route, Routes,
    Link as RouterLink,
    Outlet,
    BrowserRouter
} from "react-router-dom";

import {Participant, Participants } from "./participant.jsx"
import {Tournament, Tournaments } from "./tournament.jsx"
import {Round, Rounds} from "./round.jsx"
import getCookie from './cookie.js';

import { Link, Switch, Box } from '@mui/material';

 
function App() {
    const [tournaments, setTournaments] = useState()

    useEffect(() => {
        if(tournaments == null) {
            fetch(`/api/tournament/`).then(resp=>resp.json()).then(json=>{
                setTournaments(json)
            })
        } 
    })

    return (
      <BrowserRouter>   
            <Routes>
                <Route path="/" element={<Tournaments tournaments={tournaments}/>}>
                    <Route path="/:slug/*" element={<Tournament  tournaments={tournaments}/>} />
                </Route>
            </Routes>
      </BrowserRouter>
    )
}


const div = document.getElementById('root')
const root = ReactDOM.createRoot(div) 
root.render(<App/>)
console.log('main.js 0.02')



 