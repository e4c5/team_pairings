//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { Button }  from '@mui/material';

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

    return (
       <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Rank</TableCell>
              <TableCell align="left">Name</TableCell>
              <TableCell align="right">Seed</TableCell>
              <TableCell align="right">Round Wins</TableCell>
              <TableCell align="right">Game Wins</TableCell>
              <TableCell align="right">Spread</TableCell>
              { auth && <TableCell align="right">Actions</TableCell> }
            </TableRow>
          </TableHead>
          <TableBody>
            { tournament?.participants?.map((row, idx) => (
              <TableRow
                key={row.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell align="left">{ idx + 1}</TableCell>
                <TableCell component="th" scope="row">
                    <Link to={ `${row.id}` } component={RouterLink}>{row.name}</Link>
                </TableCell>
                <TableCell align="right">{row.seed}</TableCell>
                <TableCell align="right">{row.round_wins}</TableCell>
                <TableCell align="right">{row.game_wins}</TableCell>
                <TableCell align="right">{row.spread}</TableCell>
                {auth && 
                    <TableCell align="right">
                        <Switch checked={row.offed != 0} onChange={ e => toggleParticipant(e, idx) }/>
                        <Button variant="contained" onClick = { e => deleteParticipant(e, idx)}>Del</Button>
                    </TableCell>
                }
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
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
                <div className='row'>
                    <div className='row'>Board</div>
                    <div className='col'>Player</div>
                    <div className='col'>Wins</div>
                    <div className='col'>Margin</div>
                </div>
                { participant.members.map(p => (
                    <div className='row' key={p.id}>
                        <div className='col'>{p.board}</div>
                    </div>
                    )
                )}
            </div>
        )
    }
    return <div></div>
}
