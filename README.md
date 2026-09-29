# SETC  Bus Chatbot

A web-based bus information retrieval chatbot that allows users to interactively query bus routes, schedules, and location information.

The application uses a Flask backend to process user queries against structured bus-service datasets and provides an interactive chatbot interface through Typebot.

## 🚀 Live Demo

**Try the chatbot:** [BUS Information Retrieval Bot](https://typebot.co/bus-tracking-bot-3hucl5s)

The chatbot is publicly accessible and can be used from both desktop and mobile devices.

---

## 📌 Overview

The SETC Bus Chatbot is designed to simplify access to bus transportation information through a conversational interface.

Users can enter queries such as:

- Bus route information between two locations
- Bus service details
- Route numbers
- Source and destination information
- General chatbot queries

The backend processes the query and retrieves the relevant information from structured bus datasets.

---

## ✨ Features

- Interactive chatbot-based bus information retrieval
- Bus route and source/destination lookup
- Bus schedule information retrieval
- Location-based query processing
- Fuzzy matching for location names
- Structured JSON-based chatbot responses
- Flask REST API
- Interactive Typebot frontend
- Web-based deployment
- Publicly accessible live demo

---

## 🏗️ System Architecture

```text
User
  │
  ▼
Typebot Chatbot Interface
  │
  ▼
Flask Application
  │
  ├── Query Processing
  │
  ├── JSON Response Matching
  │
  └── Bus Route Search
          │
          ▼
   cleaned_data.csv
          │
          ▼
     Query Result
          │
          ▼
     Typebot Response
