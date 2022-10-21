//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';
import * as ReactDOM from 'react-dom';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';


function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) {
        return match[2];
    }
}
/*
name = models.CharField(max_length=128)
played = models.IntegerField(default=0, null=True)
game_wins = models.FloatField(default=0, null=True)
round_wins = models.FloatField(default=0, null=True)
tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')

spread = models.IntegerField(default=0, null=True)
position = models.IntegerField(default=0, null=True)
offed = models.IntegerField(default=0, null=True)
seed = models.IntegerField(default=0, null=True)
*/
const Participants = (props) => {
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
            {props.rows && props.rows.map((row, idx) => (
              <TableRow
                key={row.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell align="right">{ idx + 1}</TableCell>
                <TableCell component="th" scope="row">
                  {row.name}
                </TableCell>
                <TableCell align="right">{row.round_wins}</TableCell>
                <TableCell align="right">{row.game_wins}</TableCell>
                <TableCell align="right">{row.spread}</TableCell>
                <TableCell align="right">{row.offed}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

const Tournament = () => {
    const [name, setName] = React.useState('')
    const [seed, setSeed] = React.useState('')
    const [participants, setParticipants] = React.useState(null)

    useEffect(() => {
        if(participants == null) {
            fetch('/participant/').then(resp => resp.json()).then(json =>{
                setParticipants(json)
                console.log('Updated')
            })
        }
    })

    const handleChange = (e, p) => {
        if(p == 'name') {
            setName(e.target.value) 
        }
        else {
            setSeed(e.target.value)
        }
    }

    const add = e => {
        fetch('/participant/', 
            { method: 'POST', 'credentials': 'same-origin',
              headers: 
              {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
              },
              body: JSON.stringify({ tournament: 1, name: name, seed: seed})
            }).then(resp => resp.json()).then(json => {
                setParticipants([...participants, json])
                setSeed(seed + 1)
                setName('')
            })
    }

    return (
        <div>
            <Participants rows={participants} /> 
            <TextField size='small' placeholder='Name' 
                value={name} onChange={ e => handleChange(e, 'name')} />
            <TextField size='small' placeholder='seed' type='number'
                value={seed} onChange={ e => handleChange(e, 'seed')} />
            <Button variant="contained" onClick = { e => add(e)}>Add</Button>
        </div>)
}

const div = document.getElementById('root')
const root = ReactDOM.createRoot(div) 
root.render(<Tournament/>)
console.log('main.js 0.01.1')