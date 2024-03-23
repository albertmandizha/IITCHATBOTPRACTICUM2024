const contentContainer = document.querySelector('.content-container');
const headerIcon = document.querySelector('.header-icon');

// Event listeners for buttons
document.getElementById("fileBtn").addEventListener("click", function() {
  fetchFileUploadContent();
});

document.getElementById('chatResponsesBtn').addEventListener('click', () => {
  fetchData('chatResponsesBtn');
});

document.getElementById('qaTableBtn').addEventListener('click', () => {
  fetchData('qaTableBtn');
});

document.getElementById('qaTagsBtn').addEventListener('click', () => {
  fetchData('qaTagsBtn');
});

document.getElementById('tagTableBtn').addEventListener('click', () => {
  fetchData('tagTableBtn');
});

document.getElementById('unansweredBtn').addEventListener('click', () => {
  fetchData('unansweredBtn');
});

document.getElementById('chatbotDemoBtn').addEventListener('click', () => {
  contentContainer.innerHTML = '<p>Chatbot Demo content goes here...</p>';
});

function fetchData(buttonId) {
  fetch(`http://127.0.0.1:5000/get_data/${buttonId}`)
    .then(response => response.json())
    .then(data => {
      let tableHTML = '<div class="table-container">';
      tableHTML += '<table cellspacing="0" cellpadding="5" border="1" style="width: 100%;">';
      tableHTML += '<thead><tr>';
      for (const key of Object.keys(data[0])) {
        tableHTML += `<th>${key}</th>`;
      }
      tableHTML += '</tr></thead><tbody>';

      for (const row of data) {
        tableHTML += '<tr>';
        for (const cell of Object.values(row)) {
          tableHTML += `<td contenteditable="true" style="border: 1px solid #ccc; padding: 5px;">${cell}</td>`;
        }
        tableHTML += '</tr>';
      }

      tableHTML += '</tbody></table>';

      // Add "Download" button for QA Table
      if (buttonId === 'qaTableBtn') {
        tableHTML += '<div class="button-container">';
        tableHTML += '<button id="downloadQATableBtn">Download</button>';
        tableHTML += '</div>';
      }

      tableHTML += '</div>';
      contentContainer.innerHTML = tableHTML;

      // Add event listener for "Download" button
      if (buttonId === 'qaTableBtn') {
        document.getElementById('downloadQATableBtn').addEventListener('click', downloadQATable);
      }
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
}

function fetchFileUploadContent() {
  const filePath = "/CS Team/Dashboard/index1.html";

  fetch(filePath)
    .then(response => response.text())
    .then(data => {
      const contentDiv = document.createElement('div');
      contentDiv.innerHTML = data;
      contentContainer.appendChild(contentDiv);

      const script1 = document.createElement('script');
      script1.src = '/CS Team/Dashboard/script1.js';
      document.body.appendChild(script1);

      const style1 = document.createElement('link');
      style1.rel = 'stylesheet';
      style1.href = '/CS Team/Dashboard/style1.css';
      document.head.appendChild(style1);
    })
    .catch(error => {
      console.error('Error fetching file:', error);
    });
}

// Event listener for header icon
headerIcon.addEventListener('click', () => {
  alert('Personal Information and Logout option goes here...');
});

function downloadQATable() {
  const downloadLink = document.createElement('a');
  downloadLink.href = 'http://127.0.0.1:5000/download_qa_table';
  downloadLink.download = 'qa_table.csv';
  downloadLink.click();
}