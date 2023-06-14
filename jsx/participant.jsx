//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';
import {
    useParams,
    Link,
} from "react-router-dom";
import { ResultTable , ResultList} from './result.jsx';
import { useTournament, useTournamentDispatch } from './context.jsx';
import getCookie from './cookie.js';

const individual = [
    ["Rank", "pos"],
    ["Name", "name"],
    ["Rating", "rating"],
    ["Won", "game_wins"],
    ["Spread", "spread"],
]

const team = [
    ["Rank", "pos"],
    ["Name", "name"],
    ["Rating", "rating"],
    ["Round Wins", "round_wins"],
    ["Game Wins", "game_wins"], 
    ["Spread", "spread"],
]

/**
 * Component for displaying a list of participants
 * A participant maybe a team for a team tournament.
 * @param {*} props 
 * @returns 
 */
export function Participants(props) {
    const tournament = useTournament();
    const dispatch = useTournamentDispatch();

    const auth = document.getElementById('hh') && document.getElementById('hh').value
    const columns = tournament?.team_size ? [...team ] : [...individual]

    if (auth) {
        columns.push(["Actions"])
    }

    /**
     * Switch the on / off state of a participant.
     * @param {*} e 
     * @param {*} idx 
     * @param {*} toggle 
     */
    function toggleParticipant(e, idx) {
        const p = tournament.participants[idx];
        p['offed'] = p.offed == 0 ? 1 : 0;

        fetch(`/api/tournament/${tournament.id}/participant/${p.id}/`,
            {
                method: 'PUT', 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify(p)
            }).then(resp => resp.json()).then(json => dispatch({ type: 'editParticipant', participant: json }))
    }

    /**
     * Deletes the participant only possible if no games played
     * @param {*} e 
     * @param {*} idx 
     */
    function deleteParticipant(e, idx) {
        const p = tournament.participants[idx];
        fetch(`/api/tournament/${tournament.id}/participant/${p.id}/`,
            {
                method: "DELETE", 'credentials': 'same-origin',
                headers:
                {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify(p)
            }).then(resp => {
                if (resp.ok) {
                    dispatch({ type: 'deleteParticipant', participant: p })
                }
            })
    }

    function isStarted() {
        return tournament.rounds[0].paired
    }

    function changeOrder(field) {
        const order = tournament?.order || 'rank'

        if (field == order) {
            dispatch({ type: 'sort', field: `-${field}` })
        }
        else {
            dispatch({ type: 'sort', field: field })
        }
    }

    function getHeading(name, field) {
        const order = tournament?.order || 'rank'
        if (order == field) {
            return (
                <th className=' text-center' onClick={e => changeOrder(field)} key={field}>
                    {name}<i className='bi-sort-down-alt ml-2'></i>
                </th>)
        }
        if (order == `-${field}`) {
            return (
                <th  className='text-center'  onClick={e => changeOrder(field)} key={field}>
                    {name}<i className='bi-sort-up-alt ml-2'></i>
                </th>)
        }
        return (
            <th  className=' text-center' onClick={e => changeOrder(field)} key={field}>
                {name}
            </th>)
    }

    return (
        <table className='table table-striped align-middle table-bordered table-dark'>
            <thead>
                <tr>
                    {columns.map(col => {
                        if (col.length == 2) {
                            return getHeading(col[0], col[1]);
                        }
                        return <th key={col[0]}>{col[0]}</th>
                    }
                    )}
                </tr>
            </thead>
            <tbody>
                {tournament?.participants?.map((row, idx) => (
                    <tr key={row.id}>
                        <td className="text-end">{row.pos}</td>
                        <td component="th" scope="row">
                            <Link to={`${row.id}`}>
                                { tournament.team_size ? row.name : `${row.name} (#${row.seed})` }
                            </Link>
                        </td>
                        <td className="text-end">{row.rating}</td>
                        { tournament.team_size ? 
                            <><td className="text-end">{row.round_wins}</td>
                                <td className="text-end">{row.game_wins}</td>
                            </>
                            : <td className="text-end">{row.game_wins}</td>
                        }
                        <td className="text-end">{row.spread}</td>
                        {auth &&
                            <td className="text-end">
                                <div className='d-inline-flex'>
                                    <div className='form-check form-switch'>
                                        <input className="form-check-input" type="checkbox"
                                            checked={row.offed != 0} onChange={e => toggleParticipant(e, idx)} />
                                    </div>
                                    {!isStarted() &&
                                        <div className='form-col'>
                                            <i className='bi-x-circle' onClick={e => deleteParticipant(e, idx)}></i>
                                        </div>
                                    }
                                </div>
                            </td>
                        }
                    </tr>
                ))}
            </tbody>
        </table>

    );
}

/**
 * Display information about a single participant.
 * @param {*} props 
 * @returns 
 */
export function Participant() {
    const params = useParams();
    const [participant, setParticipant] = useState()
    const tournament = useTournament()

    useEffect(() => {
        if (participant == null && tournament) {
            fetch(`/api/tournament/${tournament.id}/participant/${params.id}/`)
            .then(resp => resp.json())
            .then(json => {
                // when the participants record is retrieved it may not be in 
                // sorted order. When sorting , we can assume that the round id
                // will be in the same order as the round number. Thats because
                // when a tournament is created all it's rounds are created at
                // the same time and in order.
                json.results.sort( (a, b) => a.round_id - b.round_id)
                setParticipant(json)
            })
        }
    }, [tournament, participant])

    function editScore(e) {
        console.log('editscore')
    }

    if (participant) {
        return (
            <div>
                <h2><Link to={`/${tournament.slug}`}>{tournament.name}</Link></h2>
                <h3>{participant.name}</h3>
                {tournament?.entry_mode == 'P' 
                    ? <ResultList results={participant.results} teamId={participant.id} />  
                    : <ResultTable results={participant.results} editScore={editScore} />
                }

            </div>
        )
    }
    return <div></div>
}

console.log('Participant 0.02')