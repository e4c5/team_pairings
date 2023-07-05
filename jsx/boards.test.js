/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Boards } from './boards.jsx';
import { act } from "react-dom/test-utils";
import { useTournament } from './context';
import '@testing-library/jest-dom/extend-expect'; 

// Mock the useTournament hook
jest.mock('./context', () => ({
  useTournament: jest.fn(),
}));

describe('Boards component', () => {
  // Mock the data returned by useTournament hook
  const tournamentMock = {
    id: 123,
    slug: 'tournament-slug',
    name: 'Tri Wizard',
    team_size: 3,
  };

  // Mock the data returned by the API fetch
  const apiResponseMock = [
    {
        "board": 1,
        "team_id": 1741,
        "name": "Hogwarts",
        "games_won": 4,
        "margin": 1135
    },
    {
        "board": 2,
        "team_id": 1744,
        "name": "Beauxbatons",
        "games_won": 4,
        "margin": 833
    },
    {
        "board": 3,
        "team_id": 1740,
        "name": "Durmstrang",
        "games_won": 4,
        "margin": 502
    }];

  it('renders the component with board results', async () => {
    // Mock the useTournament hook to return the tournament data
    useTournament.mockReturnValue(tournamentMock);

    // Mock the fetch API to return the sample data
    global.fetch = jest.fn().mockResolvedValue({
      json: jest.fn().mockResolvedValue(apiResponseMock),
    });

    const { getByText, container, debug } = await act(() => render(
        <MemoryRouter>
            <Boards />
        </MemoryRouter>
        )
    );
    await waitFor(() => expect(global.fetch).toHaveBeenCalledTimes(1));

    // Check if the tournament name is rendered
    expect(container.innerHTML).toContain('Tri Wizard')
    
    // Check if the board results are rendered
    for (let i = 0; i < tournamentMock.team_size; i++) {
      const board = i + 1;
      const boardHeader = getByText(`Board ${board}`);
      expect(boardHeader).toBeInTheDocument();

      const teamA = getByText('Hogwarts');

      // Check if the table with team information is rendered
      expect(boardHeader.closest('table')).toBeInTheDocument();
      expect(teamA.closest('table')).toBeInTheDocument();
    }
  });

  it('renders the component without board results', async () => {
    // Mock the useTournament hook to return the tournament data
    useTournament.mockReturnValue(tournamentMock);

    // Mock the fetch API to return null (no board results)
    global.fetch = jest.fn().mockResolvedValue({
      json: jest.fn().mockResolvedValue(null),
    });

    const { container, queryByText } = await act(() =>render(
        <MemoryRouter>
            <Boards />
        </MemoryRouter>
        )
    );

    // Wait for the data to be loaded (useEffect)
    await waitFor(() => expect(global.fetch).toHaveBeenCalledTimes(2));

    // Check if the tournament name is rendered
    expect(container.innerHTML).toContain('Tri Wizard')

    // Check if the board results are not rendered
    for (let i = 0; i < tournamentMock.team_size; i++) {
      const board = i + 1;
      const boardHeader = queryByText(`Board ${board}`);
      expect(boardHeader).toBeNull();
    }
  });
});
