import React, { useState, useEffect } from 'react';

/**
 * Autocomplete component based on 
 * https://github.com/krissnawat/simple-react-autocomplete/
 * 
 */
export class Autocomplete extends React.Component {
	static defaultProperty = {
		suggestions: []
	};
	constructor(props) {
		super(props);
		this.state = {
				activeSuggestion: 0,
				filteredSuggestions: [],
				showSuggestions: false,
				styles: {}
		};
	}

	onChange = e => {
		const { suggestions } = this.props;
		const userInput = e.currentTarget.value;
		let filteredSuggestions = [];
		
		if(userInput.length > 2) {
			filteredSuggestions = suggestions.filter(
					suggestion =>
                    this.props.check(suggestion, userInput.toLowerCase())
			);
            console.log(filteredSuggestions)
			const rect = e.target.getBoundingClientRect();
			this.setState({
				activeSuggestion: 0,
				filteredSuggestions,
				showSuggestions: true,
				styles: { top: e.top + e.height + 10, left: e.left}
			});
		}
		
		this.props.onChange(e);
	};

	onClick(e, player) {
		this.setState({
			activeSuggestion: 0,
			filteredSuggestions: [],
			showSuggestions: false,
		});
		this.props.onSelect(player)
	};
	
	onKeyDown = e => {
		const { activeSuggestion, filteredSuggestions } = this.state;

		if (e.keyCode === 13) {
			this.setState({
				activeSuggestion: 0,
				showSuggestions: false,
			});
			this.props.onSelect(filteredSuggestions[activeSuggestion])
			
		} else if (e.keyCode === 38) {
			if (activeSuggestion === 0) {
				return;
			}

			this.setState({ activeSuggestion: activeSuggestion - 1 });
		} else if (e.keyCode === 40) {
			if (activeSuggestion - 1 === filteredSuggestions.length) {
				return;
			}

			this.setState({ activeSuggestion: activeSuggestion + 1 });
		}
	};

	render() {
		const {
			onChange,
			onClick,
			onKeyDown,
			state: {
				activeSuggestion,
				filteredSuggestions,
				showSuggestions
			}
		} = this;
		
		let suggestionsListComponent;
		let userInput = this.props.userInput
		
		if (showSuggestions) { 
			if (filteredSuggestions.length) {
				suggestionsListComponent = (
						<table className="suggestions table" style={this.state.styles}>
						  <thead><tr><th>Symbol</th></tr></thead>
						  <tbody>
							{filteredSuggestions.map((suggestion, index) => {
								let className;
								if (index === activeSuggestion) {
									className = "suggestion-active";
								}
	
								return (
										<tr className={className} key={suggestion.name} onClick={e => this.onClick(e, suggestion)}>
										   <td>{suggestion.name}</td>
										</tr>
								);
							})}
						  </tbody>	
						</table>
				);
			} else {
				suggestionsListComponent = null;
			}
		}

        console.log(suggestionsListComponent)
		return (
				<React.Fragment>
					<input 	type="text"	className='form-control'
                        onChange={onChange}	onKeyDown={onKeyDown} value={this.props.userInput} />
				    {suggestionsListComponent}
				</React.Fragment>
		);
	}
}
