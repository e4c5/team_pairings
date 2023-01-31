import React, { useState, useEffect } from 'react';
import { useParams, Link } from "react-router-dom";

import getCookie from './cookie.js';
import { useTournament, useTournamentDispatch } from './context.jsx';
import Result from './result.jsx';
import { Autocomplete } from './autocomplete.jsx';

/**
 * A tournament round. 
 * if the round has ben paired will have set of results but no scores
 * 
 * When completed the round will have set of results with each one
 * containing a score
 * @param {*} props 
 * @returns 
 */
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

    function autoCompleteCheck(name, txt) {
        return name.toLowerCase().indexOf(txt) > -1
    }

    if (round?.paired && results) {
        
        return (
            <>
                {names && names.length && (
                    <div className='row'>
                        <div className='col'>
                            <Autocomplete suggestions={names} value={p1?.name ? p1.name : ''}
                                onChange={(e, newvalue) => changeName(e, newvalue)}
                                check={autoCompleteCheck}
                                />
                        </div>
                        <div className='col'>
                            <input value={won} placeholder="Games won" className='form-control'
                                onChange={e => handleChange(e, 'won')} />
                        </div>
                        <div className='col'>
                            <input value={score1} placeholder="Score for team1"  className='form-control'
                                onChange={e => handleChange(e, 'score1')} type='number' />
                        </div>
                        <div className='col'>
                            <input value={p2?.name ? p2.name : ""} placeholder="Opponent"
                                className='form-control'
                                size='small' onChange={e => { console.log('changed') }} />
                        </div>
                        <div className='col'>
                            <input value={lost} placeholder="Games won" disabled type='number' 
                                className='form-control' />
                        </div>
                        <div className='col'>
                            <input value={score2} placeholder="Score for team2" 
                                 className='form-control' type='number'
                                onChange={e => handleChange(e, 'score2')} />
                        </div>
                        <div className='col'>
                            <button className='btn btn-primary' onClick={e => addScore()}>Add score</button>
                        </div>
                    </div>

                )}
                
                    <table className='table table-striped table-dark table-bordered'>
                        <thead>
                            <tr>
                                <td sx={{ border: 1 }} align="left">Team 1</td>
                                <td sx={{ border: 1 }} align="right">Wins</td>
                                <td sx={{ border: 1 }} align="right">Total Score</td>
                                <td sx={{ border: 1 }} align="left">Team 2</td>
                                <td sx={{ border: 1 }} align="right">Wins</td>
                                <td sx={{ border: 1 }} align="right">Total Score</td>
                                <td sx={{ border: 1 }} align="right"></td>
                            </tr>
                        </thead>
                        <tbody>
                            {results.map((r, idx) => <Result key={r.id} r={r} 
                                index={idx} editScore={editScore} />)}
                        </tbody>
                    </table>
                
            </>

        )
    }
    else {
        return (
            <div>
                This is a round that has not yet been paired
                <div><button className='btn btn-primary' onClick={e => pair(e)}>Pair</button></div>
            </div>
        )
    }
}

export function Rounds(props) {
    const tournament = useTournament();
    const dispatch = useTournamentDispatch()

    return (
        <div>
            <div className='btn-group' aria-label="outlined primary button group">
                {
                    tournament?.rounds?.map(r => 
                            <Link to={'round/' + r.round_no} key={r.round_no}>
                                <button className='btn btn-primary'>{r.round_no}</button></Link>)
                }
            </div>
        </div>
    )
}

console.log('Rounds 0.01.8')