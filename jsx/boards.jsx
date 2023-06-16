import React, { useState, useEffect } from 'react';
import { useTournament } from './context.jsx';
import { Link } from "react-router-dom";

export function Boards() {
    const tournament = useTournament();
    const [boards, setBoards] = useState()
    

    useEffect(() => {
        if (boards == null && tournament) {
            fetch(`/api/tournament/${tournament.id}/boards/`)
            .then(resp => resp.json())
            .then(json => {
                setBoards(json)
            })
        }
    }, [tournament, boards])

    function boardResults(results) {
        if(results?.length) {
            const b = results[0].board
            return (
                <table key={b} className='table table-striped mb-4'>
                    <thead>
                        <tr><td colSpan="3" className='fs-3'>Board {b}</td></tr>
                        <tr><td>Team</td><td>Wins</td><td>Margin</td></tr>
                    </thead>
                    <tbody>
                        { results.map(row =>(
                            <tr key={row.team_id}>
                                <td className=''>{ row.name}</td>
                                <td className='text-end'>{ row.games_won}</td>
                                <td className='text-end'>{ row.margin}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )
        }
    }

    const results = []
    for(let i = 0 ; i < tournament?.team_size ; i++) {
        results.push(boardResults(boards?.filter(row => row.board == i + 1)))
    }
    return (<>
        <h2><Link to={`/${tournament?.slug}`}>{tournament?.name}</Link></h2>
        <h3>Board by board results</h3>
        <>
            { results }
        </>
    </>)
}