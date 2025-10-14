import { useState, useEffect } from "react";
import Navbar from "./navBar";
import MenuLateral from "./MenuLateral";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import "../styles/chat.css";

// Ícones
import iconeUsuario from "../assets/icone_usuario_chat.svg";
import iconeTodos from "../assets/Todos.svg";
import iconeAtendimento from "../assets/Atendimento.svg";
import iconeProfessores from "../assets/Professor.svg";
import iconeAlunos from "../assets/alunos.svg";
import iconeEnviar from "../assets/Paper_Plane.svg";

const API_URL = "http://localhost:8000"; // mesmo padrão do calendário

function Chat() {
  const [conversas, setConversas] = useState([]);
  const [mensagens, setMensagens] = useState([]);
  const [conversaAtiva, setConversaAtiva] = useState(null);
  const [filtroAtivo, setFiltroAtivo] = useState("Todos");
  const [novaMensagem, setNovaMensagem] = useState("");

  // 🔹 Busca conversas do usuário (simula GET /chats)
  useEffect(() => {
    const fetchConversas = async () => {
      try {
        const token = localStorage.getItem("accessToken");
        if (!token) return console.warn("Token ausente — login necessário.");

        const resp = await fetch(`${API_URL}/chats`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!resp.ok) throw new Error("Erro ao carregar conversas");

        const data = await resp.json();
        setConversas(data);
      } catch (err) {
        console.error("Erro ao buscar conversas:", err);
      }
    };

    fetchConversas();
  }, []);

  // 🔹 Busca mensagens da conversa ativa (simula GET /chats/:id/messages)
  useEffect(() => {
    const fetchMensagens = async () => {
      if (!conversaAtiva) return;
      try {
        const token = localStorage.getItem("accessToken");
        const resp = await fetch(`${API_URL}/chats/${conversaAtiva}/messages`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!resp.ok) throw new Error("Erro ao carregar mensagens");

        const data = await resp.json();
        setMensagens(data);
      } catch (err) {
        console.error("Erro ao buscar mensagens:", err);
      }
    };

    fetchMensagens();
  }, [conversaAtiva]);

  // 🔹 Enviar mensagem (simula POST /messages)
  const enviarMensagem = async () => {
    if (novaMensagem.trim() === "" || !conversaAtiva) return;

    const token = localStorage.getItem("accessToken");
    const msg = {
      content: novaMensagem,
      conversationId: conversaAtiva,
    };

    try {
      const resp = await fetch(`${API_URL}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(msg),
      });

      if (!resp.ok) throw new Error("Erro ao enviar mensagem");

      const nova = await resp.json();
      setMensagens((prev) => [...prev, nova]);
      setNovaMensagem("");
    } catch (err) {
      console.error("Erro ao enviar mensagem:", err);

      // fallback local (mock)
      setMensagens((prev) => [
        ...prev,
        {
          autor: "Você",
          conteudo: novaMensagem,
          hora: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          tipo: "enviada",
        },
      ]);
      setNovaMensagem("");
    }
  };

  return (
    <>
      <Navbar />

      <div className="chat-layout d-flex">
        <MenuLateral />

        <div className="container-fluid mt-4">
          <div className="row">
            {/* 🔹 Lista de conversas */}
            <div className="col-md-4">
              <div className="card shadow-sm">
                <div className="card-body p-0">
                  {/* Barra de pesquisa */}
                  <div className="p-3 border-bottom">
                    <div className="input-group">
                      <span className="input-group-text bg-light border-end-0">
                        <i className="bi bi-search"></i>
                      </span>
                      <input
                        type="text"
                        className="form-control border-start-0"
                        placeholder="Pesquisar"
                      />
                    </div>
                  </div>

                  {/* Filtros */}
                  <div className="d-flex justify-content-around text-center py-3 border-bottom bg-light">
                    {[
                      { nome: "Todos", icon: iconeTodos },
                      { nome: "Atendimento", icon: iconeAtendimento },
                      { nome: "Professores", icon: iconeProfessores },
                      { nome: "Alunos", icon: iconeAlunos },
                    ].map((filtro, index) => (
                      <div
                        key={index}
                        className="filtro-item d-flex flex-column align-items-center"
                        onClick={() => setFiltroAtivo(filtro.nome)}
                        style={{ cursor: "pointer" }}
                      >
                        <div
                          className={`filtro-icone rounded-circle d-flex align-items-center justify-content-center mb-1 ${
                            filtroAtivo === filtro.nome ? "ativo" : ""
                          }`}
                        >
                          <img src={filtro.icon} alt={filtro.nome} width="28" height="28" />
                        </div>
                        <div
                          className={`small fw-semibold ${
                            filtroAtivo === filtro.nome ? "text-primary" : "text-secondary"
                          }`}
                        >
                          {filtro.nome}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Conversas */}
                  <div className="list-group list-group-flush">
                    {(conversas.length ? conversas : [
                      // Mock local
                      { id: 1, nome: "Atendimento UCB", ultimaMensagem: "Olá! Em que posso ajudar?", hora: "18:27" },
                      { id: 2, nome: "Professor(a) Paulo Lemes", ultimaMensagem: "Entendi, obrigado!", hora: "18:20" },
                    ]).map((chat) => (
                      <div
                        key={chat.id}
                        className={`list-group-item list-group-item-action d-flex align-items-start ${
                          conversaAtiva === chat.id ? "bg-light" : ""
                        }`}
                        onClick={() => setConversaAtiva(chat.id)}
                      >
                        <img
                          src={iconeUsuario}
                          alt="Ícone do usuário"
                          width="42"
                          height="42"
                          className="me-3"
                        />
                        <div className="flex-grow-1">
                          <div className="d-flex justify-content-between">
                            <strong>{chat.nome || chat.title}</strong>
                            <small>{chat.hora || "--:--"}</small>
                          </div>
                          <div className="text-muted small">
                            {chat.ultimaMensagem || "Nova conversa"}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* 🔹 Área do chat */}
            <div className="col-md-8">
              <div className="card shadow-sm chat-card">
                <div className="card-header bg-light d-flex align-items-center">
                  {conversaAtiva ? (
                    <>
                      <img
                        src={iconeUsuario}
                        alt="Ícone do usuário"
                        width="38"
                        height="38"
                        className="me-2"
                      />
                      <strong>
                        {conversas.find((c) => c.id === conversaAtiva)?.nome || "Carregando..."}
                      </strong>
                    </>
                  ) : (
                    <strong>Selecione uma conversa</strong>
                  )}
                </div>

                <div className="card-body chat-body">
                  {conversaAtiva ? (
                    mensagens.length === 0 ? (
                      <div className="text-center text-muted mt-4">
                        Nenhuma mensagem nesta conversa.
                      </div>
                    ) : (
                      <div className="d-flex flex-column gap-2">
                        {mensagens.map((msg, index) => (
                          <div
                            key={index}
                            className={`d-flex flex-column ${
                              msg.tipo === "enviada" ? "align-self-end" : "align-self-start"
                            }`}
                          >
                            <div
                              className={`msg-balao ${
                                msg.tipo === "enviada" ? "enviada" : "recebida"
                              }`}
                            >
                              {msg.conteudo || msg.content}
                            </div>
                            <small className="text-muted">
                              {msg.hora || msg.timestamp?.slice(11, 16)}
                            </small>
                          </div>
                        ))}
                      </div>
                    )
                  ) : (
                    <div className="text-center text-muted mt-4">
                      Escolha uma conversa à esquerda para começar.
                    </div>
                  )}
                </div>

                {/* Campo de envio */}
                {conversaAtiva && (
                  <div className="card-footer bg-light">
                    <div className="input-group align-items-center">
                      <span className="input-group-text bg-transparent border-0 fs-4">
                        <i className="bi bi-plus-circle"></i>
                      </span>
                      <input
                        type="text"
                        className="form-control border-0"
                        placeholder="Digite uma mensagem"
                        value={novaMensagem}
                        onChange={(e) => setNovaMensagem(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && enviarMensagem()}
                      />
                      <span className="input-group-text bg-transparent border-0 fs-4">
                        <i className="bi bi-mic"></i>
                      </span>
                      <button
                        className="btn btn-enviar d-flex align-items-center justify-content-center"
                        onClick={enviarMensagem}
                      >
                        <img src={iconeEnviar} alt="Enviar" width="20" height="20" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default Chat;