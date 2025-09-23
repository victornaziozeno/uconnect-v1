// calendario.js

document.addEventListener('DOMContentLoaded', function () {
    let calendarioElemento = document.getElementById('calendar');
    let eventoAtual = null;
    const API_URL = 'http://127.0.0.1:8000/api/events'; // URL do nosso backend

    // pega intervalo de hoje (00:00 até 23:59)
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
        // 🔄 NOVO: Carrega eventos da API
        events: function(fetchInfo, successCallback, failureCallback) {
            fetch(API_URL)
                .then(response => response.json())
                .then(data => {
                    // Mapeia os dados da API para o formato que o FullCalendar entende
                    const events = data.map(event => ({
                        id: event.id,
                        title: event.title,
                        start: event.start, // O backend já retorna como 'start'
                        end: event.end, // Adicionar se tiver
                        extendedProps: {
                            descricao: event.description,
                            tipo: event.tipo || 'evento-geral'
                        },
                        className: event.tipo || 'evento-geral'
                    }));
                    successCallback(events);
                    // A agenda lateral é atualizada após os eventos serem carregados
                    setTimeout(atualizarAgendaHoje, 0); 
                })
                .catch(error => {
                    console.error('Erro ao buscar eventos:', error);
                    failureCallback(error);
                });
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
            document.getElementById('editarTipoEvento').value = eventoAtual.classNames[0] || "evento-geral";

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

    // Função para atualizar o painel lateral (sem alterações)
    function atualizarAgendaHoje() {
        let eventos = calendario.getEvents().filter(evento => {
            let inicio = evento.start;
            let fim = evento.end || evento.start;
            return (inicio < amanha && fim >= hoje);
        });
        
        document.getElementById("today-date").innerText = new Date().toLocaleDateString("pt-BR", { weekday: "long", day: "2-digit", month: "long", year: "numeric" });
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

    // ➕ Adicionar evento (MODIFICADO)
    document.getElementById('formAdicionarEvento').addEventListener('submit', function (e) {
        e.preventDefault();
        let titulo = document.getElementById('tituloEvento').value;
        let data = document.getElementById('dataEvento').value;
        let horaInicio = document.getElementById('horaInicioEvento').value;
        let descricao = document.getElementById('descricaoEvento').value;
        
        let dataInicio = new Date(data + "T" + (horaInicio || "00:00") + ":00");

        const novoEvento = {
            title: titulo,
            start: dataInicio.toISOString(),
            descricao: descricao,
        };

        fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(novoEvento)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            calendario.refetchEvents(); // Recarrega os eventos do servidor
            document.getElementById('formAdicionarEvento').reset();
            bootstrap.Modal.getInstance(document.getElementById('adicionarEventoModal')).hide();
        })
        .catch(error => console.error('Erro ao adicionar evento:', error));
    });

    // ✏️ Editar evento (MODIFICADO)
    document.getElementById('formEditarEvento').addEventListener('submit', function (e) {
        e.preventDefault();
        if (eventoAtual) {
            let titulo = document.getElementById('editarTituloEvento').value;
            let data = document.getElementById('editarDataEvento').value;
            let horaInicio = document.getElementById('editarHoraInicioEvento').value;
            let descricao = document.getElementById('editarDescricaoEvento').value;
            
            let dataInicio = new Date(data + "T" + (horaInicio || "00:00") + ":00");

            const eventoAtualizado = {
                title: titulo,
                start: dataInicio.toISOString(),
                descricao: descricao
            };

            fetch(`${API_URL}/${eventoAtual.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(eventoAtualizado)
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                calendario.refetchEvents();
                bootstrap.Modal.getInstance(document.getElementById('editarEventoModal')).hide();
            })
            .catch(error => console.error('Erro ao editar evento:', error));
        }
    });

    // ❌ Excluir evento (MODIFICADO)
    document.getElementById('btnExcluirEvento').addEventListener('click', function () {
        if (eventoAtual && confirm('Tem certeza que deseja excluir este evento?')) {
            fetch(`${API_URL}/${eventoAtual.id}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                calendario.refetchEvents();
                bootstrap.Modal.getInstance(document.getElementById('editarEventoModal')).hide();
            })
            .catch(error => console.error('Erro ao excluir evento:', error));
        }
    });
});