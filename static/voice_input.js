(function () {
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var statusEl = document.getElementById("voice-status");
    var langEl = document.getElementById("voice-lang");
    var buttons = document.querySelectorAll("[data-voice-target]");

    function setStatus(text) {
        if (statusEl) statusEl.textContent = text;
    }

    if (!buttons.length) return;

    if (!SpeechRecognition) {
        buttons.forEach(function (btn) {
            btn.addEventListener("click", function () {
                setStatus("Voice input is not supported in this browser.");
            });
        });
        return;
    }

    var recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    var targetId = null;
    var listening = false;
    var transcript = "";

    recognition.onresult = function (event) {
        transcript = (event.results[0][0].transcript || "").trim();
    };

    recognition.onerror = function (event) {
        listening = false;
        buttons.forEach(function (b) { b.classList.remove("listening"); });
        if (event.error === "not-allowed") {
            setStatus("Microphone permission was denied. You can still type.");
        } else {
            setStatus("Voice input is not supported in this browser.");
        }
    };

    recognition.onend = function () {
        listening = false;
        buttons.forEach(function (b) { b.classList.remove("listening"); });
        if (transcript && targetId) {
            var el = document.getElementById(targetId);
            if (el) el.value = transcript;
            setStatus("Captured. You can edit the field if needed.");
        }
    };

    buttons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            if (listening) {
                try { recognition.stop(); } catch (e) {}
                return;
            }
            targetId = btn.getAttribute("data-voice-target");
            transcript = "";
            recognition.lang = langEl ? langEl.value : "en-IN";
            try {
                listening = true;
                btn.classList.add("listening");
                setStatus("Listening… speak now.");
                recognition.start();
            } catch (err) {
                listening = false;
                btn.classList.remove("listening");
                setStatus("Voice input is not supported in this browser.");
            }
        });
    });
})();
