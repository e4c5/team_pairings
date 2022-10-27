import React, { useState, useEffect } from 'react';
import { Button, ButtonGroup, TextField }  from '@mui/material';
import { Table, TableBody, TableCell,
         TableContainer, TableHead, TableRow } from '@mui/material';
import {Paper, Tooltip} from '@mui/material';
import { Link, Switch, Box } from '@mui/material';

import {
    useParams,
    Link as RouterLink,
    Outlet,
} from "react-router-dom";

import getCookie from './cookie.js';



export function Round(props) {
    const params = useParams()
    const [round, setRound] = React.useState(null)
    const [results, setResults] = React.useState(null)

    useEffect(() => {
        if(round == null) {
            // round numbers start from 0
            setRound(props.rounds[params.id -1])
            
        }
        else
        {
            if(results == null) {
                fetch(`/api/${round.id}/result/`).then(resp => resp.json()).then(json => setResults(json))
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

    console.log(results)
    if(round?.paired && results) {
        const tournament = props.tournament
        return(
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
                        { results.map(r => (
                            <TableRow key={r.id}>
                                <TableCell>{ r.first.name }</TableCell>
                                <TableCell>{ r.games_won } / { tournament.team_size - r.games_won }</TableCell>
                                <TableCell>{ r.score1 }</TableCell>
                                <TableCell>{ r.second.name }</TableCell>
                                <TableCell>{ tournament.team_size - r.games_won } / { r.games_won }</TableCell>
                                <TableCell>{ r.score1 }</TableCell>
                            </TableRow>
                        ))}
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

console.log('Rounds 0.01')