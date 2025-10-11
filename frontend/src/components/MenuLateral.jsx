import React, { useState } from "react";
import "../styles/menulateral.css";

// 🔹 importe seus SVGs (ajuste os nomes conforme os seus arquivos)
import iconLista from "../assets/Lista.svg";
import iconColaboracao from "../assets/Colaboracao.svg";
import iconCalendario from "../assets/Calendario.svg";
import iconChat from "../assets/Chat.svg";
import iconFeed from "../assets/Feed.svg";

function SideMenu() {
  const [active, setActive] = useState("calendar");

  const menuItems = [
    { id: "dashboard", icon: iconLista },
    { id: "colaboração", icon: iconColaboracao },
    { id: "calendario", icon: iconCalendario },
    { id: "feed", icon: iconFeed },
    { id: "chat", icon: iconChat },
    
  ];

  return (
    <div className="side-menu">
      <ul className="menu-list">
        {menuItems.map((item) => (
          <li
            key={item.id}
            className={`menu-item ${active === item.id ? "active" : ""}`}
            onClick={() => setActive(item.id)}
          >
            <img src={item.icon} alt={item.label} className="menu-icon" />
            <span className="menu-label">{item.label}</span>
          </li>
        ))}
      </ul>

      
    </div>
  );
}

export default SideMenu;