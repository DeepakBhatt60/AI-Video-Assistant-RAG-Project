from dotenv import load_dotenv
from utils.audio_processor import process_input, get_youtube_transcript_text
from core.transcriber import transcribe_all
from core.summary import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

def run_pipeline(source:str, language : str="english")->dict:
    print("starting AI Video Assistant")

    transcript = None
    is_youtube = source.startswith("http://") or source.startswith("https://")

    if is_youtube:
        print("Trying YouTube captions first (fast path, no download needed)...")
        transcript = get_youtube_transcript_text(source)

    if transcript:
        print("Captions found — skipping audio download and transcription.")
    else:
        print("No usable captions found — falling back to audio download + transcription.")
        chunks = process_input(source)
        transcript = transcribe_all(chunks, language)

    print(f"raw transcription (first 300 characters) {transcript[:300]}")
    title=generate_title(transcript)

    summary=summarize(transcript)

    action_item=extract_action_items(transcript)

    decisions=extract_key_decisions(transcript)

    questions=extract_questions(transcript)

    rag_chain=build_rag_chain(transcript)

    return{
        "title": title,
        "transcript":transcript,
        "summary":summary,
        "action_items":action_item,
        "key_decisions":decisions,
        "open_questions":questions,
        "rag_chain":rag_chain, 
    }
if __name__ == "__main__":
    # CLI entry point
    source = input("Enter YouTube URL or local file path: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"
    result = run_pipeline(source, language)

    print("\n" + "=" * 60)
    print(f"📌 Title: {result['title']}")
    print(f"\n📋 Summary:\n{result['summary']}")
    print(f"\n✅ Action Items:\n{result['action_items']}")
    print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")
    print(f"\n❓ Open Questions:\n{result['open_questions']}")
    print("=" * 60)

    # Phase 2 — Chat with your meeting via RAG
    print("\n💬 Chat with your meeting (type 'exit' to quit)\n")
    rag_chain = result["rag_chain"]
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break
        if not question:
            continue
        answer = ask_question(rag_chain, question)
        print(f"\n🤖 Assistant: {answer}\n")
