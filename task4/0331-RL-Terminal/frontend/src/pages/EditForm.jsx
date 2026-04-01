import { useNavigate, useParams } from 'react-router-dom';
import { useState, useEffect } from "react";
import Swal from "sweetalert2";
import { getNoteById, updateNote } from "../api/notes";

export default function EditForm() {
    const { id } = useParams();
    const [note, setNote] = useState({
        title: '',
        details: '',
    });
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const fetchNote = async () => {
            try {
                const data = await getNoteById(id);
                setNote(data.content);
            } catch (err) {
                Swal.fire({
                    icon: 'error',
                    title: 'Oops...',
                    text: 'Failed to load note!',
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
    }

    const navigate = useNavigate();
    const submitHandler = async (event) => {
        event.preventDefault();
        setSubmitting(true);
        try {
            await updateNote(id, note);
            navigate(`/details/${id}`);
            Swal.fire('Your note has been updated successfully!');
        } catch (err) {
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: err.response?.data?.msg || 'Failed to update note!',
            });
        } finally {
            setSubmitting(false);
        }
    }

    if (loading) {
        return <div style={{ textAlign: 'center', marginTop: '2rem' }}>Loading...</div>;
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
                    required
                />
                <textarea
                    name="details"
                    rows="5"
                    value={note.details}
                    onChange={changeHandler}
                    placeholder="Describe Your Note ..."
                    required
                ></textarea>
                <button type="submit" disabled={submitting}>
                    {submitting ? 'Saving...' : 'Save Changes'}
                </button>
            </form>
        </div>
  )
}
