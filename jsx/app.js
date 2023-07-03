//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';

import {
    Route, Routes,
    useNavigate
} from "react-router-dom";

import { Participant} from "./participant.jsx"
import { Tournament, Tournaments } from "./tournament.jsx"
import { Round } from "./round.jsx"
import { Boards } from './boards.jsx';
import { TournamentEditor } from './editor.jsx';
import { useTournament, useTournamentDispatch } from './context.jsx';
import { Theme } from './theme.jsx';

/**
 * The main entry point.
 * 
 * This project is setup to provide read only data for non authenticated users
 * and read/write for logged in users. We implement it strictly in the backend. 
 * All end points will return forbidden http status codes for PUT, PATH, DELETE
 * and POST for no authenticated users.
 * 
 * Even when a user has been authenticated he needs to be identified as a 
 * director for the tournament in order to sucessfully send PUT, POST etc to
 * the backend.
 * 
 * So how does react find out if the user is authenticated or not, well 
 * there are lots of different ways but it was chosen that a hidden html field
 * is the solution here. It doesn't matter that a user will be able to attack
 * the page through the developer tools and add such a hidden field, all he
 * will manage to achieve is to see a few HTML forms that he cannot use.
 * @returns 
 */
export default function App() {
    const [tournaments, setTournaments] = useState()

    const tournament = useTournament()
    const tournamentDispatch = useTournamentDispatch();
    const navigate = useNavigate()

    const [ws, setWs] = useState()

    useEffect(() => {
        /**
         * For real time updates use websockets.
         */
        let wssUrl = window.location.protocol == 'https:' 
            ? `wss://${location.host}/ws/`
            : `ws://${location.host}/ws/`


        const ws = new WebSocket(wssUrl)
        ws.onmessage = function (e) {
            const obj = JSON.parse(e.data)
            console.log(obj)
            
            if (obj.participant) {
                // add a new participant to the event
                tournamentDispatch(
                    { type: 'editParticipant', participant: obj.participant, tid: obj.tournament_id }
                )
            }
            if (obj.participants) {
                // replace all the participants with new data
                tournamentDispatch(
                    { type: 'participants', participants: obj.participants, tid: obj.tournament_id }
                )
            }
            if (obj.results) {
                // replace the results for the given round
                if (obj.round_no) {
                    tournamentDispatch(
                        {
                            type: 'updateResult', result: obj.results,
                            round: obj.round_no -1, tid: obj.tournament_id
                        }
                    )
                }
            }
            if (obj.round) {
                // update a reound
                tournamentDispatch(
                    { type: 'editRound', round: obj.round, tid: obj.tournament_id }
                )

            }
        }
        setWs(ws)
    }, [])

    /**
     * Initial list of tournaments fetched as http
     */
    function fetchTournaments() {
        fetch(`/api/tournament/`).then(resp => resp.json()).then(json => {
            setTournaments(json)
        })
    }

    useEffect(() => {
        document.title = 'Herald :: Scrabble Tournament Management'
        if (tournaments == null) {
            fetchTournaments()
        }
    }, [])

    /**
     * This effect supports bookmarkable URLs.
     * If a react route is saved as a bookmark and visited later or the page is
     * simply reloaded, this effect fetches the neccassary data to recreate the
     * route and navigate there.
     */
    useEffect(() => {
        if (tournaments != null) {
            const path = document.getElementById('frm')
            if (path?.innerText.length > 1) {
                const parts = path.innerText.split('/')
                if (parts.length > 1) {
                    const slug = parts[0] === "" ? parts[1] : parts[0];
                    tournaments?.map(t => {
                        if (t.slug == slug) {
                            fetch(`/api/tournament/${t.id}/`).then(resp => resp.json()
                            ).then(json => {
                                tournamentDispatch({ type: 'replace', value: json })
                            })
                        }
                    })
                }
                navigate(path.innerText)
            }
        }
    }, [tournaments])

    function saveTournament(e) {
        e.preventDefault()
        console.log('Save tournament')
    }

    return (
        <>
        <div className='float-end mt-3'><Theme/></div>
            <Routes>
                <Route path="/" element={<Tournaments tournaments={tournaments} />}></Route>
                <Route path="/new" 
                    element={
                        <TournamentEditor />
                    }>
                </Route>
                <Route path="/:slug" >
                    <Route path=""
                        element={<Tournament tournaments={tournaments} />}
                    />
                    <Route path="boards" element={<Boards />} />
                    <Route path=":id" element={<Participant />} />
                    <Route path="round/:id" element={<Round />} />
                </Route>
            </Routes>
        </>
    )
}

console.log('App.js 0.1')