/**
 * @jest-environment jsdom
 */
import '@testing-library/jest-dom/extend-expect'; 
import { act } from "react-dom/test-utils";
import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { Confirm } from './dialog.js';

describe('Confirm component', () => {
  it('renders correctly and handles user interactions', async () => {
    const mockSetModal = jest.fn();
    const mockOnCodeChange = jest.fn();
    const mockConfirmDelete = jest.fn();

    const { getByTestId, getByPlaceholderText, getByText } = await act(() =>  render(
        <Confirm
            display={true}
            setModal={mockSetModal}
            code="test123"
            onCodeChange={mockOnCodeChange}
            confirmDelete={mockConfirmDelete}
        />
        )
    );

    // Check if the modal is displayed
    const modal = getByTestId('exampleModal');
    expect(modal).toHaveStyle('display: block');

    // Check if the modal title and body are rendered correctly
    expect(getByText('Confirm delete')).toBeInTheDocument();
    expect(getByText('You are about to delete all results in a round, this cannot be undone. Please type your username in the box below and hit confirm if you want to proceed.')).toBeInTheDocument();

    // Type a username in the input field and check if the onCodeChange handler is called
    const inputElement = getByPlaceholderText('Type your username here');
    fireEvent.change(inputElement, { target: { value: 'newusername' } });
    expect(mockOnCodeChange).toHaveBeenCalledWith(expect.any(Object));

    // Click on the Confirm button and check if the confirmDelete handler is called
    const confirmButton = getByText('Confirm');
    fireEvent.click(confirmButton);
    expect(mockConfirmDelete).toHaveBeenCalledTimes(1);

    // Click on the Cancel button and check if the setModal handler is called
    const cancelButton = getByText('Cancel');
    fireEvent.click(cancelButton);
    expect(mockSetModal).toHaveBeenCalledTimes(1);
    expect(mockSetModal).toHaveBeenCalledWith(false);
  });

  it('hides the modal when display prop is false', async () => {
    const { getByTestId } = render(
      <Confirm
        display={false}
        setModal={() => {}}
        code=""
        onCodeChange={() => {}}
        confirmDelete={() => {}}
      />
    );

    // Check if the modal is hidden
    const modal = getByTestId('exampleModal');
    expect(modal).toHaveStyle('display: none');
  });
});