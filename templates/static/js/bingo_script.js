//Función para generar múltiples cartones de bingo
function generateCards() {
    const numCards = document.getElementById('num-cards').value;
    const bingoCardsContainer = document.getElementById('bingo-cards');
    bingoCardsContainer.innerHTML = '';

    for (let i = 0; i < numCards; i++) {
        const card = generateCard();
        bingoCardsContainer.appendChild(card);
    }

    //Iniciar la llamada de números
    startCallingNumbers();
}

//Función para generar un cartón de bingo único
function generateCard() {
    const numbers = [];

    //Generar números para cada columna del cartón
    for (let i = 0; i < 9; i++) {
        const column = [];
        //Generar números en el rango correspondiente a la columna
        for (let j = i * 10 + 1; j <= (i + 1) * 10; j++) {
            column.push(j);
        }
        //Mezclar los números de la columna
        shuffleArray(column);
        //Agregar los números al arreglo principal
        numbers.push(...column);
    }

    //Mezclar todos los números del cartón
    shuffleArray(numbers);

    //Elegir aleatoriamente 12 posiciones para cubrir
    const coveredIndices = [];
    while (coveredIndices.length < 12) {
        const index = Math.floor(Math.random() * 27); //Hay 27 celdas en total
        if (!coveredIndices.includes(index)) {
            coveredIndices.push(index);
        }
    }

    //Crear la tabla del cartón de bingo
    const table = document.createElement('table');
    table.classList.add('bingo-card');
    const tbody = document.createElement('tbody');

    let counter = 0;
    for (let i = 0; i < 3; i++) {
        const row = document.createElement('tr');
        for (let j = 0; j < 9; j++) {
            const cell = document.createElement('td');
            if (coveredIndices.includes(counter)) { //Comprobar si la celda debe estar cubierta
                const cover = document.createElement('div');
                cover.classList.add('initial-cover');
                cell.appendChild(cover);
            } else {
                cell.textContent = numbers[counter];
            }
            row.appendChild(cell);
            counter++;
        }
        tbody.appendChild(row);
    }

    table.appendChild(tbody);
    return table;
}

//Función para mezclar un arreglo usando el algoritmo de Fisher-Yates (mezcla aleatoria)
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

//Función para reiniciar los cartones de bingo
function resetCards() {
    const bingoCardsContainer = document.getElementById('bingo-cards');
    bingoCardsContainer.innerHTML = '';
    numbersCalled.length = 0;
    currentNumber = 0;
    if (numberCallInterval) {
        clearInterval(numberCallInterval);
    }
    document.getElementById('bingo-ball').textContent = '';
}

//Variables para mantener el estado del juego
let currentNumber = 0;
const numbersCalled = [];
let numberCallInterval;

//Función para iniciar la llamada de números
function startCallingNumbers() {
    if (numberCallInterval) {
        clearInterval(numberCallInterval);
    }
    numberCallInterval = setInterval(callNumber, 2000); //Llamada de número cada 2 segundos
}

//Función para animar la llamada de un número
async function callNumber() {
    const ball = document.getElementById('bingo-ball');

    //Generar un nuevo número aleatorio no llamado antes
    do {
        
        const response = await fetch("/generate_bingo_number", {method: "POST"});
        const data = await response.json();
        console.log(data.number);
        
        currentNumber = data.number;
        
    } while (numbersCalled.includes(currentNumber));

    ball.textContent = currentNumber;
    numbersCalled.push(currentNumber);

    //Tachar el número en el cartón de bingo
    const bingoCells = document.querySelectorAll('.bingo-card td');


    if (!checkBingo()) {
        bingoCells.forEach(cell => {
            if (cell.textContent === currentNumber.toString()) {
                const cover = document.createElement('div');
                cover.classList.add('number-cover');
                cell.appendChild(cover);
            }
        });
    } else{
        alert("¡Ganaste!");
    }   
}

//Función para comprobar si hay bingo en algún cartón
function checkBingo() {
    const cards = document.querySelectorAll('.bingo-card');
    for (const card of cards) {
        const cells = card.querySelectorAll('td');
        let allCovered = true;
        for (const cell of cells) {
            if (cell.textContent !== '' && !cell.querySelector('.initial-cover') && !cell.querySelector('.number-cover')) {
                allCovered = false;
                break;
            }
        }
        if (allCovered) {
            return true;
        }
    }
    return false;
}