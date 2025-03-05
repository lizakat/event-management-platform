document.addEventListener('DOMContentLoaded', function () {
    const pathname = window.location.pathname;

    if (pathname === '/') {
        const toggleSwitch = document.getElementById('toggleSwitch');
        const username = document.getElementById('username');
        const surname = document.getElementById('surname');
        const nextButton = document.getElementById('nextButton');

        if (toggleSwitch) {
            toggleSwitch.addEventListener('click', function () {
                this.classList.toggle('active');
            });
        }

        function validateField(field, minLength = 2, maxLength = 20) {
            const value = field.value.trim();
            const errorMessage = field.parentElement.querySelector('.error-message');
            const nameRegex = /^[A-Za-zА-Яа-яЁё]+$/;

            if (!errorMessage) return false;

            if (!value) {
                errorMessage.textContent = "Заполните это поле";
                field.classList.add("input-error");
                return false;
            }

            if (value.length < minLength) {
                errorMessage.textContent = `Минимальная длина — ${minLength} символа`;
                field.classList.add("input-error");
                return false;
            }
            if (value.length > maxLength) {
                errorMessage.textContent = `Максимальная длина — ${maxLength} символов`;
                field.classList.add("input-error");
                return false;
            }
            if (!nameRegex.test(value)) {
                errorMessage.textContent = "Используйте только буквы";
                field.classList.add("input-error");
                return false;
            }
            errorMessage.textContent = "";
            field.classList.remove("input-error");
            return true;
        }

        function validateForm() {
            const isUsernameValid = validateField(username);
            const isSurnameValid = validateField(surname);
            return isUsernameValid && isSurnameValid;
        }

        nextButton.addEventListener("click", function () {
            if (validateForm()) {
                const nameValue = encodeURIComponent(username.value.trim());
                const surnameValue = encodeURIComponent(surname.value.trim());
                const role_id = toggleSwitch.classList.contains('active') ? 1 : 2;
                window.location.href = `/register?name=${nameValue}&surname=${surnameValue}&role_id=${role_id}`;
            }
        });

        [username, surname].forEach(field => {
            field.addEventListener("input", () => validateField(field));
        });
    }

    if (pathname === '/register') {
        document.getElementById('registerButton').addEventListener('click', function() {
            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;
            const confirmPassword = document.getElementById('register-confirm-password').value;

            if (password !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }

            const urlParams = new URLSearchParams(window.location.search);
            const name = urlParams.get('name');
            const surname = urlParams.get('surname');
            const role_id = urlParams.get('role_id');

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
                window.location.href = '/login';
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });

        document.querySelector('.button-code').addEventListener('click', function() {
            alert('Code resent!');
        });
    }

    if (pathname === '/login') {
        document.getElementById('button').addEventListener('click', function() {
            window.location.href = '/main-page';
        });
    }

    if (pathname === '/forgot-password') {
        document.getElementById('button').addEventListener('click', function() {
            window.location.href = '/notification-password';
        });
    }

    if (pathname === '/new-password') {
        document.getElementById('button').addEventListener('click', function() {
            window.location.href = '/login';
        });
    }

    if (pathname === '/notification-password') {
        document.getElementById('button').addEventListener('click', function() {
            window.location.href = '/new-password';
        });
    }
});
