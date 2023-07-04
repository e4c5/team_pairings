import React, { useState, useEffect } from 'react';
import { useTournament } from './context.jsx';


/**
 * Display an individual result
 * @param {*} param0 
 * @returns 
 */
export function Result({r, index, editScore}) {
    const tournament = useTournament()
    const editable = document.getElementById('hh') && document.getElementById('hh').value;

    function get_p1(r) {
        if(r.p1) {
            return r.p1.name
        }
        for(let i = 0 ; i < tournament.participants.length ; i++) {
            if(tournament.participants[i].id == r.p1_id) {
                return tournament.participants[i].name
            }
        }
    }

    function get_p2(r) {
        if(r.p2) {
            return r.p2.name
        }
        for(let i = 0 ; i < tournament.participants.length ; i++) {
            if(tournament.participants[i].id == r.p2_id) {
                return tournament.participants[i].name
            }
        }
    }

    function gamesLost(r) {
        if(r.games_won === undefined || r.games_won === null) {
            return ""
        }
        if(r.p2?.name == "Bye" || r.p2?.name.startsWith('Absent')) {
            return "";
        }
        if(tournament.team_size) {
            if(tournament.entry_mode == 'T') {
                return tournament.team_size - r.games_won
            }
            else {
                const played = r.boards?.length;
                return played - r.games_won;
            }
        }
        return 1 - r.games_won;
    }

    function resultIn() {
        return (
            <tr>
                <td>{ r.table ? r.table : ""} </td>
                <td className={ r.games_won > 0 ? 'bg-success-subtle' : ''}>
                    { get_p1(r)} #{r.p1?.seed}  {`${r.p1_id == r.starting_id && tournament.team_size ? " (first) " : ""}` }
                </td>
                <td className="text-end" >{ r.games_won }</td>
                <td className="text-end" >{ r.score1 }</td>
                <td className={ r.games_won > 0 ? '' : 'bg-success-subtle'}>
                    { get_p2(r) } #{r.p2?.seed} {`${r.p2_id == r.starting_id && tournament.team_size ? " (first) " : ""}` }
                </td>
                <td className="text-end">
                    { gamesLost(r) }
                </td>
                <td className="text-end">
                    { r.p2?.name == "Bye" || r.p2?.name.startsWith('Absent') ? "" : r.score2 }
                </td>
                { editable &&
                    <td className="text-end">
                        <button className='btn btn-primary' onClick={e => editScore(e, index)}>
                            <i className='bi-pencil' ></i>
                        </button>
                    </td>
                }
                
            </tr>
        )
    }

    return resultIn()
}


/**
 * Display an individual result for a team tournament.
 * 
 * Intended for use with tournaments where we keep track of each individual
 * board's performance seperately
 * @param {*} param0 
 * @returns 
 */
export function TeamResult({r, index, teamId}) {
    const tournament = useTournament()
    const editable = document.getElementById('hh') && document.getElementById('hh').value;

    function get_p1(r) {
        if(r.p1) {
            return r.p1.name
        }
        for(let i = 0 ; i < tournament.participants.length ; i++) {
            if(tournament.participants[i].id == r.p1_id) {
                return tournament.participants[i].name
            }
        }
    }

    function get_p2(r) {
        if(r.p2) {
            return r.p2.name
        }
        for(let i = 0 ; i < tournament.participants.length ; i++) {
            if(tournament.participants[i].id == r.p2_id) {
                return tournament.participants[i].name
            }
        }
    }

    function gamesLost(r) {
        console.log(r)
        if(r.games_won === undefined || r.games_won === null) {
            return ""
        }
        if(tournament.team_size) {
            if(tournament.entry_mode == 'T') {
                return tournament.team_size - r.games_won
            }
            else {
                const played = r.boards?.length;
                return played - r.games_won;
            }
        }
        return 1 - r.games_won;
    }

    
    function resultIn() {
        return (
            <>
                <tr>
                    <td>{ r.table ? r.table : ""}</td>
                    <td >{ get_p1(r)} #{r.p1?.seed}  {`${r.p1_id == r.starting_id ? " (first) " : ""}` }</td>
                    <td className="text-end" >{ r.games_won }</td>
                    <td className="text-end" >{ r.score1 }</td>
                    <td>{ get_p2(r) } #{r.p2?.seed} {`${r.p2_id == r.starting_id ? " (first) " : ""}` }</td>
                    <td className="text-end">
                        { gamesLost(r) }
                    </td>
                    <td className="text-end">{ r.score2 }</td>
                    <td className="text-end">
                        { 
                            r.p1_id == teamId ? r.score1 - r.score2 : r.score2 - r.score1
                        }
                    </td>
                </tr>
                {r.boards !== null && 
                    <tr>
                        <td colSpan={8}>
                            <table className='table table-sm'>
                                <thead>
                                    <tr>
                                        <th className='text-center'>Board</th>
                                        <th className='text-center'>Player 1 Score</th>
                                        <th className='text-center'>Player 2 Score</th>
                                        <th className='text-center'>Margin</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    { r.boards.map(board => (
                                        
                                            <tr>
                                                <td className='text-end'>{board.board}</td>
                                                <td className='text-end'>{board.score1}</td>
                                                <td className='text-end'>{board.score2}</td>
                                                <td className='text-end'>{board.team1_id == teamId ? board.score1 - board.score2 
                                                    : board.score2 - board.score1 }</td>
                                            </tr>)
                                        )
                                    }
                                </tbody>
                            </table>
                        </td>
                    </tr>
                }
            </>
        )
    }
    return resultIn()
}

/**
 * Display the results of a round or a particpant as a table
 * @param {*} param0 
 * @returns 
 */
export function ResultTable({editScore, results}) {
    const tournament = useTournament()
    const editable = document.getElementById('hh') && document.getElementById('hh').value;

    if(results && results.length) {
        return (
            <table className='table table-dark-subtle table-bordered' id='results'>
                <thead>
                    { tournament?.team_size ?
                        <tr>
                            <th align="right">Table</th>
                            <th align="left">Team 1</th>
                            <th align="right">Wins</th>
                            <th align="right">Total Score</th>
                            <th align="left">Team 2</th>
                            <th align="right">Wins</th>
                            <th align="right">Total Score</th>
                            { editable && <th align="right"></th> }
                        </tr>
                        :
                        <tr>
                            <th align="right">Table</th>
                            <th align="left">Player 1</th>
                            <th align="right">Result</th>
                            <th align="right">Score</th>
                            <th align="left">Player 2</th>
                            <th align="left">Result</th>
                            <th align="right">Score</th>
                            { editable && <th align="right"></th> }
                        </tr>
                    }
                </thead>
                <tbody>
                    {results.map((r, idx) => <Result key={r.id} r={r}
                        index={idx} editScore={editScore} />)}
                </tbody>
            </table>
        )
    }
    return null
}

/**
 * Display the results of a round or a particpant as bunch of rows.
 * 
 * Also supports the embedded list of board by board result for team events.
 * @param {*} param0 
 * @returns 
 */
export function TeamResultTable({results, teamId}) {
    const tournament = useTournament()
    if(results && results.length) {
        return (
            <table className='table table-striped table-dark-subtle table-bordered' id='results'>
                <thead>
                    <tr>
                        <th align="right">Table</th>
                        <th align="left">Team 1</th>
                        <th align="right">Wins</th>
                        <th align="right">Total Score</th>
                        <th align="left">Team 2</th>
                        <th align="right">Wins</th>
                        <th align="right">Total Score</th>
                        <th align="right">Margin</th>
                    </tr>
                </thead>
                <tbody>
                    {results.map((r, idx) => <TeamResult key={r.id} r={r} index={idx} teamId={teamId} />)}
                </tbody>
            </table>
        )
    }
    
    return null
}

console.log('Results.js 0.02')