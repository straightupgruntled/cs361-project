"""Microservice client classes for ZMQ-based microservice communication."""

import io
import json
import zmq
from kivy.core.image import Image as CoreImage

# Small Pool Microservice - ImageScraper

class ImageMicroClient:
    def __init__(self, port=7050):
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{port}")

    def fetch_raw(self, url, edits=[], output_format="PNG"):
        request = {"url": url, "image-edits": edits, "output_format": output_format}
        self.socket.send_json(request)
        meta, image_bytes = self.socket.recv_multipart()
        meta = json.loads(meta.decode())
        if meta.get("status") != "success":
            raise RuntimeError(meta.get("message", "Image fetch failed"))
        return meta, image_bytes

    def fetch_texture(self, url, edits=[], output_format="PNG"):
        meta, image_bytes = self.fetch_raw(url, edits, output_format)
        texture = CoreImage(io.BytesIO(image_bytes), ext=output_format.lower()).texture
        return texture

    def fetch(self, url, edits=[], output_format="PNG"):
        # Convenience wrapper: returns Kivy texture directly
        return self.fetch_texture(url, edits, output_format)


# Large Pool Microservices - FileImporter, UndoRedo, FuzzSearch

class FileImporterMicroClient:
    def __init__(self, port=7051):
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{port}")

    def open_file_dialog(self, file_types=["png", "jpg", "jpeg", "gif", "all"]):
        message = "R " + " ".join(file_types)
        try:
            self.socket.send_string(message)
            file_path = self.socket.recv_string()
            if file_path == "unknown file path":
                raise RuntimeError("No file selected")
            return file_path
        except Exception as e:
            raise RuntimeError(f"Error opening file dialog: {e}")


class UndoRedoClient:
    def __init__(self, state=None, port=7052):
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{port}")
        if state:
            self.record(state)

    def record(self, state):
        self.socket.send_json({"command": "record", "action": "draw", "state": state})
        return self.socket.recv_json()

    def undo(self):
        self.socket.send_json({"command": "undo"})
        return self.socket.recv_json()

    def redo(self):
        self.socket.send_json({"command": "redo"})
        return self.socket.recv_json()


class FuzzSearchMicroClient:
    def __init__(self, port=7053):
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{port}")

    def search_projects(self, search_term, project_names):
        if not search_term.strip() or not project_names:
            return [(name, 100) for name in project_names]

        # Format message for microservice: "R search_term 'project1' 'project2' ..."
        message = f"R {search_term} " + " ".join(f"'{name}'" for name in project_names)
        try:
            self.socket.send_string(message)
            response = self.socket.recv_string()

            # Parse response: "[95, 70, 45]" -> [95, 70, 45]
            scores = json.loads(response)

            # Return list of (name, score) tuples sorted by score
            results = list(zip(project_names, scores))
            results.sort(key=lambda x: x[1], reverse=True)
            return results
        except Exception as e:
            print(f"Error during fuzzy search: {e}")
            return [(name, 100) for name in project_names]
