import React, { useState, useEffect } from 'react';

/**
 * Autocomplete component based on 
 * https://github.com/krissnawat/simple-react-autocomplete/
 * 
 */
export function Autocomplete({suggestions, check, onChange, onSelect, value}) {
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
				styles: { top: e.top + e.height + 10, left: e.left}
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
			setState({
				activeSuggestion: 0,
				showSuggestions: false,
			});
			onSelect(filteredSuggestions[activeSuggestion])
			
		} else if (e.keyCode === 38) {
			if (activeSuggestion === 0) {
				return;
			}

			setState({ activeSuggestion: activeSuggestion - 1 });
		} else if (e.keyCode === 40) {
			if (activeSuggestion - 1 === filteredSuggestions.length) {
				return;
			}

			setState({ activeSuggestion: activeSuggestion + 1 });
		}
	};

    let suggestionsListComponent;
    
    if (state.showSuggestions) { 
        if (state.filteredSuggestions.length) {
            suggestionsListComponent = (
                <div className="suggestions row" style={state.styles}>
                    {state.filteredSuggestions.map((suggestion, index) => {
                        let className;
                        if (index === state.activeSuggestion) {
                            className = "suggestion-active";
                        }

                        return (
                            <div className={className} key={suggestion} onClick={e => onClick(e, suggestion)}>
                                 {suggestion}
                            </div>
                        );
                    })}
                </div>
            );
        } else {
            suggestionsListComponent = null;
        }
    }

    return (
            <React.Fragment>
                <input 	type="text"	className='form-control'
                    onChange={onTyped}	onKeyDown={onKeyDown} value={value} />
                {suggestionsListComponent}
            </React.Fragment>
    );

}
