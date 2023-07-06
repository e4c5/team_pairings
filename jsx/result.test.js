/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { Result, TeamResult } from './result.jsx';
import { useTournament } from './context.jsx';
import { act } from "react-dom/test-utils";
import '@testing-library/jest-dom/extend-expect'

// Mock the useTournament hook
jest.mock('./context.jsx', () => ({
    useTournament: jest.fn(),
}));

// Define the tournament mock data
const tournamentMock = {
    id: 1,
    team_size: 2, // Set the required properties for your test
    entry_mode: 'T',
    participants: [
        { id: 1, name: 'Participant 1', seed: 1 },
        { id: 2, name: 'Participant 2', seed: 2 },
    ],
};

// Define the props for the Result component
const resultProps = {
    r: {
        table: 1,
        p1_id: 1,
        p2_id: 2,
        p1: { id: 1, name: 'Participant 1', seed: 1 },
        p2: { id: 2, name: 'Participant 2', seed: 2 },
        games_won: 1,
        score1: 2,
        score2: 1,
        starting_id: 1,
    },
    index: 0,
    editScore: jest.fn(),
};

describe("Tests the results component", () => {
    it('renders singles result correctly', async () => {
        // Mock the useTournament hook to return the tournament mock data
        useTournament.mockReturnValue(tournamentMock);
        const { getByText, queryByRole } = await act(async () =>
            render(<table><tbody><Result {...resultProps} /></tbody></table>)
        )

        // Assertions for the rendered singles result
        expect(getByText(/Participant 1/)).toBeInTheDocument(); // Check for the first participant name and seed
        expect(getByText(/Participant 2/)).toBeInTheDocument(); // Check for the first participant name and seed

        expect(queryByRole('button')).toBeNull(); // Check for the edit button (should be missing)
    });

    it('renders team result correctly', async () => {
        // Update the resultProps to match the team result scenario
        resultProps.r.p1 = { name: 'Team 1' };
        resultProps.r.p2 = { name: 'Team 2' };

        // Mock the useTournament hook to return the tournament mock data
        useTournament.mockReturnValue(tournamentMock);

        const { getByText, queryByRole } = await act(async () =>
            render(<table><tbody><Result {...resultProps} /></tbody></table>)
        )

        // Assertions for the rendered team result
        expect(getByText(/Team 1/)).toBeInTheDocument(); // Check for the first team name and seed
        expect(getByText(/Team 2/)).toBeInTheDocument(); // Check for the first team name and seed
        expect(queryByRole('button')).toBeNull(); // Check for the edit button (should be missing)

    });
})


describe('TeamResult component', () => {
    const teamId = 123;
    const r = {
        table: '1',
        p1: { name: 'Ravenclaw', seed: 1 },
        p1_id: 1,
        starting_id: 1,
        games_won: 2,
        score1: 4,
        p2: { name: 'Slitheryn', seed: 2 },
        p2_id: 2,
        score2: 2,
        boards: [
            { board: 1, score1: 2, score2: 1, team1_id: 1 },
            { board: 2, score1: 1, score2: 2, team1_id: 2 },
        ],
    };

    beforeEach(() => {
        useTournament.mockReturnValue({...tournamentMock, entry_mode: 'P'});
    });

    it('renders the board result correctly', async () => {
        const { getByText, getAllByText } = await act(() => render(
            <table>
                <tbody>
                    <TeamResult r={r} index={0} teamId={teamId} />
                </tbody>
            </table>
        )
        );

        expect(getByText(/Ravenclaw/)).toBeInTheDocument();
        expect(getByText(/Slitheryn/)).toBeInTheDocument();
        expect(getByText(/Player 1 Score/)).toBeInTheDocument();
        expect(getByText(/Player 2 Score/)).toBeInTheDocument();
        expect(getByText(/Margin/)).toBeInTheDocument();
    });
    
});
