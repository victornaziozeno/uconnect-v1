document.addEventListener('DOMContentLoaded', function () {
    let calendarioElemento = document.getElementById('calendar');
    
    let eventoAtual = null;

    async function buscarEventos() {
        try {
            const response = await fetch('http://127.0.0.1:8000/events/'); // URL da sua API
            if (!response.ok) {
                throw new Error('Falha ao buscar eventos da API');
            }
            const eventosDaApi = await response.json();

            // O FullCalendar espera 'start', então adaptamos os nomes
            return eventosDaApi.map(evento => ({
                id: evento.id,
                title: evento.title,
                start: evento.timestamp,
                // <-- CORREÇÃO 2: Adiciona uma classe ao evento.
                // Isso evita o erro 'classNames[0]' ao clicar para editar.
                className: 'evento-geral', 
                extendedProps: {
                    descricao: evento.description,
                    // Adicionado para consistência, usado no popover e na edição
                    tipo: 'evento-geral' 
                }
            }));
        } catch (error) {
            console.error("Erro:", error);
            alert("Não foi possível carregar os eventos do calendário.");
            return []; // Retorna vazio em caso de erro
        }
    }
    
    // Pega intervalo de hoje (00:00 até 23:59)

    let hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    let amanha = new Date(hoje);
    amanha.setDate(hoje.getDate() + 1);

    let calendario = new FullCalendar.Calendar(calendarioElemento, {
        initialView: 'dayGridMonth',
        locale: 'pt-br',
        themeSystem: 'bootstrap5',
        editable: true,
        height: 550,
        allDaySlot: false,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        buttonText: {
            today: 'Hoje',
            month: 'Mês',
            week: 'Semana',
            day: 'Dia',
            list: 'Lista'
        },
        events: buscarEventos,
        
        eventsSet: function() {
            atualizarAgendaHoje();
        },
       
        eventClick: function (detalhes) {
            eventoAtual = detalhes.event;
            let inicio = eventoAtual.start;
            let fim = eventoAtual.end;

            document.getElementById('editarTituloEvento').value = eventoAtual.title;
            document.getElementById('editarDataEvento').value = inicio.toISOString().slice(0, 10);
            document.getElementById('editarHoraInicioEvento').value = inicio.toTimeString().slice(0, 5);
            document.getElementById('editarHoraFimEvento').value = fim ? fim.toTimeString().slice(0, 5) : "";
            document.getElementById('editarDescricaoEvento').value = eventoAtual.extendedProps.descricao || "";
            document.getElementById('editarTipoEvento').value = eventoAtual.extendedProps.tipo || "evento-geral";

            let modal = new bootstrap.Modal(document.getElementById('editarEventoModal'));
            modal.show();
        },
        eventDidMount: function (detalhes) {
            let inicio = detalhes.event.start ? detalhes.event.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "";
            let fim = detalhes.event.end ? detalhes.event.end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "";
            let tipo = detalhes.event.extendedProps.tipo || "Não informado";

            new bootstrap.Popover(detalhes.el, {
                title: detalhes.event.title,
                content: `
                  <b>Descrição:</b> ${detalhes.event.extendedProps.descricao || 'Sem descrição'}<br>
                  <b>Horário:</b> ${inicio} - ${fim || "..."}<br>
                  <b>Tipo:</b> ${tipo}
                `,
                placement: "top",
                trigger: "hover",
                html: true,
                container: "body"
            });
        }
    });

    calendario.render();

    // <-- CORREÇÃO 1: A chamada inicial para 'atualizarAgendaHoje()' foi removida daqui 
    // para evitar a "race condition". Agora ela é controlada pelo 'eventsSet'.

    // 🔄 Atualizar painel lateral
    function atualizarAgendaHoje() {
        let eventos = calendario.getEvents().filter(evento => {
            let inicio = evento.start;
            let fim = evento.end || evento.start;
            return (inicio < amanha && fim >= hoje); // evento ocupa parte do dia
        });

        document.getElementById("today-date").innerText =
            new Date().toLocaleDateString("pt-BR", { weekday: "long", day: "2-digit", month: "long", year: "numeric" });

        let listaEventos = document.getElementById("eventList");
        listaEventos.innerHTML = "";

        if (eventos.length === 0) {
            listaEventos.innerHTML = "<li class='text-muted'>Sem eventos hoje</li>";
            return;
        }

        eventos.sort((a, b) => a.start - b.start).forEach(evento => {
            let itemLista = document.createElement("li");
            itemLista.className = "mb-3";
            itemLista.innerHTML = `<b>${evento.title}</b><br>
              ⏰ ${evento.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} 
              - ${evento.end ? evento.end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "..."} 
              <br><small>${evento.extendedProps.descricao || ""}</small>`;
            listaEventos.appendChild(itemLista);
        });
    }

    // ➕ Adicionar evento
  document.getElementById('formAdicionarEvento').addEventListener('submit', async function (e) {
    e.preventDefault();

    // --- INÍCIO DA MODIFICAÇÃO ---

    // 1. Pega o token de acesso do localStorage
    const token = localStorage.getItem('accessToken');

    // 2. Verifica se o token existe. Se não, o usuário não está logado.
    if (!token) {
        alert("Você precisa estar logado para adicionar um evento.");
        // Opcional: redirecionar para a página de login
        // window.location.href = '/login.html'; 
        return;
    }

    // --- FIM DA MODIFICAÇÃO ---

    const titulo = document.getElementById('tituloEvento').value;
    const data = document.getElementById('dataEvento').value;
    const horaInicio = document.getElementById('horaInicioEvento').value;
    const descricao = document.getElementById('descricaoEvento').value;
    const tipoEvento = document.getElementById('tipoEvento').value;
    const dataTimestamp = new Date(data + "T" + (horaInicio || "00:00") + ":00").toISOString();

    const novoEvento = {
        title: titulo,
        description: descricao,
        timestamp: dataTimestamp,
        eventType: tipoEvento,
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/events/', {
            method: 'POST',
            // --- INÍCIO DA MODIFICAÇÃO ---
            headers: {
                'Content-Type': 'application/json',
                // 3. Adiciona o cabeçalho de autorização com o token
                'Authorization': `Bearer ${token}`
            },
            // --- FIM DA MODIFICAÇÃO ---
            body: JSON.stringify(novoEvento),
        });

        if (!response.ok) {
            // Verifica se o erro é especificamente de autenticação
            if (response.status === 401) {
                throw new Error('Sua sessão expirou. Por favor, faça login novamente.');
            }
            throw new Error('Falha ao salvar o evento.');
        }

        document.getElementById('formAdicionarEvento').reset();
        bootstrap.Modal.getInstance(document.getElementById('adicionarEventoModal')).hide();
        calendario.refetchEvents();

    } catch (error) {
        console.error("Erro ao adicionar evento:", error);
        // Exibe a mensagem de erro específica (ex: sessão expirada)
        alert(error.message);
    }
    });

    // ✏️ Editar evento
    document.getElementById('formEditarEvento').addEventListener('submit', function (e) {
        e.preventDefault();
        if (eventoAtual) {
            let titulo = document.getElementById('editarTituloEvento').value;
            let data = document.getElementById('editarDataEvento').value;
            let horaInicio = document.getElementById('editarHoraInicioEvento').value;
            let horaFim = document.getElementById('editarHoraFimEvento').value;
            let descricao = document.getElementById('editarDescricaoEvento').value;
            let tipo = document.getElementById('editarTipoEvento').value;

            let dataInicio = new Date(data + "T" + (horaInicio || "00:00") + ":00");
            let dataFim = horaFim ? new Date(data + "T" + horaFim + ":00") : new Date(dataInicio.getTime() + 30 * 60000);

            eventoAtual.setProp('title', titulo);
            eventoAtual.setStart(dataInicio);
            eventoAtual.setEnd(dataFim);
            eventoAtual.setExtendedProp('descricao', descricao);
            eventoAtual.setExtendedProp('tipo', tipo);
            eventoAtual.setProp('classNames', [tipo]);

            bootstrap.Modal.getInstance(document.getElementById('editarEventoModal')).hide();
        }
    });

    // ❌ Excluir evento
    document.getElementById('btnExcluirEvento').addEventListener('click', function () {
        if (eventoAtual) {
            eventoAtual.remove();
            bootstrap.Modal.getInstance(document.getElementById('editarEventoModal')).hide();
        }
    });
});