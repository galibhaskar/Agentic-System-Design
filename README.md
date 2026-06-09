# Agentic System Design

# Environment Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/galibhaskar/agentic-system-design.git
   cd agentic-system-design
   ```

2. Install UV if you haven't already:
   ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Create a virtual environment and activate it:
   ```bash 
    uv env venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```  

3. Install the required dependencies:
   ```bash
    uv add -r requirements.txt
    ```

4. Set up your environment variables by creating a `.env` file in the root directory of the project and adding the necessary API keys. You can refer to the `.env.example` file for the required variables.

    ```bash
        cp .env.example .env
    ```

5. Run the project:
   ```bash
    uv run week1/semantic_rag.py
   ```
---

# Week 1:

# Class-1:
- Introduction to RAG
- Implementation of Semantic RAG
- Experimentation on topK and chunk parameters.
- Tracing in LangSmith
