//npx babel --watch jsx --out-dir tournament/static/js/ --presets react-app/dev 
import Button from '@mui/material/Button';

const Bada = () => {
    return <Button variant="contained">Hello World</Button>
}

const div = document.getElementById('root')
const root = ReactDOM.createRoot(div) 
root.render(<Bada/>)
console.log('main.js 0.01')