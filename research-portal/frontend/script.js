console.log("Frontend Loaded");

const API_BASE = "http://127.0.0.1:8000";


async function uploadFile() {

    const fileInput = document.getElementById("fileInput");
    const status = document.getElementById("status");
    const downloadLink = document.getElementById("downloadLink");

    if (!fileInput.files.length) {
        alert("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    status.innerText = "Processing...";

    try {
        const response = await fetch(
            `${API_BASE}/extract-financials`,
            {
                method: "POST",
                body: formData
            }
        );

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        console.log("API Response:", data);

        // Build status message with metadata
        let statusMsg = `✅ Extraction completed | ${data.rows_extracted} rows extracted`;
        
        if (data.currency) {
            statusMsg += ` | Currency: ${data.currency}`;
        }
        if (data.unit) {
            statusMsg += ` | Unit: ${data.unit}`;
        }
        if (data.notes && data.notes.length > 0) {
            statusMsg += ` | ⚠️ ${data.notes.join('; ')}`;
        }
        
        status.innerText = statusMsg;

        // ---------- SHOW TABLE ----------
        if (data.headers && data.rows) {
            displayTable(data.headers, data.rows);
        }

        // ---------- SHOW DOWNLOAD LINK ----------
        if (data.excel_file) {
            const fileUrl = `${API_BASE}/${data.excel_file}`;

            console.log("Download URL:", fileUrl);

            downloadLink.href = fileUrl;
            downloadLink.download = data.excel_file.split('/').pop();
            downloadLink.style.display = "inline-block";
            downloadLink.innerText = "⬇️ Download Excel";
        } else {
            downloadLink.innerText = "No file generated";
            downloadLink.style.display = "inline-block";
        }

        // Refresh downloads list
        loadDownloads();

    } catch (error) {
        console.error(error);
        status.innerText = "Error connecting to backend ❌";
    }
}


async function loadDownloads() {
    const fileList = document.getElementById("fileList");
    fileList.innerHTML = '<li class="no-files">Loading...</li>';

    try {
        const response = await fetch(`${API_BASE}/outputs-list`);
        
        if (!response.ok) {
            throw new Error("Failed to load downloads");
        }

        const data = await response.json();
        const files = data.files || [];

        if (files.length === 0) {
            fileList.innerHTML = '<li class="no-files">No files available yet. Extract financial data to generate downloads.</li>';
            return;
        }

        fileList.innerHTML = '';

        files.forEach(file => {
            const listItem = document.createElement('li');
            listItem.className = 'file-item';
            listItem.innerHTML = `
                <div class="file-info">
                    <div class="file-name">📄 ${file.filename}</div>
                    <div class="file-meta">Size: ${file.size_mb} MB | Generated: ${file.date}</div>
                </div>
                <a href="${API_BASE}${file.url}" download="${file.filename}" class="file-download-btn">
                    ⬇️ Download
                </a>
            `;
            fileList.appendChild(listItem);
        });

    } catch (error) {
        console.error("Error loading downloads:", error);
        fileList.innerHTML = '<li class="no-files">Failed to load downloads. Check that the backend is running.</li>';
    }
}


function displayTable(headers, rows) {

    const table = document.getElementById("resultTable");
    const thead = table.querySelector("thead");
    const tbody = table.querySelector("tbody");

    thead.innerHTML = "";
    tbody.innerHTML = "";

    let headerRow = "<tr>";

    headers.forEach(header => {
        headerRow += `<th>${header}</th>`;
    });

    headerRow += "</tr>";

    thead.innerHTML = headerRow;

    rows.forEach(row => {
        let rowHtml = "<tr>";

        row.forEach(cell => {
            rowHtml += `<td>${cell}</td>`;
        });

        rowHtml += "</tr>";

        tbody.innerHTML += rowHtml;
    });

    table.style.display = "table";
}
