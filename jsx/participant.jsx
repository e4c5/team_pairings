//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';

import {
    useParams,
    Link as RouterLink,
} from "react-router-dom";

import { Link, Switch } from '@mui/material';
import { useTournament, useTournamentDispatch } from './context.jsx';
import getCookie from './cookie.js';

export function Participants(props) {
    const tournament = useTournament();
    const dispatch = useTournamentDispatch();
    
    const auth = document.getElementById('hh') && document.getElementById('hh').value

    /**
     * Switch the on / off state of a participant.
     * @param {*} e 
     * @param {*} idx 
     * @param {*} toggle 
     */
    function toggleParticipant(e, idx) {
        const p = tournament.participants[idx];
        p['offed'] = p.offed == 0 ? 1 : 0;

        fetch(`/api/tournament/${tournament.id}/participant/${p.id}/`, 
            { method: 'PUT', 'credentials': 'same-origin',
              headers: 
              {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
              },
              body: JSON.stringify(p)
        }).then(resp => resp.json()).then(json => dispatch({type: 'editParticipant', participant: json}))
    }

    /**
     * Deletes the participant only possible if no games played
     * @param {*} e 
     * @param {*} idx 
     */
    function deleteParticipant(e, idx) {
        const p = tournament.participants[idx];
        fetch(`/api/tournament/${tournament.id}/participant/${p.id}/`, 
            { method: "DELETE", 'credentials': 'same-origin',
              headers: 
              {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
              },
              body: JSON.stringify(p)
        }).then(resp => {
             if(resp.ok) {
                dispatch({type: 'deleteParticipant', participant: p})
            }
        })
    }

    function isStarted() {
        return tournament.rounds[0].paired
    }
    return (
       
        <table className='table table-striped align-middle table-bordered table-dark'>
          <thead>
            <tr>
              <td>Rank</td>
              <td className="text-left">Name</td>
              <td className="text-right">rating</td>
              <td className="text-right">Round Wins</td>
              <td className="text-right">Game Wins</td>
              <td className="text-right">Spread</td>
              { auth && <td className="text-right">Actions</td> }
            </tr>
          </thead>
          <tbody>
            { tournament?.participants?.map((row, idx) => (
              <tr
                key={row.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <td className="text-left">{ idx + 1}</td>
                <td component="th" scope="row">
                    <Link to={ `${row.id}` } component={RouterLink}>{row.name}</Link>
                </td>
                <td className="text-right">{row.rating}</td>
                <td className="text-right">{row.round_wins}</td>
                <td className="text-right">{row.game_wins}</td>
                <td className="text-right">{row.spread}</td>
                {auth && 
                    <td className="text-right">
                        <div className='d-inline-flex'>
                            <div className='form-check form-switch'>
                                <input className="form-check-input" type="checkbox"
                                    checked={row.offed != 0} onChange={ e => toggleParticipant(e, idx) }/>
                            </div>
                            { !isStarted() &&
                                <div className='form-col'>
                                    <i className='bi-x-circle' onClick = { e => deleteParticipant(e, idx)}></i>
                                </div>
                            }
                        </div>
                    </td>
                }
              </tr>
            ))}
          </tbody>
        </table>
      
     );
}

export function Participant(props) {
    const params = useParams();
    const [participant, setParticipant] = useState()
    const tournament = useTournament()

    useEffect(() => {
        if(participant == null && tournament) {
            fetch(`/api/tournament/${tournament.id}/participant/${params.id}/`).then(resp=>resp.json()).then(json=>{
                setParticipant(json)
                console.log(json)
            })
        } 
    },[tournament, participant])

    if(participant) {
        return (
            <div>
                <h2>{participant.name}</h2>
                <table className='table'>
                    <thead>
                        <tr>
                            <th>Board</th>
                            <th>Player</th>
                            <th>Wins</th>
                            <th>Margin</th>
                        </tr>
                    </thead>
                    <tbody>
                        { participant.members.map(p => (
                            <tr key={p.id}>
                                <td>{p.board}</td>
                                <td>{p.name}</td>
                                <td>{p.wins}</td>
                                <td>{p.spread}</td>
                            </tr>
                            )
                        )}
                    </tbody>
                </table>
            </div>
        )
    }
    return <div></div>
}
