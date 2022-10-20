//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 

const Bada = () => {
    return 'Hello from react'
}

const div = document.getElementById('root')
const root = ReactDOM.createRoot(div) 
root.render(<Bada/>)
console.log('main.js 0.01')