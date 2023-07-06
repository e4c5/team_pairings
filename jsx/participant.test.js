/**
 * @jest-environment jsdom
 */

import { act } from "react-dom/test-utils";
import { MemoryRouter } from 'react-router-dom';
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { Participant } from './participant.jsx';
import { useTournament } from './context';
import { ResultTable, TeamResultTable } from './result.jsx';
import '@testing-library/jest-dom/extend-expect'
import { TournamentEditor } from './editor.jsx';

// mock fetch to return a static list of participants

jest.mock('./context', () => ({
    useTournament: jest.fn(),
}));

describe('Participant component', () => {
    it('should render participant', async () => {
        const tournamentMock = {
            id: 123,
            slug: 'tournament-slug',
            name: 'Tri Wizard',
            team_size: 3,
          };

        const participant = {
            "id": 1800,
            "name": "Jessica Richardson",
            "played": 0,
            "game_wins": 0,
            "round_wins": 0,
            "spread": 0,
            "offed": 0,
            "rating": 1335,
            "tournament_id": 41,
            "seed": 7,
            "white": 0,
            "members": null,
            "results": [
                {
                    "id": 5295,
                    "p1_id": 1797,
                    "p2_id": 1800,
                    "table": 3,
                    "boards": null,
                    "score1": null,
                    "score2": null,
                    "round_id": 339,
                    "games_won": null,
                    "starting_id": 1800
                }
            ]
        }
        tournamentMock.participants = [participant];
        useTournament.mockReturnValue(tournamentMock);
        global.fetch = jest.fn().mockResolvedValue({
            json: jest.fn().mockResolvedValue(participant),
        });

        await act(async () => {
            render(<MemoryRouter><Participant /></MemoryRouter>);
        });

    })
})
