\# FlyRank Auth API



A backend authentication API built with FastAPI and Supabase as part of the FlyRank AI Internship Backend AI Engineering track.



\## Features



\- User signup

\- User login

\- Access and refresh token authentication

\- Protected profile endpoint

\- Protected dashboard endpoint

\- Token verification through Supabase

\- Protected logout endpoint

\- Swagger UI with Bearer authentication



\## Tech Stack



\- Python 3.12

\- FastAPI

\- Supabase Auth

\- Pydantic Settings

\- HTTPX

\- Uvicorn



\## Project Structure



```text

flyrank-auth-api/

├── app/

│   ├── main.py

│   ├── config.py

│   ├── supabase\_client.py

│   ├── auth\_dependency.py

│   └── routers/

│       └── auth.py

├── .env.example

├── .gitignore

├── README.md

└── requirements.txt

