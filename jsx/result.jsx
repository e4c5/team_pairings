import React, { useState, useEffect } from 'react';
import { useTournament, useTournamentDispatch } from './context.jsx';


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

    function resultIn() {
        return (
            <tr>
                <td >{ get_p1(r) }</td>
                <td className="text-right" >{ r.games_won } </td>
                <td className="text-right" >{ r.score1 }</td>
                <td>{ get_p2(r) }</td>
                <td className="text-right">{ tournament.team_size - r.games_won } </td>
                <td className="text-right">{ r.score2 }</td>
                <td className="text-right">
                    { editable &&
                        <button className='btn btn-primary' onClick={e => editScore(e, index)}>
                            <i className='bi-pencil' ></i>
                        </button>
                    }
                </td>
            </tr>
        )
    }

    function resultOut() {
        return (
            <tr>
                <td>{ get_p1(r) }</td>
                <td></td>
                <td></td>
                <td>{ get_p2(r) }</td>
                <td></td>
                <td></td>
                <td></td>
            </tr>
        )
    }

    if(r.score1) {
        return resultIn()
    }
    else {
        return resultOut();
    }
}

/**
 * Display the results of a round or a particpant as a table
 * @param {*} param0 
 * @returns 
 */
export function ResultList({editScore, results}) {
    if(results && results.length) {
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
    return null
}