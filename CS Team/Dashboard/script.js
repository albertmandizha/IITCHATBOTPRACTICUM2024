const contentContainer = document.querySelector('.content-container');
const headerIcon = document.querySelector('.header-icon');

// Event listeners for buttons
document.getElementById("fileBtn").addEventListener("click", function() {
  fetchFileUploadContent();
});

document.getElementById('chatResponsesBtn').addEventListener('click', () => {
  fetchData('chatResponsesBtn', 'Question and Answer Details');
});

document.getElementById('tagTableBtn').addEventListener('click', () => {
  fetchData('tagTableBtn', 'Tag Table');
});

document.getElementById('unansweredBtn').addEventListener('click', () => {
  fetchData('unansweredBtn');
});

document.getElementById('chatbotDemoBtn').addEventListener('click', () => {
  contentContainer.innerHTML = '<p>Chatbot Demo content goes here...</p>';
});


function fetchData(buttonId, heading) {
  fetch(`http://127.0.0.1:5000/get_data/${buttonId}`)
    .then(response => response.json())
    .then(data => {
      let tableHTML = `<div class="table-container"><h2>${heading}</h2>`;
      tableHTML += '<table cellspacing="0" cellpadding="5" border="1" style="width: 100%;">';
      tableHTML += '<thead><tr>';
      tableHTML += '<th>Question</th>';
      tableHTML += '<th>Answer</th>';
      tableHTML += '<th>Tag</th>';
      tableHTML += '<th>Option</th>';
      tableHTML += '</tr></thead><tbody>';

      for (const row of data) {
        tableHTML += '<tr>';
        tableHTML += `<td contenteditable="true" style="border: 1px solid #ccc; padding: 5px;">${row[0] || ''}</td>`;
        tableHTML += `<td contenteditable="true" style="border: 1px solid #ccc; padding: 5px;">${row[1] || ''}</td>`;
        tableHTML += `<td contenteditable="true" style="border: 1px solid #ccc; padding: 5px;">${row[2] || ''}</td>`;
        tableHTML += `<td contenteditable="true" style="border: 1px solid #ccc; padding: 5px;">${row[3] || ''}</td>`;
        tableHTML += '</tr>';
      }

      tableHTML += '</tbody></table></div>';
      contentContainer.innerHTML = tableHTML;
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
}

// Event listener for header icon
headerIcon.addEventListener('click', () => {
  alert('Personal Information and Logout option goes here...');
});

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