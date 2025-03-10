let sessionId = "";

// async function loadSessions() {
//     let response = await fetch("/sessions");
//     let data = await response.json();
//     let sessionsDiv = document.getElementById("sessions");
//     sessionsDiv.innerHTML = "";
//     data.forEach(session => {
//         let btn = document.createElement("div");
//         btn.className = "chat-session";
//         btn.textContent = session.title;
//         btn.onclick = () => loadChat(session._id);
//         sessionsDiv.appendChild(btn);
//     });
// }

async function newChat() {
    let response = await fetch("/new_session", { method: "POST" });
    let data = await response.json();
    sessionId = data.session_id;
    document.getElementById("chat").innerHTML = "";
    loadSessions();
    connectWebSocket();
}

async function loadChat(id) {
    sessionId = id;
    let response = await fetch(`/history?session_id=${id}`);
    let data = await response.json();
    let chatDiv = document.getElementById("chat");
    chatDiv.innerHTML = "";
    data.forEach(msg => {
        let div = document.createElement("div");
        div.className = `message ${msg.sender}`;
        div.textContent = msg.text;
        chatDiv.appendChild(div);
    });
    connectWebSocket();
}

let ws;
function connectWebSocket() {
    if (ws) ws.close();
    ws = new WebSocket(`ws://localhost:8000/ws?session_id=${sessionId}`);
    ws.onmessage = event => {
        let chatDiv = document.getElementById("chat");
        let div = document.createElement("div");
        div.className = "message ai";
        div.textContent = event.data;
        chatDiv.appendChild(div);
    };
}

function sendMessage() {
    let inputField = document.getElementById("input");
    let userMessage = inputField.value;
    if (!userMessage) return;
    let chatDiv = document.getElementById("chat");
    let div = document.createElement("div");
    div.className = "message user";
    div.textContent = userMessage;
    chatDiv.appendChild(div);
    ws.send(userMessage);
    inputField.value = "";
}

// async function deleteChat(sessionId) {
//     if (confirm("Are you sure you want to delete this chat?")) {
//         await fetch(`/delete_session?session_id=${sessionId}`, { method: "POST" });
//         loadSessions();  // Refresh chat list
//     }
// }

// async function loadSessions() {
//     let response = await fetch("/sessions");
//     let data = await response.json();
//     let sessionsDiv = document.getElementById("sessions");
//     sessionsDiv.innerHTML = "";
//     data.forEach(session => {
//         let sessionDiv = document.createElement("div");
//         sessionDiv.className = "chat-session";
        
//         let chatTitle = document.createElement("span");
//         chatTitle.textContent = session.title;
        
//         let deleteBtn = document.createElement("button");
//         deleteBtn.textContent = "❌";
//         deleteBtn.style.marginLeft = "10px";
//         deleteBtn.onclick = () => deleteChat(session._id);
        
//         sessionDiv.appendChild(chatTitle);
//         sessionDiv.appendChild(deleteBtn);
//         sessionDiv.onclick = () => loadChat(session._id);
//         sessionsDiv.appendChild(sessionDiv);
//     });
// }

async function loadSessions() {
    let response = await fetch("/sessions");
    let data = await response.json();
    let sessionsDiv = document.getElementById("sessions");
    sessionsDiv.innerHTML = "";

    data.forEach(session => {
        let sessionDiv = document.createElement("div");
        sessionDiv.className = "chat-session";
        
        let chatContainer = document.createElement("div");
        chatContainer.style.display = "flex";
        chatContainer.style.justifyContent = "space-between";
        chatContainer.style.alignItems = "center";
        chatContainer.style.width = "100%";

        let chatTitle = document.createElement("span");
        chatTitle.textContent = session.title.length > 20 ? session.title.substring(0, 20) + "..." : session.title;

        let deleteBtn = document.createElement("span");
        deleteBtn.innerHTML = "❌";
        deleteBtn.className = "delete-icon";
        deleteBtn.onclick = (event) => {
            event.stopPropagation(); // Prevent clicking the chat when deleting
            deleteChat(session._id);
        };

        chatContainer.appendChild(chatTitle);
        chatContainer.appendChild(deleteBtn);
        sessionDiv.appendChild(chatContainer);
        sessionDiv.onclick = () => loadChat(session._id);
        sessionsDiv.appendChild(sessionDiv);
    });
}

// async function deleteChat(sessionId) {
//     if (confirm("Are you sure you want to delete this chat?")) {
//         await fetch(`/delete_session?session_id=${sessionId}`, { method: "POST" });
//         loadSessions(); // Refresh chat list
//     }
// }

async function deleteChat(sessionId) {
    if (confirm("Are you sure you want to delete this chat?")) {
        await fetch(`/delete_session?session_id=${sessionId}`, { method: "DELETE" });
        loadSessions(); // Refresh chat list
    }
}



window.onload = () => {
    loadSessions();
    fetch("/default_session").then(res => res.json()).then(data => {
        if (data.session_id) {
            loadChat(data.session_id);
        } else {
            newChat();
        }
    });
};
