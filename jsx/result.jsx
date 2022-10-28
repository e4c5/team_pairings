import React, { useState, useEffect } from 'react';
import { Button }  from '@mui/material';

import EditIcon from '@mui/icons-material/Edit';

import { Table, TableBody, TableCell,
         TableContainer, TableHead, TableRow } from '@mui/material';

export default function Result({r, tournament, index, editScore}) {
    const editable = document.getElementById('editable')

    function resultIn() {
        if(editable) {

        }
        return (
            <TableRow>
                <TableCell sx={{border:1}} >{ r.first.name }</TableCell>
                <TableCell align="right" sx={{border:1}} >{ r.games_won } - { tournament.team_size - r.games_won }</TableCell>
                <TableCell align="right" sx={{border:1}} >{ r.score1 }</TableCell>
                <TableCell sx={{border:1}} >{ r.second.name }</TableCell>
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
                <TableCell sx={{border:1}} >{ r.first.name }</TableCell>
                <TableCell sx={{border:1}} ></TableCell>
                <TableCell sx={{border:1}} ></TableCell>
                <TableCell sx={{border:1}} >{ r.second.name }</TableCell>
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
