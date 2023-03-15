//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import React, { useState, useEffect } from 'react';
import {
    useParams,
    Link,
} from "react-router-dom";
import { ResultList } from './result.jsx';
import { useTournament, useTournamentDispatch } from './context.jsx';
import getCookie from './cookie.js';

export function Participants(props) {
    const tournament = useTournament();
    const dispatch = useTournamentDispatch();

    const auth = document.getElementById('hh') && document.getElementById('hh').value
    const columns = [
        ["Rank", "pos"],
        ["Name", "name"],
        ["Rating", "rating"],
        ["Round Wins", "round_wins"],
        ["Game Wins", "game_wins"],
        ["Spread", "spread"],
    ]

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
                <th onClick={e => changeOrder(field)} key={field}>
                    {name}<i className='bi-sort-down-alt ml-2'></i>
                </th>)
        }
        if (order == `-${field}`) {
            return (
                <th onClick={e => changeOrder(field)} key={field}>
                    {name}<i className='bi-sort-up-alt ml-2'></i>
                </th>)
        }
        return (
            <th onClick={e => changeOrder(field)} key={field}>
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
                    <tr
                        key={row.id}
                        sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                    >
                        <td className="text-left">{row.pos}</td>
                        <td component="th" scope="row">
                            <Link to={`${row.id}`}>{row.name}</Link>
                        </td>
                        <td className="text-right">{row.rating}</td>
                        <td className="text-right">{row.round_wins}</td>
                        <td className="text-right">{row.game_wins}</td>
                        <td className="text-right">{row.spread}</td>
                        {auth &&
                            <td className="text-right">
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

export function Participant(props) {
    const params = useParams();
    const [participant, setParticipant] = useState()
    const tournament = useTournament()

    useEffect(() => {
        if (participant == null && tournament) {
            fetch(`/api/tournament/${tournament.id}/participant/${params.id}/`).then(resp => resp.json()).then(json => {
                setParticipant(json)
            })
        }
    }, [tournament, participant])

    function editScore(e) {

    }

    if (participant) {
        return (
            <div>
                <h2><Link to={`/${tournament.slug}`}>{tournament.name}</Link></h2>
                <h3>{participant.name}</h3>
                <table className='table'>
                    <thead>
                        <tr>
                            <th>Board</th>
                            <th>Player</th>
                            <th>Wins</th>
                            <th>Margin</th>
                        </tr>
                    </thead>
                    <tbody>
                        {participant?.members?.map(p => (
                            <tr key={p.id}>
                                <td>{p.board}</td>
                                <td>{p.name}</td>
                                <td>{p.wins}</td>
                                <td>{p.spread}</td>
                            </tr>
                        )
                        )}
                    </tbody>
                </table>

                <ResultList results={participant.results} editScore={editScore} />

            </div>
        )
    }
    return <div></div>
}

console.log('Participant 0.01')