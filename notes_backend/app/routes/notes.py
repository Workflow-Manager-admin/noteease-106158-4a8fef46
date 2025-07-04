from flask_smorest import Blueprint
from flask.views import MethodView
from flask import abort
from marshmallow import Schema, fields, validate

# In-memory storage for notes
NOTES = {}
NEXT_NOTE_ID = 1

blp = Blueprint(
    "Notes",
    "notes",
    url_prefix="/notes",
    description="CRUD endpoints for notes"
)

class NoteSchema(Schema):
    id = fields.Int(dump_only=True, description="Unique ID of the note")
    title = fields.Str(required=True, validate=validate.Length(min=1), description="Title of the note")
    content = fields.Str(required=True, validate=validate.Length(min=1), description="Content of the note")

class NoteCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1), description="Title of the note")
    content = fields.Str(required=True, validate=validate.Length(min=1), description="Content of the note")

class NoteUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1), description="Title of the note")
    content = fields.Str(validate=validate.Length(min=1), description="Content of the note")

def get_note_or_404(note_id: int):
    note = NOTES.get(note_id)
    if note is None:
        abort(404, description=f"Note with id {note_id} not found")
    return note

@blp.route("/")
class NotesList(MethodView):
    # PUBLIC_INTERFACE
    def get(self):
        """
        Get all notes
        Returns a list of all notes
        """
        return [note for note in NOTES.values()]

    # PUBLIC_INTERFACE
    @blp.arguments(NoteCreateSchema)
    @blp.response(201, NoteSchema)
    def post(self, note_data):
        """
        Create a new note
        ---
        Request Body: {title: str, content: str}
        Response: The created note object
        """
        global NEXT_NOTE_ID
        note = {
            "id": NEXT_NOTE_ID,
            "title": note_data["title"],
            "content": note_data["content"]
        }
        NOTES[NEXT_NOTE_ID] = note
        NEXT_NOTE_ID += 1
        return note

@blp.route("/<int:note_id>")
class NoteResource(MethodView):
    # PUBLIC_INTERFACE
    @blp.response(200, NoteSchema)
    def get(self, note_id):
        """
        Get a note by its id
        Returns the note if found
        """
        return get_note_or_404(note_id)

    # PUBLIC_INTERFACE
    @blp.arguments(NoteUpdateSchema)
    @blp.response(200, NoteSchema)
    def put(self, note_data, note_id):
        """
        Update an existing note
        Updates title, content or both
        """
        note = get_note_or_404(note_id)
        if "title" in note_data:
            note["title"] = note_data["title"]
        if "content" in note_data:
            note["content"] = note_data["content"]
        return note

    # PUBLIC_INTERFACE
    def delete(self, note_id):
        """
        Delete a note by its id
        Returns success status
        """
        get_note_or_404(note_id)
        del NOTES[note_id]
        return {"message": f"Note {note_id} deleted"}
