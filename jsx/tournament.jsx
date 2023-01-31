import React, { useState, useEffect } from 'react';

import { useParams, Link } from "react-router-dom";
import getCookie from './cookie.js';
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
        console.log(params.slug)
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
                <input size='small' placeholder='Name' data-test-id='name'
                    value={name} onChange={ e => handleChange(e, 'name')} />
                <input size='small' placeholder='seed' 
                    type='number' data-test-id='seed'
                    value={seed} onChange={ e => handleChange(e, 'seed')} />
                <button className='btn btn-primary' onClick = { e => add(e)} data-test-id='add'>
                    Add
                </button>
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
            <ul>
            { props.tournaments?.map(t => 
                <li key={t.id}>
                    <Link to={"/" + t.slug} >{ t.name }</Link>
                </li>) 
            }
            </ul>

        </div>
    )
}

console.log('Tournament 0.03')