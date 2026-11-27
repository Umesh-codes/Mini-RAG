# Project Guidelines: Spec-Driven Development

1. **Workflow Enforcement (OpenSpec):**
   - Always use OpenSpec for any new feature, bug fix, or refactor.
   - Run `openspec-propose` to create the 4 planning artifacts (`proposal.md`, `specs/`, `design.md`, `tasks.md`) first.
   - Never write application code until the user gives explicit approval (`apply`).
2. **Tech Stack Boundaries:**
   - Python 3.10+
   - LangChain & ChromaDB (`./chroma_db`)
   - Local AI Server: LM Studio at `http://127.0.0.1:1235/v1`
3. **Security:** Never commit `.env` or secrets.