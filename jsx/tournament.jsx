import React, { useState, useEffect } from 'react';

import { Button, List, ListItem, TextField }  from '@mui/material';
import {
    useParams,
    Route, Routes,     
    Link as RouterLink,
} from "react-router-dom";

import {Participant, Participants } from "./participant.jsx"
import {Round, Rounds} from "./round.jsx"
import getCookie from './cookie.js';

import { Link, Switch, Box } from '@mui/material';
 
export function Tournament(props) {
    const params = useParams()
    const [name, setName] = React.useState('')
    const [seed, setSeed] = React.useState('')
    
    useEffect(() => {
        const tournament = props.tournament;

        props.tournaments?.map(t => {
            if(t.slug == params.slug) {
                if(tournament !== t) {
                    console.log('update')
                    /* if the tournament has changed, fetch it's rounds and participants */
                    fetch(`/api/${t.id}/participant/`).then(resp => resp.json()).then(json =>{
                        console.log('setting participans to ', json)
                        props.setParticipants(json)
                    })
                    props.setTournament(t)

                    fetch(`/api/${t.id}/round/`).then(resp => resp.json()).then(json =>{
                        props.setRounds(json)
                    })
                }
            }
        })    
    }, [props.tournament])

    const handleChange = (e, p) => {
        if(p == 'name') {
            setName(e.target.value) 
        }
        else {
            setSeed(e.target.value)
        }
    }

    function toggleParticipant(e, idx) {
        const p = props.participants[idx];
        p['offed'] = p.offed == 0 ? 1 : 0;
        console.log(`/api/${props.tournament.id}/participant/${p.id}`)
        fetch(`/api/participant/${p.id}/`, 
            { method: 'PUT', 'credentials': 'same-origin',
              headers: 
              {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
              },
              body: JSON.stringify(p)
            }).then(resp => resp.json()).then(json => {
                const old = [...props.participants]
                old[idx] = json
                props.setParticipants(old)
        })
    }

    function delParticipant(e, idx) {
        console.log('delete');
    }

    const add = e => {
        fetch(`/api/${props.tournament.id}/participant/`, 
            { method: 'POST', 'credentials': 'same-origin',
              headers: 
              {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
              },
              body: JSON.stringify({ tournament: 1, name: name, seed: seed})
            }).then(resp => resp.json()).then(json => {
                props.setParticipants([...props.participants, json])
                setSeed(seed + 1)
                setName('')
            })
    }

    function updateStandings(result) {
        const p = props.participants.map(team => {
            if(team.id == result.first.id) {
                return result.first
            }
            else if(team.id == result.second.id) {
                return result.second
            }
            else {
                return team
            }
        })
        props.setParticipants(p)
    }

    return (
        <div>
                <Participants rows={props.participants} tournament={props.tournament} 
                    delParticipant={ delParticipant } toggleParticipant = { toggleParticipant}
                /> 
                <TextField size='small' placeholder='Name' 
                    value={name} onChange={ e => handleChange(e, 'name')} />
                <TextField size='small' placeholder='seed' type='number'
                    value={seed} onChange={ e => handleChange(e, 'seed')} />
                <Button variant="contained" onClick = { e => add(e)}>Add</Button>
                <Rounds rounds={props.rounds} tournament={props.tournament}/>
            
        </div>)
}


export function Tournaments(props) {
    const id = useParams();

    return (
        <div>
            <List>
            { props.tournaments?.map(t => 
                <ListItem key={t.id}>
                    <Link to={"/" + t.slug} component={RouterLink} >{ t.name }</Link>
                </ListItem>) 
            }
            </List>

        </div>
    )
}

console.log('Tournament 0.02')