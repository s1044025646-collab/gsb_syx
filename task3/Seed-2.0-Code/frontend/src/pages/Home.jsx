import React, { useEffect, useState } from "react";
import AddNote from "../components/AddNote";
import NoteCard from "../components/NoteCard";
import { notesAPI } from "../api/notesAPI";
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
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchNotes = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await notesAPI.getAllNotes();
                if (data.content) {
                    setNotes(data.content);
                } else {
                    setNotes([]);
                }
            } catch (err) {
                setError(err.message || "Failed to fetch notes");
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: err.message || "Failed to fetch notes",
                });
            } finally {
                setLoading(false);
            }
        };
        fetchNotes();
    }, []);

    if (loading) {
        return (
            <div style={msgStyle}>Loading...</div>
        );
    }

    if (error) {
        return (
            <div style={msgStyle}>Error: {error}</div>
        );
    }

    return (
        <div>
            <h1 className="headline">
                Save Your <span>Notes</span> Here
            </h1>

            <div className="cards">
                {notes && notes.length > 0 ? (
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
