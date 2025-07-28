def extract_info(text):
    lines = text.strip().split("\n")
    stream_key = ""
    title = ""
    source = ""
    loop = False

    for line in lines:
        line = line.strip()

        if line.lower().startswith("stream key:"):
            stream_key = line.split(":", 1)[1].strip()
        elif line.lower().startswith("title:"):
            title = line.split(":", 1)[1].strip()
        elif line.lower().startswith("source:"):
            source = line.split(":", 1)[1].strip()
        elif line.lower().startswith("loop:"):
            loop_value = line.split(":", 1)[1].strip().lower()
            loop = loop_value in ["yes", "true", "1"]

    return {
        "stream_key": stream_key,
        "title": title,
        "source": source,
        "loop": loop
    }
