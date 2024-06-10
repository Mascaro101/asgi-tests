document.addEventListener('DOMContentLoaded', () => {
    //Espera a que el DOM esté completamente cargado antes de ejecutar el código
    const lever = document.getElementById('lever');
    //Obtiene el elemento de la palanca por su ID
    lever.addEventListener('mousedown', () => {
        //Agrega un evento al hacer clic y mantener presionada la palanca
        lever.classList.add('active');
        //Añade la clase 'active' para simular el movimiento de la palanca
        setTimeout(spin, 300);
    });
    document.addEventListener('mouseup', () => {

        lever.classList.remove('active');
        //Quita la clase 'active' para detener la simulación de la palanca
    });
    initializeReels();
});

const symbols = ['🍒', '🍋', '🍉', '🍇', '🍓', '⭐'];
let totalMoney = 100;
//Damos el valor del dinero, en este caso 100

function initializeReels() {
    //Función para inicializar los carriles
    for (let i = 1; i <= 3; i++) {
        //Itera sobre los tres carriles
        const reel = document.getElementById(`reel${i}`);
        //Obtiene cada carril por su ID
        const symbolsContainer = document.createElement('div');
        //Crea un nuevo contenedor de símbolos
        symbolsContainer.classList.add('symbols');
        //Añade la clase 'symbols' al contenedor
        symbolsContainer.innerHTML = getSymbolsHTML();
        //Llena el contenedor con los símbolos
        reel.appendChild(symbolsContainer);
        //Añade el contenedor de símbolos al carril correspondiente
    }
}

function getSymbolsHTML() {
    //Función para obtener el HTML de los símbolos
    let html = '';
    //Inicia con una cadena vacía
    for (let i = 0; i < symbols.length * 3; i++) {
        //Itera sobre los símbolos, repitiéndolos tres veces
        html += `<div class="symbol">${symbols[i % symbols.length]}</div>`;
        //Añade cada símbolo al HTML
    }
    return html;

}

function spin() {
    //Función para girar los carriles
    const betAmount = parseInt(document.getElementById('betAmount').value);
    //Obtiene el valor de la apuesta y lo convierte a número entero
    if (isNaN(betAmount) || betAmount <= 0 || betAmount > totalMoney) {
        //Verifica si la apuesta es inválida, no dejara girar los carriles si es invalida
        document.getElementById('result').textContent = 'Apuesta inválida';
        return;
    }

    //Actualizaciones necesarias si se pierde o se gana al dinero
    totalMoney -= betAmount;
    document.getElementById('totalMoney').textContent = totalMoney;


    const results = [];
    const spinDurations = [1000, 1500, 2000];

    for (let i = 1; i <= 3; i++) {
        //Itera sobre los tres carriles
        const reel = document.getElementById(`reel${i}`).querySelector('.symbols');
        const randomDuration = spinDurations[Math.floor(Math.random() * spinDurations.length)];
        // Selecciona una duración aleatoria para el giro
        const randomPosition = Math.floor(Math.random() * symbols.length) + symbols.length;

        results.push(symbols[randomPosition % symbols.length]);

        animateReel(reel, randomPosition * 180, randomDuration);
        //Anima el giro del carril
    }

    setTimeout(() => {
        checkResult(results, betAmount);
    }, Math.max(...spinDurations) + 100);
}

function animateReel(reel, position, duration) {
    //Esta funcion es la que dara la animacion a los giros de los carriles
    reel.style.transition = `transform ${duration}ms ease-out`;
    reel.style.transform = `translateY(-${position}px)`;

    setTimeout(() => {
        reel.style.transition = 'none';

        reel.style.transform = `translateY(-${position % (symbols.length * 180)}px)`;

    }, duration);

}

function checkResult(results, betAmount) {
    //Función para verificar los resultados y calcular las ganancias
    let winnings = 0;

    if (results[0] === results[1] && results[1] === results[2]) {
    
        winnings = betAmount * 5;
    } else if (results[0] === results[1] || results[1] === results[2]) {

        winnings = betAmount * 2;
    }

    totalMoney += winnings;

    document.getElementById('totalMoney').textContent = totalMoney;
    //Actualiza el dinero total mostrado en la interfaz

    if (winnings > 0) {
        document.getElementById('result').textContent = `¡Ganaste ${winnings}€!`;
    } else {
        document.getElementById('result').textContent = 'No ganaste nada. Inténtalo de nuevo.';
    }
}
