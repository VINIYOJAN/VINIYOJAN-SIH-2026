# VINIYOJAN | SIH 2026

### Smart Fixed Deposit Receipt (FDR) Management & Verification

**A FinTech prototype by Team VINIYOJAN for Smart India Hackathon 2026.**

<p align="center">
  <a href="https://github.com/viniyogan/VINIYOJAN-SIH-2026/blob/main/VINIYOJAN_SIH_2026_Demo.mp4">
    <img src="https://img.shields.io/badge/▶_Watch_Project_Demo-Video-DC2626?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch Project Demo"/>
  </a>
</p>

---

## About the Project

VINIYOJAN explores how digital workflows can make Fixed Deposit Receipt (FDR) management more organized, transparent, and efficient.

The prototype combines a web interface, backend services, and a simulated banking service to demonstrate FDR-related record management, document review, verification workflows, and maturity monitoring.

## Features

- 🏦 **FDR Management** — Organize and review fixed deposit records.
- 📄 **Document Review** — Support document submission and verification workflows.
- ⏰ **Maturity Monitoring** — Track maturity-related information and alerts.
- 🔎 **Verification Workflow** — Demonstrate verification using a simulated bank service.
- 📊 **Audit Visibility** — Improve visibility into application activities.

*Feature availability depends on the current prototype implementation.*

## Technology Stack

<p align="left">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"/>
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest"/>
  <img src="https://img.shields.io/badge/Recharts-22B5BF?style=for-the-badge&logoColor=white" alt="Recharts"/>
</p>

## System Architecture

```mermaid
flowchart TD
    A[User] --> B[React + Vite Frontend]
    B --> C[FastAPI Backend]
    C --> D[Database Layer]
    C --> E[Mock Bank Service]
    C --> F[Alerts and Workflows]
```

The frontend communicates with the backend API. The backend manages application logic and configured data operations, while the mock-bank service simulates banking interactions for demonstration purposes.

## Repository Structure

```text
VINIYOJAN-SIH-2026/
├── VINIYOJAN_SIH_2026_Demo.mp4
└── VINIYOJAN/
    ├── backend/
    │   ├── app/                 # API and application logic
    │   ├── tests/               # Backend tests
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── frontend/
    │   ├── src/                 # UI source and styles
    │   ├── index.html
    │   ├── package.json
    │   └── Dockerfile
    ├── mock-bank/               # Simulated bank service
    ├── docs/                    # Architecture and demo guides
    ├── scripts/                 # Demo utilities
    ├── docker-compose.yml       # Service orchestration
    ├── .env.example             # Environment template
    ├── .gitignore
    ├── README.md                # Detailed project documentation
    
```

## Getting Started

### Prerequisites

- Git
- Node.js and npm
- Python and pip
- Docker Desktop with Docker Compose (for containerized setup)

### 1. Clone the Repository

```bash
git clone https://github.com/viniyogan/VINIYOJAN-SIH-2026.git
cd VINIYOJAN-SIH-2026/VINIYOJAN
```

### 2. Configure Environment Variables

Review `.env.example` and follow the project's configuration instructions. Create the required local environment file with appropriate values.

**Never commit real credentials, API keys, passwords, or private financial data.**

### 3. Start with Docker

Run from the `VINIYOJAN/` directory:

```bash
docker compose up --build
```

Review `docker-compose.yml` for service ports and configuration.

To stop the services:

```bash
docker compose down
```

### Run the Frontend Separately

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite. For backend setup, install `backend/requirements.txt` and follow the backend's configuration and startup instructions.

## Project Documentation

| Resource | Description |
|---|---|
| [Architecture](VINIYOJAN/docs/architecture.md) | System design and components |
| [Demo Script](VINIYOJAN/docs/demo-script.md) | Project demonstration guide |
| [Implementation Status](VINIYOJAN/docs/IMPLEMENTATION_STATUS.md) | Current implementation details |
| [Submission Checklist](VINIYOJAN/SUBMISSION_CHECKLIST.md) | Submission preparation |
| [Detailed README](VINIYOJAN/README.md) | Application-level documentation |

## 🎥 Video Demonstration

**VINIYOJAN — SIH 2026 Project Demo**

[▶ View the demo video on GitHub](https://github.com/viniyogan/VINIYOJAN-SIH-2026/blob/main/VINIYOJAN_SIH_2026_Demo.mp4)

GitHub may not preview the MP4 inline. If playback is unavailable, open the video file page and use its download option.

## Team

**Team VINIYOJAN**  
Smart India Hackathon 2026

## Disclaimer

VINIYOJAN is a student-built demonstration prototype. The mock-bank service simulates banking interactions and does not represent an official bank integration or authoritative financial verification. The project is not presented as a production-ready financial system.

---

<p align="center">
  <sub>Built with curiosity, collaboration, and practical FinTech problem-solving.</sub>
</p>
