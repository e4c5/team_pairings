import { tournamentReducer } from './context'
// Jest unit test

describe('Tournament Reducer', () => {
    it('should replace participants list', () => {
        const state = {}
        const action = {
            type: 'participants',
            participants : [
                {id: 1, name: 'John Doe', pos: 2},
                {id: 2, name: 'Jane Doe', pos: 1}
            ]
        }
        const result = tournamentReducer(state, action);
        expect(result.participants).toEqual([
            {id: 2, name: 'Jane Doe', pos: 1},
            {id: 1, name: 'John Doe', pos: 2}
        ])
    });
    
    it('should handle adding a participant', () => {
        // given
        const state = {
            participants: [
                {id: 1, name: 'John Doe'},
                {id: 2, name: 'Jane Doe'}
            ]
        };

        const action = {
            type: 'addParticipant',
            participant: {id: 3, name: 'John Smith'}
        };
        
        // when
        const result = tournamentReducer(state, action);

        // then
        expect(result.participants).toContainEqual(action.participant);
        expect(result.participants).toHaveLength(3);
    });

    it('should handle editing a participant', () => {
        // given
        const state = {
            participants: [
                {id: 1, name: 'John Doe'},
                {id: 2, name: 'Jane Doe'}
            ]
        };

        const action = {
            type: 'editParticipant',
            participant: {id: 2, name: 'Jane Smith'}
        };
        
        // when
        const result = tournamentReducer(state, action);

        // then
        expect(result.participants).toContainEqual(action.participant);
        expect(result.participants).toHaveLength(2);
    });

    it('should handle deleting a participant', () => {
        // given
        const state = {
            participants: [
                {id: 1, name: 'John Doe'},
                {id: 2, name: 'Jane Doe'}
            ]
        };

        const action = {
            type: 'deleteParticipant',
            participant: {id: 2, name: 'Jane Doe'}
        };
        
        // when
        const result = tournamentReducer(state, action);

        // then
        expect(result.participants).not.toContainEqual(action.participant);
        expect(result.participants).toHaveLength(1);
    });

    it('should handle updating results', () => {
        let state = {
            num_rounds: 3,
            participants: [
                {id: 1, name: 'John Doe'},
                {id: 2, name: 'Jane Doe'},
                {id: 3, name: 'John Smith'},
                {id: 4, name: 'Jane Smith'}
            ]
        };

        const action = {
            type: 'updateResult',
            round: 0,
            result: [
                {p1: 1, p2: 2, score: 3}
            ]
        };
        
        // when
        state = tournamentReducer(state, action);

        // then
        expect(state.results).not.toBeUndefined();
        expect(state.results).toHaveLength(3);
        expect(state.results[0]).toContainEqual(action.result[0]);
        expect(state.participants).toHaveLength(4);

        action.result = [
            {p1: 1, p2: 2, score: 3},
            {p1: 3, p2: 4, score: 100}
        ]
        
        state = tournamentReducer(state, action);
        expect(state.results[0]).toContain(action.result[0])
        expect(state.results[0]).toContain(action.result[1])
    });

    it('should handle adding rounds', () => {
        // given
        const state = {
            rounds: [ 
                {id: 1, name: 'Round 1'},
                {id: 2, name: 'Round 2'}
            ]
        };

        const action = {
            type: 'updateRounds',
            rounds: [{id: 3, name: 'Round 3'}]
        };
        
        // when
        const result = tournamentReducer(state, action);

        // then
        
        expect(result.rounds).toHaveLength(1);
    });

    it('should handle editing a round', () => {
        // given
        const state = {
            rounds: [ 
                {id: 1, name: 'Round 1'},
                {id: 2, name: 'Round 2'}
            ]
        };

        const action = {
            type: 'editRound',
            round: {id: 2, name: 'Round 3'}
        };
        
        // when
        const result = tournamentReducer(state, action);

        // then
        expect(result.rounds).toContainEqual(action.round);
        expect(result.rounds).toHaveLength(2);
    });

    it('should handle sorting', () => {
        // given
        const state = {
            participants: [
                {id: 1, name: 'John Doe'},
                {id: 2, name: 'Jane Doe'}
            ]
        };

        const action = {
            type: 'sort',
            field: 'name'
        };
        
        // when
        const result = tournamentReducer(state, action);

        // then
        expect(result.order).toEqual('name');
        expect(result.participants[0].name).toBe('Jane Doe');
        expect(result.participants[1].name).toBe('John Doe');
    });

    it('should handle reset/replace', () => {
        // given
        const state = {
            participants: [
                {id: 1, name: 'John Doe'},
                {id: 2, name: 'Jane Doe'}
            ]
        };

        const action = {
            type: 'reset',
            value: {
                participants: [
                    {id: 3, name: 'Bob Smith'}
                ]
            }
        };
        
        // when
        const result = tournamentReducer(state, action);

        // then
        expect(result.participants).toEqual(action.value.participants);
    });
});