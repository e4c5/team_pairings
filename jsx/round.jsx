import React, { useState, useEffect } from 'react';

import {
    Button, ButtonGroup, TextField,
    Autocomplete, Box,
} from '@mui/material';

import {
    Table, TableBody, TableCell,
    TableContainer, TableHead, TableRow
} from '@mui/material';

import { Paper, Tooltip, Grid } from '@mui/material';


import {
    useParams,
    Link as RouterLink,
} from "react-router-dom";

import getCookie from './cookie.js';
import { useTournament, useTournamentDispatch } from './context.jsx';
import Result from './result.jsx';



export function Round(props) {
    const params = useParams()
    const [round, setRound] = useState(null)
    const [results, setResults] = useState(null)
    const [names, setNames] = useState([])
    const [resultId, setResultId] = useState(0)
    const [p1, setP1] = useState({})
    const [p2, setP2] = useState({})
    const [score1, setScore1] = useState('')
    const [score2, setScore2] = useState('')
    const [won, setWon] = useState('')
    const [lost, setLost] = useState('')
    const tournament = useTournament();
    const dispatch = useTournamentDispatch()

    function fetchResults(round) {
        if (!round) {
            return
        }
        fetch(`/api/tournament/${tournament.id}/${round.id}/result/`).then(resp => resp.json()
        ).then(json => {
            setResults(json)
            const left = []
            json.forEach(e => {
                if (e.score1 || e.score2) {
                    //
                }
                else {
                    left.push(e.p1.name)
                    left.push(e.p2.name)
                }
            })
            setNames(left)
        })
    }

    useEffect(() => {

        if (round == null || round.round_no != params.id) {
            if(tournament) {
                // round numbers start from 0
                fetchResults(tournament.rounds[params.id - 1])
                setRound(tournament.rounds[params.id - 1])
            }
        }
        else {
            if (results == null) {
                fetchResults(setRound(tournament.rounds[params.id - 1]))
            }
        }
    },[tournament, round])

    function pair() {
        fetch(`/api/tournament/${tournament.id}/round/${params.id}/pair/`,
            {
                method: 'POST', 'credentials': 'same-origin',
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
        fetch(`/api/tournament/${tournament.id}/${round.id}/result/${resultId}/`, {
            method: 'PUT', 'credentials': 'same-origin',
            headers:
            {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ score1: score1, score2: score2, games_won: won, round: round.id })
        }).then(resp => resp.json()).then(json => {
            const res = [...results];
            for (let i = 0; i < res.length; i++) {
                if (results[i].p1.name == p1.name) {
                    res[i].score1 = score1;
                    res[i].score2 = score2;
                    res[i].games_won = won;
                    setResults(res)
                    break;
                }
            }
            setNames(names.filter(name => name != p1.name && name != p2.name))
            setP1({})
            setP2({})
            setWon('')
            setScore1('')
            setScore2('')
            props.updateStandings(json)
        })
    }

    function handleChange(e, name) {

        if (name == 'score1') {
            setScore1(e.target.value)
        }
        if (name == 'score2') {
            setScore2(e.target.value)
        }
        if (name == 'won') {
            setWon(e.target.value)
            setLost(tournament.team_size - e.target.value)
        }
    }

    function changeName(e, name) {

        results.forEach(result => {
            if (name == result.p1.name) {
                setP1(result.p1)
                setP2(result.p2)
                setResultId(result.id)
            }
            if (name == result.p2.name) {
                setP1(result.p2)
                setP2(result.p1)
                setResultId(result.id)
            }

        })
    }

    function editScore(e, index) {
        const result = results[index]
        setP1(result.p1)
        setP2(result.p2)
        setResultId(result.id)
        setNames([result.p1.name, result.p2.name])
        setScore1(result.score1)
        setScore2(result.score2)
        setWon(result.games_won)
    }

    if (round?.paired && results) {
        
        return (
            <>
                {names && names.length && (
                    <Grid container>
                        <Grid item xs>
                            <Autocomplete options={names} freeSolo disableClearable
                                size='small' value={p1?.name ? p1.name : ''}
                                onChange={(e, newvalue) => changeName(e, newvalue)}
                                renderInput={(params) => (
                                    <TextField
                                        {...params} placeholder="Team Name"
                                        label="Team Name"
                                        InputProps={{
                                            ...params.InputProps,
                                            type: 'search',
                                        }}
                                    />
                                )} />
                        </Grid>
                        <Grid item xs>
                            <TextField value={won} placeholder="Games won" size='small'
                                onChange={e => handleChange(e, 'won')} />
                        </Grid>
                        <Grid item xs>
                            <TextField value={score1} placeholder="Score for team1" size='small'
                                onChange={e => handleChange(e, 'score1')} type='number' />
                        </Grid>
                        <Grid item xs>
                            <TextField value={p2?.name ? p2.name : ""} placeholder="Opponent"
                                size='small' onChange={e => { console.log('changed') }} />
                        </Grid>
                        <Grid item xs>
                            <TextField value={lost} placeholder="Games won" disabled type='number' size='small' />
                        </Grid>
                        <Grid item xs>
                            <TextField value={score2} placeholder="Score for team2" size='small' type='number'
                                onChange={e => handleChange(e, 'score2')} />
                        </Grid>
                        <Grid item xs>
                            <Button variant='submit' onClick={e => addScore()}>Add score</Button>
                        </Grid>
                    </Grid>

                )}
                <TableContainer component={Paper}>
                    <Table sx={{ minWidth: 650 }} aria-label="simple table">
                        <TableHead>
                            <TableRow>
                                <TableCell sx={{ border: 1 }} align="left">Team 1</TableCell>
                                <TableCell sx={{ border: 1 }} align="right">Wins</TableCell>
                                <TableCell sx={{ border: 1 }} align="right">Total Score</TableCell>
                                <TableCell sx={{ border: 1 }} align="left">Team 2</TableCell>
                                <TableCell sx={{ border: 1 }} align="right">Wins</TableCell>
                                <TableCell sx={{ border: 1 }} align="right">Total Score</TableCell>
                                <TableCell sx={{ border: 1 }} align="right"></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {results.map((r, idx) => <Result key={r.id} r={r} 
                                index={idx} editScore={editScore} />)}
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
    const tournament = useTournament();
    const dispatch = useTournamentDispatch()

    console.log(tournament?.rounds)
    return (
        <Box>
            <ButtonGroup variant="contained" aria-label="outlined primary button group">
                {
                    tournament?.rounds?.map(r =>
                        <Tooltip title={r.pairing_system + ' based on ' + r.based_on + ' with ' + r.repeats + ' repeats'} key={r.id}>
                            <Button component={RouterLink}
                                to={'round/' + r.round_no} >{r.round_no}</Button>
                        </Tooltip>
                    )
                }
            </ButtonGroup>
        </Box>
    )
}

console.log('Rounds 0.01.8')