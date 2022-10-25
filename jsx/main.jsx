//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';
import * as ReactDOM from 'react-dom';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import {
    createBrowserRouter,
    createRoutesFromElements,
    RouterProvider,
    useParams,
    Route,
    Routes,
    Link as RouterLink,
    BrowserRouter,
    Outlet
} from "react-router-dom";


import { Link, Switch } from '@mui/material';
 

function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) {
        return match[2];
    }
}

const Participants = (props) => {
    const tourny = props.tournament;

    return (
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Rank</TableCell>
              <TableCell align="right">Name</TableCell>
              <TableCell align="right">Seed</TableCell>
              <TableCell align="right">Round Wins</TableCell>
              <TableCell align="right">Game Wins</TableCell>
              <TableCell align="right">Spread</TableCell>
              <TableCell align="right">Offed</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {props.rows && props.rows.map((row, idx) => (
              <TableRow
                key={row.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell align="left">{ idx + 1}</TableCell>
                <TableCell component="th" scope="row">
                    <Link to={ `${row.id}` } component={RouterLink}>{row.name} {row.id}</Link>
                </TableCell>
                <TableCell align="right">{row.seed}</TableCell>
                <TableCell align="right">{row.round_wins}</TableCell>
                <TableCell align="right">{row.game_wins}</TableCell>
                <TableCell align="right">{row.spread}</TableCell>
                <TableCell align="right">{ (tourny && tourny.is_editable)
                    ? <Switch checked={row.offed != 0} onChange={ e => props.toggleParticipant(e, idx) }/>
                    : <Switch checked={row.offed != 0} onChange={ e => props.delParticipant(e, idx) }/> }
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

const Tournament = () => {
    const [name, setName] = React.useState('')
    const [seed, setSeed] = React.useState('')
    const [participants, setParticipants] = React.useState(null)
    const [tournament, setTournament] = React.useState(null)

    useEffect(() => {
        if(participants == null) {
            fetch('/api/participant/').then(resp => resp.json()).then(json =>{
                setParticipants(json)
                console.log('Updated')
            })
        }
        if(tournament == null) {
            fetch('/api/tournament/1/').then(resp => resp.json()).then(json =>{
                setTournament(json)
                console.log('Updated')
            })
        }
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
    const id = useParams();
    const [participant, setParticipant] = useState()

    useEffect(() => {
        if(participant == null) {
            fetch(`/api/participant/${id}`).then(resp=>resp.json()).then(json=>{
                setParticipant(json)
            })
        } 
    })

    return <div>Hello World </div>
}

const router = createBrowserRouter(
    createRoutesFromElements(
        <Route element={<Rounds/>}>
            <Route index element={<Tournament />} />
            <Route path="/:id" element={<Participant/>} />
            <Route path="/round/:id" element={<Round/>} />
        </Route>
    )
)

const div = document.getElementById('root')
const root = ReactDOM.createRoot(div) 
root.render(
    <RouterProvider router={router} />    
)
console.log('main.js 0.01.10')



 