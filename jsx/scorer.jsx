import React, { useState, useEffect, forwardRef } from 'react';
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
        const { current, tournament } = this.props;
        if(! tournament.team_size) {
            if(current.score1 == current.score2) {
                current.games_won = 0.5
            }
            else if(current.score1 > current.score2) {
                current.games_won = 1
            }
            else {
                current.games_won = 0
            }
        }
        this.postScore(current)
    }

    postScore(current, callBack) {
        // the dispatch here comes from the reducer() function in round.jsx

        const { dispatch, tournament, round } = this.props;
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
                p1: current.p1.id, p2: current.p2.id,
                board: current.board, round: round_id,
                score2: current.score2, games_won: current.won
            })
        }).then(resp => resp.json()).then(json => {
            
            if(current.pending && tournament.entry_mode != 'P') {
                // reset has to be retired
                dispatch({ type: 'reset' })
                dispatch({
                    type: 'pending',
                    names: current.pending.filter(
                        name => name != current.p1.name && name != current.p2.name
                    )
                })
            }
            else {
                dispatch({type: 'replace',
                    value: {...current, 
                        name: '', p1: {}, p2: {}, won: '', lost: '',
                        score1: '', score2: '', board: '', resultId: null
                    }
                })
                
            }
            if(callBack) {
                callBack(json)
            }
        })
    }

    /**
     * Detect who has won the game in an individual tournament based on scores.
     * @param {*} match 
     */
    detectWin(match, name) {
        if(match.p1.name.toLowerCase().includes(name)) {
            match.score1 = Number(parts[1])
            match.score2 = Number(parts[3])
        }
        else {
            match.score2 = Number(parts[1])
            match.score1 = Number(parts[3])
            
        }
        if(match.score1 == match.score2) {
            match.won = 0.5
        }
        else if(match.score1 > match.score2) {
            match.won = 1
        }
        else {
            match.won = 0
        }
    }
    /**
     * Updates the various input boxes 
     */
    handleChange(e, fieldName, kwargs) {
        const { current, dispatch, tournament } = this.props;

        if(tournament.team_size === null && (fieldName == 'score1' || fieldName == 'score2')) {
            if(current.score2 !== undefined && current.score2 !== undefined) {
                const score1 = fieldName == 'score1' ? e.target.value : current.score1;
                const score2 = fieldName == 'score2' ? e.target.value : current.score2;
                let won = 0;
                if(score1 == score2) {
                    won = 0.5
                }
                else if(score1 > score2) {
                    won = 1
                }
                else {
                    won = 0
                }
                const lost = 1 - won
                dispatch({ type: 'won', won: won })
                dispatch({ type: 'lost', lost: lost })
            }   
        }

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
                        type: 'autoComplete', name: name, boards: result.boards,
                        p1: result.p1, p2: result.p2, resultId: result.id,
                        score1: tournament.entry_mode == 'T' ? result.score1 : "",
                        score2: tournament.entry_mode == 'T' ? result.score2 : "",
                    })
                    matched = true;
                }
                if (name == result.p2.name) {
                    dispatch({
                        type: 'autoComplete', name: name, boards: result.boards,
                        p1: result.p2, p2: result.p1, resultId: result.id,
                        score1: tournament.entry_mode == 'T' ? result.score2 : "",
                        score2: tournament.entry_mode == 'T' ? result.score1 : "",
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
                <div className='col col-md-2'>
                    <Autocomplete
                        suggestions={current.pending} placeholder='name'
                        value={current.name}
                        onChange={e => this.handleChange(e, 'name')}
                        onSelect={(e, suggestion) => this.handleChange(e, 'name', suggestion)}
                        check={autoCompleteCheck}
                    />
                </div>
                <div className='col col-md-2'>
                    <input value={current.won} placeholder="Games won"
                        className='form-control' type='number' data-test-id='games-won'
                        onChange={e => this.handleChange(e, 'won')} />
                </div>
                <div className='col col-md-2'>
                    <input value={current.score1} placeholder="Score for team1" 
                        className='form-control' data-test-id='score1'
                        onChange={e => this.handleChange(e, 'score1')} type='number' />
                </div>
                <div className='col col-md-2'>
                    {/* see handlechange 'name' for why how this works */}
                    <input value={current.p2?.name ? current.p2.name : ""}
                        placeholder="Opponent" data-test-id='p2' disabled
                        className='form-control' onChange={e => { }} />
                </div>
                <div className='col col-md-2'>
                    <input value={current.lost} placeholder="Games won" disabled type='number'
                        className='form-control' />
                </div>
                <div className='col col-md-2'>
                    <input value={current.score2} placeholder="Score for team2"
                        className='form-control' data-test-id='score2'
                        type='number' onChange={e => this.handleChange(e, 'score2')} />
                </div>
                <div className='col col-md-2'>
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
            scores.push(
                <tr key={ i + 1 }>
                    <td>{ i + 1 }</td><td></td><td></td>
                </tr>
            )
        }
        current?.boards?.forEach(board => {
            if(current.resultId && board) {
                if(current.p1.id == board.team1_id) {
                    scores[board.board -1] =(
                        <tr key={board.board}>
                            <td>{ board.board }</td><td>{board.score1}</td><td>{board.score2}</td>
                        </tr>
                    )
                    
                }
                else {
                    scores[board.board -1] =(
                        <tr key={board.board}>
                            <td>{ board.board }</td><td>{board.score2}</td><td>{board.score1}</td>
                        </tr>
                    )
                }
            }
        })
            
        return <tbody>{ scores }</tbody>
    }
    render() {    
        const { current, dispatch, tournament } = this.props;

        return (
            <>
            <div className='row'>
                <div className='col-lg col-md-2'>
                    <Autocomplete
                        suggestions={current.pending} placeHolder='Team name'
                        value={current.name}
                        onChange={e => this.handleChange(e, 'name')}
                        onSelect={(e, suggestion) => this.handleChange(e, 'name', suggestion)}
                        check={autoCompleteCheck}
                    />
                </div>
                <div className='col-lg col-md-2'>
                    <input value={current.board} placeholder="Board Number" className='form-control'
                        data-test-id='board'
                        onChange={e => this.handleChange(e, 'board')} />
                </div>
                <div className='col-lg col-md-2'>
                    <input value={current.score1} placeholder="Score for player1"
                        className='form-control' data-test-id='score1'
                        onChange={e => this.handleChange(e, 'score1')} type='number' />
                </div>
                <div className='col-lg col-md-2'>
                    {/* see handlechange 'name' for how this works */}
                    <input value={current.p2?.name ? current.p2.name : ""} placeholder="Opponent"
                        className='form-control' data-test-id='p2' disabled
                        size='small' onChange={e => { }} />
                </div>
                <div className='col-lg col-md-2'>
                    <input value={current.score2} placeholder="Score for player2"
                        className='form-control' data-test-id='score2' 
                        type='number'
                        onChange={e => this.handleChange(e, 'score2')} />
                </div>
                <div className='col-lg col-md-2'>
                    <button className='btn btn-primary'
                        disabled={current.resultId == ''}
                        onClick={e => this.addScore()}>
                        <i className='bi-plus' ></i>
                    </button>
                </div>
            </div>
            <div className='row mt-3 mb-3'>
                <div className='col-10 offset-1'>
                    <table className='table'>
                        { current.resultId ? 
                            (<thead>
                                <tr><th>Board</th>
                                    <th><b>{current.name}</b> score</th>
                                    <th><b>{current.p2?.name ? current.p2.name : ""}</b> score</th>
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

class _TSHStyle extends Editor {
    constructor(props) {
        super(props)
        this.state = {tsh: '', error: ''}
    }

    tshAction(e) {
        if(e.key == 'Enter') {
            const parts = this.state.tsh.toLowerCase().trim().split(' ')
            if(parts[0] == "pair") {

            }
            else if(parts[0] == "unpair") {
                if(parts.length == 3) {
                    const results = this.getRoundResults()
                    results?.forEach(result => {
                        if(result.p1.name.toLowerCase().includes(parts[1]) || result.p2.name.toLowerCase().includes(parts[1])) {
                            if(result.p1.name.toLowerCase().includes(parts[1]) || result.p2.name.toLowerCase().includes(parts[1])) {
                                const { dispatch, tournament, round } = this.props;
                                const round_id = tournament.rounds[round - 1].id
                                fetch(`/api/tournament/${tournament.id}/result/${round_id}/${result.id}/`, {
                                    method: 'DELETE', 'credentials': 'same-origin',
                                    headers:
                                    {
                                        'Content-Type': 'application/json',
                                        "X-CSRFToken": getCookie("csrftoken")
                                    }
                                }).then(resp => resp.json()).then(json => {
                                    dispatch({ type: 'reset' })
                                    this.setState({tsh: '', error: ''})
                                })
                            }
                        }    
                    }) 
                }
            }
            else if(parts.length == 4) {
                let match = null;
                let found = false;
                const results = this.getRoundResults()
                const seed1 = Number(parts[0])
                const seed2 = Number(parts[2])

                results?.forEach(result => {
                    const p1 = result.p1.name.toLowerCase()
                    const p2 = result.p2.name.toLowerCase()
                    if(p1.includes(parts[0]) || p2.includes(parts[0]) || result.p1.seed == seed1 || result.p2.seed == seed1) {
                        if(p1.includes(parts[2]) || p2.includes(parts[2]) || result.p1.seed == seed2 || result.p2.seed == seed2) {
                            if(! found) {
                                found = true;
                                if(result.score1 || result.score2) {
                                    this.setState({error: 'Already has a score'})
                                }
                                else {
                                    match = { ...result, resultId: result.id }
                                }
                            }
                            else {
                                this.setState({error: 'Multiple matches'})
                                match = null;
                            }
                        }
                    }
                })
                if(match && found) {
                    if(match.p1.name.toLowerCase().includes(parts[0])) {
                        match.score1 = Number(parts[1])
                        match.score2 = Number(parts[3])
                    }
                    else {
                        match.score2 = Number(parts[1])
                        match.score1 = Number(parts[3])
                        
                    }
                    if(match.score1 == match.score2) {
                        match.won = 0.5
                    }
                    else if(match.score1 > match.score2) {
                        match.won = 1
                    }
                    else {
                        match.won = 0
                    }
                    this.postScore(match, 
                        json => {this.setState({tsh: '', error: ''})})
                }
                else if (!found){
                    this.setState({error: 'No matching entry'})    
                }
            }
            else {
                this.setState({error: 'huh?'})
            }
        }
    }

    render() {
        return (
            <div>
                <div className='row mt-1'>
                        <div className='col-12'>
                            <input type='text' className='form-control' onKeyDown={e => this.tshAction(e)}
                                placeholder='TSH style data entry' data-test-id='tsh-style-entry'
                                value={this.state.tsh} onChange={e => this.setState({tsh: e.target.value}) } />
                        </div>
                    </div>
                    <div className='row mt-1 mb-1'>
                        <div className='col-12'>
                            { this.state.error }
                        </div>
                </div>
            </div>
        )
    }
}
/**
 * Scorer for individual events
 * @returns 
 */
class _IndividualTournamentScorer extends Editor {

    render() {
        const { current, dispatch, tournament } = this.props;
        return (
                <div className='row'>
                    <div className='col-lg col-md-2'>
                        <Autocomplete
                            suggestions={current.pending} placeHolder='Player name'
                            value={current.name}
                            onChange={e => this.handleChange(e, 'name')}
                            onSelect={(e, suggestion) => this.handleChange(e, 'name', suggestion)}
                            check={autoCompleteCheck}
                        />
                    </div>
                    <div className='col-lg col-md-2'>
                        <input value={current.won} placeholder="Result" 
                            className='form-control' type='number' data-test-id='games-won'
                            onChange={e => this.handleChange(e, 'won')} disabled />
                    </div>
                    <div className='col-lg col-md-2'>
                        <input value={current.score1} placeholder="Score for Player1" 
                            className='form-control' data-test-id='score1' ref={this.props.forward}
                            onChange={e => this.handleChange(e, 'score1')} type='number' />
                    </div>
                    <div className='col-lg col-md-2'>
                        {/* see handlechange 'name' for why how this works */}
                        <input value={current.p2?.name ? current.p2.name : ""}
                            placeholder="Opponent" data-test-id='p2' disabled
                            className='form-control' onChange={e => { }} />
                    </div>
                    <div className='col-lg col-md-2'>
                        <input value={current.lost} placeholder="Result" disabled type='number'
                            className='form-control' />
                    </div>
                    <div className='col-lg col-md-2'>
                        <input value={current.score2} placeholder="Score for Player2"
                            className='form-control' data-test-id='score2'
                            type='number' onChange={e => this.handleChange(e, 'score2')} />
                    </div>
                    <div className='col-lg col-md-2 text-end'>
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

export const IndividualTournamentScorer = forwardRef((props, ref) => {
    const tournament = useTournament();
    const tournamentDispatch = useTournamentDispatch()

    return <_IndividualTournamentScorer tournament={tournament} {...props} forward={ref} />
});

export function TSHStyle(props) {
    const tournament = useTournament();
    const tournamentDispatch = useTournamentDispatch()

    return <_TSHStyle tournament={tournament} {...props} />
}


console.log('scorer 0.04')
