(function () {
    var assessmentId = window.GRAMINTEL_ASSESSMENT_ID;
    var fab = document.getElementById("chat-fab");
    var panel = document.getElementById("chat-panel");
    var closeBtn = document.getElementById("chat-close");
    var headingBtn = document.getElementById("open-chat-heading");
    var form = document.getElementById("chat-form");
    var input = document.getElementById("chat-input");
    var log = document.getElementById("chat-log");
    var statusEl = document.getElementById("chat-status");
    var micBtn = document.getElementById("chat-mic");
    var quick = document.getElementById("chat-quick");
    var loaded = false;

    if (!fab || !panel) return;

    function setStatus(text) {
        if (statusEl) statusEl.textContent = text || "";
    }

    function appendBubble(role, text) {
        var div = document.createElement("div");
        div.className = "chat-bubble " + (role === "user" ? "user" : "bot");
        div.textContent = text;
        log.appendChild(div);
        log.scrollTop = log.scrollHeight;
    }

    function openPanel() {
        panel.hidden = false;
        fab.setAttribute("aria-expanded", "true");
        if (!loaded) {
            loaded = true;
            appendBubble("bot", "Hi! I can explain your business assessment.");
            if (assessmentId) {
                fetch("/api/chat/" + assessmentId)
                    .then(function (res) { return res.json(); })
                    .then(function (data) {
                        (data.messages || []).forEach(function (m) {
                            var role = (m.sender === "user") ? "user" : "bot";
                            appendBubble(role, m.message);
                        });
                        log.scrollTop = log.scrollHeight;
                    })
                    .catch(function () {
                        appendBubble("bot", "Chat history could not be loaded. You can still ask a question.");
                    });
            }
        }
        if (input) input.focus();
    }

    function closePanel() {
        panel.hidden = true;
        fab.setAttribute("aria-expanded", "false");
    }

    function sendMessage(text) {
        var message = (text || "").trim();
        if (!message) return;
        appendBubble("user", message);
        input.value = "";
        setStatus("Thinking…");
        fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ assessment_id: assessmentId, message: message })
        })
            .then(function (res) { return res.json().then(function (data) { return { ok: res.ok, data: data }; }); })
            .then(function (result) {
                setStatus("");
                if (result.data && result.data.reply) {
                    appendBubble("bot", result.data.reply);
                    return;
                }
                appendBubble("bot", (result.data && result.data.error) || "Could not answer that.");
            })
            .catch(function () {
                setStatus("");
                appendBubble("bot", "Network error. The assistant runs locally — check that the Flask app is running.");
            });
    }

    fab.addEventListener("click", function () {
        if (panel.hidden) openPanel();
        else closePanel();
    });
    if (closeBtn) closeBtn.addEventListener("click", closePanel);
    if (headingBtn) headingBtn.addEventListener("click", openPanel);

    var params = new URLSearchParams(window.location.search);
    if (params.get("chat") === "1" || window.location.hash === "#chat") {
        openPanel();
    }

    if (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();
            sendMessage(input.value);
        });
    }

    if (quick) {
        quick.addEventListener("click", function (event) {
            var btn = event.target.closest("button[data-q]");
            if (!btn) return;
            sendMessage(btn.getAttribute("data-q"));
        });
    }

    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        if (micBtn) {
            micBtn.addEventListener("click", function () {
                setStatus("Voice input is not supported in this browser.");
            });
        }
        return;
    }

    var recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    var listening = false;
    var transcript = "";

    recognition.onresult = function (event) {
        transcript = (event.results[0][0].transcript || "").trim();
    };
    recognition.onerror = function (event) {
        listening = false;
        if (micBtn) micBtn.classList.remove("listening");
        setStatus("Voice input is not supported in this browser.");
    };
    recognition.onend = function () {
        listening = false;
        if (micBtn) micBtn.classList.remove("listening");
        if (transcript && input) {
            input.value = transcript;
            setStatus("Voice captured. Press send when ready.");
        }
    };

    if (micBtn) {
        micBtn.addEventListener("click", function () {
            if (listening) {
                try { recognition.stop(); } catch (e) {}
                return;
            }
            transcript = "";
            recognition.lang = "hi-IN";
            try {
                listening = true;
                micBtn.classList.add("listening");
                setStatus("Listening…");
                recognition.start();
            } catch (err) {
                listening = false;
                micBtn.classList.remove("listening");
                setStatus("Voice input is not supported in this browser.");
            }
        });
    }
})();
