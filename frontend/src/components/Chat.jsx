import { useState, useEffect, useRef } from "react";
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

// Import das funções da API
import { 
  getConversations, 
  getMessages, 
  sendMessage, 
  markAllMessagesAsRead,
  createConversation 
} from "../services/api";

function Chat() {
  const [conversas, setConversas] = useState([]);
  const [mensagens, setMensagens] = useState([]);
  const [conversaAtiva, setConversaAtiva] = useState(null);
  const [filtroAtivo, setFiltroAtivo] = useState("Todos");
  const [novaMensagem, setNovaMensagem] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const chatBodyRef = useRef(null);

  // 🔹 Busca conversas do usuário
  useEffect(() => {
    fetchConversas();
  }, [filtroAtivo]);

  // 🔹 Busca mensagens da conversa ativa
  useEffect(() => {
    if (conversaAtiva) {
      fetchMensagens();
      // Marcar todas as mensagens como lidas ao abrir a conversa
      markAllMessagesAsRead(conversaAtiva).catch(console.error);
    }
  }, [conversaAtiva]);

  // 🔹 Auto-scroll para última mensagem
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [mensagens]);

  const fetchConversas = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getConversations(filtroAtivo);
      setConversas(data);
    } catch (err) {
      console.error("Erro ao buscar conversas:", err);
      setError("Erro ao carregar conversas");
    } finally {
      setLoading(false);
    }
  };

  const fetchMensagens = async () => {
    if (!conversaAtiva) return;
    
    try {
      setLoading(true);
      const data = await getMessages(conversaAtiva);
      setMensagens(data);
    } catch (err) {
      console.error("Erro ao buscar mensagens:", err);
      setError("Erro ao carregar mensagens");
    } finally {
      setLoading(false);
    }
  };

  const enviarMensagem = async () => {
    if (novaMensagem.trim() === "" || !conversaAtiva) return;

    const msgData = {
      content: novaMensagem.trim(),
      conversationId: conversaAtiva,
    };

    try {
      const novaMsgEnviada = await sendMessage(msgData);
      setMensagens((prev) => [...prev, novaMsgEnviada]);
      setNovaMensagem("");
      
      // Atualizar a lista de conversas para refletir a última mensagem
      fetchConversas();
    } catch (err) {
      console.error("Erro ao enviar mensagem:", err);
      setError("Erro ao enviar mensagem");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      enviarMensagem();
    }
  };

  const selecionarConversa = (conversaId) => {
    setConversaAtiva(conversaId);
    setError(null);
  };

  // Filtragem local de conversas por pesquisa
  const conversasFiltradas = conversas.filter((conv) => {
    const nome = conv.nome || conv.title || "";
    return nome.toLowerCase().includes(searchTerm.toLowerCase());
  });

  // Obter conversa ativa atual
  const conversaAtualObj = conversas.find((c) => c.id === conversaAtiva);

  // Formatar timestamp das mensagens
  const formatarHora = (timestamp) => {
    if (!timestamp) return "";
    const date = new Date(timestamp);
    return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <>
      <Navbar />

      <div className="chat-layout d-flex">
        <MenuLateral />

        <div className="container-fluid mt-4">
          {error && (
            <div className="alert alert-danger alert-dismissible fade show" role="alert">
              {error}
              <button 
                type="button" 
                className="btn-close" 
                onClick={() => setError(null)}
              ></button>
            </div>
          )}

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
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
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
                    ].map((filtro) => (
                      <div
                        key={filtro.nome}
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
                  <div className="list-group list-group-flush" style={{ maxHeight: "500px", overflowY: "auto" }}>
                    {loading && conversas.length === 0 ? (
                      <div className="text-center p-4">
                        <div className="spinner-border text-primary" role="status">
                          <span className="visually-hidden">Carregando...</span>
                        </div>
                      </div>
                    ) : conversasFiltradas.length === 0 ? (
                      <div className="text-center text-muted p-4">
                        Nenhuma conversa encontrada
                      </div>
                    ) : (
                      conversasFiltradas.map((chat) => (
                        <div
                          key={chat.id}
                          className={`list-group-item list-group-item-action d-flex align-items-start ${
                            conversaAtiva === chat.id ? "bg-light" : ""
                          }`}
                          onClick={() => selecionarConversa(chat.id)}
                          style={{ cursor: "pointer" }}
                        >
                          <img
                            src={iconeUsuario}
                            alt="Ícone do usuário"
                            width="42"
                            height="42"
                            className="me-3"
                          />
                          <div className="flex-grow-1">
                            <div className="d-flex justify-content-between align-items-start">
                              <strong className="text-truncate" style={{ maxWidth: "200px" }}>
                                {chat.nome || chat.title || "Sem título"}
                              </strong>
                              <small className="text-muted">{chat.hora || ""}</small>
                            </div>
                            <div className="d-flex justify-content-between align-items-center">
                              <div className="text-muted small text-truncate" style={{ maxWidth: "200px" }}>
                                {chat.ultimaMensagem || "Sem mensagens"}
                              </div>
                              {chat.unreadCount > 0 && (
                                <span className="badge bg-primary rounded-pill">
                                  {chat.unreadCount}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* 🔹 Área do chat */}
            <div className="col-md-8">
              <div className="card shadow-sm chat-card">
                <div className="card-header bg-light d-flex align-items-center justify-content-between">
                  {conversaAtiva && conversaAtualObj ? (
                    <>
                      <div className="d-flex align-items-center">
                        <img
                          src={iconeUsuario}
                          alt="Ícone do usuário"
                          width="38"
                          height="38"
                          className="me-2"
                        />
                        <div>
                          <strong>{conversaAtualObj.nome || conversaAtualObj.title}</strong>
                          <div className="small text-muted">
                            {conversaAtualObj.participants?.length || 0} participante(s)
                          </div>
                        </div>
                      </div>
                      <button 
                        className="btn btn-sm btn-outline-secondary"
                        onClick={fetchMensagens}
                        disabled={loading}
                      >
                        <i className="bi bi-arrow-clockwise"></i>
                      </button>
                    </>
                  ) : (
                    <strong>Selecione uma conversa</strong>
                  )}
                </div>

                <div className="card-body chat-body" ref={chatBodyRef}>
                  {conversaAtiva ? (
                    loading && mensagens.length === 0 ? (
                      <div className="text-center mt-4">
                        <div className="spinner-border text-primary" role="status">
                          <span className="visually-hidden">Carregando...</span>
                        </div>
                      </div>
                    ) : mensagens.length === 0 ? (
                      <div className="text-center text-muted mt-4">
                        Nenhuma mensagem nesta conversa. Seja o primeiro a enviar!
                      </div>
                    ) : (
                      <div className="d-flex flex-column gap-2">
                        {mensagens.map((msg) => {
                          const isSent = msg.sender?.id !== undefined && msg.senderId !== undefined;
                          const isMyMessage = msg.sender?.registration === localStorage.getItem("registration");
                          
                          return (
                            <div
                              key={msg.id}
                              className={`d-flex flex-column ${
                                isMyMessage ? "align-self-end" : "align-self-start"
                              }`}
                            >
                              {!isMyMessage && msg.sender && (
                                <small className="text-muted mb-1">
                                  {msg.sender.name}
                                </small>
                              )}
                              <div
                                className={`msg-balao ${
                                  isMyMessage ? "enviada" : "recebida"
                                }`}
                              >
                                {msg.content}
                              </div>
                              <small className="text-muted mt-1">
                                {formatarHora(msg.timestamp)}
                              </small>
                            </div>
                          );
                        })}
                      </div>
                    )
                  ) : (
                    <div className="text-center text-muted mt-4">
                      <i className="bi bi-chat-dots" style={{ fontSize: "4rem", opacity: 0.3 }}></i>
                      <p className="mt-3">Escolha uma conversa à esquerda para começar</p>
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
                        onKeyPress={handleKeyPress}
                        disabled={loading}
                      />
                      <span className="input-group-text bg-transparent border-0 fs-4">
                        <i className="bi bi-mic"></i>
                      </span>
                      <button
                        className="btn btn-enviar d-flex align-items-center justify-content-center"
                        onClick={enviarMensagem}
                        disabled={loading || novaMensagem.trim() === ""}
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