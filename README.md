# PyTone

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Features](#2-features)
3. [Architecture and Tech Stack](#3-architecture-and-tech-stack)
4. [Algorithm](#4-algorithm)
5. [Installation and Setup](#5-installation-and-setup)
   - [Prerequisites](#prerequisites)
   - [MySQL Quick Setup](#mysql-quick-setup)
   - [Project Installation](#project-installation)

## 1. Project Overview

PyTone is a **Music Recognition Application** designed to identify songs from short audio snippets. It functions similarly to Shazam, allowing users to train the system with new music via YouTube and identify tracks using their microphone.

The application uses **audio fingerprinting** to create unique hashes based on spectral peaks, ensuring accuracy even with short or noisy recordings.

## 2. Features

### 🎧 Identification

- **Microphone Input:** Record a short clip directly from the UI to identify a song.
- **Song Matching:** Uses a custom hashing algorithm to match audio fingerprints against the database.
- **Result Display:** Shows the song title, artist and redirects to the youtube video.

### 🧠 Training (Learning)

- **YouTube Integration:** Paste a YouTube URL to automatically download, process, and add a song to the database.
- **Automatic Fingerprinting:** Converts audio into a spectrogram, extracts peaks, and generates hashes for storage.

### 🖥️ User Interface

- **Web Interface:** Built with **Gradio** for a clean, responsive local web app.
- **Navigation:** Separate tabs for **Identification**, **Training New Songs**, **Already Trained Songs**, and **Identification History**.

## 3. Architecture and Tech Stack

### Tech Stack

| Component            | Technology          | Description                                               |
| -------------------- | ------------------- | --------------------------------------------------------- |
| **Frontend / UI**    | **Gradio**          | Interactive web interface for recording audio and inputs. |
| **Core Logic**       | **Python**          | Handles signal processing and application logic.          |
| **Audio Processing** | **Librosa / NumPy** | Used for Spectrogram generation and peak extraction.      |
| **Database**         | **MySQL**           | Stores song metadata and fingerprint hashes.              |
| **External API**     | **yt-dlp**          | Fetches audio and metadata from YouTube.                  |

### System Flow

1. **Input:** Audio is captured via **Mic** (Identification) or **YouTube** (Training).
2. **Preprocessing:** Signal is converted to **Mono** and **downsampled**.
3. **Spectrogram:** **FFT** (Fast Fourier Transform) converts time-domain signal to **frequency-domain**.
4. **Fingerprinting:** Local **peaks** are extracted and hashed using the **"Anchor-Target"** method.
5. **Matching/Storage:** Hashes are stored in **MySQL** (Training) or queried to find the **best match** (Identification).

## 4. Algorithm

PyTone implements a constellation-based fingerprinting algorithm:

1. **Spectrogram:** Audio is divided into overlapping windows to create a 2D map of frequency vs. time.
2. **Peak Extraction:** Identifies the "loudest" points (peaks) in specific frequency bands (Low, Mid, High).
3. **Hashing:**

- Pairs an **Anchor Point** with a **Target Point**.
- Creates a hash based on: `Frequency1 | Frequency2 | TimeDelta`.

4. **Matching:** In the identification phase, the system looks for the highest number of matching hashes that align with a specific time offset relative to the original song.

## 5. Installation and Setup

### Prerequisites

- **Python 3.8+**
- **MySQL Server**
- **FFmpeg** (Required by `yt-dlp` and `librosa` for audio processing).

### MySQL Quick Setup

1. Install MySQL Server.
2. Open your SQL shell or Workbench and run the following commands:

```sql
-- Create a new use
CREATE USER 'pytone_user'@'localhost' IDENTIFIED BY 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON *.* TO 'pytone_user'@'localhost';
FLUSH PRIVILEGES;
```

### Project Installation

1. **Clone the repository:**

```sh
git clone https://github.com/adrianageamanu/PyTone
cd ./PyTone
```

2. **Create and Activate Virtual Environment:**

```sh
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies:**

```sh
pip install -r requirements.txt
```

4. **Environment Configuration:**
   Copy the example environment file and configure your database credentials:

```sh
cp .env.example .env
```

Open `.env` and fill in your `DB_HOST`, `DB_USER` and `DB_PASSWORD`.

5. **Run the Application:**

```sh
python3 app.py
```
