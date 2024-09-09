const websocket = new WebSocket('ws://localhost:8765');
let isMyTurn = false;
let myFigure = null;

const messageBox = document.getElementById('messages');
const newGameButton = document.getElementById('newGameButton');  // Получаем кнопку "Новая игра"

// Добавляем обработчик для кнопки "Новая игра"
newGameButton.addEventListener('click', () => {
    location.reload();  // Перезагружаем страницу
});

// Инициализация игрового поля
const cells = document.querySelectorAll('.cell');
cells.forEach(cell => {
    cell.addEventListener('click', () => {
        if (isMyTurn && !cell.classList.contains('disabled')) {
            const position = cell.getAttribute('data-pos');
            websocket.send(position);  // Отправляем координаты на сервер
        }
    });
});

// Обработка сообщений от сервера
websocket.onmessage = function (event) {
    const message = event.data;
    console.log(message)
    if (message.startsWith('Добро пожаловать')) {
        updateMessage(message);  // Приветственное сообщение
    } else if (message.startsWith('Ваш ход')) {
        isMyTurn = true;
        updateMessage("Ваш ход");
    } else if (message.includes('Игра началась')) {
        updateMessage('Игра началась');
    } else if (message === 'Вы победили') {
        updateMessage('Вы победили!');
        disableBoard();
    } else if (message === 'Вы проиграли') {
        updateMessage('Вы проиграли!');
        disableBoard();
    } else if (message === 'Ожидайте хода соперника'){
        updateMessage(message)
    } else if (message === 'Ход соперника'){
        updateMessage(message)
    } else if (message === "Соперник вышел. Вы победили"){
        updateMessage(message)
    }
    else {
         // Обновляем состояние игрового поля
         updateBoard(message);
    }
};

function updateBoard(boardState) {
    const rows = boardState.split('\r\n');
    rows.forEach((row, rowIndex) => {
        row.split('').forEach((cellValue, colIndex) => {
            const cell = document.querySelector(`.cell[data-pos="${rowIndex + 1} ${colIndex + 1}"]`);
            cell.textContent = cellValue !== '-' ? cellValue : '';
            if (cellValue !== '-') {
                cell.classList.add('disabled');
            }
        });
    });
}

function updateMessage(message) {
    messageBox.textContent = message;
}

function disableBoard() {
    cells.forEach(cell => cell.classList.add('disabled'));
}
