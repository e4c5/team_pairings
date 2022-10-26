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

import Participants from "./participant.jsx"
import getCookie from './cookie.js';

import { Link, Switch, Box } from '@mui/material';

 

const Tournament = (props) => {
    const params = useParams()
    const [name, setName] = React.useState('')
    const [seed, setSeed] = React.useState('')
    const [participants, setParticipants] = React.useState(null)
    const [tournament, setTournament] = React.useState(null)

    console.log('Tournament')
    useEffect(() => {
        props.tournaments?.map(t => {
            if(t.slug == params.slug) {
                if(tournament != t) {
                    setTournament(t)
                    fetch(`/api/${t.id}/participant/`).then(resp => resp.json()).then(json =>{
                        setParticipants(json)
                    })
                }
            }
        })    
    })

    const handleChange = (e, p) => {
        if(p == 'name') {
            setName(e.target.value) 
        }
        else {
            setSeed(e.target.value)
        }
    }

    function toggleParticipant(e, idx) {
        const p = participants[idx];
        p['offed'] = p.offed == 0 ? 1 : 0;
        console.log(`/api/participant/${p.id}`)
        fetch(`/api/participant/${p.id}/`, 
            { method: 'PUT', 'credentials': 'same-origin',
              headers: 
              {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
              },
              body: JSON.stringify(p)
            }).then(resp => resp.json()).then(json => {
                const old = [...participants]
                old[idx] = json
                setParticipants(old)
        })
    }

    function delParticipant(e, idx) {
        console.log('delete');
    }


    const add = e => {
        fetch('/api/participant/', 
            { method: 'POST', 'credentials': 'same-origin',
              headers: 
              {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
              },
              body: JSON.stringify({ tournament: 1, name: name, seed: seed})
            }).then(resp => resp.json()).then(json => {
                setParticipants([...participants, json])
                setSeed(seed + 1)
                setName('')
            })
    }

    return (
        <div>
            <Participants rows={participants} tournament={tournament} 
                delParticipant={ delParticipant } toggleParticipant = { toggleParticipant}
            /> 
            <TextField size='small' placeholder='Name' 
                value={name} onChange={ e => handleChange(e, 'name')} />
            <TextField size='small' placeholder='seed' type='number'
                value={seed} onChange={ e => handleChange(e, 'seed')} />
            <Button variant="contained" onClick = { e => add(e)}>Add</Button>
        </div>)
}

function Round(props) {
    const params = useParams()
    const [round, setRound] = React.useState(null)
    const [results, setResults] = React.useState(null)

    useEffect(() => {
        if(round == null) {
            fetch(`/api/round/${params.id}/`).then(resp => resp.json()).then(json =>{
                setRound(json)
                if(json.pair) {
                    fetch(`/api/result/?round=${params.id}/`).then(resp=>resp.json()
                    ).then(json=>{
                        setResults(json)
                    })
                }
            })
        }
    })

    if(round?.paired) {
        <TableContainer component={Paper}>
            <Table sx={{ minWidth: 650 }} aria-label="simple table">
                <TableHead>
                  <TableRow>
                    <TableCell>Rank</TableCell>
                    <TableCell align="right">Team 1</TableCell>
                    <TableCell align="right">W/L</TableCell>
                    <TableCell align="right">Round Wins</TableCell>
                    <TableCell align="right">Spread</TableCell>
                    <TableCell align="right">Team 2</TableCell>
                    <TableCell align="right">W/L</TableCell>
                    <TableCell align="right">Round Wins</TableCell>
                    <TableCell align="right">Spread</TableCell>
                    
                  </TableRow>
                </TableHead>
                <TableBody>

                </TableBody>
            </Table>
        </TableContainer>
    }
    else {
        return (
            <div>
                This is a round that has not yet been paired
                <div><Button>Pair</Button></div>
            </div>
        )
    }
}
  
const Rounds = (props) => {
    const [rounds, setRounds] = React.useState(null)
    useEffect(() => {
        if(rounds == null) {
            fetch('/api/round/').then(resp => resp.json()).then(json =>{
                setRounds(json)
            })
        }
    })
    
    if(rounds == null) {
        return <div><Outlet/></div>
    }
    else {
        return (
            <>
            <Outlet rounds={rounds} />
            <Link to="/" component={RouterLink}>S. Thomas Scrabble Bash</Link>
            <ButtonGroup variant="contained" aria-label="outlined primary button group">
                {
                    rounds.map(r => 
                        <Tooltip title={r.pairing_system + ' based on ' + r.based_on + ' with ' + r.repeats + ' repeats'}  key={r.id}>
                            <Button component={RouterLink} 
                              to={ '/round/' + r.round_no} >{r.round_no}</Button>
                        </Tooltip>
                    ) 
                }
            </ButtonGroup>
            </>
        )
    }
}

const Participant = (props) => {
    const params = useParams();
    const [participant, setParticipant] = useState()

    useEffect(() => {
        if(participant == null) {
            fetch(`/api/participant/${params.id}`).then(resp=>resp.json()).then(json=>{
                setParticipant(json)
            })
        } 
    })

    return <div>Hello World </div>
}
function Tournaments(props) {
    const id = useParams();

    return (
        <div>
            <List>
            { props.tournaments?.map(t => 
                <ListItem key={t.id}>
                    <Link to={"/" + t.slug} component={RouterLink} >{ t.name }</Link>
                </ListItem>) 
            }
            </List>
            <Outlet/>
        </div>
    )
}

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
                    <Route path="/:slug" element={<Tournament  tournaments={tournaments}/>} />
                    <Route element={<Rounds/>}>
                        <Route path="/tournament/:id" element={<Participant/>} />
                        <Route path="/round/:id" element={<Round/>} />
                    </Route>
                </Route>
            </Routes>
      </BrowserRouter>
    )
}


const div = document.getElementById('root')
const root = ReactDOM.createRoot(div) 
root.render(<App/>)
console.log('main.js 0.01.13')



 