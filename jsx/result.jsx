import React, { useState, useEffect } from 'react';
import { Button }  from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { TableCell, TableRow } from '@mui/material';
import { useTournament, useTournamentDispatch } from './context.jsx';
  
export default function Result({r, index, editScore}) {
    const editable = document.getElementById('editable')
    const dispatch = useTournamentDispatch()
    const tournament = useTournament()

    function resultIn() {
        if(editable) {

        }
        return (
            <TableRow>
                <TableCell sx={{border:1}} >{ r.p1.name }</TableCell>
                <TableCell align="right" sx={{border:1}} >{ r.games_won } - { tournament.team_size - r.games_won }</TableCell>
                <TableCell align="right" sx={{border:1}} >{ r.score1 }</TableCell>
                <TableCell sx={{border:1}} >{ r.p2.name }</TableCell>
                <TableCell align="right" sx={{border:1}} >{ tournament.team_size - r.games_won } - { r.games_won }</TableCell>
                <TableCell align="right" sx={{border:1}} >{ r.score2 }</TableCell>
                <TableCell align="right" sx={{border:1}} >
                        <Button onClick={e => editScore(e, index)}><EditIcon/></Button>
                </TableCell>
            </TableRow>
        )
    }

    function resultOut() {
        return (
            <TableRow>
                <TableCell sx={{border:1}} >{ r.p1.name }</TableCell>
                <TableCell sx={{border:1}} ></TableCell>
                <TableCell sx={{border:1}} ></TableCell>
                <TableCell sx={{border:1}} >{ r.p2.name }</TableCell>
                <TableCell sx={{border:1}} ></TableCell>
                <TableCell sx={{border:1}} ></TableCell>
                <TableCell sx={{border:1}} ></TableCell>
            </TableRow>
        )
    }

    if(r.score1) {
        return resultIn()
    }
    else {
        return resultOut();
    }
}
