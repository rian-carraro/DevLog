// script.js — DevLog
// Funções de interatividade do sistema

// Confirmação antes de excluir um registro
function confirmarExclusao() {
    return confirm('Tem certeza que deseja excluir este registro?');
}

// Indicador de força de senha no cadastro
const campSenha = document.getElementById('senha');
const barraSenha = document.getElementById('barra-senha');
const textoForca = document.getElementById('texto-forca');

if (campSenha) {
    campSenha.addEventListener('input', function () {
        const senha = campSenha.value;
        let forca = 0;

        if (senha.length >= 4)  forca++;
        if (senha.length >= 8)  forca++;
        if (/[A-Z]/.test(senha)) forca++;
        if (/[0-9]/.test(senha)) forca++;
        if (/[^A-Za-z0-9]/.test(senha)) forca++;

        const niveis = [
            { texto: '',         classe: '',        largura: '0%'   },
            { texto: 'Fraca',    classe: 'bg-danger',   largura: '25%'  },
            { texto: 'Regular',  classe: 'bg-warning',  largura: '50%'  },
            { texto: 'Boa',      classe: 'bg-info',     largura: '75%'  },
            { texto: 'Forte',    classe: 'bg-success',  largura: '100%' },
            { texto: 'Forte',    classe: 'bg-success',  largura: '100%' },
        ];

        const nivel = niveis[forca];
        barraSenha.className = `progress-bar ${nivel.classe}`;
        barraSenha.style.width = nivel.largura;
        textoForca.textContent = nivel.texto ? `Senha ${nivel.texto}` : '';
    });
}
