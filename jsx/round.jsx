import React, { useState, useEffect, useReducer } from 'react';
import { useParams, Link } from "react-router-dom";

import getCookie from './cookie.js';
import { useTournament, useTournamentDispatch } from './context.jsx';
import { ResultList } from './result.jsx';
import { Autocomplete } from './autocomplete.jsx';

/**
 * Initial value for the result entry form
 */
const editorState = {
    name: '', p1: {}, p2: {}, won: '', lost: '', pending: [],
    score1: '', score2: '',
}

function reducer(state, action) {
    switch (action.type) {
        case "typed":
            return { ...state, name: action.name }

        case 'autoComplete':
            return {
                ...state, p1: action.p1, p2: action.p2,
                resultId: action.resultId,
                name: action.name
            }

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
    const [current, dispatch] = useReducer(reducer, editorState)
    /*
     * Store the round number counting from 1. That means you need to deduct
     * 1 when reading full data for the round in the tournament.rounds array
     */
    const [round, setRound] = useState(null)

    const tournament = useTournament();
    const tournamentDispatch = useTournamentDispatch()
    const editable = document.getElementById('hh') && document.getElementById('hh').value;

    /**
     * This effect loads the current data for the round.
     */
    useEffect(() => {
        if (tournament) {
            
            const results = getRoundResults()
            console.log(results)
            if (results === undefined ) {
                fetchResults(tournament.rounds[params.id - 1])
            }
            else {
                updatePending(results)
            }
        }
        // round numbers start from 0 params.id is the round number
        // not the round id.
        if(round !== params.id) {
            setRound(params.id)            
        }
    }, [tournament, round])

    function getRoundDetails() {
        if(tournament && tournament.rounds && round) {
            return tournament.rounds[round -1]
        }
        return undefined;
    }

    function getRoundResults() {
        if(tournament && tournament.results && round) {
            return tournament.results[round -1]
        }
        return undefined;
    }

    /**
     * Fetch the results for this round. 
     * If the round has been paired but the scores have not been entered
     * they will all be set to null. 
     * @param {*} round 
     * @returns 
     */
    function fetchResults(round) {
        console.log('FETCHING REULTS')

        const roundDetails = getRoundDetails()
        if (roundDetails === undefined) {
            return
        }
        
        fetch(
            `/api/tournament/${tournament.id}/${roundDetails.id}/result/`
        ).then(resp => resp.json()
        ).then(json => {
            tournamentDispatch(
                { type: 'updateResult', round: round.round_no -1, result: json }
            )
            updatePending(json)
        })
    }

    /**
     * Updates the list of teams for whom we do not have a result yet
     * @param {*} json 
     */
    function updatePending(json) {
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
        const round_id = tournament.rounds[round -1].id
        fetch(`/api/tournament/${tournament.id}/round/${round_id}/pair/`,
            {
                method: 'POST', 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({})
            }).then(resp => resp.json()).then(json => {
                if (json.status !== "ok") {
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
        const roundDetails = getRoundDetails()
        
        fetch(`/api/tournament/${tournament.id}/round/${roundDetails.id}/unpair/`,
            {
                method: 'POST', 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({})
            }).then(resp => resp.json()).then(json => {
                if (json.status !== "ok") {
                    setError(json.message)
                }
            })
    }

    /**
     * Adds a round score.
     * @param {*} e 
     */
    function addScore(e) {
        const round_id = tournament.rounds[round -1].id
        fetch(`/api/tournament/${tournament.id}/${round_id}/result/${current.resultId}/`, {
            method: 'PUT', 'credentials': 'same-origin',
            headers:
            {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                score1: current.score1,
                score2: current.score2, games_won: current.won, round: round_id
            })
        }).then(resp => resp.json()).then(json => {
            dispatch({ type: 'reset' })
            dispatch({
                type: 'pending',
                names: current.pending.filter(
                    name => name != current.p1.name && name != current.p2.name
                )
            })
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
            const results = getRoundResults()

            results?.forEach(result => {
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
            if (!matched) {
                if (current?.p1?.name) {
                    dispatch({
                        type: 'autoComplete', name: name,
                        p1: {}, p2: {}, resultId: null
                    })
                }

                else {
                    dispatch({ type: "typed", name: name })
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
        const results = getRoundResults()
        if(results) {
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
    }

    function autoCompleteCheck(name, txt) {
        return name.toLowerCase().indexOf(txt) > -1
    }


    function editor() {
        if (!editable) {
            return <></>
        }
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
                        size='small' onChange={e => { }} />
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
                        disabled={current.resultId == ''}
                        onClick={e => addScore()}>
                        <i className='bi-plus' ></i>
                    </button>
                </div>
            </div>
        )
    }
    
    const roundDetails = getRoundDetails()
    if (roundDetails?.paired) {
        
        return (
            <div>
                <h2><Link to={`/${tournament.slug}`}>{tournament.name}</Link></h2>
                <h3>Results for round : {round}</h3>
                {editor()}
                <ResultList results={getRoundResults()} editScore={editScore} />
                <div className='row'>
                    <div className='col'>
                        {editable &&
                            <button className='btn btn-warning' onClick={unpair}>Unpair</button>
                        }
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
                        {tournament?.participants?.map((row, idx) => {
                            if (row.name != 'Bye') {
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
                            else {
                                return null
                            }
                        })
                        }
                    </tbody>
                </table>
                <div className='row'>
                    <div className='col'>
                        {editable &&
                            <button className='btn btn-warning' onClick={pair}>Pair</button>
                        }
                    </div>
                </div>
                <div className='row'>
                    <div className='col'>{error}</div>
                </div>
            </div>
        )
    }
}

export function Rounds() {
    const tournament = useTournament();
    const dispatch = useTournamentDispatch()
    
    return (
        <div className='row mt-3'>
            <div className='col-sm-2'><h3>Rounds: </h3></div>
            <div className='col-sm-10 btn-group' aria-label="outlined primary button group">
                {
                    tournament?.rounds?.map(r =>
                        <Link to={'round/' + r.round_no} key={r.round_no}>
                            <button className='btn btn-primary me-1'>{r.round_no}</button></Link>)
                }
            </div>
        </div>
    )
}

console.log('Rounds 0.02')