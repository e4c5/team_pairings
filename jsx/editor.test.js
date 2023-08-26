/**
 * @jest-environment jsdom
 */

import { act } from "react-dom/test-utils";
import '@testing-library/jest-dom/extend-expect'; 
import { MemoryRouter } from 'react-router-dom';
import React from 'react';
import { render, screen, fireEvent, waitFor , waitForElementToBeRemoved} from '@testing-library/react';
import { TournamentEditor } from './editor.jsx';

// Mock the fetch function since we're not testing API calls in this unit test
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ slug: 'tournament-slug' }),
  })
);

// Mock the getCookie function since it's not defined in the test environment
// You can replace this with an actual implementation if needed
const getCookie = jest.fn(() => 'mock-csrf-token');

describe('TournamentEditor component', () => {
  it('renders correctly and handles user interactions', async () => {
    await act(() => render(<MemoryRouter><TournamentEditor /></MemoryRouter>))

    // Check if the "New Tournament" card header is rendered correctly
    const cardHeader = screen.getByText('New Tournament');
    expect(cardHeader).toBeInTheDocument();

    // Check if the "Create" button is rendered correctly and if it's disabled when required fields are empty
    const createButton = screen.getByText('Create');
    expect(createButton).toBeInTheDocument();
    expect(createButton).toBeDisabled();
    
  });
  it('handles user interactions', async () => {
    const {debug} = await act(() => render(<TournamentEditor />))
    // Check if the "Name" input field is rendered correctly
    const nameInput = screen.getByTestId('name')
    fireEvent.change(nameInput, { target: { value: 'Tournament Name' } });
    expect(nameInput.value).toBe('Tournament Name');

    // Check if the "Start Date" input field is rendered correctly and set the value using useRef
    const startDateInput = screen.getByTestId('date')
    fireEvent.change(startDateInput, { target: { value: '2023-07-05' } });
    expect(startDateInput.value).toBe('2023-07-05');

    // Check if the "Number of Rounds" input field is rendered correctly
    const numRoundsInput = screen.getByTestId('rounds')
    fireEvent.change(numRoundsInput, { target: { value: '3' } });
    expect(numRoundsInput.value).toBe('3');

    // Check if the "Tournament Type" select field is rendered correctly
    const tournamentTypeSelect = screen.getByTestId('type')
    fireEvent.change(tournamentTypeSelect, { target: { value: 'T' } });
    expect(tournamentTypeSelect.value).toBe('T');

    // Check if the "Team size" input field is rendered correctly for the selected tournament type
    const teamSizeInput = screen.getByTestId('team-size')
    fireEvent.change(teamSizeInput, { target: { value: '4' } });
    expect(teamSizeInput.value).toBe('4');


    // Enable the button by filling in the required fields
    fireEvent.change(nameInput, { target: { value: 'Tournament Name' } });
    fireEvent.change(numRoundsInput, { target: { value: '3' } });
    fireEvent.change(startDateInput, { target: { value: '2023-07-05' } });
    fireEvent.change(teamSizeInput, { target: { value: '4' } });

    const createButton = screen.getByText('Create');
    expect(createButton).not.toBeDisabled();

    // Mock window.location.href and window.location.assign
    const originalLocation = window.location;
    delete window.location;
    window.location = { href: '', assign: jest.fn() };

    
    // Click on the "Create" button and check if the saveTournament function is called
    fireEvent.click(createButton);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith('/api/tournament/', expect.any(Object));

    // Check if the "saveTournament" function updates the start_date property in the state correctly
    // This will test that the useRef is correctly used in saveTournament function
    const startDate = '2023-07-06';
    fireEvent.change(startDateInput, { target: { value: startDate } });
    fireEvent.click(createButton);

    // the fecth want work without auth so testing stops here.
    expect(fetch).toHaveBeenCalledWith('/api/tournament/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': undefined
      },
      body: JSON.stringify({
        name: 'Tournament Name',
        start_date: startDate, // Check if the start_date is updated correctly
        num_rounds: '3',
        round_robin: false,
        entry_mode: 'T',
        private: true,
        team_size: '4',
        
      }),
    });
  });
});

describe('TournamentEditor component', () => {
    it('renders correctly and checks conditional rendering', async () => {
        const { getByTestId, getByRole } = await act(() => render(<MemoryRouter><TournamentEditor /></MemoryRouter>))

        // Check initial rendering (Round Robin should be selected)
        expect(getByTestId('non-rr')).toBeChecked();
        expect(getByTestId('rounds')).toBeVisible();

        // Click on non round robin and check if Number of Rounds input is visible
        fireEvent.click(getByTestId('rr'));
        await waitFor(() => expect(screen.getByTestId('rr')).toBeChecked());
        expect(getByTestId('non-rr')).not.toBeChecked();
        expect(screen.queryByTestId('rounds')).not.toBeInTheDocument();


    });
});