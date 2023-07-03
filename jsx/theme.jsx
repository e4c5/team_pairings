/**
 * Provides Ability to switch between light and dark themes.
 * 
 * The dark theme is great as long as you don't need to print the standings.
 * Indeed one of the objectives of this software is to reduce paper usage by
 * placing the pairings online but this wouldn't work for children's events
 */

import React, {
    createContext, useContext, useReducer
} from 'react';

const ThemeContext = createContext(null)
const ThemeDispatchContext = createContext(null)
const getStoredTheme = () => localStorage.getItem('theme')
const setStoredTheme = theme => localStorage.setItem('theme', theme)

const setTheme = theme => {
    document.documentElement.setAttribute('data-bs-theme', theme)
    setStoredTheme(theme)
}

const getPreferredTheme = () => {
    const storedTheme = getStoredTheme()
    if (storedTheme) {
        return storedTheme
    }

    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function ThemeProvider({ children }) {
    const [theme, dispatch] = useReducer(
        themeReducer,
        {theme : 'dark', icon: 'bi-moon-stars-fill'}
    );
  
    return (
        <ThemeContext.Provider value={theme}>
            <ThemeDispatchContext.Provider value={dispatch}>
                {children}
            </ThemeDispatchContext.Provider>
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    return useContext(ThemeContext);
}

export function useThemeDispatch() {
    return useContext(ThemeDispatchContext);
}


export function themeReducer(state, action) {
    // i keep typing this as action instead of type!! so ....
    const type = action.type || action.action;
    switch (type) {
        case 'switch':
            if (state.theme === 'dark') 
            {
                setTheme('light')
                return { theme: 'light', icon: 'bi-moon-stars-fill'}
            }
            setTheme('dark')
            return { theme: 'dark', icon: 'bi-sun-fill'}
        
        default: {
            throw Error('Unknown action: ' + action.type);
        }
    }
}

export function Theme () {
    const theme = useTheme()
    const themeDispatch = useThemeDispatch()

    function clicked(e) {
        themeDispatch({action: 'switch'})    
    }
    
    return (
        <button className="btn btn-link nav-link"
                data-bs-theme-value="light"
                type="button"
                onClick={e => clicked(e)}
                aria-label="Toggle theme">
                    <i className={ "bi " + theme.icon }></i>
        </button>
    )
}