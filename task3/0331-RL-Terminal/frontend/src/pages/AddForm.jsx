import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Swal from "sweetalert2";
import { addNote } from "../api/notes";
import 'animate.css/animate.min.css';

export default function AddForm() {
    const [note, setNote] = useState({
        title: "",
        details: "",
    });
    const [loading, setLoading] = useState(false);

    const changeHandler = (event) => {
      const { name, value} = event.target;
      setNote( {...note, [name]: value});
    };

    const navigate = useNavigate();
    const submitHandler = async (event) => {
      event.preventDefault();
      setLoading(true);
      try {
        await addNote(note);
        navigate('/');
        Swal.fire({
          title: 'Your note has been added successfully!',
          showClass: {
            popup: 'animate__animated animate__fadeInDown'
          },
          hideClass: {
            popup: 'animate__animated animate__fadeOutUp'
          }
        });
      } catch (err) {
        Swal.fire({
          icon: 'error',
          title: 'Oops...',
          text: err.response?.data?.msg || 'Failed to save note!',
        });
      } finally {
        setLoading(false);
      }
    };
    return (
        <div>
            <h1 className="headline">
                Add <span>Note</span>
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
                <button type="submit" disabled={loading}>
                  {loading ? 'Saving...' : 'Save Note'}
                </button>
            </form>
        </div>
    );
}
