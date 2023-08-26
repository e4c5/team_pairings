/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { Autocomplete } from './autocomplete.jsx';
import { act } from "react-dom/test-utils";
import '@testing-library/jest-dom/extend-expect'; 

// Sample suggestions data for testing
const suggestions = ['apple', 'banana', 'cherry', 
            'grape 1', 'grape 2', 'grape 3', 'orange'];

// Mock the onSelect function for testing
const mockOnSelect = jest.fn();

describe('Autocomplete renders correctly and handles user input',  () => {
    it('Reacts to user input', async () => {
        const { getByPlaceholderText, queryByText, getByText, debug } = await act(() => 
            render(
                <Autocomplete
                    suggestions={suggestions}
                    check={(suggestion, userInput) => suggestion.includes(userInput)}
                    onChange={() => {}}
                    onSelect={mockOnSelect}
                    value=""
                    placeHolder="Type here..."
                />
            )
        );
        const inputElement = getByPlaceholderText('Type here...');

        // Type user input and check if suggestions are displayed correctly
        fireEvent.change(inputElement, { target: { value: 'app' } });

        // Verify that suggestions are displayed
        expect(queryByText('apple')).toBeInTheDocument();
        expect(queryByText('banana')).toBeNull();

        // Click on a suggestion
        fireEvent.click(getByText('apple'));

        // Check if onSelect is called with the correct suggestion
        expect(mockOnSelect).toHaveBeenCalledWith(expect.any(Object), 'apple');

        // Clear the suggestions after selecting
        expect(queryByText('apple')).not.toBeInTheDocument();
        expect(queryByText('banana')).not.toBeInTheDocument();

        // Type another user input and check if suggestions are displayed correctly
        fireEvent.change(inputElement, { target: { value: 'gra' } });

        // Verify that suggestions are displayed
        await waitFor(() => {
            expect(queryByText('grape 1')).toBeInTheDocument()
        });

        // Use arrow keys to navigate through suggestions
        fireEvent.keyDown(inputElement, { keyCode: 40 }); // Press DOWN
        fireEvent.keyDown(inputElement, { keyCode: 40 }); // Press DOWN again

        // Verify that the active suggestion is highlighted
        await waitFor(() => {
            expect(getByText('grape 3')).toHaveClass('smart_autocomplete_highlight')
        });

        // press cursor up
        fireEvent.keyDown(inputElement, { keyCode: 38 });
        expect(getByText('grape 2')).toHaveClass('smart_autocomplete_highlight');

        // Press ENTER to select the suggestion
        fireEvent.keyDown(inputElement, { keyCode: 13 });

        // Check if onSelect is called with the correct suggestion
        expect(mockOnSelect).toHaveBeenCalledWith(expect.any(Object), 'grape 2');
    })
});