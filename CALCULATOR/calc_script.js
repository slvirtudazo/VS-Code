// Get the display element where we show numbers and results
const display = document.getElementById('display');

// Variables to track calculator state
let currentInput = '0';      // What the user is currently typing
let previousInput = '';      // The first number before an operation
let operation = null;        // The operation to perform (+, -, ×, ÷, %)
let shouldResetDisplay = false;  // Flag to know when to start fresh input

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
    // If we just calculated a result, start fresh with new number
    if (shouldResetDisplay) {
        currentInput = num;
        shouldResetDisplay = false;
    } else {
        // Add digit to current input (replace '0' if it's the only character)
        currentInput = currentInput === '0' ? num : currentInput + num;
    }
    updateDisplay();
}

// Function to handle decimal point
function inputDecimal() {
    // Start fresh if we just calculated
    if (shouldResetDisplay) {
        currentInput = '0.';
        shouldResetDisplay = false;
    } 
    // Only add decimal if there isn't one already
    else if (!currentInput.includes('.')) {
        currentInput += '.';
    }
    updateDisplay();
}

// Function to handle operation buttons (+, -, ×, ÷)
function handleOperation(nextOperation) {
    const inputValue = parseFloat(currentInput);
    
    // If we already have a previous operation pending, calculate it first
    if (operation && !shouldResetDisplay) {
        calculate();
    } else {
        // Store the current number as the first operand
        previousInput = currentInput;
    }
    
    // Set the new operation and prepare for next input
    operation = nextOperation;
    shouldResetDisplay = true;
}

// Function to perform the actual calculation
function calculate() {
    const prev = parseFloat(previousInput);
    const current = parseFloat(currentInput);
    
    // Don't calculate if we don't have valid numbers
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
            // Prevent division by zero
            result = current === 0 ? 'Error' : prev / current;
            break;
        case '%':
            // Percent: divide by 100
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
    // Remove last character, or reset to '0' if empty
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

// Add keyboard support - listen for keydown events on the entire document
document.addEventListener('keydown', (event) => {
    const key = event.key;
    
    // Handle number keys (both top row and numpad)
    if (key >= '0' && key <= '9') {
        inputNumber(key);
    }
    // Handle decimal point (period or comma on some keyboards)
    else if (key === '.' || key === ',') {
        inputDecimal();
    }
    // Handle addition (plus sign or equals/plus key)
    else if (key === '+') {
        handleOperation('+');
    }
    // Handle subtraction (minus sign or dash)
    else if (key === '-') {
        handleOperation('−');
    }
    // Handle multiplication (asterisk or x key)
    else if (key === '*' || key.toLowerCase() === 'x') {
        handleOperation('×');
    }
    // Handle division (forward slash)
    else if (key === '/') {
        handleOperation('÷');
    }
    // Handle percent (% key, usually Shift+5)
    else if (key === '%') {
        handlePercent();
    }
    // Handle equals (Enter key or equals sign)
    else if (key === 'Enter' || key === '=') {
        calculate();
    }
    // Handle erase/backspace (Backspace or Delete key)
    else if (key === 'Backspace' || key === 'Delete') {
        erase();
    }
    // Handle all clear (Escape key or 'c' key)
    else if (key === 'Escape' || key.toLowerCase() === 'c') {
        allClear();
    }
});