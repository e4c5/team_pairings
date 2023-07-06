import { reducer } from './round.jsx';

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
