const display = document.getElementById('display');

// Variables to track calculator state
let currentInput = '0';                     // What the user is currently typing
let previousInput = '';                     // The first number before an operation
let operation = null;                       // The operation to perform
let shouldResetDisplay = false;             // Flag to know when to start fresh input

// Get all the buttons using getElementById
const allClearBtn = document.getElementById('all-clear');
const eraseBtn = document.getElementById('erase');
const percentBtn = document.getElementById('percent');
const divideBtn = document.getElementById('divide');
const multiplyBtn = document.getElementById('multiply');
const subtractBtn = document.getElementById('subtract');
const addBtn = document.getElementById('add');
const equalsBtn = document.getElementById('equals');
const decimalBtn = document.getElementById('decimal');

// Number buttons
const zeroBtn = document.getElementById('zero');
const oneBtn = document.getElementById('one');
const twoBtn = document.getElementById('two');
const threeBtn = document.getElementById('three');
const fourBtn = document.getElementById('four');
const fiveBtn = document.getElementById('five');
const sixBtn = document.getElementById('six');
const sevenBtn = document.getElementById('seven');
const eightBtn = document.getElementById('eight');
const nineBtn = document.getElementById('nine');

// Function to update the display screen
function updateDisplay() {
    display.textContent = currentInput;
}

// Function to handle number button clicks
function inputNumber(num) {
    if (shouldResetDisplay) {
        currentInput = num;
        shouldResetDisplay = false;
    } else {
        currentInput = currentInput === '0' ? num : currentInput + num;
    }
    updateDisplay();
}

// Function to handle decimal point
function inputDecimal() {
    if (shouldResetDisplay) {
        currentInput = '0.';
        shouldResetDisplay = false;
    } 
    else if (!currentInput.includes('.')) {
        currentInput += '.';
    }
    updateDisplay();
}

// Function to handle operation buttons (+, -, ×, ÷)
function handleOperation(nextOperation) {
    const inputValue = parseFloat(currentInput);
    
    if (operation && !shouldResetDisplay) {
        calculate();
    } else {
        previousInput = currentInput;
    }
    
    operation = nextOperation;
    shouldResetDisplay = true;
}

// Function to perform the actual calculation
function calculate() {
    const prev = parseFloat(previousInput);
    const current = parseFloat(currentInput);
    
    // Prevents from calculating if there are no valid numbers
    if (isNaN(prev) || isNaN(current)) return;
    
    let result;
    
    // Perform calculation based on the operation
    switch (operation) {
        case '+':
            result = prev + current;
            break;
        case '−':
            result = prev - current;
            break;
        case '×':
            result = prev * current;
            break;
        case '÷':
            result = current === 0 ? 'Error' : prev / current;
            break;
        case '%':
            result = prev / 100;
            break;
        default:
            return;
    }
    
    // Update display with result and prepare for next operation
    currentInput = result.toString();
    operation = null;
    previousInput = '';
    shouldResetDisplay = true;
    updateDisplay();
}

// Function to handle percent button
function handlePercent() {
    const value = parseFloat(currentInput);
    currentInput = (value / 100).toString();
    updateDisplay();
}

// Function to clear everything (AC button)
function allClear() {
    currentInput = '0';
    previousInput = '';
    operation = null;
    shouldResetDisplay = false;
    updateDisplay();
}

// Function to erase current input (X button)
function erase() {
    if (currentInput.length > 1) {
        currentInput = currentInput.slice(0, -1);
    } else {
        currentInput = '0';
    }
    updateDisplay();
}

// Add event listeners to all number buttons
zeroBtn.addEventListener('click', () => inputNumber('0'));
oneBtn.addEventListener('click', () => inputNumber('1'));
twoBtn.addEventListener('click', () => inputNumber('2'));
threeBtn.addEventListener('click', () => inputNumber('3'));
fourBtn.addEventListener('click', () => inputNumber('4'));
fiveBtn.addEventListener('click', () => inputNumber('5'));
sixBtn.addEventListener('click', () => inputNumber('6'));
sevenBtn.addEventListener('click', () => inputNumber('7'));
eightBtn.addEventListener('click', () => inputNumber('8'));
nineBtn.addEventListener('click', () => inputNumber('9'));

// Add event listeners to operation buttons
addBtn.addEventListener('click', () => handleOperation('+'));
subtractBtn.addEventListener('click', () => handleOperation('−'));
multiplyBtn.addEventListener('click', () => handleOperation('×'));
divideBtn.addEventListener('click', () => handleOperation('÷'));
percentBtn.addEventListener('click', () => handlePercent());

// Add event listeners to special buttons
decimalBtn.addEventListener('click', () => inputDecimal());
equalsBtn.addEventListener('click', () => calculate());
allClearBtn.addEventListener('click', () => allClear());
eraseBtn.addEventListener('click', () => erase());

// Listen for keydown events on the entire document
document.addEventListener('keydown', (event) => {
    const key = event.key;
    
    if (key >= '0' && key <= '9') {
        inputNumber(key);
    }
    else if (key === '.' || key === ',') {
        inputDecimal();
    }
    else if (key === '+') {
        handleOperation('+');
    }
    else if (key === '-') {
        handleOperation('−');
    }
    else if (key === '*' || key.toLowerCase() === 'x') {
        handleOperation('×');
    }
    else if (key === '/') {
        handleOperation('÷');
    }
    else if (key === '%') {
        handlePercent();
    }
    else if (key === 'Enter' || key === '=') {
        calculate();
    }
    else if (key === 'Backspace' || key === 'Delete') {
        erase();
    }
    else if (key === 'Escape' || key.toLowerCase() === 'c') {
        allClear();
    }
});