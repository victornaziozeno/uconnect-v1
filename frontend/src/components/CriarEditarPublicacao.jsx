import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "./navBar";
import MenuLateral from "./MenuLateral";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import { createPost, updatePost, getPost } from "../services/api";

export default function CriarEditarPublicacao() {
  const navigate = useNavigate();
  const { postId } = useParams();
  const isEditing = !!postId;

  const [titulo, setTitulo] = useState("");
  const [conteudo, setConteudo] = useState("");
  const [tipo, setTipo] = useState("announcement");
  
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);
  const [carregando, setCarregando] = useState(false);

  useEffect(() => {
    if (isEditing) {
      const loadPost = async () => {
        try {
          setCarregando(true);
          const post = await getPost(postId);
          setTitulo(post.title);
          setConteudo(post.content);
          setTipo(post.type);
        } catch (error) {
          console.error("Erro ao carregar publicação:", error);
          setErro("Erro ao carregar publicação para edição");
        } finally {
          setCarregando(false);
        }
      };
      loadPost();
    }
  }, [isEditing, postId]);

  const podeEnviar = titulo.trim().length >= 3 && 
                     conteudo.trim().length >= 3 && 
                     !enviando;

  const handleEnviar = async () => {
    if (!podeEnviar) return;
    
    try {
      setErro(null);
      setEnviando(true);

      const postData = {
        title: titulo.trim(),
        content: conteudo.trim(),
        type: tipo,
      };

      if (isEditing) {
        await updatePost(postId, postData);
      } else {
        await createPost(postData);
      }

      navigate("/comunicados");
    } catch (e) {
      console.error(e);
      setErro(e.message || "Falha ao salvar publicação");
    } finally {
      setEnviando(false);
    }
  };

  const handleCancelar = () => {
    navigate("/comunicados");
  };

  if (carregando) {
    return (
      <>
        <Navbar />
        <div className="d-flex">
          <MenuLateral />
          <div className="container-fluid mt-4">
            <div className="text-center p-4">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Carregando…</span>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="d-flex">
        <MenuLateral />
        <div className="container-fluid mt-4">
          {erro && (
            <div className="alert alert-danger alert-dismissible fade show" role="alert">
              {erro}
              <button type="button" className="btn-close" onClick={() => setErro(null)} />
            </div>
          )}

          <div className="card shadow-sm">
            <div className="card-header bg-primary text-white fw-semibold">
              {isEditing ? "Editar Publicação" : "Nova Publicação"}
            </div>

            <div className="card-body">
              <div className="mb-3">
                <label className="form-label fw-semibold">Tipo de Publicação</label>
                <div className="btn-group w-100" role="group">
                  <input
                    type="radio"
                    className="btn-check"
                    name="tipo"
                    id="tipoAnnouncement"
                    value="announcement"
                    checked={tipo === "announcement"}
                    onChange={(e) => setTipo(e.target.value)}
                    disabled={enviando}
                  />
                  <label className="btn btn-outline-primary" htmlFor="tipoAnnouncement">
                    <i className="bi bi-megaphone me-2"></i>
                    Comunicado Oficial
                  </label>

                  <input
                    type="radio"
                    className="btn-check"
                    name="tipo"
                    id="tipoNotice"
                    value="notice"
                    checked={tipo === "notice"}
                    onChange={(e) => setTipo(e.target.value)}
                    disabled={enviando}
                  />
                  <label className="btn btn-outline-primary" htmlFor="tipoNotice">
                    <i className="bi bi-info-circle me-2"></i>
                    Aviso Geral
                  </label>
                </div>
                <small className="text-muted d-block mt-2">
                  {tipo === "announcement" 
                    ? "Comunicados oficiais são importantes e aparecem em destaque"
                    : "Avisos gerais são informações menos urgentes"}
                </small>
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">Título</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Ex.: Aviso sobre suspensão de aulas"
                  value={titulo}
                  onChange={(e) => setTitulo(e.target.value)}
                  disabled={enviando}
                  maxLength={200}
                />
                <div className="d-flex justify-content-between mt-1">
                  <small className="text-muted">Mínimo 3 caracteres</small>
                  <small className="text-muted">{titulo.length}/200</small>
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">Conteúdo</label>
                <textarea
                  className="form-control"
                  placeholder="Escreva o conteúdo da publicação..."
                  rows={8}
                  value={conteudo}
                  onChange={(e) => setConteudo(e.target.value)}
                  disabled={enviando}
                  maxLength={5000}
                />
                <div className="d-flex justify-content-between mt-1">
                  <small className="text-muted">Mínimo 3 caracteres</small>
                  <small className="text-muted">{conteudo.length}/5000</small>
                </div>
              </div>

              <div className="d-flex justify-content-between mt-4">
                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={handleCancelar}
                  disabled={enviando}
                >
                  <i className="bi bi-x-circle me-2"></i>
                  Cancelar
                </button>

                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleEnviar}
                  disabled={!podeEnviar}
                >
                  {enviando ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      {isEditing ? "Salvando…" : "Publicando…"}
                    </>
                  ) : (
                    <>
                      <i className={`bi ${isEditing ? 'bi-check-circle' : 'bi-send'} me-2`}></i>
                      {isEditing ? "Salvar Alterações" : "Publicar"}
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          <div className="my-3 small text-muted">
            <i className="bi bi-info-circle me-2"></i>
            {tipo === "announcement" 
              ? "Comunicados são enviados como notificação para todos os usuários"
              : "Avisos ficam disponíveis no mural sem notificação automática"}
          </div>
        </div>
      </div>
    </>
  );
}
