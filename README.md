Health AI Assistant (IBM Granite GUI) - Final Report Format
1. INTRODUCTION
1.1 Project Overview
The Health AI Assistant is a dedicated, standalone graphical user interface (GUI) application developed using Python. Its core functionality revolves around providing users with general health information and answering common health-related questions. This is achieved by integrating with and leveraging the advanced capabilities of IBM Watsonx AI's Granite large language models (LLMs). The application is designed to offer a direct, interactive conversational experience within a single window, eliminating the complexities associated with web-based deployments or separate backend server management.
1.2 Purpose
The primary purpose of this project is to create an accessible and user-friendly AI assistant focused on health inquiries. It aims to demonstrate the practical application of IBM Watsonx AI's generative models in a desktop environment, providing immediate, informative responses to health-related questions while securely handling API credentials through environment variables. The project serves as a clear example of how to build an intelligent, responsive GUI application that interacts with powerful cloud-based AI services without exposing sensitive information.
2. IDEATION PHASE
2.1 Problem Statement
The problem addressed is the need for an easily accessible, interactive, and secure AI tool that can provide general health information and answer common health questions. Users often seek quick, reliable information without navigating complex websites or dealing with multi-component software setups. The challenge is to deliver this intelligence directly to the user's desktop while adhering to best practices for API key security and ensuring the application remains responsive during AI processing.
3. REQUIREMENT ANALYSIS
3.1 Customer Journey Map
(This section would typically illustrate a user's step-by-step interaction with the system. For this GUI, a simplified journey would involve: Launching the app -> Typing a question -> Receiving an AI response -> Continuing the conversation or exiting.)
3.2 Solution Requirement
The solution requires:
A user-friendly graphical interface for input and output.
Integration with IBM Watsonx AI's Granite models for natural language understanding and generation.
Secure handling of IBM Cloud API keys and Project IDs via environment variables.
Asynchronous processing of AI requests to maintain GUI responsiveness.
Clear communication of AI's role as an assistant, not a medical professional.
Error handling for API communication and configuration issues.
Cross-platform compatibility (inherent with Python and tkinter).
3.3 Data Flow Diagram


Flow Description:
User Input: User types a query into the GUI.
GUI to Background Thread: The GUI (main thread) passes the query to a new background thread.
Authentication (Initial): A background thread (initiated at startup) calls IBM Cloud IAM with the IBM_API_KEY to get an access_token (IAM Token).
AI Request: The background thread uses the IAM Token, IBM_PROJECT_ID, and the user's query to make an HTTP POST request to the WATSONX_AI_ENDPOINT (e.g., https://eu-de.ml.cloud.ibm.com/ml/v1-beta/generation/text).
IBM Watsonx AI Processing: The Granite model processes the full_prompt (which includes system instructions and the user's query) and generates a response.
Response to Queue: The AI's response is sent back to the background thread, which then places it into a queue.Queue.
Queue to GUI: The main GUI thread continuously monitors this queue. When a response is available, it retrieves it.
GUI Update: The GUI's chat display is updated with the AI's response.
3.4 Technology Stack
Programming Language: Python 3.x
GUI Framework: tkinter (Standard Python library)
HTTP Requests: requests library
Concurrency: threading module
Inter-thread Communication: queue module
Cloud AI Platform: IBM Watsonx AI
Foundation Model: IBM Granite (e.g., ibm/granite-13b-instruct-v2)
Authentication Service: IBM Cloud IAM
4. PROJECT DESIGN
4.1 Problem Solution Fit
This project directly addresses the problem of needing an accessible AI health assistant by providing a self-contained, desktop-based GUI. The use of Python and tkinter ensures broad compatibility and ease of distribution for a local application. By leveraging IBM Watsonx AI, it taps into state-of-the-art LLM capabilities. Crucially, the design prioritizes security by relying on environment variables for sensitive credentials, a robust solution that avoids hardcoding API keys. The threading implementation resolves the common GUI freezing issue associated with long-running network operations, ensuring a smooth user experience.
4.2 Proposed Solution
The proposed solution is a desktop application that functions as a conversational Health AI Assistant. It presents a simple chat interface where users can type questions. The application then securely communicates with IBM Watsonx AI, specifically using a Granite model, to generate relevant health information. The responses are displayed back to the user in the chat window. The application is designed to be self-contained within a single Python script, simplifying deployment and execution for end-users.
4.3 Solution Architecture
The architecture is a client-side (desktop) application with an integrated "backend" logic for API communication. It follows a multi-threaded design:
Main Thread (GUI): Responsible for rendering the tkinter GUI, handling user input events, and updating the display. It remains responsive by offloading heavy tasks.
Background Threads (API Calls): Dedicated threads are spawned for two main purposes:
Initial Authentication: To obtain an IAM token from IBM Cloud IAM.
AI Query Processing: To send user queries to the IBM Watsonx AI Granite model and receive responses.
Queue for Communication: A queue.Queue object acts as a safe conduit for passing results (like the IAM token or AI responses) from the background threads back to the main GUI thread for display, preventing race conditions or GUI update errors.
Environment Variables: External configuration for IBM_API_KEY, IBM_PROJECT_ID, and WATSONX_AI_ENDPOINT ensures sensitive data is not embedded in the code.
Prompt Engineering: Each AI request includes a carefully crafted system_instruction within the full_prompt to guide the Granite model's behavior and ensure health-specific, disclaimer-inclusive responses.
5. PROJECT PLANNING & SCHEDULING
5.1 Project Planning
(This section would detail project phases, timelines, and resource allocation. As this is a completed project, this section is not applicable for a retrospective report. For a new project, it would include phases like Requirements Gathering, Design, Development, Testing, Deployment.)
6. FUNCTIONAL AND PERFORMANCE TESTING
6.1 Performance Testing
Formal performance testing (e.g., load testing, stress testing) was not conducted for this single-user, local application. However, the use of threading ensures that the GUI remains responsive during the potentially time-consuming API calls to IBM Watsonx AI. Users will observe "AI is thinking..." status messages, but the application window itself will not freeze or become unresponsive. Functional testing involves verifying correct responses to health queries and proper handling of authentication and API errors.
7. RESULTS
7.1 Output Screenshots
Here is a screenshot of the application running in a terminal:

8. ADVANTAGES & DISADVANTAGES
Advantages:
Ease of Use: Single Python script, no complex web server setup required for the end-user.
Security: Credentials managed securely via environment variables.
Responsiveness: Multi-threading prevents GUI freezing during AI processing.
Direct AI Integration: Leverages powerful IBM Granite models directly.
Clear Persona: AI is explicitly guided to act as a health assistant with disclaimers.
Offline Development: Can be developed and tested locally without a deployed web server.
Disadvantages:
Scalability: Not designed for multi-user or high-traffic scenarios (a web application with a robust backend would be needed for that).
Deployment: Requires Python and requests library to be installed on the user's machine. Packaging into an executable (e.g., with PyInstaller) would add complexity.
Dependency on IBM Cloud: Requires an active IBM Cloud account, Watsonx AI service, and associated costs.
No Persistent Chat History: The current version does not save chat history between sessions.
Limited Customization: tkinter offers basic GUI elements; more complex or modern UIs would require other frameworks (e.g., PyQt, Kivy).
9. CONCLUSION
The Health AI Assistant project successfully demonstrates the creation of an interactive, desktop-based AI chatbot using Python's tkinter and integrating with IBM Watsonx AI's Granite models. It effectively addresses the need for secure credential handling and maintains GUI responsiveness through multi-threading. This project serves as a robust example of bringing advanced generative AI capabilities to a local application, providing a valuable tool for accessing general health information.
10. FUTURE SCOPE
Conversational Memory: Implement a mechanism to pass chat history to the Granite model for more coherent and context-aware conversations.
Model Selection: Allow users to select different Granite models or adjust generation parameters from the GUI.
Persistent Chat History: Implement saving and loading of chat conversations (e.g., to a local file or a simple database).
Enhanced UI/UX: Explore more modern GUI frameworks (e.g., PyQt, Kivy, or even Electron for a desktop web app) for a richer user experience.
Executable Packaging: Package the application into a standalone executable (e.g., using PyInstaller) to simplify distribution to users who don't have Python installed.
Speech-to-Text/Text-to-Speech: Integrate IBM Watson Speech services for voice interaction.
11. APPENDIX
Source Code (if any)
Dataset Link
This project utilizes a pre-trained large language model (IBM Granite) and does not rely on a specific external dataset for its operation. The model's knowledge is derived from its extensive training data.
GitHub
GitHub Repository: https://github.com/iamhemasunder/smartinternz.git
