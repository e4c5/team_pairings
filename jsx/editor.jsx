import React, { useState, useEffect, useRef } from 'react';

import { useParams, Link } from "react-router-dom";
import { Participants } from './participant.jsx';
import { Rounds } from './round.jsx';

export function TournamentEditor({ tournament, tournamentChanged, saveTournament }) {
    const ref = useRef(null)
    return (
        <div>
            <div>Name: <input type="text" className="input-control"
                onChange={e => tournamentChanged({ ...tournament, name: e.target.value })} /></div>
            <div>
                <input type="date" initialvalue={tournament.start_date} ref={ref}
                    />
            </div>
            <div>
                Number of Rounds
                <input type="number" value={tournament.num_rounds} 
                    onChange={e => tournamentChanged({...tournament, num_rounds: e.target.value})} />
            </div>
            <div>
                <button className="btn btn-primary" onClick={saveTournament}>Create</button>
            </div>
        </div>
    )
} 
