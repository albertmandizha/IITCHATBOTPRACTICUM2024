const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");

let userMessage = null; // Variable to store message by user
const inputInitHeight = chatInput.scrollHeight;

const createChatLi = (message, className) => {
  // Create a chat <li> element with passed message and className
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", `${className}`);
  let chatContent =
    className === "outgoing"
      ? `<p></p>`
      : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
  chatLi.innerHTML = chatContent;
  chatLi.querySelector("p").textContent = message;
  return chatLi; // Return chat <li> element
};

const generateResponse = (chatElement, userMessage, action) => {
  const API_URL = "http://localhost:5000/sendMessage";
  const messageElement = chatElement.querySelector("p");

  // Clear any previous content in the message element
  messageElement.textContent = "";

  // Define the data to be sent in the AJAX request
  const requestData = {
    message: userMessage,
    action: action,
  };

  // Define the AJAX request options
  const requestOptions = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestData),
  };

  // Send AJAX request to Flask backend
  fetch(API_URL, requestOptions)
    .then((response) => response.json())
    .then((data) => {
      if (data.actions) {
        // If actions are received, create buttons for each question
        data.actions.forEach((action) => {
          const button = document.createElement("button");
          button.textContent = action.question;
          button.classList.add("action-button");
          button.addEventListener("click", () =>
            handleSubActionButton(action.question)
          );
          messageElement.appendChild(button);
        });
      } else {
        // If regular message received, display it
        messageElement.textContent = data.message;
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      messageElement.classList.add("error");
      messageElement.textContent = "Oops! Something went wrong. Please try again.";
    })
    .finally(() => (chatbox.scrollTo(0, chatbox.scrollHeight)));
};

const handleChat = () => {
  userMessage = chatInput.value.trim();
  if (!userMessage) return;

  // Clear the input textarea and set its height to default
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`;

  // Append the user's message to the chatbox
  chatbox.appendChild(createChatLi(userMessage, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);

  setTimeout(() => {
    // Display "Thinking..." message while waiting for the response
    const incomingChatLi = createChatLi("Thinking...", "incoming");
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);
    generateResponse(incomingChatLi, userMessage, null);
  }, 600);
};

chatInput.addEventListener("input", () => {
  // Adjust the height of the input textarea based on its content
  chatInput.style.height = `${inputInitHeight}px`;
  chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
  // If Enter key is pressed without Shift key and the window
  // width is greater than 800px, handle the chat
  if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleChat();
  }
});
sendChatBtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () =>
  document.body.classList.remove("show-chatbot")
);
chatbotToggler.addEventListener("click", () =>
  document.body.classList.toggle("show-chatbot")
);

const handleActionButton = (action) => {
  // Clear the input textarea and set its height to default
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`;

  // Append the user's action to the chatbox
  chatbox.appendChild(createChatLi(action, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);

  setTimeout(() => {
    // Display "Thinking..." message while waiting for the response
    const incomingChatLi = createChatLi("Thinking...", "incoming");
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);
    generateResponse(incomingChatLi, null, action); // Pass the action as userMessage
  }, 600);
};

const handleSubActionButton = (action) => {
  // Clear the input textarea and set its height to default
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`;

  // Append the clicked question to the chatbox
  chatbox.appendChild(createChatLi(action, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);

  setTimeout(() => {
    const incomingChatLi = createChatLi("Thinking...", "incoming");
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);
    generateResponse(incomingChatLi, action, null);
  }, 600);
};

const fetchTopActions = () => {
  const API_URL = "http://localhost:5000/getTopActions";

  fetch(API_URL)
    .then((response) => response.json())
    .then((data) => {
      const actionButtonsContainer = document.getElementById("actionButtons");
      actionButtonsContainer.innerHTML = ""; // Clear previous buttons

      data.actions.forEach((action) => {
        const button = document.createElement("button");
        button.textContent = action.action;
        button.classList.add("action-button");
        button.addEventListener("click", () => handleActionButton(action.action));
        actionButtonsContainer.appendChild(button);
      });
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};

// Call the fetchTopActions function when the page loads
window.addEventListener("load", fetchTopActions);