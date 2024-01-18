import psycopg2
try:
    conn = psycopg2.connect("dbname='someaitools' user='maxloo' host='localhost' password='4444'")
    print("Connected successfully")
except Exception as e:
    print("Unable to connect to the database")
    print(e)

def summarize_pdf(file_path, filename):
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load_and_split()
        docs_two_pages = docs[:2]
        summaries = []
        text_splitter1 = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        llm = ChatOpenAI(model_name="gpt-3.5-turbo-1106")
        for page_number, page_text in enumerate(docs_two_pages, start=1):
            word_count = len(str(page_text).split())
            target_summary_length = int(word_count * 0.25)  # 25% of the original length

            texts1 = text_splitter1.split_text(str(page_text))
            chain1 = load_summarize_chain(llm, chain_type="map_reduce")

            # Adjust the summarization process to aim for the target_summary_length
            # This might involve adjusting the prompt or parameters for your model.
            # For example, you might include a prompt like:
            # "Please summarize the following text in about {target_summary_length} words."
            # Or adjust the parameters of the summarization chain if it supports that.
            page_summary = chain1.run(text_splitter1.create_documents(texts1), target_length=target_summary_length)

            summaries.append(f"Page {page_number} (Word Count: {word_count}): {page_summary}\n\n")
        combined_summary = '  '.join(summaries)
        all_combined = "Summary of " + filename + ":\n\n" + combined_summary
        total = all_combined
    except Exception as e:
        print(traceback.format_exc())
        return f"An error occurred: {str(e)}"
    return total
