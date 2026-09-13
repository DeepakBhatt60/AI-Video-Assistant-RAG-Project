# 🎥 AI Video Assistant – RAG

An AI-powered Video Assistant that converts YouTube videos or local audio/video files into useful insights such as **transcripts, summaries, action items, key decisions, and open questions**.

It also uses **Retrieval-Augmented Generation (RAG)** to allow users to ask questions about the processed video content.

---

## 🚀 Features

- 🎥 Process YouTube videos
- 📁 Process local audio/video files
- 📝 Automatic transcription
- 📋 AI-generated summaries
- ✅ Extract action items
- 🔑 Identify key decisions
- ❓ Extract open questions
- 💬 Chat with the processed video using RAG
- 🌐 Streamlit web interface
- 🌍 Supports English and Hinglish
- ⚡ Uses YouTube captions when available to avoid unnecessary audio downloading

---

## 🧠 How It Works

```text
YouTube URL / Local Video
          ↓
   Caption Extraction
          ↓
   Audio Processing
          ↓
     Transcription
          ↓
   Text Processing
          ↓
    ┌─────┴─────┐
    ↓           ↓
  Summary      RAG
    ↓           ↓
 Insights    Q&A Chat
