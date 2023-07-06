import React, { useState, useEffect, useReducer, useRef } from 'react';
import { useParams, Link } from "react-router-dom";

import getCookie from './cookie.js';
import { useTournament, useTournamentDispatch } from './context.jsx';
import { ResultTable } from './result.jsx';
import { Confirm } from './dialog.js';
import { ScoreByTeam, ScoreByPlayer, IndividualTournamentScorer, TSHStyle } from './scorer.jsx'

/**
 * Initial value for the result entry form
 */
const editorState = {
    name: '', p1: {}, p2: {}, won: '', lost: '', pending: [],
    score1: '', score2: '', board: ''
}

/**
 * Reducer for result entry section
 * @param {*} state 
 * @param {*} action 
 * @returns 
 */
export function reducer(state, action) {

    switch (action.type) {
        case "typed":
            return { ...state, name: action.name }

        case 'autoComplete':
            return {
                ...state, p1: action.p1, p2: action.p2,
                resultId: action.resultId,
                name: action.name, boards: action.boards
            }
        case 'board':
            return { ...state, board: action.board }

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
    /*
     * for display of any errors recieved from the api
     */
    const [error, setError] = useState('')
    const [current, dispatch] = useReducer(reducer, editorState)
    /*
     * Store the round number counting from 1. That means you need to deduct
     * 1 when reading full data for the round in the tournament.rounds array
     */
    const [round, setRound] = useState(null)

    const [modal, setModal] = useState(false)
    const [code, setCode] = useState('')

    /* tie this ref to the score field */
    const ref = React.useRef(null);

    const tournament = useTournament();
    const tournamentDispatch = useTournamentDispatch()
    const editable = document.getElementById('hh') && document.getElementById('hh').value;

    /**
     * This effect loads the current data for the round.
     */
    useEffect(() => {
        if (tournament) {
            const results = getRoundResults()
            if (results === undefined || results.length === 0) {
                fetchResults()
            }
            else {
                updatePending(results)
            }
        }
        setError('')

    }, [tournament, round])

    useEffect(() => {
        // round numbers start from 0 params.id is the round number
        // not the round id.
        if (round !== params.id) {
            setRound(params.id)
        }

    }, [params]);

    function getRoundDetails() {
        if (tournament && tournament.rounds && round) {
            return tournament.rounds[round - 1]
        }
        return undefined;
    }

    function getRoundResults() {
        if (tournament && tournament.results && round) {
            return tournament.results[round - 1]
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
    function fetchResults() {
        const roundDetails = getRoundDetails()
        if (roundDetails === undefined || roundDetails.paired === false) {
            return
        }

        fetch(
            `/api/tournament/${tournament.id}/result/?round=${roundDetails.id}`
        ).then(resp => resp.json()
        ).then(json => {
            tournamentDispatch(
                { type: 'updateResult', tid: tournament.id,
                    round: roundDetails.round_no - 1, result: json }
            )
            //updatePending(json)
        })
    }

    /**
     * Updates the list of teams for whom we do not have a result yet
     * @param {*} json 
     */
    function updatePending(json) {
        const names = []
        json.forEach(e => {
            if (tournament.entry_mode == 'T' && (e.score1 || e.score2)) {
                //
            }
            else {
                names.push(e.p1.name)
                names.push(e.p2.name)
            }
        })
        dispatch({ type: 'pending', names: names , tid: tournament.id})
    }
    /**
     * Pair this round.
     */
    function pair() {
        /* 
         * note that it's the id of the round in the DB that we send
         * rather than the round number
         */
        const round_id = tournament.rounds[round - 1].id
        fetch(`/api/tournament/${tournament.id}/pair/`,
            {
                method: 'POST', 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({id: round_id})
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
        const round_id = tournament.rounds[round - 1].id
        fetch(`/api/tournament/${tournament.id}/unpair/`,
            {
                method: 'POST', 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({id: round_id})
            }).then(resp => resp.json()).then(json => {
                if (json.status !== "ok") {
                    setError(json.message)
                }
            })
    }

    /**
     * Truncates the tourament by clearing results and pairing for this round.
     */
    function truncate(e) {
        setModal(true)
    }

    /**
     * Edit a previously entered score or add a new one.
     * 
     * Called by the edit icon in the child component <Result/> clicking on it
     * will change the editor area to show the scores for that particular game
     * if the score had not already been entered most fields will be blank but
     * two names for the players/teams will be filled.
     * 
     * Note that this does not update the results in the server. For that
     * @see addscore in scorer.jsx 
     * 
     * @param {*} e 
     index 
     */
    function editScore(e, index) {
        /* Edit a score means replacing the contents of the form with the 
         * existing score
         */
        console.log('editScore')
        console.log(current)
        const results = getRoundResults()
        if (results) {
            const result = results[index]
            dispatch({
                type: 'replace',
                value: {
                    p1: result.p1, p2: result.p2,
                    name: result.p1.name,
                    resultId: result.id, pending: current.pending,
                    score1: result.score1 || '',
                    score2: result.score2 || '',
                    board: result.board || '',
                    boards: result.boards || [],
                    won: result.games_won === null ? '' : result.games_won,
                    lost: (tournament.team_size || 1) - result.games_won
                }
            })
            ref.current?.scrollIntoView({ behavior: 'smooth' });
            ref.current?.focus()
        }
    }

    function confirmDelete(e) {
        setModal(false)
        const roundDetails = getRoundDetails()
        fetch(`/api/tournament/${tournament.id}/truncate/`,
            {
                method: 'POST', 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ 'td': code , id: roundDetails.id })
            }).then(resp => resp.json()).then(json => {
                if (json.status !== "ok") {
                    setError(json.message)
                }
                else {
                    window.location.reload()
                }
            })
        setCode('')
    }

    function editor() {
        if (!editable) {
            return <></>
        }
        if(tournament.team_size) {
            if (tournament.entry_mode == 'T') {
                return <ScoreByTeam current={current} dispatch={dispatch}  round={round} />
            }
            return <ScoreByPlayer current={current} dispatch={dispatch} round={round} />
        }
        
        return (
            <>
                <IndividualTournamentScorer current={current} dispatch={dispatch} ref={ref} round={round} />
                <TSHStyle current={current} dispatch={dispatch} round={round} />
            </>
        )
    }

    /**
     * Fill a tournament with random data.
     * Available only for private tournaments as a means of carrying out a 
     * dray run.
     */
    function randomFill() {

        fetch(`/api/tournament/${tournament.id}/random_results/`,
            {
                method: 'POST', 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
            }).then(resp => resp.json()).then(json => {
                if (json.status !== "ok") {
                    setError(json.message)
                }
            })
    }

    const roundDetails = getRoundDetails()
    if (roundDetails?.paired) {
        return (
            <div>
                <h2><Link to={`/${tournament.slug}`}>{tournament.name}</Link></h2>
                <h3>Results for round : {round}</h3>
                {editor()}
                <ResultTable results={getRoundResults()} editScore={editScore} />
                <div className='row'>
                    <div className='col'>
                        {editable &&
                            <button className='btn btn-warning' onClick={unpair} data-test-id='unpair'>
                                Unpair
                            </button>
                        }
                    </div>
                    <div className='col'>
                        {editable &&
                            <button className='btn btn-danger' onClick={truncate} data-test-id='unpair'>
                                Truncate
                            </button>
                        }
                        
                    </div>
                    { tournament.private && 
                        <div className='col'>
                            <button className='btn btn-light'
                                 onClick={randomFill}>Random Fill
                            </button>
                        </div>
                    }
                </div>
                <div>{error}</div>
                <Confirm code={code} onCodeChange={e => setCode(e.target.value)} display={modal}
                    setModal={setModal} confirmDelete={confirmDelete} />
                <Rounds />
            </div>
        )
    }
    else {
        return (
            <div>
                <h2><Link to={`/${tournament?.slug}`}>{tournament?.name}</Link></h2>
                This is a round that has not yet been paired
                <table className='table'>
                    <tbody>
                        {tournament?.participants?.map((row, idx) => {
                            if (row.name != 'Bye' && row.name != 'Absent') {
                                return (
                                    <tr  key={row.id} >
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
                            <button className='btn btn-warning' onClick={pair} data-test-id='pair'>
                                Pair
                            </button>
                        }
                    </div>
                </div>
                <div className='row'>
                    <div className='col'>{error}</div>
                </div>
                <Rounds />
            </div>
        )
    }
}

export function Rounds() {
    const tournament = useTournament();

    if (tournament?.entry_mode == 'P') {
        return (
            <div className='row mt-3'>
                <div className='col-sm-2'><h3>Rounds: </h3></div>
                <div className='col-sm-9 btn-group' aria-label="outlined primary button group">
                    {
                        tournament?.rounds?.map(r =>
                            <Link to={`/${tournament.slug}/round/${r.round_no}`} key={r.round_no}>
                                <button className='btn btn-primary me-1'>{r.round_no}</button></Link>)
                    }
                </div>
                <div className='col-sm-1'>
                    <Link to={`/${tournament.slug}/boards`}>
                                <button className='btn btn-primary me-1'>Boards</button></Link>
                </div>
            </div>
        )
    }
    else {
        return (
            <div className='row mt-3'>
                <div className='col-sm-2'><h3>Rounds: </h3></div>
                <div className='col-sm-10 btn-group' aria-label="outlined primary button group">
                    {
                        tournament?.rounds?.map(r =>
                            <Link to={`/${tournament.slug}/round/${r.round_no}`} key={r.round_no}>
                                <button className='btn btn-primary me-1'>{r.round_no}</button></Link>)
                    }
                </div>
            </div>
        )
    }
}

console.log('Rounds 0.03.1')