import React, { useState, useEffect } from 'react';
import { Button, ButtonGroup, TextField,
     Autocomplete, Box, IconButton
}  from '@mui/material';

import EditIcon from '@mui/icons-material/Edit';

import { Table, TableBody, TableCell,
         TableContainer, TableHead, TableRow } from '@mui/material';

import {Paper, Tooltip, Grid} from '@mui/material';


import {
    useParams,
    Link as RouterLink,
} from "react-router-dom";

import getCookie from './cookie.js';
import Result from './result.jsx';

import { Container } from '@mui/system';

export function Round(props) {
    const params = useParams()
    const [round, setRound] = React.useState(null)
    const [results, setResults] = React.useState(null)
    const [names, setNames] = React.useState([])
    const [resultId, setResultId] = React.useState(0)
    const [first, setFirst] = React.useState({})
    const [second, setSecond] = React.useState({})
    const [score1, setScore1] = React.useState('')
    const [score2, setScore2] = React.useState('')
    const [won, setWon] = React.useState('')
    const [lost, setLost] = React.useState('')

    function fetchResults(round) {
        if(! round) {
            return
        }
        fetch(`/api/${round.id}/result/`).then(resp => resp.json()
        ).then(json => {
            setResults(json)
            const left = []
            json.forEach(e =>{
                if(e.score1 || e.score2) {
                    //
                }
                else { 
                    left.push(e.first.name)
                    left.push(e.second.name)
                }
            })
            setNames(left)
        })
    }

    useEffect(() => {
        if(round == null || round.round_no != params.id) {
          
            // round numbers start from 0
            fetchResults(props.rounds[params.id -1])
            setRound(props.rounds[params.id -1])
        }
        else
        {
            if(results == null) {
                fetchResults(setRound(props.rounds[params.id -1]))
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

    function addScore(e) {
        fetch(`/api/${round.id}/result/${resultId}/`, { method: 'PUT', 'credentials': 'same-origin',
            headers: 
            {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ score1: score1, score2: score2, games_won: won, round: round.id})
        }).then(resp=>resp.json()).then(json=>{
            const res = [...results];
            for(let i = 0 ; i < res.length; i++) {
                if(results[i].first.name == first.name) {
                    res[i].score1 = score1;
                    res[i].score2 = score2;
                    res[i].games_won = won;
                    setResults(res)
                    break;
                }
            }
            setNames(names.filter(name => name != first.name && name != second.name))
            setFirst({})
            setSecond({})
            setWon('')
            setScore1('')
            setScore2('')
            props.updateStandings(json)
        })
    }

    function handleChange(e, name) {
        console.log(name)
        if(name == 'score1') {
            setScore1(e.target.value)
        }
        if(name == 'score2') {
            setScore2(e.target.value)
        }
        if(name == 'won') {
            setWon(e.target.value)
            setLost(props.tournament.team_size - e.target.value)
        }
    }

    function changeName(e, name) {
        
        results.forEach(result => {
            if(name == result.first.name) {
                setFirst(result.first)
                setSecond(result.second)
                setResultId(result.id)
            }
            if(name == result.second.name) {
                setFirst(result.second)
                setSecond(result.first)
                setResultId(result.id)
            }
            
        })
    }

    function editScore(e, index) {
        const result = results[index]
        setFirst(result.first)
        setSecond(result.second)
        setResultId(result.id)
        setNames([result.first.name, result.second.name])
        setScore1(result.score1)
        setScore2(result.score2)
        setWon(result.games_won)
    }

    if(round?.paired && results) {
        const tournament = props.tournament
        return(
            <>
              { names && names.length  && (
                    <Grid container>
                        <Grid item xs>
                            <Autocomplete options={names} freeSolo disableClearable 
                                size='small' value={first?.name ? first.name : ''}
                                onChange={ (e, newvalue) => changeName(e, newvalue)}
                                renderInput={(params) => (
                                        <TextField 
                                        {...params} placeholder="Team Name"
                                        label="Team Name"
                                        InputProps={{
                                            ...params.InputProps,
                                            type: 'search',
                                        }}
                                        />
                                )}/>
                        </Grid>
                        <Grid item xs>
                            <TextField value={won} placeholder="Games won"  size='small'
                                         onChange={ e => handleChange(e, 'won')} />
                        </Grid>
                        <Grid item xs>
                            <TextField value={score1} placeholder="Score for team1"  size='small'
                                         onChange={ e => handleChange(e, 'score1')} type='number' />
                        </Grid>
                        <Grid item xs>
                            <TextField value={ second?.name ? second.name : ""} placeholder="Opponent" 
                                 size='small' onChange={e => { console.log('changed')}} />
                        </Grid>
                        <Grid item xs>
                            <TextField value={lost} placeholder="Games won" disabled  type='number'  size='small' />
                        </Grid>
                        <Grid item xs>
                            <TextField value={score2} placeholder="Score for team2"  size='small'  type='number' 
                                         onChange={ e => handleChange(e, 'score2')} />
                        </Grid>   
                        <Grid item xs>
                            <Button variant='submit' onClick={e => addScore()}>Add score</Button>
                        </Grid>
                    </Grid>

                )}
                <TableContainer component={Paper}>
                    <Table sx={{ minWidth: 650}} aria-label="simple table">
                        <TableHead>
                        <TableRow>
                            <TableCell sx={{border:1}} align="left">Team 1</TableCell>
                            <TableCell sx={{border:1}} align="right">Wins</TableCell>
                            <TableCell sx={{border:1}} align="right">Total Score</TableCell>
                            <TableCell sx={{border:1}} align="left">Team 2</TableCell>
                            <TableCell sx={{border:1}} align="right">Wins</TableCell>
                            <TableCell sx={{border:1}} align="right">Total Score</TableCell>
                            <TableCell sx={{border:1}} align="right"></TableCell>
                        </TableRow>
                        </TableHead>
                        <TableBody>
                            { results.map((r,idx) => <Result  key={r.id} r={r} tournament={tournament} 
                                    index={idx} editScore={editScore}  />)}
                        </TableBody>
                    </Table>
                </TableContainer>
            </>
            
        )
    }
    else {
        return (
            <div>
                This is a round that has not yet been paired
                <div><Button variant='contained' onClick={e => pair(e)}>Pair</Button></div>
            </div>
        )
    }
}
  
export function Rounds(props) {
    const rounds = props.rounds
    
    if(rounds === null) {
        return <div></div>
    }
    else {
        return (
            <Box>
                
                <ButtonGroup variant="contained" aria-label="outlined primary button group">
                    {
                        rounds?.map(r => 
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

console.log('Rounds 0.01.8')