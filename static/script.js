// static/script.js
document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM Carregado. Inputmask DEVE estar definido.");

    const formPF = document.getElementById('cadastroFormPF');
    const formPJ = document.getElementById('cadastroFormPJ');

    // --- FUNÇÕES AUXILIARES ---
    function validateEmail(emailInput, confirmeEmailInput, errorDisplayElement) {
        if (!emailInput || !confirmeEmailInput || !errorDisplayElement) {
            return true;
        }
        if (emailInput.value !== confirmeEmailInput.value && confirmeEmailInput.value !== '') {
            errorDisplayElement.style.display = 'block';
            confirmeEmailInput.classList.add('is-invalid');
            return false;
        } else {
            errorDisplayElement.style.display = 'none';
            confirmeEmailInput.classList.remove('is-invalid');
            return true;
        }
    }

    function setupCepLookup(cepFieldId, logradouroFieldId, bairroFieldId, cidadeFieldId, ufFieldId, numeroFieldId) {
        const cepInput = document.getElementById(cepFieldId);
        if (cepInput) {
            cepInput.addEventListener('input', function () {
                const cepVal = cepInput.inputmask ? cepInput.inputmask.unmaskedvalue() : cepInput.value.replace(/\D/g, '');
                if (cepVal.length === 8) {
                    fetch(`https://viacep.com.br/ws/${cepVal}/json/`)
                        .then(response => response.json())
                        .then(data => {
                            if (!data.erro) {
                                if(document.getElementById(logradouroFieldId)) document.getElementById(logradouroFieldId).value = data.logradouro || '';
                                if(document.getElementById(bairroFieldId)) document.getElementById(bairroFieldId).value = data.bairro || '';
                                if(document.getElementById(cidadeFieldId)) document.getElementById(cidadeFieldId).value = data.localidade || '';
                                if(document.getElementById(ufFieldId)) document.getElementById(ufFieldId).value = data.uf || '';
                                if (document.getElementById(numeroFieldId)) document.getElementById(numeroFieldId).focus();
                            }
                        }).catch(error => console.error('Erro ao buscar CEP:', error));
                } else if (cepVal.length === 0) {
                    if(document.getElementById(logradouroFieldId)) document.getElementById(logradouroFieldId).value = '';
                    if(document.getElementById(bairroFieldId)) document.getElementById(bairroFieldId).value = '';
                    if(document.getElementById(cidadeFieldId)) document.getElementById(cidadeFieldId).value = '';
                    if(document.getElementById(ufFieldId)) document.getElementById(ufFieldId).value = '';
                }
            });
            cepInput.addEventListener('blur', function() {
                const cepVal = cepInput.inputmask ? cepInput.inputmask.unmaskedvalue() : cepInput.value.replace(/\D/g, '');
                if (cepVal.length > 0 && cepVal.length < 8) {
                    cepInput.classList.add('is-invalid');
                } else if (cepVal.length === 8 && document.getElementById(logradouroFieldId) && document.getElementById(logradouroFieldId).value === '') {
                    cepInput.classList.add('is-invalid');
                } else if (cepVal.length === 8 || cepVal.length === 0) {
                    cepInput.classList.remove('is-invalid');
                }
            });
        }
    }

    function validateAndSubmit(form, event, isPJ = false) {
        event.preventDefault();
        let isValid = true;
        const errors = [];

        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        form.querySelectorAll('.custom-invalid-feedback').forEach(el => el.remove());

        function addError(field, message) {
            if (field) {
                field.classList.add('is-invalid');
                let feedback = field.parentElement.querySelector('.custom-invalid-feedback');
                if (!feedback && field.type !== 'checkbox' && field.type !== 'radio') { // Não adicionar para checkbox/radio se o label já indica
                    feedback = document.createElement('div');
                    feedback.className = 'custom-invalid-feedback d-block'; // d-block para mostrar
                    // Tentar inserir após o input, ou no final do parent se não for direto
                    if(field.nextSibling) field.parentNode.insertBefore(feedback, field.nextSibling);
                    else field.parentElement.appendChild(feedback);
                } else if (feedback) {
                    feedback.style.display = 'block';
                }
                if(feedback) feedback.textContent = message;

                // Para checkboxes e radios, o erro pode ser mais genérico ou associado ao grupo
                 if ((field.type === 'checkbox' || field.type === 'radio') && field.parentElement.classList.contains('form-check')) {
                    // Poderia adicionar uma classe de erro ao label ou um texto de erro após o grupo
                    // Por agora, o addClass('is-invalid') no input já pode ser usado pelo CSS
                    // Para feedback visual em radios/checkboxes, pode ser melhor adicionar um span de erro
                    let groupErrorElement = field.closest('.mb-3, .col-md-6, .col-md-12').querySelector('.group-invalid-feedback');
                    if(!groupErrorElement){
                        groupErrorElement = document.createElement('div');
                        groupErrorElement.className = 'custom-invalid-feedback d-block group-invalid-feedback';
                        // Adiciona o erro ao final do contêiner do grupo de radios/checkbox
                        field.closest('.mb-3, .col-md-6, .col-md-12').appendChild(groupErrorElement);
                    }
                    groupErrorElement.textContent = message; // Mostra a mensagem de erro para o grupo
                }
            }
            if (!errors.includes(message)) { // Evita mensagens duplicadas no array de log
                errors.push(message);
            }
            isValid = false;
        }
        
        // Limpar group-invalid-feedback antes de revalidar
        form.querySelectorAll('.group-invalid-feedback').forEach(el => el.remove());


        if (isPJ) {
            if (!validateEmail(form.querySelector('#emailEmpresa'), form.querySelector('#confirmeEmailEmpresa'), form.querySelector('#emailMismatchErrorPJ'))) {
                isValid = false; // validateEmail já lida com addClass is-invalid
            }
        } else {
            if (!validateEmail(form.querySelector('#email'), form.querySelector('#confirmeEmail'), form.querySelector('#emailMismatchError'))) {
                isValid = false;
            }
        }

        form.querySelectorAll('[required]').forEach(input => {
            let fieldHasValue = true;
            if (input.type === 'checkbox') {
                if (!input.checked) fieldHasValue = false;
            } else if (input.type === 'radio') {
                const radioGroup = form.querySelectorAll(`input[name="${input.name}"]`);
                if (!Array.from(radioGroup).some(radio => radio.checked)) {
                    // Se nenhum radio no grupo está checado E este é o primeiro do grupo a ser validado
                    // Adiciona erro apenas uma vez por grupo
                    if (!errors.some(err => err.includes(input.labels[0].textContent.replace('*','').trim() || input.name))) {
                         addError(input, `O campo "${input.labels[0].textContent.replace('*','').trim() || input.name}" é obrigatório.`);
                    }
                    fieldHasValue = false; // Marcar como inválido para o isValid geral, mas o addError específico é mais complexo para grupos
                }
            } else if (input.type === 'file') {
                if (input.files.length === 0) fieldHasValue = false;
            }
            else if (!input.value.trim()) {
                fieldHasValue = false;
            }

            if (!fieldHasValue) {
                const labelElement = input.labels && input.labels.length > 0 ? input.labels[0] : input.previousElementSibling;
                const labelText = labelElement ? labelElement.textContent.replace('*','').trim() : input.name;
                // Para radios, a mensagem pode ser genérica para o grupo, tratada acima
                if (input.type !== 'radio') { // Evita duplicar mensagem de erro para radios
                    addError(input, `O campo "${labelText}" é obrigatório.`);
                }
            }
        });

        const anoCarroInput = form.querySelector('input[name^="ano_carro"]');
        if (anoCarroInput && anoCarroInput.value) {
            const ano = parseInt(anoCarroInput.value);
            const currentYear = new Date().getFullYear();
            if (isNaN(ano) || ano < 1900 || ano > currentYear + 2) {
                addError(anoCarroInput, `Ano do veículo inválido.`);
            }
        }

        const placaInput = form.querySelector('input[name^="placa_carro"]');
        if (placaInput && placaInput.value) {
            const placaVal = (placaInput.inputmask ? placaInput.inputmask.unmaskedvalue() : placaInput.value.replace('-', '')).toUpperCase();
            if (placaVal.length < 7 || !/^[A-Z]{3}[A-Z0-9]{4}$/.test(placaVal)) {
                addError(placaInput, `Formato de placa inválido.`);
            }
        }

        if (!isPJ) {
            const cpfInput = form.querySelector('#cpf');
            if (cpfInput && cpfInput.value) {
                const cpf = cpfInput.inputmask ? cpfInput.inputmask.unmaskedvalue() : cpfInput.value.replace(/\D/g, '');
                if (cpf.length !== 11) { addError(cpfInput, 'CPF inválido.'); }
            }
            const remuneracaoInput = form.querySelector('#remuneracao');
            if (remuneracaoInput && remuneracaoInput.value && isNaN(parseFloat(remuneracaoInput.value))) {
                addError(remuneracaoInput, 'Remuneração inválida.');
            }
        } else {
            const cnpjInput = form.querySelector('#cnpj');
            if (cnpjInput && cnpjInput.value) {
                const cnpj = cnpjInput.inputmask ? cnpjInput.inputmask.unmaskedvalue() : cnpjInput.value.replace(/\D/g, '');
                if (cnpj.length !== 14) { addError(cnpjInput, 'CNPJ inválido.');}
            }
        }

        if (isValid && errors.length === 0) {
            form.submit();
        } else {
            const firstInvalidField = form.querySelector('.is-invalid');
            if (firstInvalidField) {
                 firstInvalidField.focus();
                 // Rolar para o primeiro campo inválido se estiver fora da tela
                 firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            // alert("Por favor, corrija os erros indicados no formulário."); // Desabilitado para focar no feedback visual
        }
    } // Fim validateAndSubmit

    // --- LÓGICA DE APLICAÇÃO DAS MÁSCARAS E EVENT LISTENERS ---
    if (typeof Inputmask !== "undefined") {
        // Lógica para Pessoa Física
        if (formPF) {
            console.log("Configurando Formulário PF com máscaras e listeners.");
            try {
                Inputmask({ "mask": "999.999.999-99", "placeholder": "___.___.___-__", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPF.querySelector("#cpf"));
                Inputmask({ "mask": "(99) 9999[9]-9999", "placeholder": "(__) ____[9]-____", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPF.querySelector("#telCelular"));
                Inputmask({ "mask": "(99) 9999-9999", "placeholder": "(__) ____-____", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPF.querySelector("#telComercial"));
                Inputmask({ "mask": "99999-999", "placeholder": "_____-___", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPF.querySelector("#cep"));
                Inputmask({ mask: "[A|a]{3}-*{3,4}", definitions: { 'A': { validator: "[A-Za-z]", casing: "upper" }, '*': { validator: "[A-Za-z0-9]", casing: "upper" } }, placeholder: "AAA-0X00", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPF.querySelector("#placaCarro"));
                Inputmask({ "mask": "9999", "placeholder": "AAAA", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPF.querySelector("#anoCarro"));
            } catch (e) { console.error("Erro ao aplicar máscara em formPF:", e); }

            setupCepLookup('cep', 'endereco', 'bairro', 'cidade', 'estado', 'numero');

            const emailInputPF = formPF.querySelector('#email');
            const confirmeEmailInputPF = formPF.querySelector('#confirmeEmail');
            const emailMismatchErrorPF = formPF.querySelector('#emailMismatchError');
            if (confirmeEmailInputPF && emailInputPF && emailMismatchErrorPF) {
                confirmeEmailInputPF.addEventListener('blur', () => validateEmail(emailInputPF, confirmeEmailInputPF, emailMismatchErrorPF));
                emailInputPF.addEventListener('blur', () => { if(confirmeEmailInputPF.value !== '') validateEmail(emailInputPF, confirmeEmailInputPF, emailMismatchErrorPF); });
            }

            formPF.addEventListener('submit', function(event) {
                validateAndSubmit(formPF, event, false);
            });
        }

        // Lógica para Pessoa Jurídica
        if (formPJ) {
            console.log("Configurando Formulário PJ com máscaras e listeners.");
             try {
                Inputmask({ "mask": "99.999.999/9999-99", "placeholder": "__.___.___/____-__", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPJ.querySelector("#cnpj"));
                Inputmask({ "mask": "(99) 9999-9999", "placeholder": "(__) ____-____", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPJ.querySelector("#telComercialEmpresa"));
                Inputmask({ "mask": "(99) 9999[9]-9999", "placeholder": "(__) ____[9]-____", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPJ.querySelector("#telCelularContato"));
                Inputmask({ "mask": "99999-999", "placeholder": "_____-___", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPJ.querySelector("#cepEmpresa"));
                Inputmask({ mask: "[A|a]{3}-*{3,4}", definitions: { 'A': { validator: "[A-Za-z]", casing: "upper" }, '*': { validator: "[A-Za-z0-9]", casing: "upper" } }, placeholder: "AAA-0X00", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPJ.querySelector("#placaCarroPJ"));
                Inputmask({ "mask": "9999", "placeholder": "AAAA", "showMaskOnHover": false, "showMaskOnFocus": true, "clearIncomplete": false }).mask(formPJ.querySelector("#anoCarroPJ"));
            } catch (e) { console.error("Erro ao aplicar máscara em formPJ:", e); }

            setupCepLookup('cepEmpresa', 'enderecoEmpresa', 'bairroEmpresa', 'cidadeEmpresa', 'estadoEmpresa', 'numeroEmpresa');

            const emailInputPJ = formPJ.querySelector('#emailEmpresa');
            const confirmeEmailInputPJ = formPJ.querySelector('#confirmeEmailEmpresa');
            const emailMismatchErrorPJ = formPJ.querySelector('#emailMismatchErrorPJ');
            if (confirmeEmailInputPJ && emailInputPJ && emailMismatchErrorPJ) {
                confirmeEmailInputPJ.addEventListener('blur', () => validateEmail(emailInputPJ, confirmeEmailInputPJ, emailMismatchErrorPJ));
                emailInputPJ.addEventListener('blur', () => { if(confirmeEmailInputPJ.value !== '') validateEmail(emailInputPJ, confirmeEmailInputPJ, emailMismatchErrorPJ); });
            }

            formPJ.addEventListener('submit', function(event) {
                validateAndSubmit(formPJ, event, true);
            });
        }
    } else {
        console.error("Inputmask NÃO está definido! Não foi possível aplicar máscaras.");
    }

    // ### ADICIONADO: Feedback para nome de arquivo (opcional) ###
    // Este código tenta encontrar um elemento de feedback customizado.
    // Você precisaria adicionar algo como <span class="file-name-feedback ms-2"></span> ao lado do seu input de arquivo no HTML
    // para que este código atualize esse span.
    document.querySelectorAll('input[type="file"]').forEach(fileInput => {
        fileInput.addEventListener('change', function(event) {
            const feedbackElement = this.parentElement.querySelector('.file-name-feedback'); // Procura por um elemento irmão com esta classe
            if (event.target.files.length > 0) {
                const fileName = event.target.files[0].name;
                console.log("Arquivo selecionado:", fileName);
                if (feedbackElement) {
                    feedbackElement.textContent = fileName;
                }
            } else {
                if (feedbackElement) {
                    feedbackElement.textContent = ""; // Limpa se nenhum arquivo for selecionado
                }
            }
        });
    });
    // ### FIM da adição ###
});