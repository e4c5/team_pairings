import React, { useState, useEffect } from 'react';
import { useTournament, useTournamentDispatch } from './context.jsx';
  
export default function Result({r, index, editScore}) {
    const editable = document.getElementById('editable')
    const dispatch = useTournamentDispatch()
    const tournament = useTournament()

    function resultIn() {
        if(editable) {

        }
        return (
            <tr>
                <td sx={{border:1}} >{ r.p1.name }</td>
                <td className="text-right" sx={{border:1}} >{ r.games_won } - { tournament.team_size - r.games_won }</td>
                <td className="text-right" sx={{border:1}} >{ r.score1 }</td>
                <td sx={{border:1}} >{ r.p2.name }</td>
                <td className="text-right" sx={{border:1}} >{ tournament.team_size - r.games_won } - { r.games_won }</td>
                <td className="text-right" sx={{border:1}} >{ r.score2 }</td>
                <td className="text-right" sx={{border:1}} >
                        <button className='btn btn-primary' onClick={e => editScore(e, index)}>Edit</button>
                </td>
            </tr>
        )
    }

    function resultOut() {
        return (
            <tr>
                <td sx={{border:1}} >{ r.p1.name }</td>
                <td sx={{border:1}} ></td>
                <td sx={{border:1}} ></td>
                <td sx={{border:1}} >{ r.p2.name }</td>
                <td sx={{border:1}} ></td>
                <td sx={{border:1}} ></td>
                <td sx={{border:1}} ></td>
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
