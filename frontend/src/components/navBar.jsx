import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import "../styles/navbar.css";
import logoUconnect from "../assets/Logo.svg";
import userIcon from "../assets/user-icon.svg";
import notificationIcon from "../assets/icon-notificacao.svg";

function Navbar() {
    return (
        <nav className="uconnect-navbar">
            {/* 🔹 Esquerda: Logo */}
            <div className="navbar-left">
                <img
                    src={logoUconnect}
                    alt="Logo UCONNECT"
                    className="navbar-logo"
                />
            </div>

            {/* 🔹 Direita: Usuário, botão e notificação */}
            <div className="navbar-right">
                <button className="course-btn">
                    Análise e Desenvolvimento de Sistemas
                </button>

                <div className="user-info">
                    <img src={userIcon} alt="Usuário" className="user-icon" />
                    <span className="username">Gabriel</span>
                </div>

                <img
                    src={notificationIcon}
                    alt="Notificações"
                    className="notification-icon"
                />
            </div>
        </nav>
    );
}

export default Navbar;