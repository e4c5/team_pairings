/**
 * @jest-environment jsdom
 */

import { act } from "react-dom/test-utils";
import '@testing-library/jest-dom/extend-expect'
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { MemoryRouter, Routes, Route } from 'react-router-dom';
import React from 'react';

import { reducer, Rounds, Round } from './round.jsx';
import { useTournament, useTournamentDispatch } from './context';


jest.mock('./context', () => ({
    useTournament: jest.fn(),
    useTournamentDispatch: jest.fn(),
}));


describe('reducer', () => {
    const initialState = {
        name: '',
        p1: '',
        p2: '',
        resultId: '',
        boards: [],
        board: '',
        won: '',
        lost: '',
        pending: '',
        score1: '',
        score2: '',
    };

    it('handles "typed" action correctly', () => {
        const action = {
            type: 'typed',
            name: 'John',
        };

        const state = reducer(initialState, action);

        expect(state).toEqual({
            ...initialState,
            name: 'John',
        });
    });

    it('handles "autoComplete" action correctly', () => {
        const action = {
            type: 'autoComplete',
            p1: 'Player 1',
            p2: 'Player 2',
            resultId: '123',
            name: 'Result Name',
            boards: [],
        };

        const state = reducer(initialState, action);

        expect(state).toEqual({
            ...initialState,
            p1: 'Player 1',
            p2: 'Player 2',
            resultId: '123',
            name: 'Result Name',
            boards: [],
        });
    });

    // Add more test cases for other actions...

    it('throws an error for unrecognized action type', () => {
        const action = {
            type: 'unknown',
        };

        expect(() => reducer(initialState, action)).toThrowError(
            'unrecognized action unknown in reducer'
        );
    });
});


describe('Rounds component', () => {
    it('renders Rounds for entry_mode P', async () => {
        useTournament.mockReturnValue({
            entry_mode: 'P',
            slug: 'test-tournament',
            rounds: [
                { round_no: 1 },
                { round_no: 2 },
                { round_no: 3 },
            ],
        });

        render(<MemoryRouter><Rounds /></MemoryRouter>) //);

        expect(screen.getByText('Rounds:')).toBeInTheDocument();
        expect(screen.getByText('1')).toBeInTheDocument();
        expect(screen.getByText('2')).toBeInTheDocument();
        expect(screen.getByText('3')).toBeInTheDocument();
        expect(screen.getByText('Boards')).toBeInTheDocument();
    });

    it('renders Rounds for entry_mode other than P', async () => {
        useTournament.mockReturnValue({
            entry_mode: 'T',
            slug: 'test-tournament',
            rounds: [
                { round_no: 1 },
                { round_no: 2 },
            ],
        });

        render(<MemoryRouter><Rounds /></MemoryRouter>);

        expect(screen.getByText('Rounds:')).toBeInTheDocument();
        expect(screen.getByText('1')).toBeInTheDocument();
        expect(screen.getByText('2')).toBeInTheDocument();
        expect(screen.queryByText('Boards')).toBeNull();
    });
});


describe('Round', () => {
    beforeEach(() => {
        useTournamentDispatch.mockReturnValue(jest.fn())

    });

    it('Expect unpaired text, pair button will not appear because no auth', async () => {
        useTournament.mockImplementation( () => ({
            participants: [{ name: 'Player 1', id: 1}, { name: 'Player 2', id: 2 }],
            rounds: [{ id: 1, paired: false, round_no : 1 }],
        }));

        await act(() => render(
            <MemoryRouter initialEntries={['/round/1']}>
                <Routes>
                    <Route path="/round/:id" element={<Round />} />
                </Routes>
                
            </MemoryRouter>)
        );
        expect(screen.queryByTestId('pair')).toBeNull()
        expect(screen.getByText('This is a round that has not yet been paired')).toBeInTheDocument();
        expect(screen.getByText('Player 1')).toBeInTheDocument();
    });

    it('A paired round is rendered correct', async () => {
        useTournament.mockImplementation(() => ({
            participants: [{ name: 'Player 1' }, { name: 'Player 2' }],
            rounds: [{ id: 1, paired: true, round_no : 1 }],
        }));
        global.fetch = jest.fn().mockResolvedValue({
            json: jest.fn().mockResolvedValue([]),
        });

        // This approach is easier than mocking useParams
        await act(() => render(
            <MemoryRouter initialEntries={['/round/1']}>
                <Routes>
                    <Route path="/round/:id" element={<Round />} />
                </Routes>
                
            </MemoryRouter>)
        );
        expect(screen.queryByTestId('unpair')).toBeNull()
        expect(screen.queryByText('This is a round that has not yet been paired')).toBeNull();
        expect(screen.queryByText('Player 1')).not.toBeInTheDocument();
    });

    it('Unpair and scoring componet should be rendered for a logged in user', async () => {
        useTournament.mockImplementation(() => ({
            participants: [{ name: 'Player 1' }, { name: 'Player 2' }],
            rounds: [{ id: 1, paired: true, round_no : 1 }],
        }));
        global.fetch = jest.fn().mockResolvedValue({
            json: jest.fn().mockResolvedValue([]),
        });
        jest.spyOn(document, 'getElementById').mockReturnValue({ value: 'some-auth-token' });
        // This approach is easier than mocking useParams
        await act(() => render(
            <MemoryRouter initialEntries={['/round/1']}>
                <Routes>
                    <Route path="/round/:id" element={<Round />} />
                </Routes>
                
            </MemoryRouter>)
        );
        expect(screen.queryByTestId('unpair')).toBeInTheDocument()
        expect(screen.queryByTestId('truncate')).toBeInTheDocument()
        expect(screen.queryByTestId('tsh-style-entry')).toBeInTheDocument()
        expect(screen.queryByText('This is a round that has not yet been paired')).toBeNull();
        expect(screen.queryByText('Player 1')).not.toBeInTheDocument();
    });
});
