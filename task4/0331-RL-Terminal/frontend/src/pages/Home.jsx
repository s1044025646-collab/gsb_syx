import React, { useEffect, useState } from "react";
import AddNote from "../components/AddNote";
import NoteCard from "../components/NoteCard";
import { getAllNotes } from "../api/notes";
import Swal from "sweetalert2";

export default function Home() {
    const msgStyle = {
        justifyContent: "center",
        display: "flex",
        alignItems: "center",
        height: "50vh",
        color: "#aaa",
        letterSpacing: "1px",
        fontSize: "1.3em",
    };
    const [notes, setNotes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNotes = async () => {
            try {
                const data = await getAllNotes();
                setNotes(data.content || []);
            } catch (err) {
                Swal.fire({
                    icon: 'error',
                    title: 'Oops...',
                    text: 'Failed to load notes!',
                });
            } finally {
                setLoading(false);
            }
        };
        fetchNotes();
    }, []);
    return (
        <div>
            <h1 className="headline">
                Save Your <span>Notes</span> Here
            </h1>

            <div className="cards">
                {loading ? (
                    <p style={msgStyle}>Loading...</p>
                ) : notes && notes.length > 0 ? (
                    notes.map((note) => (
                        <NoteCard key={note._id} note={note} />
                    ))
                ) : (
                    <p style={msgStyle}>No Notes To Show</p>
                )}
            </div>
            <AddNote />
        </div>
    );
}
