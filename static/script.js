// static/script.js
document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM Carregado. Inputmask DEVE estar definido.");

    const formPF = document.getElementById('cadastroFormPF');
    const formPJ = document.getElementById('cadastroFormPJ');

    // --- FUNÇÕES AUXILIARES ---
    function validateEmail(emailInput, confirmeEmailInput, errorDisplayElement) {
        if (!emailInput || !confirmeEmailInput || !errorDisplayElement) {
            // Se algum dos elementos não existir na página atual, não faz nada ou retorna true
            // console.warn("Elementos de validação de email ausentes:", emailInput, confirmeEmailInput, errorDisplayElement);
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
                    // alert('CEP inválido. Deve conter 8 dígitos.'); // Pode ser muito intrusivo
                    cepInput.classList.add('is-invalid');
                } else if (cepVal.length === 8 && document.getElementById(logradouroFieldId) && document.getElementById(logradouroFieldId).value === '') {
                    // alert('CEP não encontrado ou dados de endereço indisponíveis.');
                    cepInput.classList.add('is-invalid');
                } else if (cepVal.length === 8 || cepVal.length === 0) { // Válido ou vazio
                    cepInput.classList.remove('is-invalid');
                }
            });
        }
    }

    function validateAndSubmit(form, event, isPJ = false) {
        event.preventDefault();
        let isValid = true;
        const errors = []; // Array para armazenar mensagens de erro, se precisar exibi-las de outra forma

        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        form.querySelectorAll('.custom-invalid-feedback').forEach(el => el.remove());

        function addError(field, message) {
            if (field) {
                field.classList.add('is-invalid');
                let feedback = field.parentElement.querySelector('.custom-invalid-feedback');
                if (!feedback) {
                    feedback = document.createElement('div');
                    feedback.className = 'custom-invalid-feedback';
                    field.parentElement.appendChild(feedback);
                }
                feedback.textContent = message;
            }
            errors.push(message); // Adiciona ao array de erros
            isValid = false;
        }
        
        // Revalida emails no submit
        if (isPJ) {
            if (!validateEmail(form.querySelector('#emailEmpresa'), form.querySelector('#confirmeEmailEmpresa'), form.querySelector('#emailMismatchErrorPJ'))) {
                // addError já é chamado dentro de validateEmail se houver erro e o elemento de erro existir
            }
        } else {
            if (!validateEmail(form.querySelector('#email'), form.querySelector('#confirmeEmail'), form.querySelector('#emailMismatchError'))) {
                // addError já é chamado
            }
        }

        form.querySelectorAll('[required]').forEach(input => {
            if (!input.value.trim()) {
                const labelElement = input.labels && input.labels.length > 0 ? input.labels[0] : input.previousElementSibling;
                const labelText = labelElement ? labelElement.textContent.replace('*','').trim() : input.name;
                addError(input, `O campo "${labelText}" é obrigatório.`);
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

        if (!isPJ) { // Validações específicas PF
            const cpfInput = form.querySelector('#cpf');
            if (cpfInput && cpfInput.value) {
                const cpf = cpfInput.inputmask ? cpfInput.inputmask.unmaskedvalue() : cpfInput.value.replace(/\D/g, '');
                if (cpf.length !== 11) { addError(cpfInput, 'CPF inválido.'); }
            }
            const remuneracaoInput = form.querySelector('#remuneracao');
            if (remuneracaoInput && remuneracaoInput.value && isNaN(parseFloat(remuneracaoInput.value))) {
                addError(remuneracaoInput, 'Remuneração inválida.');
            }
        } else { // Validações específicas PJ
            const cnpjInput = form.querySelector('#cnpj');
            if (cnpjInput && cnpjInput.value) {
                const cnpj = cnpjInput.inputmask ? cnpjInput.inputmask.unmaskedvalue() : cnpjInput.value.replace(/\D/g, '');
                if (cnpj.length !== 14) { addError(cnpjInput, 'CNPJ inválido.');}
            }
        }

        if (errors.length === 0) { // Verifica se o array de erros está vazio
            form.submit();
        } else {
            const firstInvalidField = form.querySelector('.is-invalid');
            if (firstInvalidField) firstInvalidField.focus();
            // alert("Por favor, corrija os erros indicados no formulário.");
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
});