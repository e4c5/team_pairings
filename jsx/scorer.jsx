import React, { useState, useEffect, useReducer } from 'react';
import { Autocomplete } from './autocomplete.jsx';
import { useTournament, useTournamentDispatch } from './context.jsx';
import getCookie from './cookie.js';


/**
 * A basic editor component
 * Whatever facebook may tell you there are some areas where
 * object oriented programing trumps functional
 */
class Editor extends React.Component {
    constructor(props) {
        super(props)
    }

    /**
     * Adds a round score.
     * @param {*} e 
     */
    addScore(e) {
        const { current, dispatch, tournament, round } = this.props;
        const round_id = tournament.rounds[round - 1].id
        fetch(`/api/tournament/${tournament.id}/result/`, {
            method: 'PUT', 'credentials': 'same-origin',
            headers:
            {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                score1: current.score1, result: current.resultId, 
                board: current.board, round: round_id,
                score2: current.score2, games_won: current.won
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
    handleChange(e, fieldName, kwargs) {
        const { current, dispatch, tournament } = this.props;

        if (fieldName == 'score1') {
            dispatch({ type: 'score1', score1: e.target.value })
        }
        else if (fieldName == 'score2') {
            dispatch({ type: 'score2', score2: e.target.value })
        }
        else if (fieldName == 'board') {
            dispatch({ type: 'board', board: e.target.value })
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
            const results = this.getRoundResults()

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

    getRoundResults() {
        const { tournament, round } = this.props
        if(tournament && tournament.results && round) {
            return tournament.results[round -1]
        }
        return undefined;
    }
}

function autoCompleteCheck(name, txt) {
    return name.toLowerCase().indexOf(txt) > -1
}

class _ScoreByTeam extends Editor {

    render() {
        const { current, dispatch, tournament } = this.props;
        return (
            <div className='row'>
                <div className='col'>
                    <Autocomplete
                        suggestions={current.pending} placeholder='name'
                        value={current.name}
                        onChange={e => this.handleChange(e, 'name')}
                        onSelect={(e, suggestion) => this.handleChange(e, 'name', suggestion)}
                        check={autoCompleteCheck}
                    />
                </div>
                <div className='col'>
                    <input value={current.won} placeholder="Games won"
                        className='form-control' type='number' data-test-id='games-won'
                        onChange={e => this.handleChange(e, 'won')} />
                </div>
                <div className='col'>
                    <input value={current.score1} placeholder="Score for team1" 
                        className='form-control' data-test-id='score1'
                        onChange={e => this.handleChange(e, 'score1')} type='number' />
                </div>
                <div className='col'>
                    {/* see handlechange 'name' for why how this works */}
                    <input value={current.p2?.name ? current.p2.name : ""}
                        placeholder="Opponent" data-test-id='p2' disabled
                        className='form-control' onChange={e => { }} />
                </div>
                <div className='col'>
                    <input value={current.lost} placeholder="Games won" disabled type='number'
                        className='form-control' />
                </div>
                <div className='col'>
                    <input value={current.score2} placeholder="Score for team2"
                        className='form-control' data-test-id='score2'
                        type='number' onChange={e => this.handleChange(e, 'score2')} />
                </div>
                <div className='col'>
                    <button className='btn btn-primary'
                        disabled={current.resultId == ''}
                        onClick={e => this.addScore()}>
                        <i className='bi-plus' ></i>
                    </button>
                </div>
            </div>
        )
    }
}

/**
 * Keep track of scores by individual player in a team.
 * The total team result is calculated as the sum of all player wins and
 * player margins.
 * @returns 
 */
class _ScoreByPlayer extends Editor {
    /**
     * Display the score for each board for this team.
     * The number of row will always match the team size. However if results
     * have not yet been entered, those rows will appear as blank.
     * 
     * @returns the board scores
     */
    boardScores() {
        const { current, dispatch, tournament } = this.props;
        const scores = []
        for(let i = 0 ; i < tournament.team_size ; i++) {
            const board = current?.boards?.[i]
            if(current.resultId && board) {
                if(current.p1_id == board.team1_id) {
                    scores.push(
                        <tr key={i}>
                            <td>{ i + 1 }</td><td>{board.score1}</td><td>{board.score2}</td>
                        </tr>
                    )
                }
                else {
                    scores.push(
                        <tr key={i}>
                            <td>{ i + 1 }</td><td>{board.score2}</td><td>{board.score1}</td>
                        </tr>
                    )
                }
            }
            else {
                scores.push(
                    <tr key={i}>
                        <td>{ i + 1 }</td><td></td><td></td>
                    </tr>
                )
            }
        }
        return <tbody>{ scores }</tbody>
    }
    render() {    
        const { current, dispatch, tournament } = this.props;
        console.log(current)
        return (
            <>
            <div className='row'>
                <div className='col'>
                    <Autocomplete
                        suggestions={current.pending} placeholder='name'
                        value={current.name}
                        onChange={e => this.handleChange(e, 'name')}
                        onSelect={(e, suggestion) => this.handleChange(e, 'name', suggestion)}
                        check={autoCompleteCheck}
                    />
                </div>
                <div className='col'>
                    <input value={current.board} placeholder="Board Number" className='form-control'
                        data-test-id='board'
                        onChange={e => this.handleChange(e, 'board')} />
                </div>
                <div className='col'>
                    <input value={current.score1} placeholder="Score for player1"
                        className='form-control' data-test-id='score1'
                        onChange={e => this.handleChange(e, 'score1')} type='number' />
                </div>
                <div className='col'>
                    {/* see handlechange 'name' for why how this works */}
                    <input value={current.p2?.name ? current.p2.name : ""} placeholder="Opponent"
                        className='form-control' data-test-id='p2'
                        size='small' onChange={e => { }} />
                </div>
                <div className='col'>
                    <input value={current.score2} placeholder="Score for player2"
                        className='form-control' data-test-id='score2' 
                        type='number'
                        onChange={e => this.handleChange(e, 'score2')} />
                </div>
                <div className='col'>
                    <button className='btn btn-primary'
                        disabled={current.resultId == ''}
                        onClick={e => this.addScore()}>
                        <i className='bi-plus' ></i>
                    </button>
                </div>
            </div>
            <div className='row'>
                <div className='col-md-10 col-offset-1'>
                    <table className='table'>
                        { current.resultId ? 
                            (<thead>
                                <tr><th>Board</th>
                                    <th>{current.name} score</th>
                                    <th>{current.p2?.name ? current.p2.name : ""} score</th>
                                </tr>
                            </thead>)
                            :
                            (<thead>
                                <tr><th>Board</th>
                                    <th>Player 1 score</th>
                                    <th>Player 2 score</th>
                                </tr>
                            </thead>)
                        }
                        { this.boardScores() }
                    </table>
                </div>
            </div>
            </>             
        )
    }
}

export function ScoreByPlayer(props) {
    const tournament = useTournament();
    const tournamentDispatch = useTournamentDispatch()

    return <_ScoreByPlayer tournament={tournament} {...props} />
}

export function ScoreByTeam(props) {
    const tournament = useTournament();
    const tournamentDispatch = useTournamentDispatch()

    return <_ScoreByTeam tournament={tournament} {...props} />
}
