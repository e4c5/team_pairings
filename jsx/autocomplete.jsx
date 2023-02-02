import React, { useState, useEffect } from 'react';

/**
 * Autocomplete component based on 
 * https://github.com/krissnawat/simple-react-autocomplete/
 * 
 */
export function Autocomplete({suggestions, check, onChange, onSelect, value, placeHolder}) {
    const [state, setState] = useState({
				activeSuggestion: 0,
				filteredSuggestions: [],
				showSuggestions: false,
				styles: {}
		})
	

	function onTyped(e) {
		const userInput = e.currentTarget.value;
		let filteredSuggestions = [];
		
		if(userInput.length > 2) {
			filteredSuggestions = suggestions.filter(
					suggestion => check(suggestion, userInput.toLowerCase())
			);
            
			const rect = e.target.getBoundingClientRect();
            
			setState({
				activeSuggestion: 0,
				filteredSuggestions,
				showSuggestions: true,
				styles: { top: rect.top + rect.height + 10, left: e.left}
			});
		}
		
		onChange(e);
	};

	function onClick(e, player) {
		setState({
			activeSuggestion: 0,
			filteredSuggestions: [],
			showSuggestions: false,
		});
		onSelect(e, player)
	};
	
	function onKeyDown(e) {
		const { activeSuggestion, filteredSuggestions } = state;

		if (e.keyCode === 13) {
			setState({...state, 
				activeSuggestion: 0,
				showSuggestions: false,
			});
			onSelect(e, filteredSuggestions[activeSuggestion])
			
		} else if (e.keyCode === 38) { // UP
            console.log('UP?')
			if (activeSuggestion === 0) {
				return;
			}

			setState({ ...state, activeSuggestion: activeSuggestion - 1 });
		} else if (e.keyCode === 40) { // DOWN
            console.log('DOWN')
			if (activeSuggestion - 1 === filteredSuggestions.length) {
				return;
			}

			setState({ ...state, activeSuggestion: activeSuggestion + 1 });
		}
	};

    let suggestionsListComponent;
    
    if (state.showSuggestions) { 
        if (state.filteredSuggestions.length) {
            suggestionsListComponent = (
                <div>
                    <ul className="smart_autocomplete_container" style={state.styles}>
                        {state.filteredSuggestions.map((suggestion, index) => {
                            let className="text-nowrap" 
                            if (index === state.activeSuggestion) {
                                className = "text-nowrap smart_autocomplete_highlight";
                            }

                            return (
                                <ul className={className} key={suggestion} onClick={e => onClick(e, suggestion)}>
                                    {suggestion}
                                </ul>
                            );
                        })}
                    </ul>
                </div>
            );
        } else {
            suggestionsListComponent = null;
        }
    }
    
    return (
            <React.Fragment>
                <input 	type="text"	className='form-control'
                    placeholder={placeHolder}
                    onChange={onTyped}	onKeyDown={onKeyDown} value={value} />
                {suggestionsListComponent}
            </React.Fragment>
    );

}
