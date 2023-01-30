import React, { useState, useEffect } from 'react';

import { Button, List, ListItem, TextField }  from '@mui/material';
import { useParams, Link as RouterLink } from "react-router-dom";
import getCookie from './cookie.js';
import { Link } from '@mui/material';
import { Participants } from './participant.jsx';
import { Rounds } from './round.jsx';
import { useTournament, useTournamentDispatch } from './context.jsx';

export function Tournament(props) {
    const params = useParams()
    const [name, setName] = useState('')
    const [seed, setSeed] = useState('')
    const dispatch = useTournamentDispatch()
    const tournament = useTournament()

    useEffect(() => {
        
        if(tournament === null || tournament.slug != params.slug) {
            props.tournaments?.map(t => {
                if(t.slug == params.slug) {
                    fetch(`/api/tournament/${t.id}/`).then(resp=>resp.json()
                    ).then(json=>{
                        dispatch({type: 'replace', value: json})                
                    })
                }
            })    
        }
    }, [props.tournaments])

    const handleChange = (e, p) => {
        if(p == 'name') {
            setName(e.target.value) 
        }
        else {
            setSeed(e.target.value)
        }
    }

    const add = e => {
        fetch(`/api/tournament/${tournament.id}/participant/`, 
            { method: 'POST', 'credentials': 'same-origin',
              headers: 
              {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
              },
              body: JSON.stringify({ tournament: 1, name: name, seed: seed})
            }).then(resp => resp.json()).then(json => {
                dispatch({type: "addParticipant", participant: json})
            })
        setSeed('')
        setName('')

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

    function addParticipant() {
        if(document.getElementById('hh') && document.getElementById('hh').value) {
            return (<>
                <TextField size='small' placeholder='Name' data-test-id='name'
                    value={name} onChange={ e => handleChange(e, 'name')} />
                <TextField size='small' placeholder='seed' 
                    type='number' data-test-id='seed'
                    value={seed} onChange={ e => handleChange(e, 'seed')} />
                <Button variant="contained" onClick = { e => add(e)} data-test-id='add'>
                    Add
                </Button>
            </>);
        }
        return null;
    }

    return (
        <div>
            <Participants /> 
            { addParticipant() }
            <Rounds/>
        </div>
    )
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

console.log('Tournament 0.03')