import React, { useState, useRef } from 'react';
import getCookie from './cookie.js';

export function TournamentEditor() {
    const [tournament, setTournament] = useState({
        name: '', start_date: '', num_rounds: 0, round_robin: false,
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
            window.location.href = `/${json.slug}/`
        })
    }

    function isDisabled() {
        return tournament.name == '' || 
               (tournament.num_rounds == 0 && tournament.round_robin == false) || 
               ref.current.value == ''
    }
    
    return (
        <div className="container mt-5">
          <div className="row justify-content-center">
            <div className="col-md-6">
                <div className="card">
                    <div className="card-header">New Tournament</div>
                    <div className="card-body">
                        <div>Name: 
                            <input type="text" className="form-control" data-testid='name'
                                onChange={e => setTournament({ ...tournament, name: e.target.value })} />
                        </div>
                        <div>
                            Start Date
                            <input type="date" initialvalue={tournament.start_date} ref={ref}
                                className="form-control"  data-testid='date'
                                />
                        </div>
                        <div>
                            <label>
                                <input type="radio" value="round-robin" 
                                    checked={tournament.round_robin} data-testid='rr'
                                    onChange={() => setTournament({...tournament, round_robin: true})}/>
                                Round Robin
                            </label>
                            <label>
                                <input type="radio" value="non-round-robin" 
                                    checked={!tournament.round_robin}  data-testid='non-rr'
                                    onChange={() => setTournament({...tournament, round_robin: false})}/>
                                Non Round Robin
                            </label>
                        </div>
                        { !tournament.round_robin &&
                            <div>
                                Number of Rounds
                                <input type="number" value={tournament.num_rounds}  className="form-control"
                                    data-testid='rounds'
                                    onChange={e => setTournament({...tournament, num_rounds: e.target.value})} />
                            </div>
                        }
                        <div>
                            Tournament Type
                            <select value={tournament.type}  className="form-control" data-testid='type'
                                onChange={e => setTournament({...tournament, entry_mode: e.target.value})} >
                                    <option value='S'>Singles</option>
                                    <option value='T'>Team</option>
                                    <option value='P'>Team with board tracking</option>
                            </select>
                        </div>
                        { tournament.entry_mode !== 'S' && 
                            <div>
                               Team size
                                <input type="number" value={tournament.team_size} 
                                    className="form-control" data-testid='team-size'
                                    onChange={e => setTournament({...tournament, team_size: e.target.value})} />
                            </div>
                        }
                        <div>
                            <button className="btn btn-primary" 
                                disabled={ isDisabled() }
                                onClick={saveTournament}>Create</button>
                        </div>
                    </div>
                </div>
              </div>
            </div>
        </div>
    )
} 

console.log('editor 0.03')
