document.addEventListener('DOMContentLoaded', () => {
    console.log("SkillSphere Frontend Loaded ✅");
    const sendBtn = document.getElementById('chat-send');
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');
    if (sendBtn && input && messages) {
        sendBtn.addEventListener('click', () => {
            const text = input.value.trim();
            if (text === '') return;
            addMessage(text, 'user');
            input.value = '';
            setTimeout(() => {
                const reply = getBotReply(text);
                addMessage(reply, 'bot');
            }, 600);
        });
    }
    function addMessage(text, sender) {
        const msg = document.createElement('div');
        msg.classList.add('chatbot-message', sender);
        msg.innerText = text;
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;
    }
    function getBotReply(input) {
        input = input.toLowerCase();
        if (input.includes('python')) return "To improve Python, practice small coding tasks daily.";
        if (input.includes('internship')) return "Check the Internships tab — you’ll find tasks for all levels!";
        if (input.includes('hello') || input.includes('hi')) return "Hi there 👋 I'm your AI mentor — here to guide your skill journey!";
        return "I'm still learning! Try asking about Python or internships.";
    }
});
document.addEventListener('DOMContentLoaded', () => {
    console.log("SkillSphere Frontend Loaded ✅");

    /* ------------------------------------------
       💬 CHATBOT FUNCTIONALITY
    ------------------------------------------ */
    const sendBtn = document.getElementById('chat-send');
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');

    if (sendBtn && input && messages) {
        sendBtn.addEventListener('click', () => {
            const text = input.value.trim();
            if (text === '') return;

            addMessage(text, 'user');
            input.value = '';

            setTimeout(() => {
                const reply = getBotReply(text);
                addMessage(reply, 'bot');
            }, 600);
        });
    }

    function addMessage(text, sender) {
        const msg = document.createElement('div');
        msg.classList.add('chatbot-message', sender);
        msg.innerText = text;
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;
    }

    function getBotReply(input) {
        input = input.toLowerCase();
        if (input.includes('python')) return "To improve Python, practice small coding tasks daily.";
        if (input.includes('internship')) return "Check the Internships tab — you’ll find tasks for all levels!";
        if (input.includes('hello') || input.includes('hi')) return "Hi there 👋 I'm your AI mentor — here to guide your skill journey!";
        return "I'm still learning! Try asking about Python or internships.";
    }

    /* ------------------------------------------
       🌙 THEME TOGGLE (Light <-> Dark)
    ------------------------------------------ */
    const themeBtn = document.getElementById("theme-toggle");
    const themeLink = document.getElementById("theme-style");

    if (themeBtn && themeLink) {
        themeBtn.addEventListener("click", () => {
            if (themeLink.getAttribute("href").includes("style.css")) {
                themeLink.setAttribute("href", "/static/css/style-dark.css");
                themeBtn.innerText = "☀️ Light Mode";
            } else {
                themeLink.setAttribute("href", "/static/css/style.css");
                themeBtn.innerText = "🌙 Dark Mode";
            }
        });
    }
});
