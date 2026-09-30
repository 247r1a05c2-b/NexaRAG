import sys
import types


def _install_stubs():
    if "chromadb" not in sys.modules:
        chromadb = types.ModuleType("chromadb")
        chromadb.PersistentClient = lambda *args, **kwargs: None
        sys.modules["chromadb"] = chromadb

    if "streamlit" not in sys.modules:
        streamlit = types.ModuleType("streamlit")
        streamlit.secrets = {}
        sys.modules["streamlit"] = streamlit

    if "google" not in sys.modules:
        google = types.ModuleType("google")
        genai = types.ModuleType("google.genai")
        genai.Client = lambda *args, **kwargs: None
        google.genai = genai
        sys.modules["google"] = google
        sys.modules["google.genai"] = genai

    if "sentence_transformers" not in sys.modules:
        st = types.ModuleType("sentence_transformers")
        st.SentenceTransformer = lambda *args, **kwargs: None
        sys.modules["sentence_transformers"] = st


_install_stubs()
