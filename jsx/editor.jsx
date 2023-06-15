import React, { useState, useRef } from 'react';
import getCookie from './cookie.js';
import { Link } from "react-router-dom";
import { Participants } from './participant.jsx';


export function TournamentEditor() {
    const [tournament, setTournament] = useState({
        name: '', start_date: '', num_rounds: 0,
        entry_mode: 'S', 'private': true, team_size: 0
    })

    const ref = useRef(null)

    function saveTournament(e) {
        e.preventDefault()
        tournament.start_date = ref.current.value
        fetch(`/api/tournament/`, {
            method: 'POST', 'credentials': 'same-origin',
            headers:
            {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(tournament)
        }).then(resp => resp.json()).then(json => {
            console.log(json)
            window.location.href = `/${json.slug}/`
        })
    }
    
    return (
        <div className="container mt-5">
          <div className="row justify-content-center">
            <div className="col-md-6">
                <div className="card">
                    <div className="card-header">New Tournament</div>
                    <div className="card-body">
                        <div>Name: 
                            <input type="text" className="form-control"
                                onChange={e => setTournament({ ...tournament, name: e.target.value })} />
                        </div>
                        <div>
                            Start Date
                            <input type="date" initialvalue={tournament.start_date} ref={ref}
                                className="form-control"
                                />
                        </div>
                        <div>
                            Number of Rounds
                            <input type="number" value={tournament.num_rounds}  className="form-control"
                                onChange={e => setTournament({...tournament, num_rounds: e.target.value})} />
                        </div>
                        <div>
                            Tournament Type
                            <select value={tournament.type}  className="form-control"
                                onChange={e => setTournament({...tournament, entry_mode: e.target.value})} >
                                    <option value='S'>Singles</option>
                                    <option value='T'>Team</option>
                                    <option value='P'>Team with board tracking</option>
                            </select>
                        </div>
                        { tournament.entry_mode !== 'S' && 
                            <div>
                               Team size
                                <input type="number" value={tournament.team_size}  className="form-control"
                                    onChange={e => setTournament({...tournament, team_size: e.target.value})} />
                            </div>
                        }
                        <div>
                            <button className="btn btn-primary" 
                                disabled={ tournament.name == '' || tournament.num_rounds == 0 || ref.current.value == '' }
                                onClick={saveTournament}>Create</button>
                        </div>
                    </div>
                </div>
              </div>
            </div>
        </div>
    )
} 

console.log('editor 0.01')