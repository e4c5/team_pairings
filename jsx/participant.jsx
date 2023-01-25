//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';

import {
    useParams,
    Link as RouterLink,
} from "react-router-dom";

import { Link, Switch } from '@mui/material';
import { useTournament, useTournamentDispatch } from './context.jsx';
import getCookie from './cookie.js';

export function Participants(props) {
    const tournament = useTournament();
    const dispatch = useTournamentDispatch()

    function toggleParticipant(e, idx) {
        const p = tournament.participants[idx];
        p['offed'] = p.offed == 0 ? 1 : 0;
        console.log(`/api/${tournament.id}/participant/${p.id}`)
        fetch(`/api/participant/${p.id}/`, 
            { method: 'PUT', 'credentials': 'same-origin',
              headers: 
              {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
              },
              body: JSON.stringify(p)
        }).then(resp => resp.json()).then(json => {
            dispatch({type: 'editParticipant', json})
        })
    }

    function delParticipant(e, idx) {
        console.log('delete');
    }

    return (
       <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Rank</TableCell>
              <TableCell align="right">Name</TableCell>
              <TableCell align="right">Seed</TableCell>
              <TableCell align="right">Round Wins</TableCell>
              <TableCell align="right">Game Wins</TableCell>
              <TableCell align="right">Spread</TableCell>
              <TableCell align="right">Offed</TableCell>
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
                <TableCell align="right">{ (tournament && tournament.is_editable)
                    ? <Switch checked={row.offed != 0} onChange={ e => toggleParticipant(e, idx) }/>
                    : <Switch checked={row.offed != 0} onChange={ e => delParticipant(e, idx) }/> }
                </TableCell>
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

    useEffect(() => {
        if(participant == null && props.tournament) {
            fetch(`/api/${props.tournament.id}/participant/${params.id}/`).then(resp=>resp.json()).then(json=>{
                setParticipant(json)
                console.log(json)
            })
        } 
    })

    return <div>Hello World </div>
}
