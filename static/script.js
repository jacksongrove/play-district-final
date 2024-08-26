// Global variable to store the thread result
var thread;

// Step 1: Define the initialize function that runs on page load
async function initialize() {
  try {
    const response = await fetch("/initialize", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    const data = await response.json();

    // Step 2: Assign the result to the global variable
    thread = data.result;
    console.log("Python code result:", thread);
  } catch (error) {
    console.error("Error:", error);
  }
}

// Step 3: Automatically run initialize() when the page loads
window.onload = initialize;

// Step 4: Modify the sendMessage function to include the thread parameter
async function sendMessage() {
  const userInput = document.getElementById("user-input").value;
  if (!userInput) return;

  const chatBox = document.getElementById("chat-box");

  // Add user message to chat box
  const userMessage = document.createElement("div");
  userMessage.className = "chat-message user-message";
  userMessage.innerText = userInput;
  chatBox.appendChild(userMessage);

  // Clear the input field
  document.getElementById("user-input").value = "";

  // Scroll to the bottom
  chatBox.scrollTop = chatBox.scrollHeight;

  // Send user message to server with the thread parameter
  const response = await fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: userInput,
      thread: thread,  // Include the thread parameter in the request
    }),
  });
  const data = await response.json();

  // Add bot response to chat box
  const botMessage = document.createElement("div");
  botMessage.className = "chat-message bot-message";
  botMessage.innerHTML = data.reply;
  chatBox.appendChild(botMessage);

  // Scroll to the bottom
  chatBox.scrollTop = chatBox.scrollHeight;
}
