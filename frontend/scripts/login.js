document.getElementById('loginForm').addEventListener('submit', function(e){
    e.preventDefault();

    const registration = document.getElementById('registration').value;
    const password = document.getElementById('password').value;

    // Simulação de autenticação
    if(registration === 'aluno123' && password === 'senha123'){
        window.location.href = 'dashboard.html';
    } else {
        document.getElementById('loginError').innerText = "Matrícula ou senha inválidas.";
    }
});
