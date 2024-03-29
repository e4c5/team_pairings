import React, { useState, useEffect, useRef } from 'react';

import { useParams, Link } from "react-router-dom";
import getCookie from './cookie.js';
import { Participants } from './participant.jsx';
import { Rounds } from './round.jsx';
import { useTournament, useTournamentDispatch } from './context.jsx';

export function Tournament(props) {
    const params = useParams()
    const [name, setName] = useState({value: '', error: ''})
    const [rating, setRating] = useState({value: '', error: ''})
    const [fill, setFill] = useState({value: '', error: '' })
    const tournamentDispatch = useTournamentDispatch()
    const tournament = useTournament()

    const ref = useRef(null)

    useEffect(() => {
        if(tournament === null || tournament.slug != params.slug) {
            props.tournaments?.map(t => {
                if(t.slug == params.slug) {
                    fetch(`/api/tournament/${t.id}/`).then(resp=>resp.json()
                    ).then(json=>{
                        tournamentDispatch({type: 'replace', value: json}) 
        
                    })
                }
            })    
        }
    }, [props.tournaments])

    const handleChange = (e, p) => {
        if(p == 'name') {
            setName({...name, value: e.target.value }) 
        }
        else if(p == 'fill') {
            setFill({...fill, value: e.target.value })
        }
        else {
            setRating({...rating, value: e.target.value})
        }
    }

    function filler(e) 
    {
        let ok = true;
        fetch(`/api/tournament/${tournament.id}/random_fill/`, 
            { method: 'POST', 'credentials': 'same-origin',
              headers: 
              {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
              },
              body: JSON.stringify({ fill: fill.value})
            }).then(resp =>{ 
                ok = resp.ok;
                if(ok) {
                    setFill({...rating, value: ''})
                }
                return resp.json()
            }).then(json => {
                ref.current.focus();
            }
        )
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
              body: JSON.stringify({ tournament: tournament.id, name: name.value, rating: rating.value})
            }).then(resp =>{ 
                ok = resp.ok;
                if(ok) {
                    setRating({...rating, value: ''})
                    setName({...name, value: ''})
                }
                return resp.json()
            }).then(json => {
                
            })
    }

    function addParticipant() {
        if(document.getElementById('hh') && document.getElementById('hh').value) {
            return (
                
                <div className='row align-middle'>
                    <div className='col-md-5 col-sm-5'>
                        <input className={ `form-control ${name.error ? 'is-invalid' : ''}` } 
                            placeholder='Name' data-testid='name' ref={ref}
                            value={name.value} onChange={ e => handleChange(e, 'name')} />
                        <div className='invalid-feedback'>
                            {name.error}
                        </div>
                    </div>
                    <div className={tournament?.private ?  'col-md-2 col-sm-2' : 'col-md-5 col-sm-5'}>
                        <input className={ `form-control ${rating.error ? 'is-invalid' : ''}` } 
                            placeholder='rating' 
                            type='number' data-testid='rating'
                            value={rating.value} onChange={ e => handleChange(e, 'rating')} />
                        <div className='invalid-feedback'>
                            {rating.error}
                        </div>
                    </div>
                    <div className='col-md-1 col-sm-1'>
                        <button className='btn btn-secondary' onClick = { e => add(e)} data-testid='add'>
                            <i className='bi-plus' ></i>
                        </button>
                    </div>
                    
                    { tournament?.private &&
                        <>
                            <div className='col-md-2 col-sm-2'>
                                <input className='form-control' placeholder='Random fill #'
                                    value={fill.value}
                                    onChange={ e => handleChange(e, 'fill')}
                                    type='number' data-testid='fill-number' />
                            </div>
                            
                            <div className='col-md-2 col-sm-2'>
                                <button className='btn btn-secondary' onClick = { e => filler(e)} data-testid='fill'>
                                    Random Fill
                                </button>
                            </div>
                        </>
                    }


                </div>);
        }
        return null;
    }

    return (
        <div>
            <h2><a href={tournament?.slug}>{ tournament?.name }</a></h2>
            <Participants /> 
            { addParticipant() }
            <Rounds/>
        </div>
    )
}


export function Tournaments(props) {
    const id = useParams();
    const auth = document.getElementById('hh') && document.getElementById('hh').value

    return (
        <div>
            <h1>Herald :: Scrabble Tournament Manager</h1>

            <ul className='list-group'>
            { props.tournaments?.map(t =>  
                <li className='list-group-item' key={t.id}>
                    <Link to={"/" + t.slug} >{ t.name }</Link>
                </li>) 
            }
            </ul>
            { auth && <Link to="/new">New Tournament</Link> }
        </div>
    )
}

console.log('Tournament 0.04')