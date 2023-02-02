import React, { useState, useEffect, useReducer } from 'react';
import { useParams, Link } from "react-router-dom";

import getCookie from './cookie.js';
import { useTournament, useTournamentDispatch } from './context.jsx';
import Result from './result.jsx';
import { Autocomplete } from './autocomplete.jsx';

const editorState = {
    name: '', p1: {}, p2: {}, won: '', lost: '', pending: [],
    score1: '', score2: '',
}

function reducer(state, action) {
    switch (action.type) {
        case "typed":
            return { ...state, name: action.name }

        case 'autoComplete':
            return { ...state, p1: action.p1, p2: action.p2,
                     resultId: action.resultId, 
                     name: action.name }

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
            return { ...state, score2: action.score2 }

        case 'replace':
            return { ...action.value }

        case 'reset':
            return {
                ...editorState,
            }

        default:
            throw Error(`unrecognized action ${action.type} in reducer`)
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
    const [error, setError] = useState('')
    const [current, dispatch] = useReducer(reducer,  editorState )
    const [round, setRound] = useState(null)
    const [results, setResults] = useState(null)
    const tournament = useTournament();
    const tournamentDispatch = useTournamentDispatch()

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
     * Fetch the results for this round. 
     * If the round has been paired but the scores have not been entered
     * they will all be set to null. 
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
            updatePendig(json)
        })
    }

    /**
     * Updates the list of teams for whom we do not have a result yet
     * @param {*} json 
     */
    function updatePendig(json) {
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
    }
    /**
     * Pair this round.
     */
    function pair() {
        /* 
         * note that it's the id of the round in the DB that we send
         * rather than the round number
         */
        fetch(`/api/tournament/${tournament.id}/round/${round.id}/pair/`,
            {
                method: 'POST', 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({})
            }).then(resp => resp.json()).then(json => {
                if (json.status === "ok") {
                    setRound({ ...round, paired: true })
                    setResults(json.results)
                    updatePendig(json.results)
                }
                else {
                    setError(json.message)
                }
            })
    }

    /**
     * UnPair this round.
     */
    function unpair() {
        /* 
         * note that it's the id of the round in the DB that we send
         * rather than the round number
         */
        fetch(`/api/tournament/${tournament.id}/round/${round.id}/unpair/`,
            {
                method: 'POST', 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({})
            }).then(resp => resp.json()).then(json => {
                if (json.status === "ok") {
                    setRound({ ...round, paired: true })
                    setResults(null)
                }
                else {
                    setError(json.message)
                }
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
                if (results[i].p1.name == current.p1.name) {
                    res[i].score1 = current.score1;
                    res[i].score2 = current.score2;
                    res[i].games_won = current.won;
                    setResults(res)
                    break;
                }
            }
            dispatch({ type: 'reset' })
            dispatch({
                type: 'pending',
                names: current.pending.filter(
                    name => name != current.p1.name && name != current.p2.name
                )
            })
            tournamentDispatch({type: 'editParticipant',
                    participant: json[0]
                }
            )
            tournamentDispatch({type: 'editParticipant',
                    participant: json[1]
                }
            )
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
            const name = (kwargs !== undefined) ? kwargs : e.target?.value;
            let matched = false;
            results.forEach(result => {
                if (name == result.p1.name) {
                    dispatch({
                        type: 'autoComplete', name: name,
                        p1: result.p1, p2: result.p2, resultId: result.id
                    })
                    matched = true;
                }
                if (name == result.p2.name) {
                    dispatch({
                        type: 'autoComplete', name: name,
                        p1: result.p2, p2: result.p1, resultId: result.id
                    })
                    matched = true;
                }
            })
            if(! matched) {
                if( current?.p1?.name) {
                    dispatch({
                        type: 'autoComplete', name: name, 
                        p1: {}, p2: {}, resultId: null
                    })
                }
                
                else {
                    dispatch({type: "typed", name: name})
                }
            }
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
            value: {
                p1: result.p1, p2: result.p2,
                name: result.p1.name, 
                resultId: result.id, pending: [],
                score1: result.score1,
                score2: result.score2,
                won: result.games_won,
                lost: tournament.team_size - result.games_won
            }
        })
    }

    function autoCompleteCheck(name, txt) {
        return name.toLowerCase().indexOf(txt) > -1
    }

    function table() {
        return (
            <table className='table table-striped table-dark table-bordered'>
                <thead>
                    <tr>
                        <td align="left">Team 1</td>
                        <td align="right">Wins</td>
                        <td align="right">Total Score</td>
                        <td align="left">Team 2</td>
                        <td align="right">Wins</td>
                        <td align="right">Total Score</td>
                        <td align="right"></td>
                    </tr>
                </thead>
                <tbody>
                    {results.map((r, idx) => <Result key={r.id} r={r}
                        index={idx} editScore={editScore} />)}
                </tbody>
            </table>
        )
    }

    function editor() {
        console.log(current)
        return (
            <div className='row'>
                <div className='col'>
                    <Autocomplete
                        suggestions={current.pending} placeholder='name'
                        value={current.name}
                        onChange={e => handleChange(e, 'name')}
                        onSelect={(e, suggestion) => handleChange(e, 'name', suggestion)}
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
                        size='small' onChange={e => {  }} />
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
                    <button className='btn btn-primary' 
                        disabled={ current.resultId == ''}
                        onClick={e => addScore()}>
                        <i className='bi-plus' ></i>
                    </button>
                </div>
            </div>
        )
    }
    if (round?.paired) {
        return (
            <div>
                <h2>{tournament?.name}</h2>
                {editor()}
                {results && results.length && table()}
                <div className='row'>
                    <div className='col'>
                        <button className='btn btn-warning' onClick={unpair}>Unpair</button>
                    </div>
                </div>
                <div>{error}</div>
            </div>
        )
    }
    else {
        return (
            <div>
                <h2>{tournament?.name}</h2>
                This is a round that has not yet been paired
                <table className='table'>
                    <tbody>
                    {   tournament?.participants?.map((row, idx) =>  {
                            if(row.name != 'Bye') {
                                return (
                                    <tr
                                        key={row.id}
                                        sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                    >
                                        <td className="text-left">{idx + 1}</td>
                                        <td component="th" scope="row">
                                            <Link to={`${row.id}`}>{row.name}</Link>
                                        </td>
                                        <td>Unpaired</td>
                                    </tr>)
                            }
                            else{
                                return null
                            }
                        })
                    }
                    </tbody>
                </table>
                <div className='row'>
                    <div className='col'>
                        <button className='btn btn-warning' onClick={pair}>Pair</button>
                    </div>
                </div>
                <div>{error}</div>
            </div>
        )
    }
}

export function Rounds(props) {
    const tournament = useTournament();
    const dispatch = useTournamentDispatch()

    return (
        <div className='row'>
            <div className='col'><h3>Rounds: </h3></div>
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

console.log('Rounds 0.02')