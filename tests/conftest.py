import sys
import types


def _install_stubs():
    chromadb = types.ModuleType("chromadb")
    chromadb.PersistentClient = lambda *args, **kwargs: None
    sys.modules["chromadb"] = chromadb
    streamlit = types.ModuleType("streamlit")
    streamlit.secrets = {}
    streamlit.session_state = {}
    sys.modules["streamlit"] = streamlit
    google = types.ModuleType("google")
    genai = types.ModuleType("google.genai")
    genai.Client = lambda *args, **kwargs: None
    google.genai = genai
    sys.modules["google"] = google
    sys.modules["google.genai"] = genai
    sentence_transformers = types.ModuleType("sentence_transformers")
    sentence_transformers.SentenceTransformer = lambda *args, **kwargs: None
    sys.modules["sentence_transformers"] = sentence_transformers


_install_stubs()
