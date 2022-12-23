/**
 * @jest-environment jsdom
 */
import React from "react";
import { unmountComponentAtNode } from "react-dom";
import { act } from "react-dom/test-utils";
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom'

//import { render, screen } from '@testing-library/react';
import App from './app';

let container = null;
beforeEach(() => {
    // setup a DOM element as a render target
    container = document.createElement("div");
    document.body.appendChild(container);

});

afterEach(() => {
    // cleanup on exiting
    unmountComponentAtNode(container);
    container.remove();
    container = null;
});


it('Renders the list of tournaments', async () => {
    const tournaments = [
        {
            "id": 1,
            "is_editable": true,
            "start_date": "2022-10-29",
            "name": "SOY",
            "rated": 0,
            "slug": "stcu20",
            "team_size": 5
        },
        {
            "id": 2,
            "is_editable": true,
            "start_date": "2022-10-29",
            "name": "PPT",
            "rated": 0,
            "slug": "stcu15",
            "team_size": 5
        }
    ]

    global.fetch = jest.fn().mockImplementation(() =>
        Promise.resolve({
            json: () => Promise.resolve(tournaments)
        })
    );

    await act(async () => {
        render(<App />, container);
    })

    const linkElement = screen.getByText(/PPT/i);
    expect(linkElement).toBeInTheDocument();
});
