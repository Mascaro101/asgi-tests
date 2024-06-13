document.addEventListener('DOMContentLoaded', () => {
    //Espera a que el DOM esté completamente cargado antes de ejecutar el código
    const palanca = document.getElementById('palanca');
    //Obtiene el elemento de la palanca por su ID
    palanca.addEventListener('mousedown', () => {
        //Agrega un evento al hacer clic y mantener presionada la palanca
        palanca.classList.add('active');
        //Añade la clase 'active' para simular el movimiento de la palanca
        setTimeout(spin, 300);
    });
    document.addEventListener('mouseup', () => {

        palanca.classList.remove('active');
        //Quita la clase 'active' para detener la simulación de la palanca
    });
    initializeCarrils();
});

const symbols = ['🍒', '🍋', '🍉', '🍇', '🍓', '⭐'];
let dinerototal = 100;
//Damos el valor del dinero, en este caso 100

function initializeCarrils() {
    //Función para inicializar los carriles
    for (let i = 1; i <= 3; i++) {
        //Itera sobre los tres carriles
        const carril = document.getElementById(`carril${i}`);
        //Obtiene cada carril por su ID
        const symbolsBloque = document.createElement('div');
        //Crea un nuevo contenedor de símbolos
        symbolsBloque.classList.add('symbols');
        //Añade la clase 'symbols' al contenedor
        symbolsBloque.innerHTML = getSymbolsHTML();
        //Llena el contenedor con los símbolos
        carril.appendChild(symbolsBloque);
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
    const apuesta = parseInt(document.getElementById('apuesta').value);
    //Obtiene el valor de la apuesta y lo convierte a número entero
    if (isNaN(apuesta) || apuesta <= 0 || apuesta > dinerototal) {
        //Verifica si la apuesta es inválida, no dejara girar los carriles si es invalida
        document.getElementById('resultado').textContent = 'Apuesta inválida';
        return;
    }

    //Actualizaciones necesarias si se pierde o se gana al dinero
    dinerototal -= apuesta;
    document.getElementById('dinerototal').textContent = dinerototal;


    const resultados = [];
    const spinDurations = [1000, 1500, 2000];

    for (let i = 1; i <= 3; i++) {
        //Itera sobre los tres carriles
        const carril = document.getElementById(`carril${i}`).querySelector('.symbols');
        const randomDuration = spinDurations[Math.floor(Math.random() * spinDurations.length)];
        // Selecciona una duración aleatoria para el giro
        const randomPosition = Math.floor(Math.random() * symbols.length) + symbols.length;

        resultados.push(symbols[randomPosition % symbols.length]);

        animateCarril(carril, randomPosition * 180, randomDuration);
        //Anima el giro del carril
    }

    setTimeout(() => {
        checkResultado(resultados, apuesta);
    }, Math.max(...spinDurations) + 100);
}

function animateCarril(carril, position, duration) {
    //Esta funcion es la que dara la animacion a los giros de los carriles
    carril.style.transition = `transform ${duration}ms ease-out`;
    carril.style.transform = `translateY(-${position}px)`;

    setTimeout(() => {
        carril.style.transition = 'none';

        carril.style.transform = `translateY(-${position % (symbols.length * 180)}px)`;

    }, duration);

}

function checkResultado(resultados, apuesta) {
    //Función para verificar los resultadoados y calcular las ganancias
    let winnings = 0;

    if (resultados[0] === resultados[1] && resultados[1] === resultados[2]) {
    
        winnings = apuesta * 5;
    } else if (resultados[0] === resultados[1] || resultados[1] === resultados[2]) {

        winnings = apuesta * 2;
    }

    dinerototal += winnings;

    document.getElementById('dinerototal').textContent = dinerototal;
    //Actualiza el dinero total mostrado en la interfaz

    if (winnings > 0) {
        document.getElementById('resultado').textContent = `¡Has ganado ${winnings}€!`;
    } else {
        document.getElementById('resultado').textContent = 'No has ganado nada. Inténtalo de nuevo.';
    }
}
