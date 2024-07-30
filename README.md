
# Generative AI Powered Search

## Project Description
The Generative AI Powered Search project is a web application designed to provide accurate and helpful responses to user queries based on context and chat history. It utilizes advanced AI models to generate responses and refine user queries. The application supports uploading and processing PDF documents, allowing users to ask questions about their content.

## Technology Stack
- **Backend:** FastAPI, Flask
- **Frontend:** Streamlit
- **Database:** Chroma
- **Libraries and Frameworks:** Langchain, Transformers, Streamlit Extras, Streamlit Authenticator, PyPDFLoader
- **AI Models:** Ollama, SentenceTransformerEmbeddings
- **Other Tools:** Docker, OpenTelemetry, Kubernetes
![Image]https://github.com/rahulkher/genAILLM/genaillm-pic1.jpg
## Folder Structure
\```
.
├── app.py
├── config.py
├── data.py
├── requirements.txt
└── README.md
\```

## Installation and Execution

### Prerequisites
- Python 3.x

### Installation
1. Clone the repository:
    \```sh
    git clone <https://github.com/rahulkher/genAILLM>
    \```
2. Navigate to the project directory:
    \```
    cd <project-directory>
    \```
3. Install the required packages:
    \```
    pip install -r requirements.txt
    \```

### Configuration
1. Set up the `.streamlit` directory and config file:
    \```
    python config.py
    \```
2. Replace the placeholder paths and API keys in `app.py` and `data.py` with your actual paths and keys.

### Execution
1. Run the Streamlit application:
    \```
    streamlit run app.py
    \```
2. Open your web browser and navigate to the provided URL (usually `http://localhost:8501`).

## Usage
- **Home Page:** Provides a chat interface for querying documents.
- **Admin Panel:** Allows managing uploaded documents and viewing the database.
- **About Us:** Provides information about the application.

## Key Features
- **Query Documents:** Upload PDF documents and ask questions about their content.
- **Refine Queries:** AI model refines user queries for improved clarity.
- **Real-time Responses:** Get accurate responses based on context and chat history.
- **Document Management:** Admin panel for managing uploaded documents and database entries.

## Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.

## Contact
For any inquiries, please contact [Rahul Kher] at [rahul.kher22@gmail.com].
