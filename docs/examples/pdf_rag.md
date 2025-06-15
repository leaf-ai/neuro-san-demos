# PDF RAG Assistant

The **PDF RAG Assistant** answers user queries using Retrieval-Augmented Generation (RAG) over a set of PDF files.

---

## File

[pdf_rag.hocon](../../registries/pdf_rag.hocon)

---

## Example Conversation

### Human:
```
what is the Evaluation Criteria in the rfp?
```

### AI (PDF RAG Assistant):
```
The evaluation criteria in the RFP are as follows:

    1. Any award made pursuant to this RFP will be based upon the proposal with appropriate information contained in the RFP.
    2. Vendors must address all matters raised in the RFP.
    3. Statements made about the performance and specifications of the proposed solution will be considered.
    4. Consideration is given to operational, technical, cost, and management requirements.
    5. Evaluation of offers will be based upon the Vendor’s responsiveness.

These criteria are used to assess the suitability of proposals and ensure they meet the necessary requirements outlined in the RFP.
```

---

## Architecture Overview

### Frontman Agent: **PDF RAG Assistant**
- Entry point for user queries.
- Parses the query and routes it to the appropriate tool (`rag_retriever`).
- Collects and composes responses from tools.

### Tool: `rag_retriever`
- Loads PDFs, builds an in-memory vector store, and answers questions based on content.
- Useful when information is embedded in static documents.

#### User-Defined Arguments
*Required*
- `urls` (list): List of PDF URLs to use for RAG.

*Optional*
- `save_vector_store` (bool): Save the vector store to a JSON file.
- `vector_store_path`(str): Path to save/load the vector store (absolute or relative to `neuro-san-studio/coded_tools/pdf_rag/`).

---

## Debugging Hints

Check the following during development or troubleshooting:

- Ensure the **agent** tool is correctly identified as the frontman (no parameters in its function definition).
- Confirm that required arguments (like `query`) are passed correctly.
- Make sure that all URLs are valid.
- Validate vectorstore loading and document parsing for the RAG tool.
- Look at logs to ensure smooth delegation across tool calls and proper response integration.

---
