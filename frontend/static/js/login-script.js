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
        const registerButton = document.getElementById('registerButton');
        const emailField = document.getElementById('register-email');
        const passwordField = document.getElementById('register-password');
        const confirmPasswordField = document.getElementById('register-confirm-password');
        const codeField = document.getElementById('register-code');

        function validateEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            const errorMessage = emailField.parentElement.querySelector('.error-message');

            if (!email) {
                errorMessage.textContent = 'Введите email';
                emailField.classList.add('input-error');
                return false;
            }
            if (!emailRegex.test(email)) {
                errorMessage.textContent = 'Некорректный email';
                emailField.classList.add('input-error');
                return false;
            }
            errorMessage.textContent = '';
            emailField.classList.remove('input-error');
            return true;
        }

        function validatePassword(password) {
            const errorMessage = passwordField.parentElement.querySelector('.error-message');

            if (!password) {
                errorMessage.textContent = 'Введите пароль';
                passwordField.classList.add('input-error');
                return false;
            }
            if (password.length < 8) {
                errorMessage.textContent = 'Пароль должен быть не менее 8 символов';
                passwordField.classList.add('input-error');
                return false;
            }
            errorMessage.textContent = '';
            passwordField.classList.remove('input-error');
            return true;
        }

        function validateConfirmPassword(password, confirmPassword) {
            const errorMessage = confirmPasswordField.parentElement.querySelector('.error-message');

            if (!confirmPassword) {
                errorMessage.textContent = 'Подтвердите пароль';
                confirmPasswordField.classList.add('input-error');
                return false;
            }
            if (password !== confirmPassword) {
                errorMessage.textContent = 'Пароли не совпадают';
                confirmPasswordField.classList.add('input-error');
                return false;
            }
            errorMessage.textContent = '';
            confirmPasswordField.classList.remove('input-error');
            return true;
        }

        function validateCode(code) {
            const errorMessage = document.querySelector('#code-container .error-message');

            if (!code) {
                errorMessage.textContent = 'Введите код';
                codeField.classList.add('input-error');
                return false;
            }

            errorMessage.textContent = '';
            codeField.classList.remove('input-error');
            return true;
        }

        async function validateCodeOnServer(email, code) {
            try {
                const response = await fetch('/auth/validate-code', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, code }),
                });
                const data = await response.json();
                return data.valid;
            } catch (error) {
                console.error('Ошибка при проверке кода:', error);
                return false;
            }
        }

        // Основная функция валидации формы
        async function validateForm() {
            const email = emailField.value.trim();
            const password = passwordField.value.trim();
            const confirmPassword = confirmPasswordField.value.trim();
            const code = codeField.value.trim();

            const isEmailValid = validateEmail(email);
            const isPasswordValid = validatePassword(password);
            const isConfirmPasswordValid = validateConfirmPassword(password, confirmPassword);
            const isCodeValid = validateCode(code);
            const errorMessage = document.querySelector('#code-container .error-message');

            if (isCodeValid) {
                 const isCodeValidOnServer = await validateCodeOnServer(email, code);
                 if (!isCodeValidOnServer) {
                     errorMessage.textContent = 'Неверный код';
                     codeField.classList.add('input-error');
                     return false;
                 }
             }
            return isEmailValid && isPasswordValid && isConfirmPasswordValid && isCodeValid;
        }

        async function isEmailRegistered(email) {
            try {
                const response = await fetch(`/auth/check-email?email=${encodeURIComponent(email)}`);
                const data = await response.json();
                return data.exists;
            } catch (error) {
                console.error('Ошибка при проверке email:', error);
                return false;
            }
        }

        function clearForm() {
            passwordField.value = '';
            confirmPasswordField.value = '';
            codeField.value = '';
        }

        registerButton.addEventListener('click', async function () {
            const email = emailField.value.trim();

            const emailExists = await isEmailRegistered(email);
            if (emailExists) {
                clearForm()
                const emailErrorMessage = emailField.parentElement.querySelector('.error-message');
                emailErrorMessage.textContent = 'Пользователь с таким email уже зарегистрирован';
                emailField.classList.add('input-error');
                return;
            }

            if (await validateForm()) {
                const password = passwordField.value.trim();

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

                fetch('/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(userData),
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => {
                            throw new Error(err.detail || 'Ошибка сервера');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Success:', data);
                    window.location.href = '/login';
                })
                .catch((error) => {
                    console.error('Error:', error);
                    alert(error.message);
                });
            }
        });

       document.querySelector('.button-code').addEventListener('click', async function () {
            const email = emailField.value.trim();

            try {
                const response = await fetch('/auth/generate-code', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email }),
                });
                const data = await response.json();
                if (data.success) {
                    alert('Код отправлен!');
                }
            } catch (error) {
                console.error('Ошибка при отправке кода:', error);
            }
        });

        emailField.addEventListener('input', () => validateEmail(emailField.value.trim()));
        passwordField.addEventListener('input', () => validatePassword(passwordField.value.trim()));
        confirmPasswordField.addEventListener('input', () => {
            validateConfirmPassword(passwordField.value.trim(), confirmPasswordField.value.trim());
        });
        codeField.addEventListener('input', () => validateCode(codeField.value.trim()));
    }

    if (pathname === '/login') {
        const loginButton = document.getElementById('button');
        const emailField = document.getElementById('login-email');
        const passwordField = document.getElementById('login-password');
        const errorMessage = document.querySelector('.error-message');
    
        function validateEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!email) {
                errorMessage.textContent = 'Введите email';
                emailField.classList.add('input-error');
                return false;
            }
            if (!emailRegex.test(email)) {
                errorMessage.textContent = 'Некорректный email';
                emailField.classList.add('input-error');
                return false;
            }
            errorMessage.textContent = '';
            emailField.classList.remove('input-error');
            return true;
        }
    
        function validatePassword(password) {
            if (!password) {
                errorMessage.textContent = 'Введите пароль';
                passwordField.classList.add('input-error');
                return false;
            }
            errorMessage.textContent = '';
            passwordField.classList.remove('input-error');
            return true;
        }
    
        loginButton.addEventListener('click', async (event) => {
            event.preventDefault();
    
            const email = emailField.value.trim();
            const password = passwordField.value.trim();
    
            const isEmailValid = validateEmail(email);
            const isPasswordValid = validatePassword(password);
    
            if (!isEmailValid || !isPasswordValid) {
                return;
            }
    
            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    credentials: 'include', // Важно для работы с куками
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    }),
                });
    
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Ошибка при входе');
                }
    
                const data = await response.json();
                
                // Сохраняем токен в localStorage (если нужно для SPA)
                if (data.access_token) {
                    localStorage.setItem('access_token', data.access_token);
                }
    
                // Перенаправляем на защищенную страницу
                window.location.href = '/main-page';
            } catch (error) {
                console.error('Ошибка:', error);
                errorMessage.textContent = error.message;
            }
        });
    
        emailField.addEventListener('input', () => validateEmail(emailField.value.trim()));
        passwordField.addEventListener('input', () => validatePassword(passwordField.value.trim()));
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
