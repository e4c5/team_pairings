//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';

import {
    Route, Routes,
    BrowserRouter
} from "react-router-dom";

import {Participant, Participants } from "./participant.jsx"
import {Tournament, Tournaments } from "./tournament.jsx"
import {Round, Rounds} from "./round.jsx"
import { TournamentProvider } from './context.jsx';
 
export default function App() {
    const [tournaments, setTournaments] = useState()

    function fetchTournaments() {
        fetch(`/api/tournament/`).then(resp=>resp.json()).then(json=>{
            setTournaments(json)
        })
    }

    useEffect(() => {
        if(tournaments == null) {
            fetchTournaments()
        } 
    })

    return (
      <BrowserRouter>   
        <TournamentProvider>
            <Routes>
                <Route path="/" element={<Tournaments tournaments={tournaments}/>}></Route>
                <Route path="/:slug" >
                    <Route path="" 
                        element={ <Tournament tournaments={tournaments} /> } 
                    />

                    <Route path=":id" element={<Participant />} />
                    <Route path="round/:id" element={<Round />} />
                </Route>
            </Routes>
        </TournamentProvider>
      </BrowserRouter>
    )
}
