import React, { useState, useEffect } from 'react';
import { useTournament, useTournamentDispatch } from './context.jsx';
  
export default function Result({r, index, editScore}) {

    const dispatch = useTournamentDispatch()
    const tournament = useTournament()
    const editable = document.getElementById('hh') && document.getElementById('hh').value;

    function resultIn() {
        return (
            <tr>
                <td >{ r.p1.name }</td>
                <td className="text-right" >{ r.games_won } - { tournament.team_size - r.games_won }</td>
                <td className="text-right" >{ r.score1 }</td>
                <td>{ r.p2.name }</td>
                <td className="text-right">{ tournament.team_size - r.games_won } - { r.games_won }</td>
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
                <td>{ r.p1.name }</td>
                <td></td>
                <td></td>
                <td>{ r.p2.name }</td>
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
