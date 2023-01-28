//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';

import {
    Route, Routes,
    BrowserRouter, useNavigate
} from "react-router-dom";

import {Participant, Participants } from "./participant.jsx"
import {Tournament, Tournaments } from "./tournament.jsx"
import {Round, Rounds} from "./round.jsx"
import { TournamentProvider } from './context.jsx';
 
export default function App() {
    const [tournaments, setTournaments] = useState()
    const navigate = useNavigate()

    function fetchTournaments() {
        fetch(`/api/tournament/`).then(resp=>resp.json()).then(json=>{
            setTournaments(json)
        })
    }

    useEffect(() => {
        document.title = 'Sri Lanka Scrabble Pairing App'
        if(tournaments == null) {
            fetchTournaments()
        } 
    },[])

    useEffect(() => {
        if(tournaments != null) {
            const path = document.getElementById('frm')
            if (path?.innerText.length > 1) {
                navigate(path.innerText)
            }
        }
    }, [tournaments])

    return (
      
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
      
    )
}
