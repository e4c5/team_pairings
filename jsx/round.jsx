import React, { useState, useEffect, useReducer } from 'react';
import { useParams, Link } from "react-router-dom";

import getCookie from './cookie.js';
import { useTournament, useTournamentDispatch } from './context.jsx';
import Result from './result.jsx';
import { Autocomplete } from './autocomplete.jsx';

function reducer(state, action) {
    switch (action.type) {
        case "typed":
            return { ...state, name: action.name }

        case 'autoComplete':
            return { ...state, p1: action.p1, p2: action.p2, resultId: action.resultId }

        case 'p1':
            return { ...state, p1: action.p1 }

        case 'p2':
            return { ...state, p1: action.p2 }

        case 'won':
            return { ...state, won: action.won }

        case 'lost':
            return { ...state, lost: action.lost }

        case 'pending':
            return { ...state, pending: action.names }

        case 'score1':
            return { ...state, score1: action.score1 }

        case 'score2':
            return { ...state, score2: action.score1 }

        case 'replace':
            return { ...action.value }

        case 'reset':
            return {
                ...state, score1: null, score2: null,
                p1: null, p2: null, won: null, name: null,
            }
    }
}
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
    const [current, dispatch] = useReducer(reducer, {})
    const [round, setRound] = useState(null)
    const [results, setResults] = useState(null)
    const tournament = useTournament();


    /**
     * This effect loads the current data for the round.
     */
    useEffect(() => {
        if (round == null || round.round_no != params.id) {
            if (tournament) {
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
    }, [tournament, round])

    /**
     * Handles the HTTP fetch of the current round data
     * @param {*} round 
     * @returns 
     */
    function fetchResults(round) {
        if (!round) {
            return
        }
        fetch(`/api/tournament/${tournament.id}/${round.id}/result/`).then(resp => resp.json()
        ).then(json => {
            setResults(json)
            const names = []
            json.forEach(e => {
                if (e.score1 || e.score2) {
                    //
                }
                else {
                    names.push(e.p1.name)
                    names.push(e.p2.name)
                }
            })
            dispatch({ type: 'pending', names: names })
        })
    }

    /**
     * Pair this round.
     */
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
                fetchResults()
            })

    }

    /**
     * Adds a round score.
     * @param {*} e 
     */
    function addScore(e) {
        fetch(`/api/tournament/${tournament.id}/${round.id}/result/${current.resultId}/`, {
            method: 'PUT', 'credentials': 'same-origin',
            headers:
            {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                score1: current.score1,
                score2: current.score2, games_won: current.won, round: round.id
            })
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
            dispatch({ action: 'reset' })
            dispatch({
                action: 'pending',
                names: names.filter(name => name != p1.name && name != p2.name)
            })
            props.updateStandings(json)
        })
    }

    /**
     * Updates the various input boxes 
     */
    function handleChange(e, fieldName, kwargs) {
        if (fieldName == 'score1') {
            dispatch({ type: 'score1', score1: e.target.value })
        }
        else if (fieldName == 'score2') {
            dispatch({ type: 'score2', score2: e.target.value })
        }
        else if (fieldName == 'won') {
            dispatch({ type: 'won', won: e.target.value })
            dispatch({ type: 'lost', lost: tournament.team_size - e.target.value })
        }
        else if (fieldName == 'name') {
            /* the name field is a special one because you can do 
             * autocomplete on it. But at the end of the day autocomplete is
             * treated just as if the user typed it in manually.
             */
            const name = e.target?.value || kwargs;
            console.log(name)
            results.forEach(result => {
                if (name == result.p1.name) {
                    dispatch({
                        type: 'autoComplete',
                        p1: result.p1, p2: result.p2, resultId: result.id
                    })
                }
                if (name == result.p2.name) {
                    dispatch({
                        type: 'autoComplete',
                        p1: result.p2, p2: result.p1, resultId: result.id
                    })
                }
            })
        }
    }

    /**
     * edit a previously entered score
     * @param {*} e 
     * @param {*} index 
     */
    function editScore(e, index) {
        /* Edit a score means replacing the contents of the form with the 
         * existing score
         */
        const result = results[index]
        dispatch({
            type: 'replace',
            p1: result.p1, p2: result.p2,
            resultId: result.id, pending: [],
            score1: result.score1,
            score2: result.score2,
            won: result.games_won,
            lost: tournament.team_size - result.games_won
        })
    }

    function autoCompleteCheck(name, txt) {
        return name.toLowerCase().indexOf(txt) > -1
    }

    if (round?.paired && results) {

        return (
            <>
                {current.pending?.length && (
                    <div className='row'>
                        <div className='col'>
                            <Autocomplete
                                suggestions={current.pending}
                                value={current.p1?.name || current.name}
                                onChange={e => handleChange(e, 'name')}
                                onSelect={ (e, suggestion) => handleChange(e, 'name', suggestion)}
                                check={autoCompleteCheck}
                            />
                        </div>
                        <div className='col'>
                            <input value={current.won} placeholder="Games won" className='form-control'
                                onChange={e => handleChange(e, 'won')} />
                        </div>
                        <div className='col'>
                            <input value={current.score1} placeholder="Score for team1" className='form-control'
                                onChange={e => handleChange(e, 'score1')} type='number' />
                        </div>
                        <div className='col'>
                            <input value={current.p2?.name ? current.p2.name : ""} placeholder="Opponent"
                                className='form-control'
                                size='small' onChange={e => { console.log('changed') }} />
                        </div>
                        <div className='col'>
                            <input value={current.lost} placeholder="Games won" disabled type='number'
                                className='form-control' />
                        </div>
                        <div className='col'>
                            <input value={current.score2} placeholder="Score for team2"
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