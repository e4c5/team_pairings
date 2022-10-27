import React, { useState, useEffect } from 'react';
import { Button, ButtonGroup, TextField,
     Autocomplete, Box  
}  from '@mui/material';

import { Table, TableBody, TableCell,
         TableContainer, TableHead, TableRow } from '@mui/material';
import {Paper, Tooltip} from '@mui/material';


import {
    useParams,
    Link as RouterLink,
    Outlet,
} from "react-router-dom";

import getCookie from './cookie.js';


function Result({r, tournament}) {
    const editable = document.getElementById('editable')

    function resultIn() {
        if(editable) {

        }
        return (
            <TableRow>
                <TableCell>{ r.first.name }</TableCell>
                <TableCell>{ r.games_won } / { tournament.team_size - r.games_won }</TableCell>
                <TableCell>{ r.score1 }</TableCell>
                <TableCell>{ r.second.name }</TableCell>
                <TableCell>{ tournament.team_size - r.games_won } / { r.games_won }</TableCell>
                <TableCell>{ r.score1 }</TableCell>
            </TableRow>
        )
    }

    function resultOut() {
        return (
            <TableRow>
                <TableCell>{ r.first.name }</TableCell>
                <TableCell></TableCell>
                <TableCell></TableCell>
                <TableCell>{ r.second.name }</TableCell>
                <TableCell></TableCell>
                <TableCell></TableCell>
            </TableRow>
        )
    }

    if(r.score1) {
        return resultIn()
    }
    else {
        return resultOut();
    }
}

export function Round(props) {
    const params = useParams()
    const [round, setRound] = React.useState(null)
    const [results, setResults] = React.useState(null)
    const [names, setNames] = React.useState([])
    const [first, setFirst] = React.useState({})
    const [second, setSecond] = React.useState({})
    const [score1, setScore1] = React.useState('')
    const [score2, setScore2] = React.useState('')

    useEffect(() => {
        if(round == null) {
            // round numbers start from 0
            setRound(props.rounds[params.id -1])
            
        }
        else
        {
            if(results == null) {
                fetch(`/api/${round.id}/result/`).then(resp => resp.json()
                ).then(json => {
                    setResults(json)
                    const left = []
                    json.forEach(e =>{
                        left.push(e.first.name)
                        left.push(e.second.name)
                    })
                    setNames(left)
                })
            }
        }
    })

    function pair() {
        fetch(`/api/round/${params.id}/pair/`,
            { method: 'POST', 'credentials': 'same-origin',
              headers: 
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
            body: JSON.stringify({})
        }).then(resp => resp.json()).then(json => {
            console.log('paired')
        })
        
    }

    function handleChange(e, name) {
        if('name' == 'score1') {
            setScore1(e.target.value)
        }
        if('name' == 'score2') {
            setScore2(e.target.value)
        }
    }
    function changeName(e, name) {
        
        results.forEach(result => {
            if(name == result.first.name) {
                setFirst(result.first)
                setSecond(result.second)
            }
            if(name == result.second.name) {
                setFirst(result.second)
                setSecond(result.first)
            }
        })
    }

    if(round?.paired && results) {
        const tournament = props.tournament
        return(
        
            <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} aria-label="simple table">
                    <TableHead>
                    <TableRow>
                        <TableCell align="right">Team 1</TableCell>
                        <TableCell align="right">Wins</TableCell>
                        <TableCell align="right">Total Score</TableCell>
                        <TableCell align="right">Team 2</TableCell>
                        <TableCell align="right">Wins</TableCell>
                        <TableCell align="right">Total Score</TableCell>
                        
                    </TableRow>
                    </TableHead>
                    <TableBody>
                        { names && (
                            <TableRow>
                                <TableCell>
                                <Autocomplete options={names} freeSolo disableClearable
                                    onChange={ (e, newvalue) => changeName(e, newvalue)}
                                    renderInput={(params) => (
                                            <TextField
                                            {...params}
                                            label="Team Name"
                                            InputProps={{
                                                ...params.InputProps,
                                                type: 'search',
                                            }}
                                            />
                                    )}/>
                                </TableCell>
                                <TableCell><TextField/></TableCell>
                                <TableCell><TextField disabled value={second?.name}/></TableCell>
                                <TableCell><TextField value={score1} placeholder="Score for team1"
                                         onChange={ e => handleChange(e, 'score1')} /></TableCell>
                                <TableCell><TextField/></TableCell>
                                <TableCell><TextField/></TableCell>
                            </TableRow>
                        )}
                        { results.map(r => <Result  key={r.id} r={r} tournament={tournament} />)}
                    </TableBody>
                </Table>
            </TableContainer>
            
            
        )
    }
    else {
        return (
            <div>
                This is a round that has not yet been paired
                <div><Button onClick={e => pair(e)}>Pair</Button></div>
            </div>
        )
    }
}
  
export function Rounds(props) {
    const rounds = props.rounds
    
    if(rounds == null) {
        return <div><Outlet/></div>
    }
    else {
        return (
            <Box>
                <Outlet rounds={rounds} />
                <ButtonGroup variant="contained" aria-label="outlined primary button group">
                    {
                        rounds.map(r => 
                            <Tooltip title={r.pairing_system + ' based on ' + r.based_on + ' with ' + r.repeats + ' repeats'}  key={r.id}>
                                <Button component={RouterLink} 
                                to={ 'round/' + r.round_no} >{r.round_no}</Button>
                            </Tooltip>
                        ) 
                    }
                </ButtonGroup>
            </Box>
        )
    }
}

console.log('Rounds 0.01.4mi')