document.getElementById('toggleSwitch').addEventListener('click', function() {
    this.classList.toggle('active');
});

document.getElementById('nextButton').addEventListener('click', function() {
    const name = document.getElementById('username').value;
    const surname = document.getElementById('surname').value;
    const role_id = document.getElementById('toggleSwitch').classList.contains('active') ? 1 : 2;

    // Переход на следующую форму с передачей данных через URL
    window.location.href = `/register?name=${encodeURIComponent(name)}&surname=${encodeURIComponent(surname)}&role_id=${role_id}`;
});

document.getElementById('registerButton').addEventListener('click', function() {
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }

    const userData = {
        name: name,
        surname: surname,
        role_id: role_id,
        email: email,
        password: password,
    };

    // Отправляем данные на сервер
    fetch('/users/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        window.location.href = '/';
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

document.querySelector('.button-code').addEventListener('click', function() {
    // Логика для повторной отправки кода
    alert('Code resent!');
});