import { useState, useEffect } from "react";
import Fullcalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import listPlugin from "@fullcalendar/list";
import ptBr from "@fullcalendar/core/locales/pt-br";
import { Tooltip, Modal } from "bootstrap";

import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "../styles/calendario.css";

// URL da API
const API_URL = "http://localhost:8000";

// --- util: data local yyyy-mm-dd (sem UTC) ---
const dataLocalYYYYMMDD = (d = new Date()) => {
  const dt = d instanceof Date ? d : new Date(d);
  const y = dt.getFullYear();
  const m = String(dt.getMonth() + 1).padStart(2, "0");
  const day = String(dt.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
};

// Função para formatar YYYY-MM-DD para DD/MM/YYYY
const formatarDataBR = (dataString) => {
  const [ano, mes, dia] = dataString.split("-");
  return `${dia}/${mes}/${ano}`;
};

function Calendario() {
  const HOJE = dataLocalYYYYMMDD();

  // Eventos
  const [eventos, setEventos] = useState([]);

  // Agenda do dia
  const [agenda, setAgenda] = useState([]);
  useEffect(() => {
    setAgenda(eventos.filter((ev) => ev.date === HOJE));
  }, [eventos, HOJE]);

  // Buscar eventos no backend
  useEffect(() => {
    const fetchEventos = async () => {
      try {
        const resp = await fetch(`${API_URL}/events`);
        if (!resp.ok) throw new Error("Erro ao buscar eventos");
        const data = await resp.json();
        
        // Converter eventos do backend
        const eventosConvertidos = data.map(ev => ({
          id: ev.id,
          title: ev.title,
          date: ev.eventDate,
          timestamp: ev.timestamp,
          startTime: ev.startTime ? ev.startTime.substring(0, 5) : "",
          endTime: ev.endTime ? ev.endTime.substring(0, 5) : "",
          hora: ev.startTime 
            ? (ev.endTime 
                ? `${ev.startTime.substring(0, 5)} - ${ev.endTime.substring(0, 5)}`
                : ev.startTime.substring(0, 5))
            : "",
          description: ev.description || "",
          descricao: ev.description || "",
          local: ev.academicGroupId || "",
          academicGroupId: ev.academicGroupId || "",
        }));
        
        console.log("Eventos convertidos:", eventosConvertidos);
        setEventos(eventosConvertidos);
      } catch (err) {
        console.error("Erro ao buscar eventos:", err);
      }
    };
    fetchEventos();
  }, []);

  // Formulário do modal
  const [formulario, setFormulario] = useState({
    id: null,
    titulo: "",
    data: "",
    inicio: "",
    fim: "",
    descricao: "",
    local: "",
  });

  const [modoEdicao, setModoEdicao] = useState(false);

  const resetarFormulario = () => {
    setFormulario({
      id: null,
      titulo: "",
      data: "",
      inicio: "",
      fim: "",
      descricao: "",
      local: "",
    });
    setModoEdicao(false);
  };

  // Criar
  const adicionarEvento = async () => {
    if (!formulario.titulo || !formulario.data) {
      alert("Preencha pelo menos o título e a data!");
      return;
    }

    const token = localStorage.getItem("accessToken");
    if (!token) {
      alert("Sessão expirada ou usuário não logado. Faça o login novamente.");
      return;
    }

    const novoEvento = {
      title: formulario.titulo,
      date: formulario.data,
      hora: formulario.inicio
        ? formulario.fim
          ? `${formulario.inicio} - ${formulario.fim}`
          : formulario.inicio
        : null,
      description: formulario.descricao,
      local: formulario.local,
    };

    console.log("Enviando para a API:", novoEvento);

    try {
      const resp = await fetch(`${API_URL}/events`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(novoEvento),
      });

      if (!resp.ok) {
        const errorData = await resp
          .json()
          .catch(() => ({ detail: "Erro desconhecido, resposta não é JSON." }));
        throw new Error(errorData.detail || `Erro ${resp.status}`);
      }

      const saved = await resp.json();
      console.log("Evento criado:", saved);
      
      // Converter evento recebido do backend
      const eventoConvertido = {
        id: saved.id,
        title: saved.title,
        date: saved.eventDate,
        timestamp: saved.timestamp,
        startTime: saved.startTime ? saved.startTime.substring(0, 5) : "",
        endTime: saved.endTime ? saved.endTime.substring(0, 5) : "",
        hora: saved.startTime 
          ? (saved.endTime 
              ? `${saved.startTime.substring(0, 5)} - ${saved.endTime.substring(0, 5)}`
              : saved.startTime.substring(0, 5))
          : "",
        description: saved.description || "",
        descricao: saved.description || "",
        local: saved.academicGroupId || "",
        academicGroupId: saved.academicGroupId || "",
      };
      
      setEventos((prev) => [...prev, eventoConvertido]);
      resetarFormulario();
    } catch (err) {
      console.error("Erro ao adicionar evento:", err);
      alert(`Não foi possível criar o evento: ${err.message}`);
    }
  };

  // Editar
  const salvarEdicao = async () => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
      alert("Sessão expirada ou usuário não logado. Faça o login novamente.");
      return;
    }

    const atualizado = {
      title: formulario.titulo,
      date: formulario.data,
      hora: formulario.inicio
        ? formulario.fim
          ? `${formulario.inicio} - ${formulario.fim}`
          : formulario.inicio
        : "",
      description: formulario.descricao,
      local: formulario.local,
    };

    console.log("Enviando atualização:", atualizado);

    try {
      const resp = await fetch(`${API_URL}/events/${formulario.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(atualizado),
      });

      if (!resp.ok) {
        const errorData = await resp
          .json()
          .catch(() => ({ detail: "Erro desconhecido." }));
        throw new Error(errorData.detail || `Erro ${resp.status}`);
      }

      const saved = await resp.json();
      console.log("Evento atualizado:", saved);

      // Converter evento recebido do backend
      const eventoConvertido = {
        id: saved.id,
        title: saved.title,
        date: saved.eventDate,
        timestamp: saved.timestamp,
        startTime: saved.startTime ? saved.startTime.substring(0, 5) : "",
        endTime: saved.endTime ? saved.endTime.substring(0, 5) : "",
        hora: saved.startTime 
          ? (saved.endTime 
              ? `${saved.startTime.substring(0, 5)} - ${saved.endTime.substring(0, 5)}`
              : saved.startTime.substring(0, 5))
          : "",
        description: saved.description || "",
        descricao: saved.description || "",
        local: saved.academicGroupId || "",
        academicGroupId: saved.academicGroupId || "",
      };

      setEventos((prev) =>
        prev.map((ev) => (ev.id === formulario.id ? eventoConvertido : ev))
      );
      resetarFormulario();
    } catch (err) {
      console.error("Erro ao editar evento:", err);
      alert(`Não foi possível editar o evento: ${err.message}`);
    }
  };

  // Excluir
  const excluirEvento = async () => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
      alert("Sessão expirada ou usuário não logado. Faça o login novamente.");
      return;
    }

    if (window.confirm("Tem certeza que deseja excluir este evento?")) {
      try {
        const resp = await fetch(`${API_URL}/events/${formulario.id}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!resp.ok) {
          const errorData = await resp
            .json()
            .catch(() => ({ detail: "Erro desconhecido ao excluir." }));
          throw new Error(errorData.detail || `Erro ${resp.status}`);
        }

        setEventos((prev) => prev.filter((ev) => ev.id !== formulario.id));
        resetarFormulario();
      } catch (err) {
        console.error("Erro ao excluir evento:", err);
        alert(`Não foi possível excluir o evento: ${err.message}`);
      }
    }
  };

  // Tooltip
  const buildTooltipHtml = (ev) => {
    return `
      <b>${ev.title}</b><br/>
      ${ev.hora ? "Horário: " + ev.hora + "<br/>" : ""}
      ${ev.local ? "Local: " + ev.local + "<br/>" : ""}
      ${ev.descricao ? "Descrição: " + ev.descricao : ""}
    `;
  };

  return (
    <div className="container mt-4">
      <div className="row">
        {/* Calendário */}
        <div className="col-md-8">
          <div className="card shadow-lg">
            <div className="card-body">
              <div className="d-flex justify-content-between mb-3">
                <h4>📅 Calendário Acadêmico - UCONNECT</h4>
                <button
                  className="btn btn-success"
                  data-bs-toggle="modal"
                  data-bs-target="#modalEvento"
                  onClick={() => resetarFormulario()}
                >
                  + Adicionar Evento
                </button>
              </div>

              <Fullcalendar
                plugins={[
                  dayGridPlugin,
                  timeGridPlugin,
                  interactionPlugin,
                  listPlugin,
                ]}
                initialView="dayGridMonth"
                locale={ptBr}
                height="600px"
                headerToolbar={{
                  left: "prev,next today",
                  center: "title",
                  right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
                }}
                views={{ dayGridMonth: { displayEventTime: false } }}
                events={eventos
                  .map((ev) => {
                    console.log("Processando evento:", ev);

                    if (!ev.timestamp) {
                      console.error("Evento sem timestamp:", ev);
                      return null;
                    }

                    const startDateTime = new Date(ev.timestamp);

                    if (isNaN(startDateTime.getTime())) {
                      console.error("Timestamp inválido:", ev);
                      return null;
                    }

                    const dateStr = ev.date;
                    const timeStr = ev.startTime || "00:00";

                    return {
                      id: ev.id?.toString(),
                      title: ev.title,
                      start: `${dateStr}T${timeStr}`,
                      allDay: false,
                      backgroundColor: "#1E90FF",
                      textColor: "#fff",
                      borderColor: "#1E90FF",
                      display: "block",
                      extendedProps: {
                        startTime: ev.startTime,
                        endTime: ev.endTime,
                        hora: ev.hora,
                        description: ev.description,
                        descricao: ev.descricao,
                        local: ev.local,
                        academicGroupId: ev.academicGroupId,
                      },
                    };
                  })
                  .filter((ev) => ev !== null)}
                eventMouseEnter={(info) => {
                  const props = info.event.extendedProps;
                  const current = {
                    title: info.event.title,
                    hora: props.hora,
                    local: props.local,
                    descricao: props.descricao,
                  };
                  const html = buildTooltipHtml(current);
                  const old = Tooltip.getInstance(info.el);
                  if (old) old.dispose();
                  const tip = new Tooltip(info.el, {
                    title: html,
                    placement: "top",
                    trigger: "manual",
                    container: "body",
                    html: true,
                  });
                  tip.show();
                }}
                eventMouseLeave={(info) => {
                  const tip = Tooltip.getInstance(info.el);
                  if (tip) tip.dispose();
                }}
                eventClick={(info) => {
                  const ev = info.event;
                  const props = ev.extendedProps;

                  console.log("Evento clicado:", {
                    id: ev.id,
                    startTime: props.startTime,
                    endTime: props.endTime,
                  });

                  setFormulario({
                    id: parseInt(ev.id, 10),
                    titulo: ev.title,
                    data: ev.startStr.split("T")[0],
                    inicio: props.startTime || "",
                    fim: props.endTime || "",
                    descricao: props.descricao || "",
                    local: props.local || "",
                  });
                  setModoEdicao(true);
                  const modalEl = document.getElementById("modalEvento");
                  const modal = Modal.getOrCreateInstance(modalEl);
                  modal.show();
                }}
              />
            </div>
          </div>
        </div>

        {/* Agenda do Dia */}
        <div className="col-md-4">
          <div className="agenda-card">
           <div className="agenda-header">
            Agenda do Dia ({formatarDataBR(HOJE)})
          </div>
            <div className="agenda-list">
              {agenda.length > 0 ? (
                agenda.map((ev) => (
                  <div key={ev.id} className="agenda-item">
                    <strong>{ev.title}</strong>
                    {ev.hora && <small className="d-block">{ev.hora}</small>}
                    {ev.local && (
                      <small className="d-block text-muted">📍 {ev.local}</small>
                    )}
                    {ev.descricao && (
                      <p className="text-muted mb-0">{ev.descricao}</p>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-muted mb-0">Nenhum evento para hoje.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      <div
        className="modal fade"
        id="modalEvento"
        tabIndex="-1"
        aria-labelledby="modalEventoLabel"
        aria-hidden="true"
      >
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title" id="modalEventoLabel">
                {modoEdicao ? "Editar Evento" : "Adicionar Evento"}
              </h5>
              <button
                type="button"
                className="btn-close"
                data-bs-dismiss="modal"
                aria-label="Fechar"
                onClick={resetarFormulario}
              ></button>
            </div>
            <div className="modal-body">
              {/* Formulário */}
              <div className="mb-3">
                <label className="form-label">Título</label>
                <input
                  type="text"
                  className="form-control"
                  value={formulario.titulo}
                  onChange={(e) =>
                    setFormulario({ ...formulario, titulo: e.target.value })
                  }
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Data</label>
                <input
                  type="date"
                  className="form-control"
                  value={formulario.data}
                  onChange={(e) =>
                    setFormulario({ ...formulario, data: e.target.value })
                  }
                />
              </div>
              <div className="row">
                <div className="col">
                  <label className="form-label">Hora de início</label>
                  <input
                    type="time"
                    className="form-control"
                    value={formulario.inicio}
                    onChange={(e) =>
                      setFormulario({ ...formulario, inicio: e.target.value })
                    }
                  />
                </div>
                <div className="col">
                  <label className="form-label">Hora de término</label>
                  <input
                    type="time"
                    className="form-control"
                    value={formulario.fim}
                    onChange={(e) =>
                      setFormulario({ ...formulario, fim: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="mb-3">
                <label className="form-label">Local</label>
                <input
                  type="text"
                  className="form-control"
                  value={formulario.local}
                  onChange={(e) =>
                    setFormulario({ ...formulario, local: e.target.value })
                  }
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Descrição</label>
                <textarea
                  className="form-control"
                  rows="2"
                  value={formulario.descricao}
                  onChange={(e) =>
                    setFormulario({ ...formulario, descricao: e.target.value })
                  }
                />
              </div>
            </div>
            <div className="modal-footer">
              {modoEdicao && (
                <button
                  type="button"
                  className="btn btn-danger me-auto"
                  onClick={excluirEvento}
                  data-bs-dismiss="modal"
                >
                  Excluir
                </button>
              )}
              <button
                type="button"
                className="btn btn-secondary"
                data-bs-dismiss="modal"
                onClick={resetarFormulario}
              >
                Cancelar
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={modoEdicao ? salvarEdicao : adicionarEvento}
                data-bs-dismiss="modal"
              >
                {modoEdicao ? "Salvar Alterações" : "Adicionar"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Calendario;