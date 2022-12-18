//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';
import * as ReactDOM from 'react-dom';

import { Button, ButtonGroup, TextField } from '@mui/material';
import { ListItem, List } from '@mui/material';
import {
    Table, TableBody, TableCell,
    TableContainer, TableHead, TableRow
} from '@mui/material';
import { Paper, Tooltip } from '@mui/material';

import {
    Route,
    Link as RouterLink, useLocation,
    Switch, Router
} from "wouter";

import { Participant, Participants } from "./participant.jsx"
import { Tournament, Tournaments } from "./tournament.jsx"
import { Round, Rounds } from "./round.jsx"
import getCookie from './cookie.js';
import { Link, Box } from '@mui/material';


function App() {
    const [tournaments, setTournaments] = useState()

    useEffect(() => {
        if (tournaments == null) {
            fetch(`/api/tournament/`).then(resp => resp.json()).then(json => {
                setTournaments(json)
            })
        }
    })
    const CurrentLoc = () => useLocation()[0];
    return (
        <div>
            <CurrentLoc/>
            <Route path="/">
                <Tournaments tournaments={tournaments} />
            </Route>
            <Route path="/:slug">
                {(params) => <Tournament params={params} tournaments={tournaments} />}
            </Route>
            {/* <Route path="/:slug/:id">
                    { (params) => <Participant params={params} tournaments={tournaments} /> }
                </Route> */}


        </div>

    )
}


const div = document.getElementById('root')
const root = ReactDOM.createRoot(div)
root.render(<App />)
console.log('main.js 0.02')



