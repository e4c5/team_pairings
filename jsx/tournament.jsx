import React, { useState, useEffect } from 'react';

import { useParams, Link } from "react-router-dom";
import getCookie from './cookie.js';
import { Participants } from './participant.jsx';
import { Rounds } from './round.jsx';
import { useTournament, useTournamentDispatch } from './context.jsx';

export function Tournament(props) {
    const params = useParams()
    const [name, setName] = useState('')
    const [rating, setrating] = useState('')
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
            setrating(e.target.value)
        }
    }

    function add(e) {
        let ok = true;
        fetch(`/api/tournament/${tournament.id}/participant/`, 
            { method: 'POST', 'credentials': 'same-origin',
              headers: 
              {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
              },
              body: JSON.stringify({ tournament: 1, name: name, rating: rating})
            }).then(resp =>{ 
                ok = resp.ok;
                setrating('')
                setName('')
                return resp.json()
            }).then(json => {
                if(ok) {
                    dispatch({type: "addParticipant", participant: json})
                }
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

    function addParticipant() {
        if(document.getElementById('hh') && document.getElementById('hh').value) {
            return (
                
                <div className='row align-middle'>
                    <div className='col'>
                        <input className='form-control' placeholder='Name' data-test-id='name'
                            value={name} onChange={ e => handleChange(e, 'name')} />
                    </div>
                    <div className='col'>
                        <input className='form-control' placeholder='rating' 
                            type='number' data-test-id='rating'
                            value={rating} onChange={ e => handleChange(e, 'rating')} />
                    </div>
                    <div className='col'>
                        <button className='btn btn-secondary' onClick = { e => add(e)} data-test-id='add'>
                            <i className='bi-plus' ></i>
                        </button>
                    </div>
                </div>);
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
            <h1>Sri Lanka Scrabble Tournament Manager</h1>

            <ul className='list-group'>
            { props.tournaments?.map(t => 
                <li className='list-group-item' key={t.id}>
                    <Link to={"/" + t.slug} >{ t.name }</Link>
                </li>) 
            }
            </ul>

        </div>
    )
}

console.log('Tournament 0.03')