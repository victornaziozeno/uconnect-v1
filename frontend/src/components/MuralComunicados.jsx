import React, { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "./navBar";
import MenuLateral from "./MenuLateral";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import { getPosts, deletePost, getCurrentUser } from "../services/api";

function MuralComunicados() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(null);
  const [tab, setTab] = useState("announcement");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);
  const [deleteModalId, setDeleteModalId] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const user = await getCurrentUser();
        setCurrentUser(user);
      } catch (error) {
        console.error("Erro ao carregar usuário:", error);
      }
    };
    loadUser();
  }, []);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setErr(null);
      const data = await getPosts(tab);
      setItems(data || []);
    } catch (e) {
      console.error(e);
      setErr("Erro ao carregar publicações");
    } finally {
      setLoading(false);
    }
  }, [tab]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const canEditDelete = (post) => {
    if (!currentUser) return false;
    if (currentUser.role === "admin" || currentUser.role === "coordinator") return true;
    return post.author?.id === currentUser.id;
  };

  const handleDelete = async () => {
    if (!deleteModalId) return;
    try {
      setDeleting(true);
      await deletePost(deleteModalId);
      setItems((prev) => prev.filter((item) => item.id !== deleteModalId));
      setDeleteModalId(null);
    } catch (error) {
      console.error("Erro ao deletar:", error);
      setErr("Erro ao deletar publicação");
    } finally {
      setDeleting(false);
    }
  };

  const canCreatePost = currentUser && 
    ["teacher", "coordinator", "admin"].includes(currentUser.role);

  return (
    <>
      <Navbar />
      <div className="d-flex">
        <MenuLateral />

        <div className="container-fluid mt-4">
          <div className="card shadow-sm">
            <div className="card-header bg-white">
              <ul className="nav nav-tabs card-header-tabs">
                <li className="nav-item">
                  <button
                    className={`nav-link ${tab === "announcement" ? "active" : ""}`}
                    onClick={() => setTab("announcement")}
                  >
                    <i className="bi bi-megaphone me-2"></i>
                    Comunicados
                  </button>
                </li>
                <li className="nav-item">
                  <button
                    className={`nav-link ${tab === "notice" ? "active" : ""}`}
                    onClick={() => setTab("notice")}
                  >
                    <i className="bi bi-info-circle me-2"></i>
                    Avisos
                  </button>
                </li>
              </ul>
            </div>

            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0">
                  {tab === "announcement" ? "Comunicados Oficiais" : "Avisos Gerais"}
                </h5>
                {canCreatePost && (
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={() => navigate("/comunicados/novo")}
                  >
                    <i className="bi bi-plus-circle me-2"></i>
                    Nova Publicação
                  </button>
                )}
              </div>

              {err && (
                <div className="alert alert-danger d-flex align-items-center" role="alert">
                  <i className="bi bi-exclamation-triangle-fill me-2"></i>
                  {err}
                </div>
              )}

              {!err && loading && (
                <div className="text-center p-4">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Carregando…</span>
                  </div>
                </div>
              )}

              {!err && !loading && items.length === 0 && (
                <div className="text-center text-muted p-4">
                  <i className="bi bi-inbox" style={{ fontSize: "3rem", opacity: 0.3 }}></i>
                  <p className="mt-3">
                    Nenhum {tab === "announcement" ? "comunicado" : "aviso"} encontrado.
                  </p>
                </div>
              )}

              <div className="d-flex flex-column gap-3">
                {items.map((item) => (
                  <div key={item.id} className="card border" style={{ borderRadius: 10 }}>
                    <div className="card-body">
                      <div className="d-flex justify-content-between align-items-start mb-2">
                        <div className="d-flex align-items-center">
                          <div className="me-3">
                            <div
                              className="rounded-circle bg-primary d-flex align-items-center justify-content-center"
                              style={{ width: 40, height: 40 }}
                            >
                              <i className="bi bi-person-fill text-white"></i>
                            </div>
                          </div>
                          <div>
                            <div className="fw-semibold text-primary">
                              {item.author?.name || "Autor Desconhecido"}
                            </div>
                            <small className="text-muted">
                              {formatDateTime(item.date)}
                            </small>
                          </div>
                        </div>

                        {canEditDelete(item) && (
                          <div className="dropdown">
                            <button
                              className="btn btn-sm btn-light"
                              type="button"
                              data-bs-toggle="dropdown"
                              aria-expanded="false"
                            >
                              <i className="bi bi-three-dots-vertical"></i>
                            </button>
                            <ul className="dropdown-menu dropdown-menu-end">
                              <li>
                                <button
                                  className="dropdown-item"
                                  onClick={() => navigate(`/comunicados/editar/${item.id}`)}
                                >
                                  <i className="bi bi-pencil me-2"></i>
                                  Editar
                                </button>
                              </li>
                              <li>
                                <button
                                  className="dropdown-item text-danger"
                                  onClick={() => setDeleteModalId(item.id)}
                                >
                                  <i className="bi bi-trash me-2"></i>
                                  Excluir
                                </button>
                              </li>
                            </ul>
                          </div>
                        )}
                      </div>

                      <h5 className="card-title mt-3">{item.title}</h5>
                      <div
                        className="card-text"
                        style={{ whiteSpace: "pre-wrap" }}
                      >
                        {item.content}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {deleteModalId && (
        <>
          <div
            className="modal fade show"
            style={{ display: "block" }}
            tabIndex="-1"
            role="dialog"
            aria-modal="true"
          >
            <div className="modal-dialog modal-dialog-centered">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Confirmar Exclusão</h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setDeleteModalId(null)}
                    disabled={deleting}
                  ></button>
                </div>
                <div className="modal-body">
                  Tem certeza que deseja excluir esta publicação? Esta ação não pode ser desfeita.
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setDeleteModalId(null)}
                    disabled={deleting}
                  >
                    Cancelar
                  </button>
                  <button
                    type="button"
                    className="btn btn-danger"
                    onClick={handleDelete}
                    disabled={deleting}
                  >
                    {deleting ? "Excluindo…" : "Excluir"}
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div className="modal-backdrop fade show"></div>
        </>
      )}
    </>
  );
}

export default MuralComunicados;