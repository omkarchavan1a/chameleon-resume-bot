# INTEGRATIONS

## NVIDIA NIM API
- **Endpoint**: `https://integrate.api.nvidia.com/v1`
- **Model**: `meta/llama-3.3-70b-instruct`
- **Purpose**: Used for core generative AI tasks (converting an original "master" resume into an ATS-optimized, Chameleon-style resume).
- **Authentication**: Bearer Token provided via `NVIDIA_API_KEY`.
- **Client Library**: Open AI's python client (`openai`) is used to construct and send the chat completion requests.

## External Libraries (Frontend)
- **Marked.js**: CDN integration (`https://cdn.jsdelivr.net/npm/marked/marked.min.js`) for converting markdown to HTML.
- **html2pdf.js**: CDN integration (`https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js`) for converting HTML to PDF.
- **Google Fonts**: Inter and JetBrains Mono imported via CDN.
