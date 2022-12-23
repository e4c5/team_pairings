//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';
import * as ReactDOM from 'react-dom';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import {
    createBrowserRouter,
    createRoutesFromElements,
    RouterProvider,
    useParams,
    Route,
    Routes,
    Link as RouterLink,
    BrowserRouter,
    Outlet
} from "react-router-dom";


import { Link, Switch } from '@mui/material';

export function Participants(props) {
    const tourny = props.tournament;

    return (
        <>
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
            {props.rows && props.rows.map((row, idx) => (
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
                <TableCell align="right">{ (tourny && tourny.is_editable)
                    ? <Switch checked={row.offed != 0} onChange={ e => props.toggleParticipant(e, idx) }/>
                    : <Switch checked={row.offed != 0} onChange={ e => props.delParticipant(e, idx) }/> }
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      </>
    );
}

export function Participant(props) {
    const params = useParams();
    const [participant, setParticipant] = useState()

    // useEffect(() => {
    //     if(participant == null && tourny) {
    //         fetch(`/api/${tourny.id}/participant/${params.id}/`).then(resp=>resp.json()).then(json=>{
    //             setParticipant(json)
    //         })
    //     } 
    // })

    return <div>Hello World </div>
}
