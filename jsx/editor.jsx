import React, { useState, useEffect } from 'react';

import { useParams, Link } from "react-router-dom";
import { Participants } from './participant.jsx';
import { Rounds } from './round.jsx';

export function TournamentEditor({ tournament, tournamentChanged, saveTournament }) {
    return (
        <div>
            <div>Name: <input type="text" className="input-control"
                onChange={e => tournamentChanged({ ...tournament, name: e.target.value })} /></div>
            <div>
                <DatePicker selected={tournament.start_date} 
                    onChange={(date) => tournamentChanged({...tournament, start_date: date}) } />
            </div>
            <div>
                <button className="btn btn-primary" onClick={saveTournament}>Create</button>
            </div>
        </div>
    )
} 
