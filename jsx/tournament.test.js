/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { Tournaments, Tournament } from './tournament.jsx';
import { act } from "react-dom/test-utils";
import '@testing-library/jest-dom/extend-expect'
import { useTournament, useTournamentDispatch } from './context';

jest.mock('./context', () => ({
    useTournament: jest.fn(),
    useTournamentDispatch: jest.fn(),
}));


describe('Tournaments component', () => {
    it('renders tournament list', async () => {
        const tournamentsMock = [
            { id: 1, name: 'Tournament 1', slug: 'tournament-1' },
            { id: 2, name: 'Tournament 2', slug: 'tournament-2' },
        ];

        await act(() => render(
            <MemoryRouter>
                <Tournaments tournaments={tournamentsMock} />
            </MemoryRouter>
        )
        );

        // Assert that the tournament list is rendered
        expect(screen.getByText('Tournament 1')).toBeInTheDocument();
        expect(screen.getByText('Tournament 2')).toBeInTheDocument();
    });

    it('renders "New Tournament" link when authenticated', async () => {
        const tournamentsMock = [
            { id: 1, name: 'Tournament 1', slug: 'tournament-1' },
        ];

        // Mock the authentication check
        jest.spyOn(document, 'getElementById').mockReturnValue({ value: 'some-auth-token' });

        await act(() => render(
            <MemoryRouter>
                <Tournaments tournaments={tournamentsMock} />
            </MemoryRouter>
        )
        );

        // Assert that the "New Tournament" link is rendered
        expect(screen.getByText('New Tournament')).toBeInTheDocument();
    });

    it('does not render "New Tournament" link when not authenticated', async () => {
        const tournamentsMock = [
            { id: 1, name: 'Tournament 1', slug: 'tournament-1' },
        ];

        // Mock the authentication check
        jest.spyOn(document, 'getElementById').mockReturnValue(null);

        await act(() => render(
            <MemoryRouter>
                <Tournaments tournaments={tournamentsMock} />
            </MemoryRouter>
        )
        );

        // Assert that the "New Tournament" link is not rendered
        expect(screen.queryByText('New Tournament')).toBeNull();
    });
});

describe('Tournament component', () => {
    it('renders tournament details', async () => {
        const tournamentMock = {
            id: 1,
            name: 'Tournament 1',
            slug: 'tournament-1',
            participants: [],
        };

        const tournamentDispatchMock = jest.fn();

        useTournament.mockReturnValue(tournamentMock);
        useTournamentDispatch.mockReturnValue(tournamentDispatchMock);

        await act(() =>render(
                <MemoryRouter initialEntries={['/tournament-1']}>
                    <Tournament tournaments={[tournamentMock]} />
                </MemoryRouter>
            )
        );

        // Assert that the tournament name is rendered
        expect(screen.getByText('Tournament 1')).toBeInTheDocument();
    });

    it('adds participant with valid input', async () => {
        const tournamentMock = {
            id: 1,
            name: 'Tournament 1',
            slug: 'tournament-1',
            participants: [],
            private: true,
        };

        const tournamentDispatchMock = jest.fn();
        
        jest.spyOn(document, 'getElementById').mockReturnValue({ value: 'some-auth-token' });
        global.fetch = jest.fn().mockResolvedValue({
            json: jest.fn().mockResolvedValue({status: 'ok'}),
        });
        
        useTournament.mockReturnValue(tournamentMock);
        useTournamentDispatch.mockReturnValue(tournamentDispatchMock);

        await act(() =>render(
                <MemoryRouter initialEntries={['/tournament-1']}>
                    <Tournament tournaments={[tournamentMock]} />
                </MemoryRouter>
            )
        );

        // Enter participant details
        fireEvent.change(screen.getByTestId('name'), { target: { value: 'John Doe' } });
        fireEvent.change(screen.getByTestId('rating'), { target: { value: '1500' } });

        // Click the "Add" button
        fireEvent.click(screen.getByTestId('add'));

    });

    it('does not add participant with invalid input', async () => {
        const tournamentMock = {
            id: 1,
            name: 'Tournament 1',
            slug: 'tournament-1',
            participants: [],
            private: true,
        };
        // Mock the authentication check
        jest.spyOn(document, 'getElementById').mockReturnValue({ value: 'some-auth-token' });

        const tournamentDispatchMock = jest.fn();

        useTournament.mockReturnValue(tournamentMock);
        useTournamentDispatch.mockReturnValue(tournamentDispatchMock);

        await act(() => render(
                <MemoryRouter initialEntries={['/tournament-1']}>
                    <Tournament tournaments={[tournamentMock]} />
                </MemoryRouter>
            )
        );

        // Enter participant details with invalid rating
        fireEvent.change(screen.getByTestId('name'), { target: { value: 'John Doe' } });
        fireEvent.change(screen.getByTestId('rating'), { target: { value: 'abc' } });

        global.fetch = jest.fn().mockResolvedValue({
            json: jest.fn().mockResolvedValue({status: 'ok'}),
        });
        // Click the "Add" button
        fireEvent.click(screen.getByTestId('add'));

        // Assert that the add function is not called
        expect(tournamentDispatchMock).not.toHaveBeenCalled();
    });

    it('performs random fill with valid input', async () => {
        const tournamentMock = {
            id: 1,
            name: 'Tournament 1',
            slug: 'tournament-1',
            participants: [],
            private: true,
        };
        // Mock the authentication check
        jest.spyOn(document, 'getElementById').mockReturnValue({ value: 'some-auth-token' });
        const tournamentDispatchMock = jest.fn();

        useTournament.mockReturnValue(tournamentMock);
        useTournamentDispatch.mockReturnValue(tournamentDispatchMock);

        await act(() => render(
            <MemoryRouter initialEntries={['/tournament-1']}>
                <Tournament tournaments={[tournamentMock]} />
            </MemoryRouter>
        )
        );

        // Enter random fill number
        fireEvent.change(screen.getByTestId('fill-number'), { target: { value: '5' } });

        global.fetch = jest.fn().mockResolvedValue({
            json: jest.fn().mockResolvedValue({status: 'ok'}),
        });

        // Click the "Random Fill" button
        fireEvent.click(screen.getByTestId('fill'));
    });

    it('does not perform random fill with invalid input', async () => {
        const tournamentMock = {
            id: 1,
            name: 'Tournament 1',
            slug: 'tournament-1',
            participants: [],
            private: true,
        };
        // Mock the authentication check
        jest.spyOn(document, 'getElementById').mockReturnValue({ value: 'some-auth-token' });
        const tournamentDispatchMock = jest.fn();

        useTournament.mockReturnValue(tournamentMock);
        useTournamentDispatch.mockReturnValue(tournamentDispatchMock);

        await act(() => render(
            <MemoryRouter initialEntries={['/tournament-1']}>
                <Tournament tournaments={[tournamentMock]} />
            </MemoryRouter>
        )
        );

        // Enter invalid random fill number
        fireEvent.change(screen.getByTestId('fill-number'), { target: { value: 'abc' } });

        // Click the "Random Fill" button
        fireEvent.click(screen.getByTestId('fill'));

        // Assert that the filler function is not called
        expect(tournamentDispatchMock).not.toHaveBeenCalled();
    });
});
