import React, { useState, useEffect } from 'react';

import { Button, List, ListItem, TextField } from '@mui/material';
import {
    Route, Router, useRouter, useLocation,
    Link as RouterLink,
} from "wouter";

import { Participant, Participants } from "./participant.jsx"
import { Round, Rounds } from "./round.jsx"
import getCookie from './cookie.js';

import { Link, Switch, Box } from '@mui/material';


const NestedRoutes = (props) => {
    const router = useRouter();
    const [parentLocation] = useLocation();

    const nestedBase = `${router.base}${props.base}`;

    // don't render anything outside of the scope
    if (!parentLocation.startsWith(nestedBase)) return null;

    // we need key to make sure the router will remount if the base changes
    return (
        <Router base={nestedBase} key={nestedBase}>
            {props.children}
        </Router>
    );
};


export function Tournament(props) {
    const [rounds, setRounds] = React.useState(null)
    const [name, setName] = React.useState('')
    const [seed, setSeed] = React.useState('')
    const [participants, setParticipants] = React.useState(null)
    const [tournament, setTournament] = React.useState(null)

    useEffect(() => {
        props.tournaments?.map(t => {
            if (t.slug == props.params.slug) {
                if (tournament != t) {
                    /* if the tournament has changed, fetch it's rounds and participants */
                    setTournament(t)

                    fetch(`/api/${t.id}/participant/`).then(resp => resp.json()).then(json => {
                        setParticipants(json)
                    })
                    console.log('Fetching sounds')
                    fetch(`/api/${t.id}/round/`).then(resp => resp.json()).then(json => {
                        console.log('rounds set to ')
                        console.log('json')
                        setRounds(json)
                    })
                }
            }
        })
    })

    const handleChange = (e, p) => {
        if (p == 'name') {
            setName(e.target.value)
        }
        else {
            setSeed(e.target.value)
        }
    }

    function toggleParticipant(e, idx) {
        const p = participants[idx];
        p['offed'] = p.offed == 0 ? 1 : 0;
        console.log(`/api/${tournament.id}/participant/${p.id}`)
        fetch(`/api/participant/${p.id}/`,
            {
                method: 'PUT', 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify(p)
            }).then(resp => resp.json()).then(json => {
                const old = [...participants]
                old[idx] = json
                setParticipants(old)
            })
    }

    function delParticipant(e, idx) {
        console.log('delete');
    }

    const add = e => {
        fetch(`/api/${tournament.id}/participant/`,
            {
                method: 'POST', 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ tournament: 1, name: name, seed: seed })
            }).then(resp => resp.json()).then(json => {
                setParticipants([...participants, json])
                setSeed(seed + 1)
                setName('')
            })
    }

    function updateStandings(result) {
        const p = participants.map(team => {
            if (team.id == result.first.id) {
                return result.first
            }
            else if (team.id == result.second.id) {
                return result.second
            }
            else {
                return team
            }
        })
        setParticipants(p)
    }

    // return (<div> 
    //         <Participants rows={participants} tournament={tournament} 
    //                 delParticipant={ delParticipant } toggleParticipant = { toggleParticipant}
    //         /> 
    //     </div>)

    const CurrentLoc = () => useLocation()[0];

    if (tournament) {
        return (
            <div>
                <CurrentLoc/>
                <NestedRoutes base={ `/${tournament.slug}`} >
                    <TextField size='small' placeholder='Name'
                        value={name} onChange={e => handleChange(e, 'name')} />
                    <TextField size='small' placeholder='seed' type='number'
                        value={seed} onChange={e => handleChange(e, 'seed')} />
                    <Button variant="contained" onClick={e => add(e)}>Add</Button>
                    {/* <Routes>
                                <Route path=":id" element={<Participant />} />
                                <Route path="round/:id" element={<Round tournament={tournament} rounds={rounds}/>} />
                        </Routes> */}
                    {/* <Rounds rounds={rounds} tournament={tournament}/> */}
                    
                    <Route path="/bada">
                        This is baaddd
                    </Route>
                    <Participants rows={participants} tournament={tournament}
                        delParticipant={delParticipant} toggleParticipant={toggleParticipant}
                    />
                </NestedRoutes>
                <RouterLink href="/bada">aFuck it</RouterLink>
            </div>)
    }
}


export function Tournaments(props) {
    return (
        <div>
            <List>
                {props.tournaments?.map(t =>
                    <ListItem key={t.id}>
                        <Link href={t.slug} component={RouterLink} >{t.name}</Link>
                    </ListItem>)
                }
            </List>

        </div>
    )
}

console.log('Tournament 0.02.1')