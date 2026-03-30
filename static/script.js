async function analyze() {
    const input = document.getElementById("inputText").value;
    const file = document.getElementById("fileInput").files[0];
    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = "<p>Analyzing... Please wait ⏳</p>";
    if (!input && !file) {
    alert("Please enter text or upload a file");
    return;
   }

    let response;

    if (file) {
        const formData = new FormData();
        formData.append("file", file);

        response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

    } else {
        response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                input: input
            })
        });
    }

    const data = await response.json();

    if (data.error) {
        resultDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
        return;
    }

    const riskClass = data.risk_level.toLowerCase();

    resultDiv.innerHTML = `

        <div class="card">
            <h2>Detected Type</h2>
            <p>${data.detected_type || "Not detected"}</p>
        </div>

        <div class="card">
            <h2>Summary</h2>
            <p>${data.summary}</p>
        </div>

        <div class="card">
            <h2>Risk Level: <span class="${riskClass}">${data.risk_level}</span></h2>
            <p>Overall Score: ${data.risk_score.overall}</p>
        </div>

        <div class="card">
            <h2>Detected Issues</h2>
            <ul>${data.detected_issues.map(i => `<li>${i}</li>`).join("")}</ul>
        </div>

        <div class="card highlight">
            <h2>Recommendations</h2>
            <ul>${data.recommendations.map(i => `<li>${i}</li>`).join("")}</ul>
        </div>

        <div class="card">
            <h2>Final Decision</h2>
            <p><b>${data.final_decision}</b></p>
        </div>

    `;
}

function clearFile() {
    const fileInput = document.getElementById("fileInput");
    fileInput.value = "";
}

function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    
    recognition.lang = "en-IN";

    recognition.onresult = function(event) {
        document.getElementById("inputText").value = event.results[0][0].transcript;
    };

    recognition.start();
}