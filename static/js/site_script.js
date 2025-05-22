// static/js/site_script.js
document.addEventListener('DOMContentLoaded', function () {
    const mainNavbar = document.getElementById('mainNavbar');
    const mainLogoInNavItems = document.querySelector('.nav-item-logo-main #mainLogo'); // Logo dentro da lista de itens
    const scrolledLogoContainer = document.querySelector('.navbar-cla .logo-container-nav'); // Logo lateral fixa
    
    // Alturas originais e scrolladas podem ser mantidas ou ajustadas no CSS diretamente
    // const originalLogoHeight = 60;
    // const scrolledLogoHeight = 45;

    function handleNavbarState() {
        if (!mainNavbar) return;

        const isScrolled = window.scrollY > 50;
        mainNavbar.classList.toggle('navbar-scrolled', isScrolled);

        // A altura da logo agora é controlada primariamente pelo CSS
        // if (mainLogoInNavItems) {
        //     mainLogoInNavItems.style.height = (isScrolled ? scrolledLogoHeight : originalLogoHeight) + 'px';
        // }

        const navbarToggler = mainNavbar.querySelector('.navbar-toggler');
        const isTogglerVisible = navbarToggler ? window.getComputedStyle(navbarToggler).display !== 'none' : false;
        const isMenuExpanded = navbarToggler ? navbarToggler.getAttribute('aria-expanded') === 'true' : false;

        if (isTogglerVisible) { // Estamos em tela pequena (menu hambúrguer é visível)
            if (scrolledLogoContainer) scrolledLogoContainer.style.display = 'block'; // Mostra sempre a logo lateral pequena
            // A logo central (mainLogoInNavItems) já está dentro do menu colapsável, o Bootstrap cuida de mostrá-la/escondê-la com o menu.
            // O CSS já esconde .nav-item-logo-main em @media (max-width: 991.98px) se você quiser que apenas a lateral apareça.
            // Ou, se a logo central deve aparecer no menu dropdown:
            // O CSS @media query para .nav-item-logo-main com order: -1 já a posiciona.
        } else { // Tela grande
            if (scrolledLogoContainer) scrolledLogoContainer.style.display = 'none'; // Esconde a logo lateral
            // A logo central (mainLogoInNavItems) está sempre visível em telas grandes.
        }
    }
    
    window.addEventListener('scroll', handleNavbarState);
    
    const navbarTogglerButton = mainNavbar ? mainNavbar.querySelector('.navbar-toggler') : null;
    if (navbarTogglerButton) {
        // Usar eventos do Bootstrap para o collapse é mais confiável
        const navCollapseElement = document.getElementById('navbarNavDropdown');
        if (navCollapseElement) {
            navCollapseElement.addEventListener('show.bs.collapse', function () {
                handleNavbarState(); // Reavalia o estado da navbar quando o menu começa a abrir
            });
            navCollapseElement.addEventListener('hide.bs.collapse', function () {
                handleNavbarState(); // Reavalia o estado da navbar quando o menu começa a fechar
            });
        }
    }
    
    handleNavbarState(); // Chama no carregamento para definir o estado inicial

    // Rodapé
    const currentYearFooter = document.getElementById("currentYearFooter");
    if (currentYearFooter) {
        currentYearFooter.textContent = new Date().getFullYear();
    }

    // Tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // ### ADICIONADO: Lógica para Formulário de Contato via WhatsApp ###
    const whatsappForm = document.getElementById('whatsappForm');
    const sendWhatsappButton = document.getElementById('sendWhatsappButton');

    if (whatsappForm && sendWhatsappButton) {
        sendWhatsappButton.addEventListener('click', function() {
            const name = document.getElementById('whatsappName').value.trim();
            const subject = document.getElementById('whatsappSubject').value.trim();
            const message = document.getElementById('whatsappMessage').value.trim();
            
            // Seu número de WhatsApp no formato internacional (sem o '+' ou '00', apenas números)
            // Substitua pelo seu número real
            const phoneNumber = "5511963213660"; // Exemplo: 55 (Brasil) 11 (DDD SP) XXXXXXXXX (Número)

            let fullMessage = "";

            if (name) {
                fullMessage += `Olá, meu nome é ${name}.`;
            } else {
                // Validar se o nome é obrigatório
                alert("Por favor, informe seu nome.");
                document.getElementById('whatsappName').focus();
                return;
            }

            if (subject) {
                fullMessage += `\nAssunto: ${subject}`;
            }
            
            if (message) {
                fullMessage += `\n\nMensagem: \n${message}`;
            } else {
                // Validar se a mensagem é obrigatória
                alert("Por favor, escreva sua mensagem.");
                document.getElementById('whatsappMessage').focus();
                return;
            }

            // Codificar a mensagem para URL
            const encodedMessage = encodeURIComponent(fullMessage);
            
            // Criar o link do WhatsApp
            const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodedMessage}`;
            
            // Abrir o link em uma nova aba
            window.open(whatsappUrl, '_blank');
        });
    }
});