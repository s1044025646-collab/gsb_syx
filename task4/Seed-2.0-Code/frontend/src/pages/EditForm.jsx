import { useNavigate, useParams } from 'react-router-dom';
import { useState, useEffect } from "react";
import Swal from "sweetalert2";
import { notesAPI } from "../api/notesAPI";

export default function EditForm() {
    const { id } = useParams();
    const [note, setNote] = useState({
        title: '',
        details: '',
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchNote = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await notesAPI.getNoteById(id);
                if (data.content) {
                    setNote(data.content);
                }
            } catch (err) {
                setError(err.message || 'Failed to fetch note');
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: err.message || 'Failed to fetch note',
                });
            } finally {
                setLoading(false);
            }
        };
        fetchNote();
    }, [id]);

    const changeHandler = (event) => {
        const {name, value} = event.target;
        setNote({ ...note, [name]: value });
    };

    const navigate = useNavigate();
    const submitHandler = async (event) => {
        event.preventDefault();
        try {
            setSaving(true);
            await notesAPI.updateNote(id, note);
            navigate(`/details/${id}`);
            Swal.fire('Your note has been updated successfully!');
        } catch (err) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: err.message || 'Failed to update note',
            });
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '2rem' }}>Loading...</div>
        );
    }

    if (error) {
        return (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#f5400f' }}>Error: {error}</div>
        );
    }

  return (
    <div>
            <h1 className="headline">
                Edit <span>Note</span>
            </h1>
            <form className="note-form" onSubmit={submitHandler}>
                <input
                    type="text"
                    name="title"
                    value={note.title}
                    onChange={changeHandler}
                    placeholder="Title of Note ..."
                />
                <textarea
                    name="details"
                    rows="5"
                    value={note.details}
                    onChange={changeHandler}
                    placeholder="Descride Your Note ..."
                ></textarea>
                <button type="submit" disabled={saving}>
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
            </form>
        </div>
  )
}
